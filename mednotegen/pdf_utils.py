from fpdf import FPDF

class PDFGenerator:
    def create_pdf(self, data, filename):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        for line in data["lines"]:
            pdf.cell(0, 10, line, ln=True)
        pdf.output(filename)
