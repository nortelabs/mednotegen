from .synthea_integration import get_random_patient_with_meds

class DoctorNoteTemplate:
    filename_prefix = "doctor_note"
    def generate(self):
        patient, meds = get_random_patient_with_meds()
        name = f"{patient['FIRST']} {patient['LAST']}"
        date = patient['BIRTHDATE']
        diagnosis = patient.get('CONDITION', 'N/A')  # Synthea doesn't directly provide, may need conditions.csv
        medication = ', '.join(meds['DESCRIPTION'].unique()) if not meds.empty else "None"
        instructions = "Take medications as prescribed. Follow up as needed."
        lines = [
            f"Doctor Note",
            f"Date: {date}",
            f"Patient: {name}",
            f"Diagnosis: {diagnosis}",
            f"Prescribed Medication: {medication}",
            "\nInstructions:",
            instructions,
        ]
        return {"lines": lines}

class PatientReportTemplate:
    filename_prefix = "patient_report"
    def generate(self):
        import re
        from datetime import datetime
        from .synthea_integration import get_random_patient_with_meds
        patient, meds = get_random_patient_with_meds()

        # Helper to strip trailing digits from names
        def strip_digits(s):
            return re.sub(r'\d+$', '', str(s)).strip()

        name = f"{strip_digits(patient['FIRST'])} {strip_digits(patient['LAST'])}"
        dob = patient['BIRTHDATE']
        sex = patient.get('GENDER', 'Unknown').capitalize()
        # Calculate age if possible
        try:
            birth_year = int(dob[:4])
            birth_month = int(dob[5:7])
            birth_day = int(dob[8:10])
            today = datetime.now()
            age = today.year - birth_year - ((today.month, today.day) < (birth_month, birth_day))
            age_str = f"{age} yrs"
        except Exception:
            age_str = "-"

        # Visit date: most recent med start or today
        visit_date = dob
        if not meds.empty and 'START' in meds.columns:
            valid_dates = meds['START'].dropna()
            if not valid_dates.empty:
                visit_date = str(valid_dates.max())
        visit_date = re.sub(r'T.*', '', str(visit_date))

        # Format medications as a line-separated list
        med_lines = []
        if not meds.empty and 'DESCRIPTION' in meds.columns:
            med_lines = [f"  - {desc}" for desc in meds['DESCRIPTION'].unique() if desc and str(desc).strip()]
        else:
            med_lines = ["  None"]

        # Header block
        lines = [
            "="*70,
            f"PATIENT VISIT SUMMARY",
            "="*70,
            f"Name: {name}    Age: {age_str}    Sex: {sex}    DOB: {dob}",
            f"Visit Date: {visit_date}",
            "-"*70,
            "",
            "Summary:",
            "",
            "Medications Prescribed:",
        ]
        lines.extend(med_lines)
        lines.append("\n" + "-"*70)
        lines.append("End of Report")
        lines.append("="*70)
        return {"lines": lines}
