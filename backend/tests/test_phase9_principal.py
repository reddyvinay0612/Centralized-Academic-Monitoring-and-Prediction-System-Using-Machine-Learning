import pytest
from backend.app import create_app

@pytest.fixture(scope='module')
def test_client():
    app = create_app('development')
    app.config['TESTING'] = True
    with app.app_context():
        with app.test_client() as client:
            yield client

def get_principal_auth(client):
    """Authenticate as Principal (principal@pesitm.edu)"""
    resp = client.post('/api/auth/login', json={
        'identifier': 'principal@pesitm.edu',
        'password': 'password123',
        'portal_role': 'principal'
    })
    assert resp.status_code == 200, f"Principal login failed: {resp.data}"
    token = resp.get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}

def get_student_auth(client):
    """Authenticate as Student (4PM21CS001)"""
    resp = client.post('/api/auth/login', json={
        'identifier': '4PM21CS001',
        'password': 'password123',
        'portal_role': 'student'
    })
    assert resp.status_code == 200, f"Student login failed: {resp.data}"
    token = resp.get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}

def test_principal_status(test_client):
    resp = test_client.get('/api/principal/status')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['module'] == 'Principal Portal API'
    assert data['status'] == 'active'

def test_principal_overview(test_client):
    headers = get_principal_auth(test_client)
    resp = test_client.get('/api/principal/overview', headers=headers)
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload['success'] is True
    data = payload['data']

    # Check Headcount
    assert data['headcount']['total_students'] >= 240
    assert data['headcount']['total_faculty'] >= 12
    assert data['headcount']['total_departments'] >= 4
    assert data['headcount']['student_faculty_ratio'] > 0

    # Check Academic Health
    assert 'college_avg_attendance' in data['academic_health']
    assert data['academic_health']['college_avg_attendance'] > 0
    assert 'college_avg_cgpa' in data['academic_health']
    assert data['academic_health']['college_avg_cgpa'] > 0

    # Check Risk Distribution
    assert 'high' in data['risk_distribution']['counts']
    assert 'medium' in data['risk_distribution']['counts']
    assert 'low' in data['risk_distribution']['counts']

def test_principal_departments_matrix(test_client):
    headers = get_principal_auth(test_client)
    resp = test_client.get('/api/principal/departments', headers=headers)
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload['success'] is True
    matrix = payload['data']
    assert len(matrix) >= 4

    dept_codes = [d['dept_code'] for d in matrix]
    assert 'CSE' in dept_codes
    assert 'ISE' in dept_codes
    assert 'ECE' in dept_codes
    assert 'CSD' in dept_codes

    cse = next(d for d in matrix if d['dept_code'] == 'CSE')
    assert cse['headcount']['students'] > 0
    assert cse['performance']['avg_attendance'] > 0
    assert cse['performance']['avg_cgpa'] > 0

def test_principal_classes_cohorts(test_client):
    headers = get_principal_auth(test_client)
    resp = test_client.get('/api/principal/classes', headers=headers)
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload['success'] is True
    classes = payload['data']
    assert len(classes) >= 12

    first_cls = classes[0]
    assert 'class_name' in first_cls
    assert 'avg_attendance' in first_cls
    assert 'avg_cie' in first_cls
    assert 'at_risk_students' in first_cls

    # Test filtering by dept_id=1 (CSE)
    filtered_resp = test_client.get('/api/principal/classes?dept_id=1', headers=headers)
    assert filtered_resp.status_code == 200
    filtered = filtered_resp.get_json()['data']
    assert len(filtered) > 0
    assert all(c['department_code'] == 'CSE' for c in filtered)

def test_principal_students_search_and_filter(test_client):
    headers = get_principal_auth(test_client)
    # 1. Fetch college-wide students
    resp = test_client.get('/api/principal/students?limit=20', headers=headers)
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload['success'] is True
    assert len(payload['data']) > 0

    first_st = payload['data'][0]
    assert 'usn' in first_st
    assert 'attendance_percentage' in first_st
    assert 'cgpa' in first_st
    assert 'risk_level' in first_st

    # 2. Search query by USN prefix
    search_resp = test_client.get('/api/principal/students?search=4PM21CS', headers=headers)
    assert search_resp.status_code == 200
    search_data = search_resp.get_json()['data']
    assert len(search_data) > 0
    assert all('4PM21CS' in s['usn'] for s in search_data)

    # 3. Filter by risk level
    risk_resp = test_client.get('/api/principal/students?risk_level=high', headers=headers)
    assert risk_resp.status_code == 200
    risk_data = risk_resp.get_json()['data']
    assert all(s['risk_level'] == 'high' for s in risk_data)

def test_principal_executive_report_pdf(test_client):
    headers = get_principal_auth(test_client)
    resp = test_client.get('/api/principal/report/executive', headers=headers)
    assert resp.status_code == 200
    assert resp.content_type == 'application/pdf'
    assert resp.data[:4] == b'%PDF', "Response is not a valid PDF document"
    assert len(resp.data) > 1000

def test_principal_rbac_access_isolation(test_client):
    student_headers = get_student_auth(test_client)
    # A student attempting to access principal endpoints must receive 403 Forbidden
    resp = test_client.get('/api/principal/overview', headers=student_headers)
    assert resp.status_code == 403
    payload = resp.get_json()
    assert payload['success'] is False
    assert payload['error'] == 'FORBIDDEN'

    # Unauthenticated request must receive 401 Unauthorized
    resp_unauth = test_client.get('/api/principal/overview')
    assert resp_unauth.status_code == 401
