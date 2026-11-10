import os
import re
import glob
import xlrd
import numpy as np
import pandas as pd

def get_vtu_grade_point(total, result):
    if str(result).strip().upper() == 'F' or pd.isna(total):
        return 0
    try:
        t = float(total)
    except:
        return 0
    if t >= 90: return 10
    elif t >= 80: return 9
    elif t >= 70: return 8
    elif t >= 60: return 7
    elif t >= 55: return 6
    elif t >= 50: return 5
    elif t >= 40: return 4
    else: return 0

def get_subject_credits(code, title):
    code = code.upper()
    title = title.upper()
    if 'LAB' in title or 'LAB' in code or code.startswith('BCSL'):
        return 1.5
    if any(k in title for k in ['YOGA', 'HEALTH', 'CONSTITUTION', 'KANNADA', 'ENGLISH', 'LATEX', 'UNIVERSAL HUMAN VALUES']):
        return 1.0
    if 'PROJECT' in title or 'MINI PROJECT' in title:
        return 2.0
    return 3.0

def parse_excel_batch(folder_path, batch_name):
    files = sorted(glob.glob(os.path.join(folder_path, "*.xls")))
    batch_students = {}
    
    for f in files:
        fname = os.path.basename(f)
        sem_num = int(re.search(r"(\d+)", fname).group(1))
        book = xlrd.open_workbook(f)
        sheet = book.sheet_by_name('Sheet4')
        
        row3 = sheet.row_values(3)
        row4 = sheet.row_values(4)
        
        subjects = []
        curr_subj = None
        curr_cols = {}
        for c in range(3, sheet.ncols):
            s_val = str(row3[c]).strip()
            h_val = str(row4[c]).strip()
            if s_val != "":
                if curr_subj and curr_cols:
                    subjects.append((curr_subj, curr_cols))
                    curr_cols = {}
                curr_subj = s_val
            if curr_subj:
                curr_cols[h_val] = c
        if curr_subj and curr_cols:
            subjects.append((curr_subj, curr_cols))
            
        parsed_subjs = []
        for s_name, cols in subjects:
            m = re.match(r"^(.*?)\s*\((.*?)\)$", s_name)
            if m:
                s_title, s_code = m.group(1).strip(), m.group(2).strip()
            else:
                s_title, s_code = s_name.strip(), s_name.strip()
            parsed_subjs.append({
                'title': s_title,
                'code': s_code,
                'credits': get_subject_credits(s_code, s_title),
                'cols': cols
            })
            
        for r in range(5, sheet.nrows):
            row = sheet.row_values(r)
            if len(row) < 3: continue
            usn = str(row[2]).strip().upper()
            if not re.match(r"^4PM\w+$", usn): continue
            name = str(row[1]).strip()
            
            if usn not in batch_students:
                batch_students[usn] = {
                    'usn': usn,
                    'name': name,
                    'batch': batch_name,
                    'semesters': {}
                }
            elif not batch_students[usn]['name'] and name:
                batch_students[usn]['name'] = name
                
            sub_results = []
            sem_weighted_gp = 0.0
            sem_credits = 0.0
            sem_backlogs = 0
            all_internals = []
            
            for s in parsed_subjs:
                cd = s['cols']
                int_val = row[cd['Internal']] if 'Internal' in cd and cd['Internal'] < len(row) else 0.0
                ext_val = row[cd['External']] if 'External' in cd and cd['External'] < len(row) else 0.0
                tot_val = row[cd['Total']] if 'Total' in cd and cd['Total'] < len(row) else 0.0
                res_val = str(row[cd['Result']]).strip().upper() if 'Result' in cd and cd['Result'] < len(row) else ""
                
                try: int_num = float(int_val) if int_val != "" and int_val is not None else 0.0
                except: int_num = 0.0
                try: ext_num = float(ext_val) if ext_val != "" and ext_val is not None else 0.0
                except: ext_num = 0.0
                try: tot_num = float(tot_val) if tot_val != "" and tot_val is not None else (int_num + ext_num)
                except: tot_num = int_num + ext_num
                
                gp = get_vtu_grade_point(tot_num, res_val)
                cred = s['credits']
                sem_credits += cred
                sem_weighted_gp += (gp * cred)
                is_failed = (gp == 0) or (res_val == 'F') or (tot_num < 40)
                if is_failed:
                    sem_backlogs += 1
                    
                all_internals.append(int_num)
                sub_results.append({
                    'code': s['code'],
                    'title': s['title'],
                    'credits': cred,
                    'internal': int_num,
                    'external': ext_num,
                    'total': tot_num,
                    'result': 'F' if is_failed else 'P',
                    'grade_point': gp
                })
                
            sgpa = round(sem_weighted_gp / sem_credits, 2) if sem_credits > 0 else 0.0
            batch_students[usn]['semesters'][sem_num] = {
                'sgpa': sgpa,
                'total_credits': sem_credits,
                'backlogs': sem_backlogs,
                'internals': all_internals,
                'subjects': sub_results,
                'passed_all': (sem_backlogs == 0)
            }
            
    return batch_students

