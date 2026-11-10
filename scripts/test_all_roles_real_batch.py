import requests
import json

BASE_URL = "http://localhost:5000"

def test_login(identifier, password, expected_role):
    url = f"{BASE_URL}/api/auth/login"
    payload = {"identifier": identifier, "password": password, "expectedRole": expected_role}
    resp = requests.post(url, json=payload)
    if resp.status_code == 200:
        data = resp.json()
        token = data.get('access_token') or data.get('data', {}).get('token')
        user_info = data.get('user') or data.get('data', {}).get('user', {})
        role = user_info.get('role')
        name = user_info.get('name')
        print(f" [PASS] Login {identifier:<16} | Role: {role:<10} | Name: {name} (HTTP 200)")
        return token, data
    else:
        print(f" [FAIL] Login {identifier:<16} | Status: {resp.status_code}, Body: {resp.text}")
        return None, None

print("\n" + "="*80)
print("VERIFYING MULTI-ROLE RBAC AUTHENTICATION WITH REAL PESITM DATASET CREDENTIALS")
print("="*80)

# 1. Student Logins (2022 and 2023 batch)
st_22_token, _ = test_login("4PM22CS001", "password123", "student")
st_23_token, _ = test_login("4PM23CS001", "password123", "student")

# 2. Parent Logins (2022 and 2023 batch)
pr_22_token, _ = test_login("parent_4pm22cs001", "password123", "parent")
pr_23_token, _ = test_login("parent_4pm23cs001", "password123", "parent")

# 3. Teacher Login
tc_token, _ = test_login("anita.rao", "password123", "teacher")

# 4. Principal Login
prnc_token, _ = test_login("principal", "password123", "principal")

# 5. Admin Login
adm_token, _ = test_login("admin", "password123", "admin")

print("\n" + "="*80)
print("VERIFYING DATA VISIBILITY & ROSTERS ACROSS DASHBOARDS")
print("="*80)

# Check Teacher Classes & Roster
if tc_token:
    headers = {"Authorization": f"Bearer {tc_token}"}
    r = requests.get(f"{BASE_URL}/api/teacher/classes", headers=headers)
    if r.status_code == 200:
        classes = r.json().get('data', [])
        print(f"[TEACHER DASHBOARD] Assigned Units: {len(classes)} classes")
        for c in classes:
            print(f"  * Class: {c['class_name']} ({c['section']}) | Subject: {c['subject_code']} - {c['subject_name']} | Enrolled Students: {c['metrics']['total_students']}")
            
            # Fetch roster for 6th sem or 8th sem
            if '6th' in c['class_name'] or '8th' in c['class_name']:
                r_roster = requests.get(f"{BASE_URL}/api/teacher/classes/{c['class_id']}/students?subject_id={c['subject_id']}", headers=headers)
                if r_roster.status_code == 200:
                    roster = r_roster.json().get('data', [])
                    print(f"    -> Roster successfully loaded: {len(roster)} students!")
                    if roster:
                        sample = roster[0]
                        print(f"       First student row: {sample['name']} ({sample['usn']}) | Att: {sample['attendance']['percentage']}% | CIE: {sample['marks']['total_cie']} | Risk: {sample['prediction']['risk_level']} | Outcome: {sample['prediction']['predicted_outcome']}")
    else:
        print(f"[TEACHER ERROR] /classes returned {r.status_code}")

# Check Principal College-Wide Students
if prnc_token:
    headers = {"Authorization": f"Bearer {prnc_token}"}
    r = requests.get(f"{BASE_URL}/api/principal/students?limit=1000", headers=headers)
    if r.status_code == 200:
        data = r.json()
        students = data.get('data', [])
        print(f"\n[PRINCIPAL DASHBOARD] College-Wide Student Registry: {len(students)} students loaded!")
        b22_cnt = sum(1 for s in students if '4PM22' in s['usn'])
        b23_cnt = sum(1 for s in students if '4PM23' in s['usn'])
        print(f"  * 2022-26 Batch Enrolled Students: {b22_cnt}")
        print(f"  * 2023-27 Batch Enrolled Students: {b23_cnt}")
    else:
        print(f"[PRINCIPAL ERROR] /students returned {r.status_code}")

# Check Admin Users
if adm_token:
    headers = {"Authorization": f"Bearer {adm_token}"}
    r = requests.get(f"{BASE_URL}/api/admin/users?limit=1000", headers=headers)
    if r.status_code == 200:
        data = r.json()
        users = data.get('data', [])
        print(f"\n[ADMIN DASHBOARD] User Directory & Access Management: {len(users)} accounts listed!")
        role_counts = {}
        for u in users:
            role_counts[u['role']] = role_counts.get(u['role'], 0) + 1
        for role, count in sorted(role_counts.items()):
            print(f"  * Role: {role:<12} -> {count} registered accounts")
    else:
        print(f"[ADMIN ERROR] /users returned {r.status_code}")

# Check AI Pass/Fail Prediction Endpoint
print("\n" + "="*80)
print("VERIFYING MACHINE LEARNING PASS/FAIL PREDICTION & EXPLAINABILITY (SHAP)")
print("="*80)
if st_22_token:
    headers = {"Authorization": f"Bearer {st_22_token}"}
    r = requests.get(f"{BASE_URL}/api/predict/pass-fail?usn=4PM22CS001", headers=headers)
    print(f"[STUDENT PREDICTION QUERY: 4PM22CS001] Status: {r.status_code}")
    if r.status_code == 200:
        body = r.json()
        st_data = body.get('student', {})
        p = body.get('prediction_result', {})
        print(f"  * Student: {st_data.get('name')} (USN: {st_data.get('usn')})")
        print(f"  * AI Prediction: {p.get('prediction')} | Pass Confidence: {p.get('pass_probability')}% | Risk Level: {p.get('risk_tier')}")
        print(f"  * Calculated CIE Total: {p.get('total_cie')}/50")
        print(f"  * Key Academic Trajectory Drivers (TreeSHAP):")
        for f in p.get('factors', [])[:3]:
            print(f"    - {f}")

# Simulation POST
sim_payload = {
    "ia1": 22.0, "ia2": 21.0, "ia3": 23.0,
    "assignment": 9.0, "lab": 18.0,
    "attendance": 88.0, "backlogs": 0, "cgpa": 7.85
}
r_sim = requests.post(f"{BASE_URL}/api/predict/pass-fail", json=sim_payload)
print(f"\n[WHAT-IF MARKS SIMULATION QUERY] Status: {r_sim.status_code}")
if r_sim.status_code == 200:
    body = r_sim.json()
    ps = body.get('prediction_result', {})
    m_info = body.get('model_info', {})
    print(f"  * Model: {m_info.get('name')}")
    print(f"  * Simulation Outcome: {ps.get('prediction')} (Pass Prob: {ps.get('pass_probability')}%, {ps.get('risk_tier')})")
    print(f"  * Total Simulated CIE: {ps.get('total_cie')}/50")
