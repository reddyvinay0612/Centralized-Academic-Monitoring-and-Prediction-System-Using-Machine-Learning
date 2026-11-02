import pytest
import json
from backend.app import create_app
from backend.extensions import db
from backend.app.models import User, Student

@pytest.fixture(scope='module')
def test_client():
    app = create_app('development')
    app.config['TESTING'] = True
    with app.app_context():
        with app.test_client() as client:
            yield client

def get_student_auth_header(client):
    """Helper to authenticate as benchmark student 4PM21CS001"""
    login_resp = client.post('/api/auth/login', json={
        'identifier': '4PM21CS001',
        'password': 'password123',
        'portal_role': 'student'
    })
    assert login_resp.status_code == 200, f"Login failed: {login_resp.data}"
    token = login_resp.get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}

def test_student_profile_endpoint(test_client):
    headers = get_student_auth_header(test_client)
    resp = test_client.get('/api/student/me', headers=headers)
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload['success'] is True
    data = payload['data']
    assert data['usn'] == '4PM21CS001'
    assert data['name'] == 'Poorvi V S'
    assert 'department' in data
    assert data['department']['dept_code'] == 'CSE'
    assert 'mentor' in data
    assert data['mentor']['name'] is not None

def test_student_attendance_endpoint(test_client):
    headers = get_student_auth_header(test_client)
    resp = test_client.get('/api/student/attendance', headers=headers)
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload['success'] is True
    data = payload['data']
    assert 'overall' in data
    assert data['overall']['total_classes'] > 0
    assert 'percentage' in data['overall']
    assert isinstance(data['subjects'], list)
    assert len(data['subjects']) > 0
    first_sub = data['subjects'][0]
    assert 'percentage' in first_sub
    assert 'is_shortage' in first_sub

def test_student_marks_and_progression_endpoint(test_client):
    headers = get_student_auth_header(test_client)
    resp = test_client.get('/api/student/marks', headers=headers)
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload['success'] is True
    data = payload['data']
    assert isinstance(data['subjects'], list)
    assert len(data['subjects']) > 0
    assert 'cie1' in data['subjects'][0]
    assert 'total_cie' in data['subjects'][0]
    assert 'progression' in data
    assert isinstance(data['progression'], list)
    assert 'summary' in data
    assert 'cgpa' in data['summary']

def test_student_timetable_endpoint(test_client):
    headers = get_student_auth_header(test_client)
    resp = test_client.get('/api/student/timetable', headers=headers)
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload['success'] is True
    data = payload['data']
    assert 'days' in data
    assert 'Monday' in data['days']
    assert 'schedule' in data
    assert 'Monday' in data['schedule']

def test_student_prediction_endpoint(test_client):
    headers = get_student_auth_header(test_client)
    resp = test_client.get('/api/student/prediction', headers=headers)
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload['success'] is True
    data = payload['data']
    assert data['risk_level'] in ('low', 'medium', 'high')
    assert 0.0 <= data['risk_score'] <= 1.0
    assert 'explanations' in data
    assert isinstance(data['explanations'], list)

def test_student_report_pdf_download(test_client):
    headers = get_student_auth_header(test_client)
    resp = test_client.get('/api/student/report/download', headers=headers)
    assert resp.status_code == 200
    assert resp.content_type == 'application/pdf'
    assert resp.data.startswith(b'%PDF')
    assert len(resp.data) > 1000

def test_student_isolation_rejection(test_client):
    headers = get_student_auth_header(test_client)
    # Student attempting to query someone else's ID
    resp = test_client.get('/api/student/me?student_id=999', headers=headers)
    assert resp.status_code == 403
    payload = resp.get_json()
    assert payload['success'] is False
    assert payload['error'] == 'FORBIDDEN'