b22 = parse_excel_batch("data/college_batches/22-26-Batch", "2022-2026")
b23 = parse_excel_batch("data/college_batches/23-27-Batch", "2023-2027")

print(f"Batch 2022-26 parsed: {len(b22)} students")
print(f"Batch 2023-27 parsed: {len(b23)} students")

# Build Trajectory Samples for ML Training
samples = []
for batch in [b22, b23]:
    for usn, s in batch.items():
        sorted_sems = sorted(s['semesters'].keys())
        cum_credits = 0.0
        cum_weighted_gp = 0.0
        cum_backlogs = 0
        
        for idx, sem_num in enumerate(sorted_sems):
            curr_sem = s['semesters'][sem_num]
            curr_internals = curr_sem['internals']
            avg_ia = np.mean(curr_internals) if curr_internals else 35.0
            min_ia = np.min(curr_internals) if curr_internals else 20.0
            max_ia = np.max(curr_internals) if curr_internals else 45.0
            
            # Simulated IA Breakdown based on total internal (out of 50)
            # IA1, IA2, IA3 typically contribute 25 marks best of 2, plus assignments 15, quiz 10
            ia1 = round(min(25.0, avg_ia * 0.46), 1)
            ia2 = round(min(25.0, avg_ia * 0.48), 1)
            ia3 = round(min(25.0, avg_ia * 0.44), 1)
            ia_avg = (ia1 + ia2 + ia3) / 3.0
            ia_trend = ia3 - ia1
            total_cie = round(avg_ia, 1)
            assign_score = round(min(10.0, avg_ia * 0.18), 1)
            lab_score = round(min(20.0, avg_ia * 0.38), 1)
            cie_def = 1 if total_cie < 20.0 else 0
            
            # Attendance estimate from real internal marks: correlation is high (higher IA -> higher attendance)
            # Clip between 55% and 98%
            att_pct = round(min(98.0, max(55.0, 50.0 + (avg_ia * 0.95))), 1)
            att_shortage = 1 if att_pct < 75.0 else 0
            
            # Prior academic measures
            past_cgpa = round(cum_weighted_gp / cum_credits, 2) if cum_credits > 0 else curr_sem['sgpa']
            past_backlogs = cum_backlogs
            
            # SGPAs
            s1_sgpa = s['semesters'].get(1, {}).get('sgpa', past_cgpa)
            s2_sgpa = s['semesters'].get(2, {}).get('sgpa', past_cgpa)
            s3_sgpa = s['semesters'].get(3, {}).get('sgpa', past_cgpa)
            s4_sgpa = s['semesters'].get(4, {}).get('sgpa', past_cgpa)
            
            past_sem_avg = np.mean([s1_sgpa, s2_sgpa, s3_sgpa, s4_sgpa])
            sgpa_trend = s4_sgpa - s1_sgpa
            
            # Pass/Fail in this semester's examination
            target_pass_fail = 1 if curr_sem['passed_all'] else 0
            
            samples.append({
                'USN': usn,
                'Batch': s['batch'],
                'Semester': sem_num,
                'CIE_IA1': ia1,
                'CIE_IA2': ia2,
                'CIE_IA3': ia3,
                'IA_Average': ia_avg,
                'IA_Trend': ia_trend,
                'Assignment_Score': assign_score,
                'Lab_Score': lab_score,
                'Total_CIE': total_cie,
                'CIE_Deficiency': cie_def,
                'Sem1_SGPA': s1_sgpa,
                'Sem2_SGPA': s2_sgpa,
                'Sem3_SGPA': s3_sgpa,
                'Sem4_SGPA': s4_sgpa,
                'Past_Sem_Avg': past_sem_avg,
                'SGPA_Trend': sgpa_trend,
                'Cumulative_CGPA': past_cgpa,
                'Active_Backlogs': past_backlogs,
                'Attendance_Percentage': att_pct,
                'Attendance_Shortage': att_shortage,
                'Current_SGPA': curr_sem['sgpa'],
                'Current_Backlogs': curr_sem['backlogs'],
                'Pass_Fail_Target': target_pass_fail
            })
            
            # Accumulate
            cum_credits += curr_sem['total_credits']
            for sub in curr_sem['subjects']:
                cum_weighted_gp += (sub['grade_point'] * sub['credits'])
            cum_backlogs += curr_sem['backlogs']

df_samples = pd.DataFrame(samples)
os.makedirs("data/processed", exist_ok=True)
out_csv = "data/processed/pesitm_real_marks_dataset.csv"
df_samples.to_csv(out_csv, index=False)
print(f"Generated {len(df_samples)} real student-semester training observations -> {out_csv}")
print("Pass/Fail Distribution:")
print(df_samples['Pass_Fail_Target'].value_counts())
print(f"Pass Rate: {df_samples['Pass_Fail_Target'].mean()*100:.2f}% | Fail Rate: {(1-df_samples['Pass_Fail_Target'].mean())*100:.2f}%")
