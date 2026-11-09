import os
import pandas as pd
import glob

dataset_dir = os.path.join("data", "23-27-Batch")
files = sorted(glob.glob(os.path.join(dataset_dir, "*.xls")))

print(f"Found {len(files)} dataset files:")
for f in files:
    print(" -", os.path.basename(f))

print("\n" + "="*80)

for f in files:
    fname = os.path.basename(f)
    print(f"\nANALYZING FILE: {fname}")
    try:
        xl = pd.ExcelFile(f, engine='xlrd')
        print(f"Sheets: {xl.sheet_names}")
        for sheet in xl.sheet_names:
            df = pd.read_excel(f, sheet_name=sheet, engine='xlrd')
            print(f"  Sheet '{sheet}': Shape = {df.shape}")
            print(f"  Columns: {list(df.columns)[:15]}... (Total {len(df.columns)})")
            print("  First 2 rows:")
            print(df.head(2).to_string())
            print("-" * 50)
    except Exception as e:
        print(f"Error reading {fname}: {e}")
