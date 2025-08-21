import os
import pandas as pd

# ====== KONFIGURASI ======
excel_file = "Talent Profile D6 REVISI.xlsx"
sheet_name = 0
column_name = "Nama"   # kolom utama untuk cocokan
pdf_folder = "TalentProfile_D6(REVISI)"

# ====== BACA DATA EXCEL ======
df = pd.read_excel(excel_file, sheet_name=sheet_name)
excel_names = df[column_name].astype(str).str.strip().str.upper().tolist()

# ====== BACA FILE PDF DI FOLDER ======
folder_files = [f for f in os.listdir(pdf_folder) if f.lower().endswith(".pdf")]
pdf_names = [f.replace("Profil_", "").replace(".pdf", "").strip().upper() for f in folder_files]

# ====== DEBUG ======
print("Jumlah baris Excel :", len(df))
print("Jumlah nama unik di Excel :", len(set(excel_names)))
print("Jumlah file PDF di folder :", len(pdf_names))
print("Jumlah nama unik di PDF :", len(set(pdf_names)))

# ====== CEK PERBEDAAN ======
missing_in_folder = set(excel_names) - set(pdf_names)
missing_in_excel = set(pdf_names) - set(excel_names)

if missing_in_folder:
    print("\nNama di Excel tapi TIDAK ada file PDF:")
    for n in missing_in_folder:
        print("-", n)

if missing_in_excel:
    print("\nNama di folder PDF tapi TIDAK ada di Excel:")
    for n in missing_in_excel:
        print("-", n)

# ====== CEK DUPLIKAT ======
dupes = df[df.duplicated([column_name], keep=False)]
if not dupes.empty:
    print("\n⚠️ Ada data duplikat di Excel:")
    print(dupes[[column_name]].to_string(index=False))
