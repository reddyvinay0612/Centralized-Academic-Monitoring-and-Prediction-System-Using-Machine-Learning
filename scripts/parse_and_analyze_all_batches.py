import os
import re
import glob
import xlrd
import pandas as pd

def parse_semester_file(filepath, sem_num, batch_name):
    book = xlrd.open_workbook(filepath)
    sheet = book.sheet_by_name('Sheet4')
    
    row3 = sheet.row_values(3) # Subject names
    row4 = sheet.row_values(4) # Headers (Internal, External, Total, Result...)
    
    # Identify subjects and their column ranges
    subjects = []
    curr_subj = None
    curr_cols = {}
    
    for c_idx in range(3, sheet.ncols):
        subj_cell = str(row3[c_idx]).strip()
        subhead = str(row4[c_idx]).strip()
        
        if subj_cell != "":
            if curr_subj and curr_cols:
                subjects.append((curr_subj, curr_cols))
                curr_cols = {}
            curr_subj = subj_cell
            
        if curr_subj:
            curr_cols[subhead] = c_idx
            
    if curr_subj and curr_cols:
        subjects.append((curr_subj, curr_cols))
        
    parsed_subjects = []
    for s_name, cols in subjects:
        # Match "SUBJECT NAME (CODE)"
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
        
    students_in_file = {}
    for r in range(5, sheet.nrows):
        row = sheet.row_values(r)
        if len(row) < 3:
            continue
        usn = str(row[2]).strip().upper()
        if not re.match(r"^4PM\w+$", usn):
            continue
        name = str(row[1]).strip()
        
        marks_data = []
        for s in parsed_subjects:
            c_dict = s['cols']
            int_val = row[c_dict['Internal']] if 'Internal' in c_dict and c_dict['Internal'] < len(row) else None
            ext_val = row[c_dict['External']] if 'External' in c_dict and c_dict['External'] < len(row) else None
            tot_val = row[c_dict['Total']] if 'Total' in c_dict and c_dict['Total'] < len(row) else None
            res_val = str(row[c_dict['Result']]).strip().upper() if 'Result' in c_dict and c_dict['Result'] < len(row) else ""
            
            try: int_num = float(int_val) if int_val != "" and int_val is not None else 0.0
            except: int_num = 0.0
            try: ext_num = float(ext_val) if ext_val != "" and ext_val is not None else 0.0
            except: ext_num = 0.0
            try: tot_num = float(tot_val) if tot_val != "" and tot_val is not None else (int_num + ext_num)
            except: tot_num = int_num + ext_num
            
            # Pass/fail determine
            # In VTU: 'P' is Pass, 'F' is Fail. If result string is empty, tot >= 40 and ext >= 18 is typically pass
            is_pass = (res_val == 'P') or (res_val == '' and tot_num >= 40 and ext_num >= 18)
            
            marks_data.append({
                'code': s['code'],
                'title': s['title'],
                'internal': int_num,
                'external': ext_num,
                'total': tot_num,
                'result': 'P' if is_pass else 'F',
                'raw_result': res_val
            })
            
        students_in_file[usn] = {
            'usn': usn,
            'name': name,
            'sem': sem_num,
            'batch': batch_name,
            'subjects': marks_data
        }
        
    return parsed_subjects, students_in_file

b22_files = sorted(glob.glob("data/college_batches/22-26-Batch/*.xls"))
b23_files = sorted(glob.glob("data/college_batches/23-27-Batch/*.xls"))

all_students_global = {}
dataset_records = []

for f in b22_files:
    fname = os.path.basename(f)
    sem_num = int(re.search(r"(\d+)", fname).group(1))
    subjs, studs = parse_semester_file(f, sem_num, "2022-2026")
    print(f"[2022-26] Sem {sem_num}: {len(subjs)} subjects, {len(studs)} students")
    for usn, s in studs.items():
        if usn not in all_students_global:
            all_students_global[usn] = {'usn': usn, 'name': s['name'], 'batch': '2022-2026', 'sems': {}}
        elif not all_students_global[usn]['name'] and s['name']:
            all_students_global[usn]['name'] = s['name']
        all_students_global[usn]['sems'][sem_num] = s['subjects']
        for sub in s['subjects']:
            dataset_records.append({
                'batch': '2022-2026',
                'usn': usn,
                'semester': sem_num,
                'subject_code': sub['code'],
                'internal': sub['internal'],
                'external': sub['external'],
                'total': sub['total'],
                'result': sub['result']
            })

for f in b23_files:
    fname = os.path.basename(f)
    sem_num = int(re.search(r"(\d+)", fname).group(1))
    subjs, studs = parse_semester_file(f, sem_num, "2023-2027")
    print(f"[2023-27] Sem {sem_num}: {len(subjs)} subjects, {len(studs)} students")
    for usn, s in studs.items():
        if usn not in all_students_global:
            all_students_global[usn] = {'usn': usn, 'name': s['name'], 'batch': '2023-2027', 'sems': {}}
        elif not all_students_global[usn]['name'] and s['name']:
            all_students_global[usn]['name'] = s['name']
        all_students_global[usn]['sems'][sem_num] = s['subjects']
        for sub in s['subjects']:
            dataset_records.append({
                'batch': '2023-2027',
                'usn': usn,
                'semester': sem_num,
                'subject_code': sub['code'],
                'internal': sub['internal'],
                'external': sub['external'],
                'total': sub['total'],
                'result': sub['result']
            })

print("\n" + "="*60)
print(f"Total Unique Students Across Batches: {len(all_students_global)}")
print(f"Total Academic Exam Subject Records: {len(dataset_records)}")
df_records = pd.DataFrame(dataset_records)
print(f"Pass count: {(df_records['result'] == 'P').sum()} ({((df_records['result'] == 'P').mean()*100):.1f}%)")
print(f"Fail count: {(df_records['result'] == 'F').sum()} ({((df_records['result'] == 'F').mean()*100):.1f}%)")
print("="*60)
