import pytest
from backend.app import create_app
from backend.app.models import Mark, Attendance, MarkHistory

@pytest.fixture(scope='module')
def test_client():
    app = create_app('development')
    app.config['TESTING'] = True
    with app.app_context():
        with app.test_client() as client:
            yield client

def get_teacher_auth(client):
    """Authenticate as Teacher (Prof. Anita Rao - CSE Class 1)"""
    resp = client.post('/api/auth/login', json={
        'identifier': 'anita.rao@pesitm.edu',
        'password': 'password123',
        'portal_role': 'teacher'
    })
    assert resp.status_code == 200, f"Teacher login failed: {resp.data}"
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

def test_bulk_marks_update_with_audit_trail(test_client):
    headers = get_teacher_auth(test_client)

    # Determine a new value that is guaranteed different from current value
    with test_client.application.app_context():
        m = Mark.query.filter_by(student_id=1, subject_id=1).first()
        curr_cie1 = float(m.cie1) if m else 30.0
        new_cie1 = 45.0 if curr_cie1 != 45.0 else 46.5

    payload = {
        'class_id': 1,
        'subject_id': 1,
        'reason': 'Phase 10 Regular CIE 1 Evaluation Entry',
        'marks': [
            {
                'student_id': 1,
                'cie1': new_cie1,
                'cie2': 46.0,
                'cie3': 40.0,
                'assignment_marks': 9.5,
                'quiz_marks': 8.5
            }
        ]
    }

    resp = test_client.post('/api/teacher/marks/bulk', headers=headers, json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert data['updated_students'] >= 1
    assert data['audit_entries'] > 0

def test_bulk_marks_missing_reason_rejection(test_client):
    headers = get_teacher_auth(test_client)

    # Missing reason
    payload = {
        'class_id': 1,
        'subject_id': 1,
        'reason': '   ',  # Empty string
        'marks': [
            {'student_id': 1, 'cie1': 45.0}
        ]
    }

    resp = test_client.post('/api/teacher/marks/bulk', headers=headers, json=payload)
    assert resp.status_code == 400
    data = resp.get_json()
    assert data['success'] is False
    assert data['error'] == 'VALIDATION_ERROR'

def test_marks_csv_template_download(test_client):
    headers = get_teacher_auth(test_client)
    resp = test_client.get('/api/teacher/classes/1/subjects/1/marks/template', headers=headers)
    assert resp.status_code == 200
    assert 'text/csv' in resp.content_type
    csv_text = resp.data.decode('utf-8')
    assert 'USN,Student_Name,CIE1_Out_Of_50' in csv_text
    assert '4PM21CS' in csv_text

def test_attendance_csv_template_download(test_client):
    headers = get_teacher_auth(test_client)
    resp = test_client.get('/api/teacher/classes/1/subjects/1/attendance/template', headers=headers)
    assert resp.status_code == 200
    assert 'text/csv' in resp.content_type
    csv_text = resp.data.decode('utf-8')
    assert 'USN,Student_Name,Classes_Held,Classes_Attended' in csv_text
    assert '4PM21CS' in csv_text

def test_class_subject_audit_history_query(test_client):
    headers = get_teacher_auth(test_client)
    resp = test_client.get('/api/teacher/classes/1/subjects/1/audit-history', headers=headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert 'data' in data
    # Check that audit items have required fields
    if len(data['data']) > 0:
        first = data['data'][0]
        assert 'student_name' in first
        assert 'field_name' in first
        assert 'old_value' in first
        assert 'new_value' in first
        assert 'reason' in first

def test_attendance_record_override_with_audit(test_client):
    headers = get_teacher_auth(test_client)
    # Fetch an attendance record id for student 1
    resp = test_client.patch('/api/teacher/attendance/1', headers=headers, json={
        'total_classes': 50,
        'attended_classes': 45,
        'reason': 'Approved Medical Leave and Sports Event Condonation'
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['success'] is True
    assert data['data']['attended_classes'] == 45
    assert data['data']['total_classes'] == 50
    assert float(data['data']['percentage']) == 90.0

def test_phase10_rbac_isolation(test_client):
    student_headers = get_student_auth(test_client)

    # 1. Student attempting bulk marks update must receive 403
    resp_marks = test_client.post('/api/teacher/marks/bulk', headers=student_headers, json={
        'class_id': 1,
        'subject_id': 1,
        'reason': 'Hacker attempt',
        'marks': [{'student_id': 1, 'cie1': 50.0}]
    })
    assert resp_marks.status_code == 403

    # 2. Student attempting attendance override must receive 403
    resp_att = test_client.patch('/api/teacher/attendance/1', headers=student_headers, json={
        'total_classes': 50,
        'attended_classes': 50,
        'reason': 'Hacker attempt'
    })
    assert resp_att.status_code == 403
