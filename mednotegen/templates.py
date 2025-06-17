class DoctorNoteTemplate:
    filename_prefix = "doctor_note"
    def generate(self, faker):
        name = faker.name()
        date = faker.date()
        diagnosis = faker.sentence(nb_words=6)
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
    def generate(self, faker):
        name = faker.name()
        dob = faker.date_of_birth(minimum_age=18, maximum_age=90)
        visit_date = faker.date_this_year()
        summary = faker.paragraph()
        lines = [
            f"Patient Report",
            f"Name: {name}",
            f"DOB: {dob}",
            f"Visit Date: {visit_date}",
            "\nSummary:",
            summary,
        ]
        return {"lines": lines}
