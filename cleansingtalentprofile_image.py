import pandas as pd

# ===== 1. Load file Excel =====
file_path = "Template_Talent Profile 28 Jul - 8 Aug (2).xlsx"
df = pd.read_excel(file_path, sheet_name="FORMAT")

# ===== 2. Filter kolom yang dibutuhkan =====
# Pastikan kolom "Nama" dan "PIC" sesuai nama di file Excel kamu
df_check = df[['Nama', 'PIC']].dropna()

# ===== 3. Cari nama yang muncul di lebih dari 1 PIC =====
# Hitung jumlah PIC unik untuk setiap nama
pic_count = df_check.groupby('Nama')['PIC'].nunique()

# Ambil hanya yang punya PIC > 1 (artinya nama itu ada di beberapa PIC)
duplicate_names = pic_count[pic_count > 1].index

# ===== 4. Ambil data detailnya =====
duplicates_detail = df_check[df_check['Nama'].isin(duplicate_names)].sort_values(by='Nama')

# ===== 5. Simpan hasil ke Excel =====
output_path = "nama_sama_di_semua_PIC.xlsx"
duplicates_detail.to_excel(output_path, index=False)

print(f"Hasil sudah disimpan ke {output_path}")
