import os
import subprocess
import pandas as pd

SYNTHEA_DIR = os.path.join(os.path.dirname(__file__), '..', 'synthea')
SYNTHEA_JAR = os.path.join(SYNTHEA_DIR, 'synthea-with-dependencies.jar')
OUTPUT_CSV_DIR = os.path.join(SYNTHEA_DIR, 'output', 'csv')

def run_synthea(num_patients=10, state="Massachusetts"):
    """Run Synthea to generate synthetic patient data."""
    if not os.path.exists(SYNTHEA_JAR):
        raise FileNotFoundError(f"Synthea JAR not found at {SYNTHEA_JAR}. Please download Synthea and place the JAR here.")
    cmd = [
        "java", "-jar", SYNTHEA_JAR,
        "-p", str(num_patients), state
    ]
    result = subprocess.run(cmd, cwd=SYNTHEA_DIR, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Synthea failed: {result.stderr}")
    print("Synthea data generated successfully.")

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

def get_random_patient_with_meds():
    """Get a random patient and their medications from Synthea data."""
    patients, medications, conditions = load_synthea_patients()
    patient = patients.sample(1).iloc[0]
    patient_id = patient['Id']
    patient_meds = medications[medications['PATIENT'] == patient_id]
    patient_conditions = conditions[conditions['PATIENT'] == patient_id]
    return patient, patient_meds, patient_conditions
