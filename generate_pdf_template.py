from fpdf import FPDF

class ProfileTemplatePDF(FPDF):
    def __init__(self, name, data):
        super().__init__()
        self.name = name
        self.data = data
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()
        self.build_template()

    def build_template(self):
        self.add_profile_box()

    def add_profile_box(self):
        self.set_fill_color(255, 255, 255)
        self.set_draw_color(200, 200, 200)
        self.rect(10, 20, 190, 260, 'DF')  # white box with border

        self.set_xy(15, 25)
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(13, 71, 161)
        self.cell(0, 10, f"Ringkasan Profil: {self.name}", ln=True)

        self.set_text_color(0, 0, 0)
        self.set_font("Helvetica", "B", 12)
        self.ln(2)
        self.cell(0, 8, "TALENT CLASSIFICATION", ln=True)
        self.set_font("Helvetica", "", 11)
        self.multi_cell(0, 6, f"- 2024: {self.data['Tahun_2024']}\n- 2023: {self.data['Tahun_2023']}\n- 2022: {self.data['Tahun_2022']}")

        self.ln(3)
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 8, "BEHAVIOUR COMPETENCIES", ln=True)
        self.set_font("Helvetica", "", 11)
        self.multi_cell(0, 6, f"- Asesmen Skor BUMN: {self.data['Skor_Asesmen']}\n- Multirater: {self.data['Skor_Multirater']}")

        # Draw box around KNOWLEDGE section
        knowledge_x = 10
        knowledge_y = self.get_y() + 3
        knowledge_w = 190
        knowledge_h = 40  # approximate height for knowledge box
        self.rect(knowledge_x, knowledge_y, knowledge_w, knowledge_h)

        self.set_xy(knowledge_x + 5, knowledge_y + 3)
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 8, "KNOWLEDGE", ln=True)
        self.set_font("Helvetica", "", 11)
        knowledge = [
            "Directorship Program IICD",
            "AI for Business Leaders ITB",
            "Driving corporate transformation with Growth Mindset ILM",
            "The 8 Characters of Transformational Leadership ILM",
            "Leading with Happiness ILM"
        ]
        knowledge_text = "\n".join([f"- {k}" for k in knowledge])
        self.multi_cell(knowledge_w - 10, 6, knowledge_text)

        # Draw box around PERSONAL ATTRIBUTES section
        personal_x = 10
        personal_y = self.get_y() + 3
        personal_w = 190
        personal_h = 50  # approximate height for personal attributes box
        self.rect(personal_x, personal_y, personal_w, personal_h)

        self.set_xy(personal_x + 5, personal_y + 3)
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 8, "PERSONAL ATTRIBUTES", ln=True)
        self.set_font("Helvetica", "", 11)
        tempat_lahir = self.data.get('Tempat_Lahir', '')
        self.multi_cell(personal_w - 10, 6, f"- Tempat & Tanggal Lahir: {tempat_lahir} {self.data['Tgl_Lahir']} ({self.data['Usia']} tahun)\n- Pendidikan: {self.data['Pendidikan']}\n- Grade: _\n- Penghargaan Masa Kerja 25 Tahun\n- Penghargaan Masa Kerja 30 Tahun")

        self.ln(3)
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 8, "5 LATEST WORKING EXPERIENCE", ln=True)
        self.set_font("Helvetica", "", 11)
        for i in range(1, 6):
            jab = self.data[f"Jabatan_{i}"]
            per = self.data[f"Periode_{i}"]
            self.multi_cell(0, 6, f"{i}. {jab} ({per})")

        self.ln(5)
        self.set_font("Helvetica", "I", 9)
        self.cell(0, 10, "Usulan Perubahan Pengurus Anak Perusahaan PT KAI", ln=True, align="C")
