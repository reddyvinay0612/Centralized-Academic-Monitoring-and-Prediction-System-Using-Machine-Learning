import os
import re
import pandas as pd
import glob

dataset_dir = os.path.join("data", "23-27-Batch")
files = sorted(glob.glob(os.path.join(dataset_dir, "*.xls")))

all_students = {}
all_subjects_by_sem = {}

for f in files:
    fname = os.path.basename(f)
    sem_num = int(re.search(r"(\d+)", fname).group(1))
    print(f"\n=================== SEMESTER {sem_num} ({fname}) ===================")
    df = pd.read_excel(f, sheet_name='Sheet4', engine='xlrd')
    
    row2 = df.iloc[2].tolist()
    row3 = df.iloc[3].tolist()
    
    # Extract subjects
    subjects = []
    curr_subj = None
    curr_cols = {}
    
    for c_idx in range(3, len(df.columns)):
        subj_cell = row2[c_idx]
        subhead = str(row3[c_idx]).strip() if pd.notna(row3[c_idx]) else ""
        
        if pd.notna(subj_cell) and str(subj_cell).strip() != "":
            if curr_subj and curr_cols:
                subjects.append((curr_subj, curr_cols))
                curr_cols = {}
            curr_subj = str(subj_cell).strip()
            
        if curr_subj:
            curr_cols[subhead] = c_idx
            
    if curr_subj and curr_cols:
        subjects.append((curr_subj, curr_cols))
        
    print(f"Detected {len(subjects)} subjects in Sem {sem_num}:")
    parsed_subjects = []
    for s_name, cols in subjects:
        # Check if subject name has code in parentheses, e.g. "COMMUNICATIVE ENGLISH(BENGK106 )"
        match = re.match(r"^(.*?)\s*\((.*?)\)$", s_name)
        if match:
            s_title = match.group(1).strip()
            s_code = match.group(2).strip()
        else:
            s_title = s_name.strip()
            s_code = s_name.strip()
        parsed_subjects.append({
            'code': s_code,
            'title': s_title,
            'cols': cols
        })
        print(f"  [{s_code}] {s_title} -> columns: {cols}")
        
    all_subjects_by_sem[sem_num] = parsed_subjects
    
    # Process student rows
    student_count = 0
    fail_counts = []
    total_marks_list = []
    
    for r_idx in range(4, len(df)):
        row = df.iloc[r_idx]
        usn_raw = row.iloc[2]
        if pd.isna(usn_raw):
            continue
        usn = str(usn_raw).strip()
        if not re.match(r"^4PM\w+$", usn):
            continue
            
        name = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""
        
        if usn not in all_students:
            all_students[usn] = {
                'name': name,
                'semesters': {}
            }
        elif not all_students[usn]['name'] and name:
            all_students[usn]['name'] = name
            
        student_count += 1
        
        # Analyze performance in this semester
        student_subjs = {}
        fails = 0
        for subj in parsed_subjects:
            c_dict = subj['cols']
            internal = row.iloc[c_dict.get('Internal')] if 'Internal' in c_dict else None
            external = row.iloc[c_dict.get('External')] if 'External' in c_dict else None
            total = row.iloc[c_dict.get('Total')] if 'Total' in c_dict else None
            res = str(row.iloc[c_dict.get('Result')]).strip() if 'Result' in c_dict else ""
            
            if res.upper() == 'F':
                fails += 1
            student_subjs[subj['code']] = {
                'internal': internal,
                'external': external,
                'total': total,
                'result': res
            }
            
        final_total = None
        for c_dict in [s['cols'] for s in parsed_subjects]:
            if 'Final Total' in c_dict:
                final_total = row.iloc[c_dict['Final Total']]
                break
        final_res = None
        for c_dict in [s['cols'] for s in parsed_subjects]:
            if 'Final Result' in c_dict:
                final_res = row.iloc[c_dict['Final Result']]
                break
                
        all_students[usn]['semesters'][sem_num] = {
            'subjects': student_subjs,
            'fails': fails,
            'final_total': final_total,
            'final_result': final_res
        }
        fail_counts.append(fails)
        
    print(f"Total students parsed in Sem {sem_num}: {student_count}")
    print(f"Pass count: {sum(1 for f in fail_counts if f == 0)}, Students with backlogs: {sum(1 for f in fail_counts if f > 0)}")

print("\n" + "="*80)
print(f"TOTAL UNIQUE STUDENTS ACROSS ALL 6 SEMESTERS: {len(all_students)}")
regular = [u for u in all_students if u.startswith('4PM23CS')]
lateral = [u for u in all_students if not u.startswith('4PM23CS')]
print(f"  Regular (2023 Batch: 4PM23CS...): {len(regular)}")
print(f"  Lateral / Other (e.g. 4PM24CS...): {len(lateral)}")
print("Sample Students:")
for u in list(all_students.keys())[:5]:
    st = all_students[u]
    print(f"  {u} - {st['name']} (Semesters recorded: {list(st['semesters'].keys())})")
