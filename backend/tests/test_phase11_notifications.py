import pytest
from backend.app import create_app
from backend.extensions import db
from backend.app.models import Notification, User

@pytest.fixture(scope='module')
def test_client():
    app = create_app('development')
    app.config['TESTING'] = True
    with app.app_context():
        with app.test_client() as client:
            yield client

def get_auth_token(client, identifier, password, role):
    resp = client.post('/api/auth/login', json={
        'identifier': identifier,
        'password': password,
        'portal_role': role
    })
    assert resp.status_code == 200, f"Login failed for {identifier}: {resp.data}"
    return {'Authorization': f"Bearer {resp.get_json()['access_token']}"}

def test_notifications_status(test_client):
    resp = test_client.get('/api/notifications/status')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['module'] == 'Notifications & In-Portal Communications Service'
    assert data['status'] == 'active'

def test_broadcast_and_delivery(test_client):
    teacher_headers = get_auth_token(test_client, 'anita.rao@pesitm.edu', 'password123', 'teacher')

    # Broadcast notification to Class 1
    resp = test_client.post('/api/notifications/broadcast', headers=teacher_headers, json={
        'class_id': 1,
        'title': 'VTU Phase 11 Academic Notification',
        'message': 'Official circular regarding semester CIE-3 timetable schedule and laboratory records.',
        'target_role': 'all'
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data['success'] is True
    assert data['dispatched_count'] > 0

def test_get_user_notifications_and_unread_count(test_client):
    student_headers = get_auth_token(test_client, '4PM21CS001', 'password123', 'student')

    # 1. Check unread count endpoint
    resp_count = test_client.get('/api/notifications/unread-count', headers=student_headers)
    assert resp_count.status_code == 200
    data_count = resp_count.get_json()
    assert data_count['success'] is True
    assert 'unread_count' in data_count

    # 2. Check full notifications list
    resp_list = test_client.get('/api/notifications', headers=student_headers)
    assert resp_list.status_code == 200
    data_list = resp_list.get_json()
    assert data_list['success'] is True
    assert len(data_list['data']) > 0

    first_notif = data_list['data'][0]
    assert 'title' in first_notif
    assert 'message' in first_notif
    assert 'status' in first_notif

def test_mark_individual_notification_as_read(test_client):
    student_headers = get_auth_token(test_client, '4PM21CS001', 'password123', 'student')

    resp_list = test_client.get('/api/notifications?unread_only=true', headers=student_headers)
    assert resp_list.status_code == 200
    notifs = resp_list.get_json()['data']

    if notifs:
        target_id = notifs[0]['id']
        resp_read = test_client.patch(f'/api/notifications/{target_id}/read', headers=student_headers)
        assert resp_read.status_code == 200
        assert resp_read.get_json()['data']['status'] == 'read'
        assert resp_read.get_json()['data']['read_at'] is not None

def test_mark_all_notifications_as_read(test_client):
    student_headers = get_auth_token(test_client, '4PM21CS001', 'password123', 'student')

    resp_read_all = test_client.post('/api/notifications/read-all', headers=student_headers)
    assert resp_read_all.status_code == 200
    assert resp_read_all.get_json()['success'] is True

    # Verify unread count is now 0
    resp_count = test_client.get('/api/notifications/unread-count', headers=student_headers)
    assert resp_count.get_json()['unread_count'] == 0

def test_delete_notification(test_client):
    student_headers = get_auth_token(test_client, '4PM21CS001', 'password123', 'student')

    resp_list = test_client.get('/api/notifications', headers=student_headers)
    notifs = resp_list.get_json()['data']
    assert len(notifs) > 0

    target_id = notifs[-1]['id']
    resp_del = test_client.delete(f'/api/notifications/{target_id}', headers=student_headers)
    assert resp_del.status_code == 200
    assert resp_del.get_json()['success'] is True

def test_notification_ownership_security(test_client):
    student1_headers = get_auth_token(test_client, '4PM21CS001', 'password123', 'student')
    student2_headers = get_auth_token(test_client, '4PM21CS002', 'password123', 'student')

    # Create a fresh notification specifically for Student 1
    with test_client.application.app_context():
        from backend.app.models import Student
        s1 = Student.query.filter_by(usn='4PM21CS001').first()
        notif = Notification(
            sender_id=2,
            recipient_user_id=s1.user_id,
            student_id=s1.student_id,
            title='Confidential Notice for Student 1',
            message='Confidential message intended solely for student 1.',
            status='sent'
        )
        db.session.add(notif)
        db.session.commit()
        st1_notif_id = notif.id

    # Student 2 attempting to mark student 1's notification as read must receive 403 Forbidden
    resp_forbidden = test_client.patch(f'/api/notifications/{st1_notif_id}/read', headers=student2_headers)
    assert resp_forbidden.status_code == 403
    assert resp_forbidden.get_json()['error'] == 'FORBIDDEN'
