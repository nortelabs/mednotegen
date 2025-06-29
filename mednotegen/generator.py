from .templates import DoctorNoteTemplate, PatientReportTemplate
from .pdf_utils import PDFGenerator
from .llm_utils import LLMGenerator
import os

import yaml

class NoteGenerator:
    def __init__(self, note_type: str = "patient_report", use_llm: bool = False):
        self.note_type = note_type
        self.use_llm = use_llm
        if note_type == "doctor_note":
            self.template = DoctorNoteTemplate()
        elif note_type == "patient_report":
            self.template = PatientReportTemplate()
        else:
            raise ValueError("Invalid note type.")
        self.llm = LLMGenerator() if use_llm else None

    @classmethod
    def from_config(cls, config_path: str):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        # Accept keys: note_type, use_llm, etc.
        return cls(
            note_type=config.get('note_type', 'patient_report'),
            use_llm=config.get('use_llm', False),
        )

    def generate_note_data(self):
        if self.use_llm and self.llm:
            content = self.llm.generate_note(self.note_type)
            lines = content.split("\n")
            return {"lines": lines}
        else:
            return self.template.generate()

    def generate_notes(self, n, output_dir):
        os.makedirs(output_dir, exist_ok=True)
        pdfgen = PDFGenerator()
        for i in range(n):
            data = self.generate_note_data()
            filename = os.path.join(output_dir, f"{self.template.filename_prefix}_{i+1}.pdf")
            pdfgen.create_pdf(data, filename)
