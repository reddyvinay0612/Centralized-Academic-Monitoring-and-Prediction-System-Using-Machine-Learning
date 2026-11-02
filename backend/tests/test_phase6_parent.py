import pytest
from backend.app import create_app
from backend.extensions import db
from backend.app.models import User, Parent, Student, ParentStudent

@pytest.fixture(scope='module')
def test_client():
    app = create_app('development')
    app.config['TESTING'] = True
    with app.app_context():
        with app.test_client() as client:
            yield client

def get_parent_auth(client):
    """Authenticate as Guardian 001 (parent_001@gmail.com)"""
    resp = client.post('/api/auth/login', json={
        'identifier': 'parent_001@gmail.com',
        'password': 'password123',
        'portal_role': 'parent'
    })
    assert resp.status_code == 200, f"Parent login failed: {resp.data}"
    token = resp.get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}

def test_parent_children_list_and_selector(test_client):
    headers = get_parent_auth(test_client)
    resp = test_client.get('/api/parent/children', headers=headers)
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload['success'] is True
    assert 'parent' in payload
    assert payload['parent']['email'] == 'parent_001@gmail.com'
    assert 'data' in payload
    assert len(payload['data']) >= 2  # Multi-child: Poorvi V S and Rohan Verma
    
    first_child = payload['data'][0]
    assert 'student_id' in first_child
    assert 'name' in first_child
    assert 'usn' in first_child
    assert 'attendance_percentage' in first_child
    assert 'risk_level' in first_child

def test_child_summary_authorized(test_client):
    headers = get_parent_auth(test_client)
    # Get children to find authorized ID
    ch_resp = test_client.get('/api/parent/children', headers=headers)
    child_id = ch_resp.get_json()['data'][0]['student_id']

    resp = test_client.get(f'/api/parent/children/{child_id}/summary', headers=headers)
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload['success'] is True
    data = payload['data']
    assert 'student' in data
    assert 'attendance' in data
    assert 'academics' in data
    assert 'finance' in data
    assert 'prediction' in data
    assert 'remarks' in data

def test_child_summary_unauthorized_isolation(test_client):
    headers = get_parent_auth(test_client)
    # Student ID 200 is not linked to Guardian 001
    resp = test_client.get('/api/parent/children/200/summary', headers=headers)
    assert resp.status_code == 403
    payload = resp.get_json()
    assert payload['success'] is False
    assert payload['error'] == 'FORBIDDEN'

def test_parent_message_dispatch(test_client):
    headers = get_parent_auth(test_client)
    ch_resp = test_client.get('/api/parent/children', headers=headers)
    child_id = ch_resp.get_json()['data'][0]['student_id']

    resp = test_client.post('/api/parent/messages', headers=headers, json={
        'student_id': child_id,
        'subject': 'Attendance & Remedial Inquiry',
        'message': 'Kindly advise on the schedule for upcoming remedial sessions for laboratory credits.'
    })
    assert resp.status_code == 201
    payload = resp.get_json()
    assert payload['success'] is True
    assert 'successfully' in payload['message']

def test_parent_messages_history(test_client):
    headers = get_parent_auth(test_client)
    resp = test_client.get('/api/parent/messages', headers=headers)
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload['success'] is True
    assert isinstance(payload['data'], list)
    assert len(payload['data']) > 0

def test_parent_child_report_pdf_download(test_client):
    headers = get_parent_auth(test_client)
    ch_resp = test_client.get('/api/parent/children', headers=headers)
    child_id = ch_resp.get_json()['data'][0]['student_id']

    resp = test_client.get(f'/api/parent/children/{child_id}/report', headers=headers)
    assert resp.status_code == 200
    assert resp.content_type == 'application/pdf'
    assert resp.data.startswith(b'%PDF')
    assert len(resp.data) > 1000
