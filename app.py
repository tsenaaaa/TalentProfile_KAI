import base64
import os
import tempfile
import zipfile
from io import BytesIO

import pandas as pd
import streamlit as st
from fpdf import FPDF

# ========== CONFIG ==========
st.set_page_config(page_title="Profil Staff PT KAI", layout="centered")

# ========== CUSTOM STYLE ==========
def set_custom_style():
    st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
        background-color: transparent;
        color: #333333;
        transition: background-color 0.3s ease;
    }

    .stApp {
        background: url('static/bgweb.jpeg') no-repeat center center fixed;
        background-size: cover;
    }

    .main > div {
        background-color: rgba(255, 255, 255, 0.85);
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(6px);
        -webkit-backdrop-filter: blur(6px);
    }

    .big-title {
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 1.5rem;
        color: #1a1a1a;
        text-shadow: 0 1px 2px rgba(255,255,255,0.6);
    }

    .card {
        background: rgba(245, 245, 245, 0.9);
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        margin-top: 1rem;
        border: 1px solid rgba(221, 221, 221, 0.7);
        transition: box-shadow 0.3s ease;
    }

    .card:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }

    .stButton>button {
        background-color: #005a9c;
        border: none;
        color: #fff;
        padding: 0.5rem 1.25rem;
        border-radius: 4px;
        font-weight: 600;
        font-size: 1rem;
        cursor: pointer;
        box-shadow: none;
        transition: background-color 0.3s ease;
    }

    .stButton>button:hover {
        background-color: #004080;
    }

    a {
        font-weight: 600;
        color: #005a9c;
        text-decoration: none;
    }
    a:hover {
        text-decoration: underline;
    }
    </style>
    """, unsafe_allow_html=True)

set_custom_style()

# ========== FONTS ==========
FONTS_DIR = "fonts"
FONT_PATH = os.path.join(FONTS_DIR, "DejaVuSans.ttf")
FONT_BOLD_PATH = os.path.join(FONTS_DIR, "DejaVuSans-Bold.ttf")
if not os.path.exists(FONTS_DIR):
    os.makedirs(FONTS_DIR)
    st.warning("Folder 'fonts' dibuat. Letakkan file DejaVuSans.ttf dan DejaVuSans-Bold.ttf di dalamnya.")
elif not (os.path.exists(FONT_PATH) and os.path.exists(FONT_BOLD_PATH)):
    st.warning("Font Unicode belum tersedia. Harap letakkan 'DejaVuSans.ttf' dan 'DejaVuSans-Bold.ttf' di folder 'fonts'.")

# ========== PDF CLASS ==========
class CustomPDF(FPDF):
    def __init__(self):
        super().__init__()
        if os.path.exists(FONT_PATH):
            self.add_font("DejaVu", "", FONT_PATH, uni=True)
        if os.path.exists(FONT_BOLD_PATH):
            self.add_font("DejaVu", "B", FONT_BOLD_PATH, uni=True)
        self.set_font("DejaVu", "", 12)

    def draw_bounded_box(self, x, y_start, content_draw_func, fixed_height=None):
        start_page = self.page_no()
        self.set_y(y_start)
        content_draw_func()  # tulis isi di sini
        end_page = self.page_no()
        y_end = self.get_y()

        if start_page == end_page:
            # Semua isi tetap di satu halaman
            self.rect(x, y_start, 190 - 2 * x, y_end - y_start)
        else:
            if fixed_height is None:
                fixed_height = 145  # fallback tinggi default
            # Kotak di halaman pertama
            self.rect(x, y_start, 190 - 2 * x, 297 - y_start - 10)
            # Kotak di halaman berikutnya (dimulai dari atas)
            self.rect(x, 10, 190 - 2 * x, fixed_height)

    def header(self):
        try:
            self.image("logo_kai.png", 10, 8, 30)
        except:
            pass
        self.set_font("DejaVu", "B", 12)
        self.set_xy(130, 12)
        self.set_text_color(33, 64, 154)
        self.cell(0, 10, "Profil Ringkas Kandidat PT KAI", ln=0, align="R")
        self.set_text_color(0, 0, 0)

    def check_page_break(self, h):
        if self.get_y() + h > self.page_break_trigger:
            self.add_page()

    def add_profile(self, data, foto_path):
        def get_val(field):
            val = str(data.get(field, "-")).strip()
            return val if val else "-"

        self.set_xy(10, 28)
        self.rect(10, 28, 190, 255)
        self.set_xy(15, 30)
        self.set_font("DejaVu", "B", 14)
        self.cell(0, 10, get_val("Nama"), ln=True)

        y_start = 42
        if foto_path:
            try:
                self.image(foto_path, x=15, y=y_start, w=30, h=38)
            except:
                pass

        self.set_xy(50, y_start)
        self.rect(50, y_start, 135, 38)
        self.set_font("DejaVu", "B", 10)
        self.set_xy(52, y_start + 2)
        self.cell(0, 6, "TALENT CLASSIFICATION:")
        self.set_font("DejaVu", "", 10)
        self.set_xy(52, y_start + 8)
        self.multi_cell(130, 5, get_val("Talent Classification"))

        self.set_xy(52, y_start + 17)
        self.set_font("DejaVu", "B", 10)
        self.cell(0, 6, "NILAI KINERJA:")
        self.set_font("DejaVu", "", 10)
        y_score = y_start + 23
        for tahun in ["2024", "2023", "2022"]:
            self.set_xy(52, y_score)
            self.cell(0, 5, f"{tahun} : {get_val(f'Nilai Kinerja ({tahun})')}")
            y_score += 5

        y_after_box = y_start + 38 + 6
        self.set_y(y_after_box)
        self.set_x(15)
        self.set_font("DejaVu", "B", 10)
        self.multi_cell(175, 6, "BEHAVIOUR COMPETENCIES", border=1, align="C")

        y_table_start = self.get_y()

        self.set_font("DejaVu", "B", 9)
        self.set_x(15)
        self.cell(87.5, 6, "BUMN Assessment", border=1, align="C")
        self.cell(87.5, 6, "Multirater", border=1, align="C")
        self.ln()

        self.set_font("DejaVu", "", 9)
        self.set_x(15)
        self.multi_cell(87.5, 5, get_val("Behaviour Competencies BUMN"), border=1)

        y_temp = self.get_y()
        self.set_xy(102.5, y_table_start + 6)
        self.multi_cell(87.5, 5, get_val("Behaviour Competencies Multirater"), border=1)

        y_next = max(self.get_y(), y_temp) + 6

        self.set_y(y_next)
        self.set_x(15)
        self.set_font("DejaVu", "B", 10)
        self.multi_cell(175, 6, "KNOWLEDGE", border=1, align="C")
        self.set_font("DejaVu", "", 9)
        self.set_x(15)
        self.multi_cell(175, 5, get_val("Knowledge"), border=1)
        y_know = self.get_y()

        self.set_y(y_know + 6)
        self.set_x(15)
        self.set_font("DejaVu", "B", 10)
        self.cell(0, 6, "5 LATEST WORKING EXPERIENCE", ln=1)
        self.line(15, self.get_y(), 190, self.get_y())
        y_exp_start = self.get_y() + 2

        for line in get_val("Working Experience").split("\n"):
            if line.strip():
                self.check_page_break(40)
                if "(" in line and ")" in line:
                    jabatan = line.split("(")[0].strip()
                    tanggal = line[line.find("("):].strip()
                else:
                    jabatan = line.strip()
                    tanggal = ""
                self.set_x(15)
                self.set_font("DejaVu", "B", 9)
                self.cell(175, 5, jabatan, ln=1)
                if tanggal:
                    self.set_x(15)
                    self.set_font("DejaVu", "", 9)
                    self.cell(175, 5, tanggal, ln=1)
        y_exp_end = self.get_y()
        self.rect(15, y_exp_start - 8, 175, y_exp_end - y_exp_start + 10)

        y_attr_start = y_exp_end + 6
        self.set_y(y_attr_start)
        self.set_x(15)
        self.set_font("DejaVu", "B", 10)
        self.cell(0, 6, "PERSONAL ATTRIBUTES", ln=1)
        self.line(15, self.get_y(), 190, self.get_y())
        y_attr_content_start = self.get_y() + 2

        start_page = self.page_no()
        y_start = self.get_y()

        for label, field in [
            ("Tempat & Tanggal Lahir", "Tempat & Tanggal Lahir"),
            ("Usia", "Usia"),
            ("Pendidikan", "Pendidikan"),
            ("Grade", "Grade"),
            ("Penghargaan", "Penghargaan"),
        ]:
            self.set_x(16)
            self.set_font("DejaVu", "B", 9)
            self.cell(43, 5, f"{label}", ln=0)
            self.cell(6, 5, ":", ln=0)
            self.set_font("DejaVu", "", 9)
            self.multi_cell(125, 5, get_val(field))

        end_page = self.page_no()
        end_y = self.get_y()

        if start_page == end_page:
            self.rect(15, y_attr_content_start - 8, 175, end_y - y_attr_content_start + 10)
        else:
            # Tentukan tinggi tetap, misalnya sama dengan halaman pertama: 145
            frame_height = 145

            # Rect untuk halaman pertama
            self.rect(15, y_attr_content_start - 8, 175, 297 - y_attr_content_start - 10)

            # Rect untuk halaman kedua - posisikan sejajar
            self.rect(15, 10, 175, frame_height)

# ========== FILE UPLOADER ==========
with st.container():
    st.markdown("<div class='content-container'>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("📁 Unggah file Excel (.xlsx)", type="xlsx")
    st.markdown("</div>", unsafe_allow_html=True)

# ========== PROCESS ==========
if uploaded_file:
    st.markdown("<div class='content-container'>", unsafe_allow_html=True)
    df = pd.read_excel(uploaded_file)
    df.columns = [col.strip().upper() for col in df.columns]

    st.write("Kolom dari Excel:", df.columns.tolist())
    rename_dict = {
        "NAMA": "Nama",
        "TALENT CLASSIFICATION": "Talent Classification",
        "WORKING EXPERIENCE": "Working Experience",
        "NILAI KINERJA (2022)": "Nilai Kinerja (2022)",
        "NILAI KINERJA (2023)": "Nilai Kinerja (2023)",
        "NILAI KINERJA (2024)": "Nilai Kinerja (2024)",
        "BEHAVIOUR COMPETENCIES (BUMN ASSESSMENT)": "Behaviour Competencies BUMN",
        "BEHAVIOUR COMPETENCIES (MULTIRATER)": "Behaviour Competencies Multirater",
        "KNOWLEDGE": "Knowledge",
        "PERSONAL ATTRIBUTES (PLACE AND DATE OF BIRTH)": "Tempat & Tanggal Lahir",
        "PERSONAL ATTRIBUTES (AGE)": "Usia",
        "PERSONAL ATTRIBUTES (EDUCATION)": "Pendidikan",
        "PERSONAL ATTRIBUTES (GRADE)": "Grade",
        "PERSONAL ATTRIBUTES (AWARD)": "Penghargaan",
        "Tempat & Tanggal Lahir": "Tempat & Tanggal Lahir",
        "PHOTO": "Foto"
    }
    # Gabungkan Tempat & Tanggal Lahir jadi satu kolom baru
    df["Tempat & Tanggal Lahir"] = df["PERSONAL ATTRIBUTES (BIRTHPLACE)"].astype(str) + ", " + df["PERSONAL ATTRIBUTES (DATE OF BIRTH)"].astype(str)

    available_cols = [k for k in rename_dict if k in df.columns]
    df_cleaned = df[available_cols].rename(columns={k: rename_dict[k] for k in available_cols})

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.caption("Preview data berhasil dimuat")
    st.dataframe(df_cleaned, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if "Nama" in df_cleaned.columns:
        st.markdown("<div class='card'>", unsafe_allow_html=True)

        selected_name = st.selectbox("Pilih nama staff", df_cleaned["Nama"].dropna().unique(), index=0)

        generate_pdf = st.button("📄 Generate & Unduh PDF")

        if generate_pdf:
            data = df_cleaned[df_cleaned["Nama"] == selected_name].iloc[0]

            pdf = CustomPDF()
            pdf.add_page()

            foto_file = str(data.get("Foto", "")).strip()
            img_path = os.path.join("Foto Talent Profile", foto_file) if foto_file else None
            if not (img_path and os.path.isfile(img_path)):
                img_path = None

            pdf.add_profile(data, img_path)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
                pdf.output(tmpfile.name)
                with open(tmpfile.name, "rb") as f:
                    base64_pdf = base64.b64encode(f.read()).decode("utf-8")
                    st.markdown(
                        f'<a href="data:application/pdf;base64,{base64_pdf}" download="Profil_{selected_name}.pdf">📅 Klik untuk Unduh PDF</a>',
                        unsafe_allow_html=True
                    )

        # New feature: Download all PDFs
        if st.button("📦 Unduh Semua PDF"):
            with tempfile.TemporaryDirectory() as tmpdirname:
                zip_path = os.path.join(tmpdirname, "profil_staff.zip")
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for name in df_cleaned["Nama"].dropna().unique():
                        data = df_cleaned[df_cleaned["Nama"] == name].iloc[0]
                        pdf = CustomPDF()
                        pdf.add_page()
                        img_path = os.path.join("Foto Talent Profile", str(data.get("Foto", "")).strip())
                        pdf.add_profile(data, img_path)

                        pdf_file_path = os.path.join(tmpdirname, f"Profil_{name}.pdf")
                        pdf.output(pdf_file_path)
                        zipf.write(pdf_file_path, arcname=f"Profil_{name}.pdf")

                with open(zip_path, "rb") as f:
                    base64_zip = base64.b64encode(f.read()).decode("utf-8")
                    st.markdown(
                        f'<a href="data:application/zip;base64,{base64_zip}" download="profil_staff.zip">📦 Klik untuk Unduh Semua PDF</a>',
                        unsafe_allow_html=True
                    )

        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.error("Kolom 'Nama' tidak tersedia dalam file Excel.")
else:
    st.info("Silakan unggah file Excel terlebih dahulu.")