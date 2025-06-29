import os
import subprocess
import pandas as pd

SYNTHEA_DIR = os.path.join(os.path.dirname(__file__), '..', 'synthea')
SYNTHEA_JAR = os.path.join(SYNTHEA_DIR, 'synthea-with-dependencies.jar')
OUTPUT_CSV_DIR = os.path.join(SYNTHEA_DIR, 'output', 'csv')

def run_synthea(num_patients=10, state="Massachusetts", city=None, seed=None, reference_date=None, clinician_seed=None, gender=None, min_age=None, max_age=None, modules=None, local_config=None, local_modules=None):
    """Run Synthea to generate synthetic patient data with advanced options."""
    if not os.path.exists(SYNTHEA_JAR):
        raise FileNotFoundError(f"Synthea JAR not found at {SYNTHEA_JAR}. Please download Synthea and place the JAR here.")
    cmd = ["java", "-jar", SYNTHEA_JAR]
    if seed is not None:
        cmd += ["-s", str(seed)]
    if reference_date is not None:
        cmd += ["-r", str(reference_date)]
    if clinician_seed is not None:
        cmd += ["-cs", str(clinician_seed)]
    if gender is not None:
        cmd += ["-g", gender]
    if min_age is not None and max_age is not None:
        cmd += ["-a", f"{min_age}-{max_age}"]
    if modules:
        cmd += ["-m", ','.join(modules)]
    if local_config is not None:
        cmd += ["-c", local_config]
    if local_modules is not None:
        cmd += ["-d", local_modules]
    cmd += ["-p", str(num_patients)]
    if state:
        cmd.append(state)
    if city:
        cmd.append(city)
    result = subprocess.run(cmd, cwd=SYNTHEA_DIR, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Synthea failed: {result.stderr}")
    print("Synthea data generated successfully.")

# Synthea module to SNOMED/ICD code mapping for filtering
MODULE_TO_CODES = {
    "cardiovascular-disease": ["44054006", "49601007", "22298006"],  # Example SNOMED codes for CVD
    "diabetes": ["44054006", "73211009"],
    # Add more modules and codes as needed
}

def load_synthea_patients():
    """Load Synthea-generated patient and medication data as pandas DataFrames. If missing, auto-generate with Synthea."""
    patients_csv = os.path.join(OUTPUT_CSV_DIR, 'patients.csv')
    medications_csv = os.path.join(OUTPUT_CSV_DIR, 'medications.csv')
    conditions_csv = os.path.join(OUTPUT_CSV_DIR, 'conditions.csv')
    if not os.path.exists(patients_csv) or not os.path.exists(medications_csv) or not os.path.exists(conditions_csv):
        print("Synthea patient data not found. Running Synthea to generate data...")
        run_synthea(num_patients=10, state="Massachusetts")
    if not os.path.exists(patients_csv) or not os.path.exists(medications_csv) or not os.path.exists(conditions_csv):
        raise FileNotFoundError("Synthea patient data could not be generated. Check Synthea installation.")
    patients = pd.read_csv(patients_csv)
    medications = pd.read_csv(medications_csv)
    conditions = pd.read_csv(conditions_csv)
    return patients, medications, conditions

def get_random_patient_with_meds(gender=None, min_age=None, max_age=None, modules=None):
    """Get a random patient and their medications from Synthea data, with demographic and module filtering."""
    import numpy as np
    from datetime import datetime
    patients, medications, conditions = load_synthea_patients()
    filtered_patients = patients.copy()
    # Gender filter
    if gender and gender.lower() in ("male", "female"):
        filtered_patients = filtered_patients[filtered_patients['GENDER'].str.lower() == gender.lower()]
    # Age filter
    if min_age is not None or max_age is not None:
        today = datetime.today()
        def calc_age(dob):
            try:
                return (today - datetime.strptime(str(dob)[:10], "%Y-%m-%d")).days // 365
            except Exception:
                return np.nan
        filtered_patients['AGE'] = filtered_patients['BIRTHDATE'].apply(calc_age)
        if min_age is not None:
            filtered_patients = filtered_patients[filtered_patients['AGE'] >= min_age]
        if max_age is not None:
            filtered_patients = filtered_patients[filtered_patients['AGE'] <= max_age]
    # Module filter (only include patients with at least one condition code in the module)
    if modules:
        all_codes = set()
        for mod in modules:
            all_codes.update(MODULE_TO_CODES.get(mod, []))
        # Find patient IDs with at least one matching condition code
        matching_ids = set(conditions[conditions['CODE'].astype(str).isin(all_codes)]['PATIENT'])
        filtered_patients = filtered_patients[filtered_patients['Id'].isin(matching_ids)]
    if filtered_patients.empty:
        raise ValueError("No patients found matching the specified filters.")
    patient = filtered_patients.sample(1).iloc[0]
    patient_id = patient['Id']
    patient_meds = medications[medications['PATIENT'] == patient_id]
    patient_conditions = conditions[conditions['PATIENT'] == patient_id]
    return patient, patient_meds, patient_conditions
