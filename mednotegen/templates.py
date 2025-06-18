import random

try:
    from provider_individual import IndividualProvider
    HAS_HEALTHCARE = True
except ImportError:
    HAS_HEALTHCARE = False

import os

def sample_from_file(filepath):
    try:
        with open(filepath, "r") as f:
            items = [line.strip() for line in f if line.strip()]
        if items:
            return random.choice(items)
    except Exception:
        pass
    return None

class DoctorNoteTemplate:
    filename_prefix = "doctor_note"
    def generate(self, faker):
        name = faker.name()
        date = faker.date()
        # Prefer public data files if available
        diagnosis = sample_from_file(os.path.join(os.path.dirname(__file__), "../data/diagnoses.txt"))
        medication = sample_from_file(os.path.join(os.path.dirname(__file__), "../data/medications.txt"))
        # Fallbacks
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
    def generate(self, faker):
        name = faker.name()
        dob = faker.date_of_birth(minimum_age=18, maximum_age=90)
        visit_date = faker.date_this_year()
        if HAS_HEALTHCARE:
            faker.add_provider(IndividualProvider)
            diagnosis = faker.taxonomy()
            summary = f"Diagnosis: {diagnosis}. " + faker.paragraph()
        else:
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
