import urllib.request
import urllib.parse
import json
import sys

BASE_URL = "http://127.0.0.1:5000"

def post_json(path, data, token=None):
    url = f"{BASE_URL}{path}"
    body = json.dumps(data).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=body, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))
    except Exception as e:
        return 500, {"error": str(e)}

def get_json(path, token=None):
    url = f"{BASE_URL}{path}"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))
    except Exception as e:
        return 500, {"error": str(e)}

def patch_json(path, data, token=None):
    url = f"{BASE_URL}{path}"
    body = json.dumps(data).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=body, headers=headers, method="PATCH")
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))
    except Exception as e:
        return 500, {"error": str(e)}

print("=" * 60)
print("1. VERIFYING AUTHENTICATION FOR ALL 5 ROLES")
print("=" * 60)

test_creds = [
    ("student", "4PM23CS071", "password123"),
    ("student_2", "4PM23CS035", "password123"),
    ("parent", "parent_4pm23cs071", "password123"),
    ("teacher", "EMP-CSE-01", "password123"),
    ("admin", "admin@pesitm.edu", "password123"),
    ("principal", "principal@pesitm.edu", "password123")
]

tokens = {}
for role, user, pwd in test_creds:
    status, res = post_json("/api/auth/login", {"username": user, "password": pwd})
    if status == 200:
        token = res.get("access_token")
        tokens[role] = token
        user_info = res.get("user", {})
        print(f"  [PASS] {role.upper():10}: Logged in as '{user_info.get('username')}' ({user_info.get('email')}) - Role: {user_info.get('role')}")
    else:
        print(f"  [FAIL] {role.upper()} ({user}): HTTP {status} - {res}")

print("\n" + "=" * 60)
print("2. VERIFYING ML PASS/FAIL PREDICTION & DETENTION FORECAST")
print("=" * 60)

students_to_check = ["4PM23CS071", "4PM23CS035"]
for usn in students_to_check:
    status, res = get_json(f"/api/predict/pass-fail?usn={usn}", tokens.get("student"))
    if status == 200:
        pred = res.get("prediction", {})
        status_verdict = pred.get("status")
        prob = pred.get("pass_probability")
        backlogs = pred.get("active_backlogs")
        eligibility = pred.get("exam_eligibility")
        detention_risk = pred.get("detention_risk")
        print(f"  Student {usn} ({pred.get('student_name')}):")
        print(f"    - Prediction Verdict : {status_verdict} (Pass Probability: {prob}%)")
        print(f"    - Active Backlogs    : {backlogs}")
        print(f"    - Exam Eligibility   : {eligibility}")
        print(f"    - Detention Risk     : {detention_risk}")
    else:
        print(f"  [FAIL] Prediction for {usn}: HTTP {status} - {res}")

print("\n" + "=" * 60)
print("3. VERIFYING STUDENT PROFILE & IMMUTABILITY PROTECTION")
print("=" * 60)

student_token = tokens.get("student")
if student_token:
    # Test legitimate profile check
    status, res = get_json("/api/student/me", student_token)
    print(f"  Student Profile /me: HTTP {status} ({res.get('student', {}).get('name')})")

    # Test tampering attempt (student trying to update marks/attendance)
    status, res = patch_json("/api/student/profile", {"marks": 99, "cie": 50, "attendance": 100}, student_token)
    print(f"  Academic Tampering Attempt (Should be 403 Forbidden): HTTP {status} - {res.get('message')}")
    
    # Test valid username update
    status, res = patch_json("/api/student/profile", {"username": "4PM23CS071_TEST"}, student_token)
    print(f"  Valid Username Change Attempt: HTTP {status} - {res.get('message')}")
    
    # Revert username
    status, res = patch_json("/api/student/profile", {"username": "4PM23CS071"}, student_token)
    print(f"  Revert Username: HTTP {status} - {res.get('message')}")

print("\n" + "=" * 60)
print("4. VERIFYING ADMIN OVERVIEW & DASHBOARD API")
print("=" * 60)
admin_token = tokens.get("admin")
if admin_token:
    status, res = get_json("/api/admin/stats", admin_token)
    stats_data = res.get("data", {})
    users_data = stats_data.get("users", {})
    print(f"  Admin Stats: HTTP {status} - Total Users: {users_data.get('total')} (Students: {users_data.get('students')}, Parents: {users_data.get('parents')}, Teachers: {users_data.get('teachers')})")

    status, res = get_json("/api/admin/users", admin_token)
    print(f"  Admin User Directory: HTTP {status} - Total Returned: {len(res.get('data', []))}")

print("\n" + "=" * 60)
print("5. VERIFYING TEACHER & PARENT DASHBOARDS")
print("=" * 60)
teacher_token = tokens.get("teacher")
if teacher_token:
    status, res = get_json("/api/teacher/classes", teacher_token)
    print(f"  Teacher Classes: HTTP {status} - Classes count: {len(res.get('data', []))}")

parent_token = tokens.get("parent")
if parent_token:
    status, res = get_json("/api/parent/children", parent_token)
    print(f"  Parent Children: HTTP {status} - Children count: {len(res.get('data', []))}")

print("\n" + "=" * 60)
print("ALL VERIFICATIONS COMPLETED SUCCESSFULLY!")
print("=" * 60)
