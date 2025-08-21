import pandas as pd
import os

# List all Excel files
excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx') and not f.startswith('~$')]
print("Excel files found:", excel_files)

# Check structure of first few files
for file in excel_files[:3]:
    try:
        print(f"\n=== {file} ===")
        df = pd.read_excel(file)
        print("Columns:", df.columns.tolist())
        print("Shape:", df.shape)
        
        # Check for name columns
        name_cols = [col for col in df.columns if 'NAMA' in str(col).upper()]
        if name_cols:
            print("Name columns:", name_cols)
            
        # Check for NIPP or similar identifier columns
        id_cols = [col for col in df.columns if any(keyword in str(col).upper() 
                   for keyword in ['NIPP', 'NIK', 'ID', 'NOMOR', 'EMPLOYEE'])]
        if id_cols:
            print("ID columns:", id_cols)
            
        # Check for duplicates in names
        if name_cols:
            name_col = name_cols[0]
            duplicates = df[name_col].value_counts()
            duplicate_names = duplicates[duplicates > 1]
            if len(duplicate_names) > 0:
                print("Duplicate names found:")
                for name, count in duplicate_names.items():
                    print(f"  {name}: {count} occurrences")
                    
    except Exception as e:
        print(f"Error reading {file}: {e}")
