import io
import pytest
from backend.app import create_app
from backend.extensions import db
from backend.app.models import User, Teacher, Student, Mark, Attendance

@pytest.fixture(scope='module')
def test_client():
    app = create_app('development')
    app.config['TESTING'] = True
    with app.app_context():
        with app.test_client() as client:
            yield client

def get_teacher_auth(client):
    """Authenticate as Prof. Anita Rao (EMP-CSE-01)"""
    resp = client.post('/api/auth/login', json={
        'identifier': 'EMP-CSE-01',
        'password': 'password123',
        'portal_role': 'teacher'
    })
    assert resp.status_code == 200, f"Teacher login failed: {resp.data}"
    token = resp.get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}

def test_teacher_classes_list(test_client):
    headers = get_teacher_auth(test_client)
    resp = test_client.get('/api/teacher/classes', headers=headers)
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload['success'] is True
    assert 'teacher' in payload
    assert payload['teacher']['employee_id'] == 'EMP-CSE-01'
    assert 'data' in payload
    assert len(payload['data']) > 0
    first_assign = payload['data'][0]
    assert 'class_name' in first_assign
    assert 'subject_code' in first_assign
    assert 'metrics' in first_assign
    assert first_assign['metrics']['total_students'] > 0

def test_teacher_roster_endpoint(test_client):
    headers = get_teacher_auth(test_client)
    classes_resp = test_client.get('/api/teacher/classes', headers=headers)
    class_id = classes_resp.get_json()['data'][0]['class_id']
    subject_id = classes_resp.get_json()['data'][0]['subject_id']

    resp = test_client.get(f'/api/teacher/classes/{class_id}/students?subject_id={subject_id}', headers=headers)
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload['success'] is True
    assert 'data' in payload
    assert len(payload['data']) > 0
    student = payload['data'][0]
    assert 'usn' in student
    assert 'attendance' in student
    assert 'marks' in student
    assert 'prediction' in student

def test_teacher_marks_update_with_audit_trail(test_client):
    headers = get_teacher_auth(test_client)
    classes_resp = test_client.get('/api/teacher/classes', headers=headers)
    class_id = classes_resp.get_json()['data'][0]['class_id']
    roster_resp = test_client.get(f'/api/teacher/classes/{class_id}/students', headers=headers)
    marks_id = roster_resp.get_json()['data'][0]['marks']['marks_id']
    assert marks_id is not None

    # 1. Negative test: Missing mandatory audit reason
    bad_resp = test_client.patch(f'/api/teacher/marks/{marks_id}', headers=headers, json={
        'cie1': 25.0
    })
    assert bad_resp.status_code == 400
    assert bad_resp.get_json()['error'] == 'VALIDATION_ERROR'

    # 2. Positive test: Update with reason
    good_resp = test_client.patch(f'/api/teacher/marks/{marks_id}', headers=headers, json={
        'cie1': 26.5,
        'reason': 'Re-evaluation of Question 2 part B per student recheck application'
    })
    assert good_resp.status_code == 200
    res_data = good_resp.get_json()
    assert res_data['success'] is True
    assert res_data['data']['cie1'] == 26.5
    assert len(res_data['audit_trail']) >= 1

    # 3. Verify history audit trail endpoint
    hist_resp = test_client.get(f'/api/teacher/marks/{marks_id}/history', headers=headers)
    assert hist_resp.status_code == 200
    hist_payload = hist_resp.get_json()
    assert hist_payload['success'] is True
    assert len(hist_payload['data']) >= 1
    assert any('Re-evaluation' in h['reason'] for h in hist_payload['data'])

def test_teacher_session_attendance_logging(test_client):
    headers = get_teacher_auth(test_client)
    classes_resp = test_client.get('/api/teacher/classes', headers=headers)
    class_id = classes_resp.get_json()['data'][0]['class_id']
    subject_id = classes_resp.get_json()['data'][0]['subject_id']
    roster_resp = test_client.get(f'/api/teacher/classes/{class_id}/students', headers=headers)
    students = roster_resp.get_json()['data'][:3]

    att_payload = {
        'class_id': class_id,
        'subject_id': subject_id,
        'date': '2026-10-31',
        'attendance_list': [{'student_id': s['student_id'], 'is_present': True} for s in students]
    }
    resp = test_client.post('/api/teacher/attendance', headers=headers, json=att_payload)
    assert resp.status_code == 200
    assert resp.get_json()['success'] is True

def test_teacher_batch_upload_csv(test_client):
    headers = get_teacher_auth(test_client)
    classes_resp = test_client.get('/api/teacher/classes', headers=headers)
    class_id = classes_resp.get_json()['data'][0]['class_id']
    subject_id = classes_resp.get_json()['data'][0]['subject_id']
    roster_resp = test_client.get(f'/api/teacher/classes/{class_id}/students', headers=headers)
    usn = roster_resp.get_json()['data'][0]['usn']

    csv_content = f"usn,cie1,cie2,cie3,assignment,quiz\n{usn},27.0,26.5,28.0,9.0,8.5\n"
    data = {
        'class_id': str(class_id),
        'subject_id': str(subject_id),
        'upload_type': 'marks',
        'file': (io.BytesIO(csv_content.encode('utf-8')), 'marks_batch.csv')
    }
    resp = test_client.post('/api/teacher/upload', headers=headers, data=data, content_type='multipart/form-data')
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload['success'] is True
    assert payload['processed_count'] >= 1

def test_teacher_notify_broadcast(test_client):
    headers = get_teacher_auth(test_client)
    classes_resp = test_client.get('/api/teacher/classes', headers=headers)
    class_id = classes_resp.get_json()['data'][0]['class_id']

    resp = test_client.post('/api/teacher/notify', headers=headers, json={
        'class_id': class_id,
        'student_ids': 'all',
        'subject': 'Laboratory Exam Schedule Notice',
        'message': 'VTU Practical Examination for Machine Learning is scheduled for next Monday at 09:00 AM.',
        'send_to_parent': True
    })
    assert resp.status_code == 201
    payload = resp.get_json()
    assert payload['success'] is True
    assert payload['dispatched_count'] > 0

def test_teacher_class_access_security_isolation(test_client):
    headers = get_teacher_auth(test_client)
    # Attempting to access non-existent / unauthorized class ID
    resp = test_client.get('/api/teacher/classes/999/students', headers=headers)
    assert resp.status_code in (403, 404)
