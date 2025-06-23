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
        from .synthea_integration import get_random_patient_with_meds
        patient, meds = get_random_patient_with_meds()
        # Remove trailing digits from names
        def strip_digits(s):
            return re.sub(r'\d+$', '', str(s)).strip()
        name = f"{strip_digits(patient['FIRST'])} {strip_digits(patient['LAST'])}"
        dob = patient['BIRTHDATE']
        # Try to use the most recent medication start date as visit date, else birthdate
        visit_date = dob
        if not meds.empty and 'START' in meds.columns:
            valid_dates = meds['START'].dropna()
            if not valid_dates.empty:
                visit_date = valid_dates.max()
        # Remove time from visit_date if present
        import re
        visit_date = re.sub(r'T.*', '', str(visit_date))
        # Format medications as a line-separated list
        if not meds.empty:
            med_lines = [f"- {desc}" for desc in meds['DESCRIPTION'].unique() if desc and str(desc).strip()]
        # Build lines with each medication as its own line
        lines = [
            f"Patient Report",
            f"Name: {name}",
            f"DOB: {dob}",
            f"Visit Date: {visit_date}",
            "",
            "Summary:",
            "Medications Prescribed:"
        ]
        if med_lines:
            lines.extend(med_lines)
        return {"lines": lines}

