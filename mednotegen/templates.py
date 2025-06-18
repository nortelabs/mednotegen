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

        if not diagnosis:
            if HAS_HEALTHCARE:
                faker.add_provider(IndividualProvider)
                diagnosis = faker.taxonomy()
            else:
                diagnosis = faker.sentence(nb_words=6)
        if not medication:
            if HAS_HEALTHCARE:
                faker.add_provider(IndividualProvider)
                medication = faker.professional_degree_school()
            else:
                medication = faker.word().capitalize()
        lines = [
            f"Doctor Note",
            f"Date: {date}",
            f"Patient: {name}",
            f"Diagnosis: {diagnosis}",
            f"Prescribed Medication: {medication}",
            "\nInstructions:",
            faker.paragraph(),
        ]
        return {"lines": lines}

class PatientReportTemplate:
    filename_prefix = "patient_report"
    def generate(self):
        from .synthea_integration import get_random_patient_with_meds
        patient, meds = get_random_patient_with_meds()
        name = f"{patient['FIRST']} {patient['LAST']}"
        dob = patient['BIRTHDATE']
        # Synthea doesn't provide visit dates directly; use birthdate as placeholder or extend integration
        visit_date = patient.get('DEATHDATE', 'N/A')  # or use another field if available
        summary = f"Patient {name}, born {dob}. Medications: {', '.join(meds['DESCRIPTION'].unique()) if not meds.empty else 'None'}"
        lines = [
            f"Patient Report",
            f"Name: {name}",
            f"DOB: {dob}",
            f"Visit Date: {visit_date}",
            "\nSummary:",
            summary,
        ]
        return {"lines": lines}

