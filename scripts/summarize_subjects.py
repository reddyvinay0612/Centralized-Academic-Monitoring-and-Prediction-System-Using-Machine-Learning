import os
import re
import pandas as pd
import glob

dataset_dir = os.path.join("data", "23-27-Batch")
files = sorted(glob.glob(os.path.join(dataset_dir, "*.xls")))

all_subjects = {}
for f in files:
    fname = os.path.basename(f)
    sem_num = int(re.search(r"(\d+)", fname).group(1))
    df = pd.read_excel(f, sheet_name='Sheet4', engine='xlrd')
    row2 = df.iloc[2].tolist()
    row3 = df.iloc[3].tolist()
    
    curr_subj = None
    curr_cols = {}
    for c_idx in range(3, len(df.columns)):
        subj_cell = row2[c_idx]
        subhead = str(row3[c_idx]).strip() if pd.notna(row3[c_idx]) else ""
        if pd.notna(subj_cell) and str(subj_cell).strip() != "":
            if curr_subj and curr_cols:
                all_subjects.setdefault(sem_num, []).append((curr_subj, curr_cols))
                curr_cols = {}
            curr_subj = str(subj_cell).strip()
        if curr_subj:
            curr_cols[subhead] = c_idx
    if curr_subj and curr_cols:
        all_subjects.setdefault(sem_num, []).append((curr_subj, curr_cols))

print("SUMMARY OF SUBJECTS PER SEMESTER:")
unique_subject_codes = set()
for sem, subjs in all_subjects.items():
    print(f"\n--- SEMESTER {sem} ({len(subjs)} subjects) ---")
    for s_name, cols in subjs:
        match = re.match(r"^(.*?)\s*\((.*?)\)$", s_name)
        if match:
            title = match.group(1).strip()
            code = match.group(2).strip()
        else:
            title = s_name.strip()
            code = s_name.strip()
        unique_subject_codes.add(code)
        print(f"  {code:12} | {title[:40]:40} | Columns: {list(cols.keys())}")

print(f"\nTotal Unique Subject Codes across all 6 semesters: {len(unique_subject_codes)}")
