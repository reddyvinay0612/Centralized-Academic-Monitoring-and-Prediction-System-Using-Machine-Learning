import os
import re
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

df = pd.read_excel('data/23-27-Batch/1-sem.xls', sheet_name='Sheet4', engine='xlrd')
row2 = df.iloc[2].tolist()
row3 = df.iloc[3].tolist()

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

print("Testing SGPA calculation on Sem 1 students:")
for r_idx in range(4, 10):
    row = df.iloc[r_idx]
    usn = row.iloc[2]
    name = row.iloc[1]
    
    total_credits = 0
    weighted_pts = 0
    backlogs = 0
    
    for s_name, cols in subjects:
        tot = row.iloc[cols.get('Total')] if 'Total' in cols else 0
        res = row.iloc[cols.get('Result')] if 'Result' in cols else 'F'
        gp = get_vtu_grade_point(tot, res)
        # Assume 3 credits for theory, 1 for health/english/etc.
        cred = 1 if ('ENGLISH' in s_name or 'HEALTH' in s_name or 'CONSTITUTION' in s_name or 'WASTE' in s_name) else 3
        total_credits += cred
        weighted_pts += cred * gp
        if gp == 0:
            backlogs += 1
            
    sgpa = round(weighted_pts / total_credits, 2) if total_credits > 0 else 0.0
    final_tot = row.iloc[subjects[-1][1].get('Final Total')] if 'Final Total' in subjects[-1][1] else 'N/A'
    print(f"{usn} - {name[:25]:25} | Final Tot: {final_tot} | SGPA: {sgpa} | Backlogs: {backlogs}")
