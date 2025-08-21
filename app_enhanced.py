"""
Enhanced App with Flexible Date Format Support for PT KAI Talent Profiles
"""

import base64
import io
import os
import tempfile
import zipfile
import re
from datetime import datetime

import pandas as pd
import streamlit as st
from fpdf import FPDF

# ========== ENHANCED DATE PARSER ==========
class EnhancedDateParser:
    """Advanced date parser supporting multiple Indonesian and international formats"""
    
    INDONESIAN_MONTHS = {
        'januari': 1, 'februari': 2, 'maret': 3, 'april': 4, 'mei': 5, 'juni': 6,
        'juli': 7, 'agustus': 8, 'september': 9, 'oktober': 10, 'november': 11, 'desember': 12
    }
    
    DATE_PATTERNS = [
        r'(\d{1,2})/(\d{1,2})/(\d{4})',      # DD/MM/YYYY
        r'(\d{1,2})-(\d{1,2})-(\d{4})',      # DD-MM-YYYY
        r'(\d{1,2})\.(\d{1,2})\.(\d{4})',     # DD.MM.YYYY
        r'(\d{4})-(\d{1,2})-(\d{1,2})',      # YYYY-MM-DD
        r'(\d{1,2})\s+(\w+)\s+(\d{4})',       # DD Month YYYY
        r'(\w+)\s+(\d{1,2}),?\s+(\d{4})',     # Month DD, YYYY
    ]
    
    @classmethod
    def parse_date(cls, date_string: str):
        """Parse date from various formats"""
        if not date_string or str(date_string).strip() in ['-', '', 'nan']:
            return None
            
        date_str = str(date_string).strip().lower()
        date_str = re.sub(r'\s+', ' ', date_str)
        
        # Try dateutil parser if available
        try:
            from dateutil import parser as date_parser
            return date_parser.parse(date_str, dayfirst=True)
        except:
            pass
            
        # Try manual pattern matching
        for pattern in cls.DATE_PATTERNS:
            match = re.search(pattern, date_str, re.IGNORECASE)
            if match:
                groups = match.groups()
                try:
                    if len(groups) == 3:
                        if pattern.startswith(r'(\d{4})'):
                            year, month, day = int(groups[0]), int(groups[1]), int(groups[2])
                        elif any(month in date_str for month in cls.INDONESIAN_MONTHS.keys()):
                            day = int(groups[0])
                            month_str = groups[1].lower()
                            year = int(groups[2])
                            
                            if month_str in cls.INDONESIAN_MONTHS:
                                month = cls.INDONESIAN_MONTHS[month_str]
                            else:
                                try:
                                    month = datetime.strptime(month_str[:3], '%b').month
                                except:
                                    continue
                        else:
                            day, month, year = int(groups[0]), int(groups[1]), int(groups[2])
                            
                        return datetime(year, month, day)
                except ValueError:
                    continue
        
        return None
    
    @classmethod
    def format_indonesian_date(cls, date_obj):
        """Format date in Indonesian style"""
        if not date_obj:
            return "-"
            
        months = [
            "Januari", "Februari", "Maret", "April", "Mei", "Juni",
            "Juli", "Agustus", "September", "Oktober", "November", "Desember"
        ]
        
        return f"{date_obj.day} {months[date_obj.month-1]} {date_obj.year}"
    
    @classmethod
    def extract_place_and_date(cls, combined_string: str):
        """Extract place and date from combined string like 'Jakarta, 15 Januari 1990'"""
        if not combined_string or str(combined_string).strip() in ['-', '', 'nan']:
            return {"place": "-", "date": None, "formatted_date": "-"}
            
        combined = str(combined_string).strip()
        
        # Split by comma
        parts = combined.split(',')
        if len(parts) >= 2:
            place = parts[0].strip()
            date_part = ','.join(parts[1:]).strip()
            
            parsed_date = cls.parse_date(date_part)
            formatted_date = cls.format_indonesian_date(parsed_date) if parsed_date else "-"
            
            return {
                "place": place,
                "date": parsed_date,
                "formatted_date": formatted_date
            }
        else:
            # Try to find date in string
            date_match = re.search(r'\d{1,2}[\s/.,-]+\w+[\s/.,-]+\d{4}', combined)
            if date_match:
                date_str = date_match.group()
                place = combined.replace(date_str, '').strip()
                parsed_date = cls.parse_date(date_str)
                formatted_date = cls.format_indonesian_date(parsed_date) if parsed_date else "-"
                
                return {
                    "place": place,
                    "date": parsed_date,
                    "formatted_date": formatted_date
                }
            
            return {
                "place": combined,
                "date": None,
                "formatted_date": "-"
            }

