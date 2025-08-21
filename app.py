import base64
import io
import os
import tempfile
import zipfile
from datetime import datetime

import pandas as pd
import streamlit as st
from fpdf import FPDF

# ========== PAGE CONFIG ==========
st.set_page_config(page_title="Profil Staff PT KAI", layout="wide", initial_sidebar_state="expanded")

# ========== CSS INJECTION ==========
st.markdown("""
<style>
    body {
        font-family: 'Segoe UI', sans-serif;
        color: #333;
    }
    .stApp {
        background: linear-gradient(rgba(255,255,255,0.95), rgba(255,255,255,0.95)), 
                    url('BGfoto.jpg') no-repeat center center fixed;
        background-size: cover;
    }
    .stButton > button {
        background: linear-gradient(90deg, #FF6600, #e65c00);
        color: white;
        border-radius: 8px;
        padding: 0.6rem 1.4rem;
        font-weight: 600;
        font-size: 1rem;
        border: none;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #e65c00, #cc5200);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# ========== CUSTOM CSS ==========
def inject_custom_css():
    st.markdown("""
    <style>
        /* Global font & colors */
        html, body, [class*="css"] {
            font-family: 'Segoe UI', sans-serif;
            color: #333;
        }
        /* Background with image overlay */
        .stApp {
            background: linear-gradient(rgba(255,255,255,0.95), rgba(255,255,255,0.95)), 
                        url('BGfoto.jpg') no-repeat center center fixed;
            background-size: cover;
        }
        /* Header */
        .main-header {
            background: linear-gradient(90deg, #003366, #FF6600);
            padding: 1.2rem;
            border-radius: 12px;
            color: white;
            text-align: center;
            font-size: 1.8rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 20px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.15);
        }
        .main-header img {
            height: 70px;
            filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.3));
            background-color: rgba(255,255,255,0.1);
            padding: 8px;
            border-radius: 8px;
        }
        /* Card */
        .info-card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
            margin-top: 1.5rem;
        }
        /* Modern button */
        div.stButton > button {
            background: linear-gradient(90deg, #FF6600, #e65c00);
            color: white;
            border-radius: 8px;
            padding: 0.6rem 1.4rem;
            font-weight: 600;
            font-size: 1rem;
            border: none;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        div.stButton > button:hover {
            background: linear-gradient(90deg, #e65c00, #cc5200);
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        /* Dataframe style */
        .dataframe {
            border-radius: 8px;
            border: 1px solid #ddd;
            overflow: hidden;
        }
    </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# ========== HEADER ==========
import os

logo_path = os.path.join(os.getcwd(), "logo_kai.png")

# Create header with logo using Streamlit columns for better display
col1, col2, col3 = st.columns([1, 3, 1])

with col2:
    if os.path.exists(logo_path):
        st.image(logo_path, width=100)
    else:
        st.error("Logo KAI tidak ditemukan")
    

# ========== FONTS ==========
FONTS_DIR = "fonts"
FONT_PATH = os.path.join(FONTS_DIR, "DejaVuSans.ttf")
FONT_BOLD_PATH = os.path.join(FONTS_DIR, "DejaVuSans-Bold.ttf")
if not os.path.exists(FONTS_DIR):
    os.makedirs(FONTS_DIR)
    st.warning("Folder 'fonts' dibuat. Letakkan file DejaVuSans.ttf dan DejaVuSans-Bold.ttf di dalamnya.")
elif not (os.path.exists(FONT_PATH) and os.path.exists(FONT_BOLD_PATH)):
    st.warning("Font Unicode belum tersedia. Harap letakkan 'DejaVuSans.ttf' dan 'DejaVuSans-Bold.ttf' di folder 'fonts'.")

# ========== DATE FORMATTER ==========
class DateFormatter:
    @staticmethod
    def format_date(date_input, output_format="%d %B %Y"):
        """
        Bisa baca tanggal dari berbagai format:
        - Excel datetime
        - Pandas Timestamp
        - String manual (12/05/1999, 12 Mei 1999, 1999-05-12, dll)
        """
        import pandas as pd

        if pd.isna(date_input) or str(date_input).strip() == "":
            return "-"

        # Kalau datetime atau Timestamp
        if isinstance(date_input, (datetime, pd.Timestamp)):
            return date_input.strftime(output_format)

        # Kalau string
        date_str = str(date_input).strip()

        # Coba berbagai format umum
        possible_formats = [
            "%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d %B %Y", "%d %b %Y"
        ]
        for fmt in possible_formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime(output_format)
            except:
                continue

        # Kalau gagal parsing → kembalikan apa adanya
        return date_str

# ========== PDF CLASS ==========
class CustomPDF(FPDF):
    def __init__(self):
        super().__init__()
        if os.path.exists(FONT_PATH):
            self.add_font("DejaVu", "", FONT_PATH, uni=True)
        if os.path.exists(FONT_BOLD_PATH):
            self.add_font("DejaVu", "B", FONT_BOLD_PATH, uni=True)
        self.set_font("DejaVu", "", 12)

    def header(self):
        try:
            # Use absolute path for logo to ensure it loads correctly
            import os
            logo_path = os.path.join(os.getcwd(), "logo_kai.png")
            if os.path.exists(logo_path):
                # Add white background rectangle for better logo visibility
                self.set_fill_color(255, 255, 255)
                self.rect(8, 6, 36, 20, 'F')
                self.image(logo_path, 10, 8, 32)
        except Exception as e:
            # Fallback if logo can't be loaded
            self.set_font("DejaVu", "B", 12)
            self.set_xy(130, 12)
            self.cell(0, 10, "PT KAI", ln=0, align="R")
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

        for label, field in [
            ("Tempat & Tanggal Lahir", "Tempat & Tanggal Lahir"),
            ("Usia", "Usia"),
            ("Pendidikan", "Pendidikan"),
            ("Grade", "Grade"),
            ("Penghargaan", "Penghargaan"),
            ("Hukuman Disiplin", "Hukuman Disiplin"),
        ]:
            self.set_x(16)
            self.set_font("DejaVu", "B", 9)
            self.cell(43, 5, f"{label}", ln=0)
            self.cell(6, 5, ":", ln=0)
            self.set_font("DejaVu", "", 9)
            self.multi_cell(125, 5, get_val(field))

        end_y = self.get_y()
        self.rect(15, y_attr_content_start - 8, 175, end_y - y_attr_content_start + 10)

# ========== FILE UPLOADER ==========
with st.container():
    st.markdown("<div class='info-card'>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("📁 Unggah file Excel (.xlsx)", type="xlsx")
    st.markdown("</div>", unsafe_allow_html=True)

# ========== PROCESS ==========
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df.columns = [col.strip().upper() for col in df.columns]

    st.markdown("<div class='info-card'>", unsafe_allow_html=True)
    st.write("Kolom dari Excel:", df.columns.tolist())
    rename_dict = {
        "NIPP": "NIPP",
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
        "PERSONAL ATTRIBUTES (HUKUMAN DISIPLIN)": "Hukuman Disiplin",
        "Tempat & Tanggal Lahir": "Tempat & Tanggal Lahir",
        "PHOTO": "Foto"
    }
    if "PERSONAL ATTRIBUTES (BIRTHPLACE)" in df.columns and "PERSONAL ATTRIBUTES (DATE OF BIRTH)" in df.columns:
        df["Tempat & Tanggal Lahir"] = (
        df["PERSONAL ATTRIBUTES (BIRTHPLACE)"].astype(str) + ", " +
        df["PERSONAL ATTRIBUTES (DATE OF BIRTH)"].apply(DateFormatter.format_date)
    )
        
    available_cols = [k for k in rename_dict if k in df.columns]
    df_cleaned = df[available_cols].rename(columns={k: rename_dict[k] for k in available_cols})

    st.caption("Preview data berhasil dimuat")
    st.dataframe(df_cleaned, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if "Nama" in df_cleaned.columns and "NIPP" in df_cleaned.columns:
        st.markdown("<div class='info-card'>", unsafe_allow_html=True)

        # === DOWNLOAD PER INDIVIDU ===
        st.subheader("Download Per Individu")
        df_cleaned["Nama_NIPP"] = df_cleaned["Nama"] + " (" + df_cleaned["NIPP"].astype(str) + ")"
        selected_person = st.selectbox("Pilih staff", df_cleaned["Nama_NIPP"].dropna().unique(), index=0)

        if st.button("📄 Generate & Unduh PDF"):
            nipp = selected_person.split("(")[-1].replace(")", "").strip()
            # Remove commas from NIPP if they exist
            nipp = nipp.replace(",", "")
            # Also handle the case where NIPP in dataframe might have commas
            df_cleaned["NIPP_CLEAN"] = df_cleaned["NIPP"].astype(str).str.replace(",", "")
            filtered_data = df_cleaned[df_cleaned["NIPP_CLEAN"] == nipp]
            if len(filtered_data) == 0:
                st.error(f"Data dengan NIPP {nipp} tidak ditemukan!")
                st.stop()
            data = filtered_data.iloc[0]

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
                        f'<a href="data:application/pdf;base64,{base64_pdf}" download="Profil_{data["Nama"]}_{data["NIPP"]}.pdf">📅 Klik untuk Unduh PDF Individu</a>', 
                        unsafe_allow_html=True
                    )

        # === DOWNLOAD PER BATCH ===
        st.subheader("Download Per Batch")
        batch_size = 50
        people = df_cleaned["Nama_NIPP"].dropna().unique()
        total_batches = (len(people) + batch_size - 1) // batch_size
        batch = st.selectbox("Pilih batch:", range(1, total_batches + 1))

        if st.button("📦 Unduh Batch PDF"):
            start = (batch - 1) * batch_size
            end = min(batch * batch_size, len(people))
            selected_people = people[start:end]

            buffer = io.BytesIO()
            # Ensure NIPP_CLEAN column exists for batch processing
            if "NIPP_CLEAN" not in df_cleaned.columns:
                df_cleaned["NIPP_CLEAN"] = df_cleaned["NIPP"].astype(str).str.replace(",", "")
            
            with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
                for person in selected_people:
                    nipp = person.split("(")[-1].replace(")", "").strip()
                    nipp = nipp.replace(",", "")
                    filtered_data = df_cleaned[df_cleaned["NIPP_CLEAN"] == nipp]
                    if len(filtered_data) > 0:
                        row = filtered_data.iloc[0]
                        pdf = CustomPDF()
                        pdf.add_page()
                        img_path = os.path.join("Foto Talent Profile", str(row.get("Foto", "")).strip())
                        pdf.add_profile(row, img_path)
                        pdf_bytes = pdf.output(dest='S')
                        zipf.writestr(f"Profil_{row['Nama']}_{row['NIPP']}.pdf", pdf_bytes)
                    else:
                        st.warning(f"Data dengan NIPP {nipp} tidak ditemukan, dilewati.")

            buffer.seek(0)
            b64 = base64.b64encode(buffer.read()).decode()
            st.markdown(
                f'<a href="data:application/zip;base64,{b64}" download="profil_batch_{batch}.zip">📥 Download Batch {batch}</a>', 
                unsafe_allow_html=True
            )

        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning("Kolom 'Nama' dan 'NIPP' wajib ada agar bisa mendownload per individu maupun per batch.")

# ========== FOOTER ==========
st.markdown("""
<div style='text-align: center; margin-top: 2rem; color: #666; font-size: 0.9rem;'>
    &copy; 2025 PT Kereta Api Indonesia (Persero). All rights reserved.
</div>
""", unsafe_allow_html=True)