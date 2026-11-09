import os
import pandas as pd
import glob

dataset_dir = os.path.join("data", "23-27-Batch")
files = sorted(glob.glob(os.path.join(dataset_dir, "*.xls")))

for f in files:
    fname = os.path.basename(f)
    print("=" * 80)
    print(f"FILE: {fname}")
    df = pd.read_excel(f, sheet_name='Sheet4', engine='xlrd')
    # Row 2 contains subject names
    # Row 3 contains subheaders (Internal, External, Total, Result, etc.)
    row2 = df.iloc[2].tolist()
    row3 = df.iloc[3].tolist()
    
    print(f"Total rows in Sheet4: {len(df)}")
    print(f"Total columns: {len(df.columns)}")
    
    # Let's map subjects to their columns
    current_subject = None
    subject_map = {}
    for col_idx, (s_name, subhead) in enumerate(zip(row2, row3)):
        if pd.notna(s_name) and str(s_name).strip() != "":
            current_subject = str(s_name).strip()
        subhead_str = str(subhead).strip() if pd.notna(subhead) else f"col_{col_idx}"
        key = current_subject if current_subject else "Header"
        if key not in subject_map:
            subject_map[key] = []
        subject_map[key].append((col_idx, subhead_str))
        
    print("\nSubjects and columns detected:")
    for subj, cols in subject_map.items():
        col_names = [f"Col {idx}: {name}" for idx, name in cols]
        print(f"  * {subj}: {col_names}")
        
    # Check student count (rows starting from row 4)
    student_rows = df.iloc[4:].dropna(subset=[df.columns[2]]) # USN column
    # Filter only rows with valid USN
    usns = student_rows[df.columns[2]].astype(str).str.strip()
    valid_usns = usns[usns.str.match(r"^4PM\w+$", na=False)]
    print(f"\nValid Students with 4PM... USNs: {len(valid_usns)}")
    if len(valid_usns) > 0:
        print(f"  First 3 USNs: {list(valid_usns[:3])}")
        print(f"  Last 3 USNs: {list(valid_usns[-3:])}")
