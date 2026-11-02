import pytest
from backend.app import create_app
from backend.extensions import db
from backend.app.models import User, Teacher, Student

@pytest.fixture(scope='module')
def test_client():
    app = create_app('development')
    app.config['TESTING'] = True
    with app.app_context():
        with app.test_client() as client:
            yield client

def get_admin_auth(client):
    """Authenticate as Administrator (admin@pesitm.edu)"""
    resp = client.post('/api/auth/login', json={
        'identifier': 'admin@pesitm.edu',
        'password': 'password123',
        'portal_role': 'admin'
    })
    assert resp.status_code == 200, f"Admin login failed: {resp.data}"
    token = resp.get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}

def test_admin_system_stats(test_client):
    headers = get_admin_auth(test_client)
    resp = test_client.get('/api/admin/stats', headers=headers)
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload['success'] is True
    assert 'users' in payload['data']
    assert payload['data']['users']['total'] > 0
    assert payload['data']['academics']['classes'] > 0

def test_admin_users_list_and_role_filter(test_client):
    headers = get_admin_auth(test_client)
    resp = test_client.get('/api/admin/users?role=student&limit=10', headers=headers)
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload['success'] is True
    assert len(payload['data']) > 0
    assert all(u['role'] == 'student' for u in payload['data'])
    assert 'usn' in payload['data'][0]

def test_admin_create_update_and_deactivate_user(test_client):
    headers = get_admin_auth(test_client)
    import uuid
    uid_suffix = str(uuid.uuid4())[:6]
    test_email = f"test_teacher_{uid_suffix}@pesitm.edu"
    test_user = f"teacher_{uid_suffix}"

    # 1. Create User
    create_resp = test_client.post('/api/admin/users', headers=headers, json={
        'username': test_user,
        'email': test_email,
        'role': 'teacher',
        'password': 'InitialPassword@123',
        'name': f"Prof. Test {uid_suffix}",
        'employee_id': f"EMP-TEST-{uid_suffix}",
        'dept_id': 1
    })
    assert create_resp.status_code == 201
    user_id = create_resp.get_json()['data']['user_id']

    # 2. Deactivate User
    deact_resp = test_client.patch(f'/api/admin/users/{user_id}', headers=headers, json={
        'active': False
    })
    assert deact_resp.status_code == 200
    assert deact_resp.get_json()['data']['active'] is False

    # 3. Verify Deactivated User Login Rejection
    login_attempt = test_client.post('/api/auth/login', json={
        'identifier': test_email,
        'password': 'InitialPassword@123',
        'portal_role': 'teacher'
    })
    assert login_attempt.status_code == 403
    assert login_attempt.get_json()['error'] == 'ACCOUNT_DEACTIVATED'

    # 4. Reactivate and Reset Password
    react_resp = test_client.patch(f'/api/admin/users/{user_id}', headers=headers, json={
        'active': True
    })
    assert react_resp.status_code == 200

    pwd_resp = test_client.post(f'/api/admin/users/{user_id}/reset-password', headers=headers, json={
        'new_password': 'UpdatedPassword@456'
    })
    assert pwd_resp.status_code == 200

def test_admin_academic_structures(test_client):
    headers = get_admin_auth(test_client)
    # Departments
    d_resp = test_client.get('/api/admin/departments', headers=headers)
    assert d_resp.status_code == 200
    assert len(d_resp.get_json()['data']) > 0

    # Classes
    c_resp = test_client.get('/api/admin/classes', headers=headers)
    assert c_resp.status_code == 200
    assert len(c_resp.get_json()['data']) > 0

    # Subjects
    s_resp = test_client.get('/api/admin/subjects', headers=headers)
    assert s_resp.status_code == 200
    assert len(s_resp.get_json()['data']) > 0

def test_admin_teaching_assignments(test_client):
    headers = get_admin_auth(test_client)
    resp = test_client.get('/api/admin/assignments', headers=headers)
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload['success'] is True
    assert isinstance(payload['data'], list)

def test_admin_audit_logs(test_client):
    headers = get_admin_auth(test_client)
    resp = test_client.get('/api/admin/audit-logs', headers=headers)
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload['success'] is True
    assert len(payload['data']) > 0
    assert 'action' in payload['data'][0]

def test_admin_role_security_rejection(test_client):
    # Authenticate as student
    student_login = test_client.post('/api/auth/login', json={
        'identifier': '4PM21CS001',
        'password': 'password123',
        'portal_role': 'student'
    })
    st_token = student_login.get_json()['access_token']
    headers = {'Authorization': f'Bearer {st_token}'}

    # Student attempting to access admin endpoints
    resp = test_client.get('/api/admin/users', headers=headers)
    assert resp.status_code == 403
    assert resp.get_json()['error'] == 'FORBIDDEN'
