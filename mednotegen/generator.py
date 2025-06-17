from .templates import DoctorNoteTemplate, PatientReportTemplate
from .pdf_utils import PDFGenerator
from .llm_utils import LLMGenerator
from faker import Faker
import os

class NoteGenerator:
    def __init__(self, note_type: str, use_llm: bool = False):
        self.note_type = note_type
        self.use_llm = use_llm
        self.faker = Faker()
        if note_type == "doctor_note":
            self.template = DoctorNoteTemplate()
        elif note_type == "patient_report":
            self.template = PatientReportTemplate()
        else:
            raise ValueError("Invalid note type.")
        self.llm = LLMGenerator() if use_llm else None

    def generate_note_data(self):
        if self.use_llm and self.llm:
            content = self.llm.generate_note(self.note_type)
            lines = content.split("\n")
            return {"lines": lines}
        else:
            return self.template.generate(self.faker)

    def generate_notes(self, n, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        pdfgen = PDFGenerator()
        for i in range(n):
            data = self.generate_note_data()
            filename = os.path.join(output_dir, f"{self.template.filename_prefix}_{i+1}.pdf")
            pdfgen.create_pdf(data, filename)
