import os
import subprocess
import pandas as pd

SYNTHEA_DIR = os.path.join(os.path.dirname(__file__), '..', 'synthea')
SYNTHEA_JAR = os.path.join(SYNTHEA_DIR, 'synthea-with-dependencies.jar')
OUTPUT_CSV_DIR = os.path.join(SYNTHEA_DIR, 'output', 'csv')

def run_synthea(num_patients=10, state="Massachusetts", city=None, seed=None, reference_date=None, clinician_seed=None, gender=None, min_age=None, max_age=None, modules=None, local_config=None, local_modules=None):
    """Run Synthea to generate synthetic patient data with advanced options."""
    if not os.path.exists(SYNTHEA_JAR):
        raise FileNotFoundError(
            f"""
Synthea JAR not found at {SYNTHEA_JAR}.

To use mednotegen, you must first clone and build Synthea:

  git clone https://github.com/synthetichealth/synthea.git
  cd synthea
  ./gradlew build check test
  cp build/libs/synthea-with-dependencies.jar .
  cd ..

Then ensure synthea-with-dependencies.jar is located at: {SYNTHEA_JAR}
            """)
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
        raise RuntimeError(f"Synthea failed: {result.stderr}\nSTDOUT:\n{result.stdout}")
    print("Synthea data generated successfully.")
    return result

# Synthea module to SNOMED/ICD code mapping for filtering
MODULE_TO_CODES = {
    # Comprehensive (non-exhaustive) lists of SNOMED CT condition codes emitted by Synthea for each module.
    # Sources: Synthea module JSON files & sample CSV exports.
    "cardiovascular-disease": [
        "22298006",  # Myocardial infarction
        "44054006",  # Diabetes mellitus (also used as CVD risk factor)
        "49601007",  # Coronary arteriosclerosis
        "414545008", # Heart failure
        "230690007", # Stroke
        "195080001", # Angina pectoris
        "394659003", # Chronic ischemic heart disease
        "703122007", # Atrial fibrillation
        "1755008",   # Pulmonary embolism
        "194828000", # Hypertensive disorder
    ],
    "diabetes": [
        "44054006",  # Diabetes mellitus
        "73211009",  # Type 2 diabetes mellitus
        "46635009",  # Type 1 diabetes mellitus
        "237599002", # Prediabetes
        "443238003", # Gestational diabetes mellitus
        "190330002", # Diabetic ketoacidosis
        "313435000", # Diabetic neuropathy
        "127013003", # Diabetic retinopathy
        "237617002", # Impaired glucose tolerance
        "59282003",  # Hyperglycemia
    ],
}

def load_synthea_patients(synthea_csv_dir=None):
    """Load Synthea-generated patient and medication data as pandas DataFrames. If missing, auto-generate with Synthea."""
    csv_dir = synthea_csv_dir or OUTPUT_CSV_DIR
    patients_csv = os.path.join(csv_dir, 'patients.csv')
    medications_csv = os.path.join(csv_dir, 'medications.csv')
    conditions_csv = os.path.join(csv_dir, 'conditions.csv')
    required_files = [patients_csv, medications_csv, conditions_csv]
    if not all(os.path.exists(f) for f in required_files):
        print(f"Synthea patient data not found. Expected in: {csv_dir}. Running Synthea to generate data...")
        result = run_synthea(num_patients=10, state="Massachusetts")
        print(f"Checking for required Synthea CSVs in: {csv_dir}")
        if os.path.exists(csv_dir):
            print("Contents of Synthea output directory:")
            for fname in os.listdir(csv_dir):
                print("  ", fname)
        else:
            print("Synthea output directory does not exist:", csv_dir)
        if not all(os.path.exists(f) for f in required_files):
            print("Synthea stdout:\n", result.stdout)
            print("Synthea stderr:\n", result.stderr)
            missing = [os.path.basename(f) for f in required_files if not os.path.exists(f)]
            raise FileNotFoundError(f"Synthea patient data could not be generated. Missing files: {missing}. Check Synthea installation and output above.")
    patients = pd.read_csv(patients_csv)
    medications = pd.read_csv(medications_csv)
    conditions = pd.read_csv(conditions_csv)
    careplans_csv = os.path.join(csv_dir, 'careplans.csv')
    if os.path.exists(careplans_csv):
        careplans = pd.read_csv(careplans_csv)
    else:
        careplans = pd.DataFrame()
    return patients, medications, conditions, careplans

def get_random_patient_with_meds(gender=None, min_age=None, max_age=None, modules=None, reference_date=None, synthea_csv_dir=None):
    """Get a random patient and their medications from Synthea data, with demographic and module filtering."""
    import numpy as np
    from datetime import datetime
    patients, medications, conditions, careplans = load_synthea_patients(synthea_csv_dir=synthea_csv_dir)
    filtered_patients = patients.copy()
    # Gender filter (accepts 'F', 'M', 'female', 'male', case-insensitive)
    if gender:
        gender_str = str(gender).strip().lower()
        # Map short forms to full
        if gender_str in ["f", "female"]:
            allowed = ["female", "f"]
        elif gender_str in ["m", "male"]:
            allowed = ["male", "m"]
        else:
            allowed = None
        if allowed:
            filtered_patients = filtered_patients[filtered_patients['GENDER'].str.lower().isin(allowed)]
    # Age filter
    if min_age is not None or max_age is not None:
        # Use reference_date if provided, else today
        if reference_date is not None:
            try:
                ref_dt = datetime.strptime(str(reference_date), "%Y%m%d")
            except Exception:
                ref_dt = datetime.today()
        else:
            ref_dt = datetime.today()
        def calc_age(dob):
            try:
                return (ref_dt - datetime.strptime(str(dob)[:10], "%Y-%m-%d")).days // 365
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
        # If no patients match after module filtering, relax this filter but keep gender and age filters
        if filtered_patients.empty:
            filtered_patients = patients.copy()
            # re-apply gender filter
            if gender and gender.lower() in ("male", "female"):
                gender_map = {"female": ["female", "f"], "male": ["male", "m"]}
                allowed = gender_map[gender.lower()]
                filtered_patients = filtered_patients[filtered_patients['GENDER'].str.lower().isin(allowed)]
            # re-apply age filter
            if min_age is not None or max_age is not None:
                if reference_date is not None:
                    try:
                        ref_dt = datetime.strptime(str(reference_date), "%Y%m%d")
                    except Exception:
                        ref_dt = datetime.today()
                else:
                    ref_dt = datetime.today()
                def calc_age(dob):
                    try:
                        return (ref_dt - datetime.strptime(str(dob)[:10], "%Y-%m-%d")).days // 365
                    except Exception:
                        return np.nan
                filtered_patients['AGE'] = filtered_patients['BIRTHDATE'].apply(calc_age)
                if min_age is not None:
                    filtered_patients = filtered_patients[filtered_patients['AGE'] >= min_age]
                if max_age is not None:
                    filtered_patients = filtered_patients[filtered_patients['AGE'] <= max_age]
    if filtered_patients.empty:
        raise ValueError("No patients found matching the specified filters.")
    patient = filtered_patients.sample(1).iloc[0]
    patient_id = patient['Id']
    patient_meds = medications[medications['PATIENT'] == patient_id]
    patient_conditions = conditions[conditions['PATIENT'] == patient_id]
    patient_careplans = careplans[careplans['PATIENT'] == patient_id] if not careplans.empty else pd.DataFrame()
    return patient, patient_meds, patient_conditions, patient_careplans
