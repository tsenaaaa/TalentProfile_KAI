
from fpdf import FPDF

class CustomPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.add_font('DejaVu', '', 'fonts/DejaVuSans.ttf', uni=True)
        self.add_font('DejaVu', 'B', 'fonts/DejaVuSans-Bold.ttf', uni=True)
        self.set_font('DejaVu', '', 12)

    def header(self):
        self.set_font('DejaVu', 'B', 14)
        self.cell(0, 10, 'Profil Staff PT KAI', ln=True, align='C')
        self.ln(5)

    def draw_bounded_box(self, title, content_lines, x, y, w, max_h):
        self.set_xy(x, y)
        self.set_font('DejaVu', 'B', 12)
        self.cell(w, 10, title, 0, ln=1)
        self.set_font('DejaVu', '', 11)

        start_y = self.get_y()
        for line in content_lines:
            if self.get_y() > 270:
                self.add_page()
                self.set_y(40)
            self.multi_cell(w, 8, line, border=0)

        box_bottom_y = self.get_y()
        self.rect(x, start_y - 10, w, box_bottom_y - (start_y - 10))

    def add_profile(self, data, img_path=None):
        if img_path:
            self.image(img_path, x=160, y=30, w=30)

        self.set_font('DejaVu', 'B', 12)
        self.cell(0, 10, f"Nama: {data.get('Nama', '-')}", ln=True)
        self.set_font('DejaVu', '', 11)

        self.ln(3)
        self.cell(0, 8, f"Talent Classification: {data.get('Talent Classification', '-')}", ln=True)
        self.cell(0, 8, f"Nilai Kinerja (2022): {data.get('Nilai Kinerja (2022)', '-')}", ln=True)
        self.cell(0, 8, f"Nilai Kinerja (2023): {data.get('Nilai Kinerja (2023)', '-')}", ln=True)
        self.cell(0, 8, f"Nilai Kinerja (2024): {data.get('Nilai Kinerja (2024)', '-')}", ln=True)

        self.ln(5)
        working_exp = str(data.get('Working Experience', '-'))
        working_exp_lines = working_exp.split('\n')
        self.draw_bounded_box("Working Experience", working_exp_lines, x=10, y=self.get_y(), w=190, max_h=100)

        self.ln(5)
        self.cell(0, 8, "Behaviour Competencies", ln=True)
        self.cell(0, 8, f"- BUMN Assessment: {data.get('Behaviour Competencies BUMN', '-')}", ln=True)
        self.cell(0, 8, f"- Multirater: {data.get('Behaviour Competencies Multirater', '-')}", ln=True)

        self.ln(5)
        knowledge = str(data.get('Knowledge', '-')).split('\n')
        self.draw_bounded_box("Knowledge", knowledge, x=10, y=self.get_y(), w=190, max_h=100)

        self.ln(5)
        self.cell(0, 8, f"Tgl Lahir: {data.get('Tgl Lahir', '-')}", ln=True)
        self.cell(0, 8, f"Usia: {data.get('Usia', '-')}", ln=True)
        self.cell(0, 8, f"Pendidikan: {data.get('Pendidikan', '-')}", ln=True)
        self.cell(0, 8, f"Grade: {data.get('Grade', '-')}", ln=True)
        self.multi_cell(0, 8, f"Penghargaan: {data.get('Penghargaan', '-')}", ln=True)