# ========== CONFIGURATION ==========
st.set_page_config(
    page_title="Profil Staff PT KAI - Enhanced",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #003366, #FF6600);
        padding: 1rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 2rem;
    }
    .info-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.08);
        margin: 1rem 0;
    }
    .metric-card {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
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

# ========== FONTS ==========
FONTS_DIR = "fonts"
FONT_PATH = os.path.join(FONTS_DIR, "DejaVuSans.ttf")
FONT_BOLD_PATH = os.path.join(FONTS_DIR, "DejaVuSans-Bold.ttf")

# ========== PDF CLASS ==========
class CustomPDF(FPDF):
    def __init__(self):
        super().__init__()
        if os.path.exists(FONT_PATH):
            self.add_font("DejaVu", "", FONT_PATH, uni=True)
        if os.path.exists(FONT_BOLD_PATH):
            self.add_font("DejaVu", "B", FONT_BOLD_PATH, uni=True)
        if os.path.exists(FONT_PATH):
            self.set_font("DejaVu", "", 12)
        else:
            self.set_font("Arial", "", 12)

    def header(self):
        try:
            self.image("logo_kai.png", 10, 8, 30)
        except:
            pass
        
        if os.path.exists(FONT_BOLD_PATH):
            self.set_font("DejaVu", "B", 12)
        else:
            self.set_font("Arial", "B", 12)
            
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

        # Process birth place and date
        birth_info = EnhancedDateParser.extract_place_and_date(
            get_val("Tempat & Tanggal Lahir")
        )
        
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

        # Use processed birth info
        birth_place = birth_info["place"]
        birth_date = birth_info["formatted_date"]
        
        for label, field, value in [
            ("Tempat & Tanggal Lahir", "Tempat & Tanggal Lahir", f"{birth_place}, {birth_date}"),
            ("Usia", "Usia", get_val("Usia")),
            ("Pendidikan", "Pendidikan", get_val("Pendidikan")),
            ("Grade", "Grade", get_val("Grade")),
            ("Penghargaan", "Penghargaan", get_val("Penghargaan")),
            ("Hukuman Disiplin", "Hukuman Disiplin", get_val("Hukuman Disiplin")),
        ]:
            self.set_x(16)
            self.set_font("DejaVu", "B", 9)
            self.cell(43, 5, f"{label}:", ln=0)
            self.cell(6, 5, ":", ln=0)
            self.set_font("DejaVu", "", 9)
            self.multi_cell(125, 5, value)

        end_y = self.get_y()
        self.rect(15, y_attr_content_start - 8, 175, end_y - y_attr_content_start + 10)

# ========== MAIN APP ==========
def main():
    st.markdown('<div class="main-header">Profil Staff PT KAI - Enhanced Date Support</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📅 Pengaturan Tanggal")
        st.info("Sistem mendukung berbagai format tanggal:\n- 15 Januari 1990\n- 23/05/1985\n- 12-03-1992\n- 30 Juni 1988")
        
        st.header("📁 Upload Data")
        uploaded_file = st.file_uploader(
            "Unggah file Excel (.xlsx)",
            type=['xlsx'],
            help="File Excel dengan kolom 'NAMA', 'TEMPAT & TANGGAL LAHIR', dll."
        )
    
    if uploaded_file:
        try:
            # Read Excel file
            df = pd.read_excel(uploaded_file)
            df.columns = [col.strip().upper() for col in df.columns]
            
            # Process date fields
            df = process_date_fields(df)
            
            # Display summary
            st.subheader("📊 Ringkasan Data")
            col1, col2, col3, col4 = st.columns(4)
            
            total_records = len(df)
            valid_dates = df['TANGGAL_VALID'].sum() if 'TANGGAL_VALID' in df.columns else 0
            invalid_dates = total_records - valid_dates
            missing_dates = df['TEMPAT_TANGGAL_LAHIR'].isna().sum() if 'TEMPAT_TANGGAL_LAHIR' in df.columns else 0
            
            with col1:
                st.metric("Total Data", total_records)
            with col2:
                st.metric("Tanggal Valid", valid_dates)
            with col3:
                st.metric("Tanggal Invalid", invalid_dates)
            with col4:
                st.metric("Data Kosong", missing_dates)
            
            # Display processed data
            st.subheader("📋 Data yang Diproses")
            display_cols = ["NAMA", "TEMPAT_LAHIR", "TANGGAL_LAHIR_FORMATTED", "TALENT_CLASSIFICATION"]
            available_cols = [col for col in display_cols if col in df.columns]
            
            if available_cols:
                st.dataframe(df[available_cols], use_container_width=True)
            
            # Download options
            st.subheader("⬇️ Opsi Download")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if "NAMA" in df.columns:
                    selected_name = st.selectbox("Pilih individu:", df["NAMA"].dropna().unique())
                    
                    if st.button("📄 Generate PDF Individu"):
                        with st.spinner("Membuat PDF..."):
                            data = df[df["NAMA"] == selected_name].iloc[0]
                            
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                                pdf = CustomPDF()
                                pdf.add_page()
                                
                                foto_file = str(data.get("FOTO", "")).strip()
                                img_path = os.path.join("Foto Talent Profile", foto_file) if foto_file else None
                                if not (img_path and os.path.isfile(img_path)):
                                    img_path = None
                                
                                pdf.add_profile(data.to_dict(), img_path)
                                pdf.output(tmp.name)
                                
                                with open(tmp.name, "rb") as f:
                                    st.download_button(
                                        label="📥 Download PDF",
                                        data=f.read(),
                                        file_name=f"Profil_{selected_name}.pdf",
                                        mime="application/pdf"
                                    )
            
            with col2:
                batch_size = st.number_input("Jumlah per batch:", min_value=1, max_value=50, value=10)
                
                names = df["NAMA"].dropna().unique()
                total_batches = (len(names) + batch_size - 1) // batch_size
                selected_batch = st.selectbox("Pilih batch:", range(1, total_batches + 1))
                
                if st.button("📦 Generate PDF Batch"):
                    with st.spinner("Membuat batch PDF..."):
                        start = (selected_batch - 1) * batch_size
                        end = min(selected_batch * batch_size, len(names))
                        selected_names = names[start:end]
                        
                        buffer = io.BytesIO()
                        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                            for name in selected_names:
                                row = df[df["NAMA"] == name].iloc[0]
                                
                                pdf = CustomPDF()
                                pdf.add_page()
                                
                                foto_file = str(row.get("FOTO", "")).strip()
                                img_path = os.path.join("Foto Talent Profile", foto_file) if foto_file else None
                                if not (img_path and os.path.isfile(img_path)):
                                    img_path = None
                                
                                pdf.add_profile(row.to_dict(), img_path)
                                
                                pdf_bytes = pdf.output(dest='S')
                                safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                                zipf.writestr(f"Profil_{safe_name}.pdf", pdf_bytes)
                        
                        buffer.seek(0)
                        st.download_button(
                            label="📥 Download ZIP Batch",
                            data=buffer.getvalue(),
                            file_name=f"batch_{selected_batch}.zip",
                            mime="application/zip"
                        )
            
            # Show invalid dates if any
            if 'TANGGAL_VALID' in df.columns:
                invalid_df = df[~df['TANGGAL_VALID']]
                if len(invalid_df) > 0:
                    st.subheader("⚠️ Tanggal yang Perlu Diperiksa")
                    st.dataframe(
                        invalid_df[["NAMA", "TEMPAT_TANGGAL_LAHIR"]],
                        use_container_width=True
                    )
        
        except Exception as e:
            st.error(f"Terjadi kesalahan: {str(e)}")
            st.info("Pastikan file Excel memiliki kolom yang sesuai.")

def process_date_fields(df):
    """Process date fields with flexible format support"""
    
    # Standard column mapping
    rename_dict = {
        "NAMA": "NAMA",
        "TALENT CLASSIFICATION": "TALENT_CLASSIFICATION",
        "WORKING EXPERIENCE": "WORKING_EXPERIENCE",
        "NILAI KINERJA (2022)": "NILAI_KINERJA_2022",
        "NILAI KINERJA (2023)": "NILAI_KINERJA_2023",
        "NILAI KINERJA (2024)": "NILAI_KINERJA_2024",
        "BEHAVIOUR COMPETENCIES (BUMN ASSESSMENT)": "BEHAVIOUR_BUMN",
        "BEHAVIOUR COMPETENCIES (MULTIRATER)": "BEHAVIOUR_MULTIRATER",
        "KNOWLEDGE": "KNOWLEDGE",
        "PERSONAL ATTRIBUTES (PLACE AND DATE OF BIRTH)": "TEMPAT_TANGGAL_LAHIR",
        "PERSONAL ATTRIBUTES (AGE)": "USIA",
        "PERSONAL ATTRIBUTES (EDUCATION)": "PENDIDIKAN",
        "PERSONAL ATTRIBUTES (GRADE)": "GRADE",
        "PERSONAL ATTRIBUTES (AWARD)": "PENGHARGAAN",
        "PERSONAL ATTRIBUTES (HUKUMAN DISIPLIN)": "HUKUMAN_DISIPLIN",
        "TEMPAT & TANGGAL LAHIR": "TEMPAT_TANGGAL_LAHIR",
        "PHOTO": "FOTO"
    }
    
    # Handle combined birthplace and date
    if "PERSONAL ATTRIBUTES (BIRTHPLACE)" in df.columns and "PERSONAL ATTRIBUTES (DATE OF BIRTH)" in df.columns:
        df["TEMPAT_TANGGAL_LAHIR"] = df["PERSONAL ATTRIBUTES (BIRTHPLACE)"].astype(str) + ", " + df["PERSONAL ATTRIBUTES (DATE OF BIRTH)"].astype(str)
    
    # Rename columns
    available_cols = [k for k in rename_dict if k in df.columns]
    df = df[available_cols].rename(columns={k: rename_dict[k] for k in available_cols})
    
    # Process birth place and date
    if "TEMPAT_TANGGAL_LAHIR" in df.columns:
        birth_info = df["TEMPAT_TANGGAL_LAHIR"].apply(EnhancedDateParser.extract_place_and_date)
        df["TEMPAT_LAHIR"] = birth_info.apply(lambda x: x["place"])
        df["TANGGAL_LAHIR_FORMATTED"] = birth_info.apply(lambda x: x["formatted_date"])
        df["TANGGAL_VALID"] = birth_info.apply(lambda x: x["date"] is not None)
    
    return df

if __name__ == "__main__":
    main()
