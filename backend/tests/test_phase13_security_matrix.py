import pytest
import uuid
from backend.app import create_app
from backend.extensions import db, bcrypt
from backend.app.models import User, Student, Teacher, Parent, Notification, Mark, MarkHistory

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

def get_admin_auth(client):
    """Helper to authenticate as admin"""
    resp = client.post('/api/auth/login', json={
        'identifier': 'admin@pesitm.edu',
        'password': 'password123',
        'portal_role': 'admin'
    })
    assert resp.status_code == 200
    return {'Authorization': f"Bearer {resp.get_json()['access_token']}"}


# ==============================================================================
# 1. VERTICAL PRIVILEGE ESCALATION PREVENTION
# ==============================================================================

def test_vertical_privilege_escalation_students(test_client):
    """
    Ensure students are blocked (403 Forbidden) from administrative, principal,
    and teacher endpoints.
    """
    student_headers = get_auth_token(test_client, '4PM21CS001', 'password123', 'student')

    # Student cannot create or list users
    resp = test_client.post('/api/admin/users', headers=student_headers, json={'username': 'hacked_admin'})
    assert resp.status_code == 403
    assert resp.get_json()['error'] == 'FORBIDDEN'

    resp = test_client.get('/api/admin/stats', headers=student_headers)
    assert resp.status_code == 403

    resp = test_client.get('/api/admin/audit-logs', headers=student_headers)
    assert resp.status_code == 403

    # Student cannot access principal executive overview or reports
    resp = test_client.get('/api/principal/overview', headers=student_headers)
    assert resp.status_code == 403

    resp = test_client.get('/api/principal/report/executive', headers=student_headers)
    assert resp.status_code == 403

    # Student cannot submit or alter marks
    resp = test_client.post('/api/teacher/marks/bulk', headers=student_headers, json={
        'class_id': 2, 'subject_id': 1, 'reason': 'Malicious escalation', 'marks': []
    })
    assert resp.status_code == 403

    # Student cannot broadcast circular notifications
    resp = test_client.post('/api/notifications/broadcast', headers=student_headers, json={
        'class_id': 1, 'title': 'Cancel Exams', 'message': 'All classes canceled'
    })
    assert resp.status_code == 403


def test_vertical_privilege_escalation_parents(test_client):
    """
    Ensure parents are strictly isolated to parent portal and cannot execute
    admin, principal, or teacher operations.
    """
    parent_headers = get_auth_token(test_client, 'parent_001@gmail.com', 'password123', 'parent')

    # Parent cannot access admin stats or users
    resp = test_client.get('/api/admin/stats', headers=parent_headers)
    assert resp.status_code == 403

    resp = test_client.post('/api/admin/users', headers=parent_headers, json={'username': 'parent_admin'})
    assert resp.status_code == 403

    # Parent cannot access principal overview
    resp = test_client.get('/api/principal/overview', headers=parent_headers)
    assert resp.status_code == 403

    # Parent cannot alter academic marks or log attendance
    resp = test_client.post('/api/teacher/marks/bulk', headers=parent_headers, json={
        'class_id': 2, 'subject_id': 1, 'reason': 'Parent mark boost', 'marks': []
    })
    assert resp.status_code == 403

    # Parent cannot broadcast notifications
    resp = test_client.post('/api/notifications/broadcast', headers=parent_headers, json={
        'class_id': 1, 'title': 'Parent circular', 'message': 'Parent broadcast attempt'
    })
    assert resp.status_code == 403


def test_vertical_privilege_escalation_teachers(test_client):
    """
    Ensure teachers cannot access system administrative controls or principal-level analytics.
    """
    teacher_headers = get_auth_token(test_client, 'anita.rao@pesitm.edu', 'password123', 'teacher')

    # Teacher cannot create or modify users
    resp = test_client.post('/api/admin/users', headers=teacher_headers, json={'username': 'rogue_teacher'})
    assert resp.status_code == 403

    resp = test_client.patch('/api/admin/users/1', headers=teacher_headers, json={'active': False})
    assert resp.status_code == 403

    resp = test_client.get('/api/admin/audit-logs', headers=teacher_headers)
    assert resp.status_code == 403

    # Teacher cannot view executive overview or download institution executive PDF
    resp = test_client.get('/api/principal/overview', headers=teacher_headers)
    assert resp.status_code == 403

    resp = test_client.get('/api/principal/report/executive', headers=teacher_headers)
    assert resp.status_code == 403


def test_vertical_privilege_escalation_principal_cannot_admin_users(test_client):
    """
    Ensure Principal role is segregated from Superadmin user creation and password resets.
    """
    principal_headers = get_auth_token(test_client, 'principal@pesitm.edu', 'password123', 'principal')

    # Principal cannot invoke admin user mutation endpoints
    resp = test_client.post('/api/admin/users', headers=principal_headers, json={
        'username': 'principal_created', 'email': 'principal_created@pesitm.edu', 'role': 'admin'
    })
    assert resp.status_code == 403

    resp = test_client.patch('/api/admin/users/2', headers=principal_headers, json={'active': False})
    assert resp.status_code == 403

    resp = test_client.post('/api/admin/users/2/reset-password', headers=principal_headers, json={
        'new_password': 'NewPassword123'
    })
    assert resp.status_code == 403


# ==============================================================================
# 2. HORIZONTAL PRIVILEGE ESCALATION (IDOR PREVENTION)
# ==============================================================================

def test_horizontal_privilege_escalation_student_idor(test_client):
    """
    Ensure Student A (Student 1) cannot read Student B's (Student 2) marks, attendance, or report card.
    """
    student1_headers = get_auth_token(test_client, '4PM21CS001', 'password123', 'student')

    # 1. Student 1 accessing Student 2's marks -> 403 Forbidden
    resp = test_client.get('/api/student/marks?student_id=2', headers=student1_headers)
    assert resp.status_code == 403
    assert 'Students can only access their own records' in resp.get_json()['message']

    # 2. Student 1 accessing Student 2's attendance -> 403 Forbidden
    resp = test_client.get('/api/student/attendance?student_id=2', headers=student1_headers)
    assert resp.status_code == 403

    # 3. Student 1 accessing Student 2's report card PDF -> 403 Forbidden
    resp = test_client.get('/api/student/report/download?student_id=2', headers=student1_headers)
    assert resp.status_code == 403
    assert 'Students can only access their own records' in resp.get_json()['message']

    # 4. Student 1 accessing their own records succeeds (200)
    resp_own = test_client.get('/api/student/marks', headers=student1_headers)
    assert resp_own.status_code == 200
    assert resp_own.get_json()['success'] is True


def test_horizontal_privilege_escalation_parent_idor(test_client):
    """
    Ensure Parent 1 (registered guardian of Student 1 only) cannot access Student 2's data.
    """
    parent1_headers = get_auth_token(test_client, 'parent_001@gmail.com', 'password123', 'parent')

    # Discover authorized child ID
    ch_resp = test_client.get('/api/parent/children', headers=parent1_headers)
    assert ch_resp.status_code == 200
    authorized_child_id = ch_resp.get_json()['data'][0]['student_id']

    # Authorized child succeeds
    resp_child1 = test_client.get(f'/api/parent/children/{authorized_child_id}/summary', headers=parent1_headers)
    assert resp_child1.status_code == 200
    assert resp_child1.get_json()['success'] is True

    # Unauthorized child (Student ID 200 is not linked) is blocked with 403 Forbidden
    resp_child_unauth = test_client.get('/api/parent/children/200/summary', headers=parent1_headers)
    assert resp_child_unauth.status_code == 403
    assert 'only access records of your registered children' in resp_child_unauth.get_json()['message']

    resp_report_unauth = test_client.get('/api/parent/children/200/report', headers=parent1_headers)
    assert resp_report_unauth.status_code == 403


def test_horizontal_privilege_escalation_teacher_class_idor(test_client):
    """
    Ensure Teacher 1 (CSE, assigned to Class 2) cannot access or modify Class 8 (ECE).
    """
    teacher_headers = get_auth_token(test_client, 'anita.rao@pesitm.edu', 'password123', 'teacher')

    # 1. Accessing unassigned Class 8 student roster -> 403 Forbidden
    resp_roster = test_client.get('/api/teacher/classes/8/students', headers=teacher_headers)
    assert resp_roster.status_code == 403
    assert 'not assigned to instruct or mentor this class' in resp_roster.get_json()['message']

    # 2. Updating marks in unassigned Class 8 -> 403 Forbidden
    resp_marks = test_client.post('/api/teacher/marks/bulk', headers=teacher_headers, json={
        'class_id': 8,
        'subject_id': 7,
        'reason': 'Cross-department marks injection',
        'marks': [{'student_id': 141, 'cie1': 40}]
    })
    assert resp_marks.status_code == 403

    # 3. Accessing assigned Class 2 roster -> 200 OK
    resp_own = test_client.get('/api/teacher/classes/2/students', headers=teacher_headers)
    assert resp_own.status_code == 200
    assert resp_own.get_json()['success'] is True


# ==============================================================================
# 3. JWT TAMPER & FORGERY PROTECTION
# ==============================================================================

def test_jwt_tamper_and_forgery_rejection(test_client):
    """
    Verify that unauthenticated, forged, or tampered JWT requests fail with 401 Unauthorized.
    """
    # 1. No header
    resp = test_client.get('/api/student/me')
    assert resp.status_code == 401

    # 2. Garbage Bearer string
    resp = test_client.get('/api/student/me', headers={'Authorization': 'Bearer totally.fake.jwt'})
    assert resp.status_code == 401

    # 3. Valid token with tampered signature
    student_headers = get_auth_token(test_client, '4PM21CS001', 'password123', 'student')
    valid_token = student_headers['Authorization'].replace('Bearer ', '')
    # Corrupt last 6 characters of token
    tampered_token = valid_token[:-6] + 'XYZ999'
    resp = test_client.get('/api/student/me', headers={'Authorization': f'Bearer {tampered_token}'})
    assert resp.status_code == 401

    # 4. Malformed Authorization scheme (Basic instead of Bearer)
    resp = test_client.get('/api/student/me', headers={'Authorization': f'Basic {valid_token}'})
    assert resp.status_code == 401


# ==============================================================================
# 4. ACCOUNT DEACTIVATION & TOKEN INVALIDATION
# ==============================================================================

def test_deactivated_account_immediate_revocation(test_client):
    """
    Verify that deactivating a user immediately invalidates active tokens
    and rejects future login attempts with 403 ACCOUNT_DEACTIVATED.
    """
    admin_headers = get_admin_auth(test_client)
    suffix = str(uuid.uuid4())[:6]
    test_email = f"sec_deact_{suffix}@pesitm.edu"
    test_username = f"sec_deact_{suffix}"

    # 1. Admin creates active test user
    resp_create = test_client.post('/api/admin/users', headers=admin_headers, json={
        'username': test_username,
        'email': test_email,
        'role': 'student',
        'password': 'password123',
        'name': f'Security Deact User {suffix}'
    })
    assert resp_create.status_code == 201
    user_id = resp_create.get_json()['data']['user_id']

    # 2. User logs in and acquires JWT
    user_headers = get_auth_token(test_client, test_email, 'password123', 'student')

    # 3. Admin deactivates user account
    resp_deact = test_client.patch(f'/api/admin/users/{user_id}', headers=admin_headers, json={'active': False})
    assert resp_deact.status_code == 200
    assert resp_deact.get_json()['data']['active'] is False

    # 4. Pre-issued token is immediately rejected on protected endpoint -> 401 ACCOUNT_INACTIVE
    resp_probe = test_client.get('/api/notifications', headers=user_headers)
    assert resp_probe.status_code == 401
    assert resp_probe.get_json()['error'] == 'ACCOUNT_INACTIVE'

    # 5. Subsequent login attempt is blocked with 403 ACCOUNT_DEACTIVATED
    resp_login = test_client.post('/api/auth/login', json={
        'identifier': test_email,
        'password': 'password123',
        'portal_role': 'student'
    })
    assert resp_login.status_code == 403
    assert resp_login.get_json()['error'] == 'ACCOUNT_DEACTIVATED'

    # 6. Admin reactivates account
    resp_react = test_client.patch(f'/api/admin/users/{user_id}', headers=admin_headers, json={'active': True})
    assert resp_react.status_code == 200

    # 7. User can log in again -> 200 OK
    resp_relogin = test_client.post('/api/auth/login', json={
        'identifier': test_email,
        'password': 'password123',
        'portal_role': 'student'
    })
    assert resp_relogin.status_code == 200


# ==============================================================================
# 5. BRUTE-FORCE RATE LIMITING & LOCKOUT SECURITY
# ==============================================================================

def test_brute_force_lockout_and_account_protection(test_client):
    """
    Verify that 5 consecutive failed login attempts trigger a 15-minute lockout,
    returning 429 ACCOUNT_LOCKED, and blocking even valid password submissions while locked.
    """
    admin_headers = get_admin_auth(test_client)
    suffix = str(uuid.uuid4())[:6]
    test_email = f"sec_lockout_{suffix}@pesitm.edu"
    test_username = f"sec_lockout_{suffix}"

    # 1. Admin creates active test user
    resp_create = test_client.post('/api/admin/users', headers=admin_headers, json={
        'username': test_username,
        'email': test_email,
        'role': 'student',
        'password': 'password123',
        'name': f'Lockout Test User {suffix}'
    })
    assert resp_create.status_code == 201
    user_id = resp_create.get_json()['data']['user_id']

    # 2. Submit 4 failed login attempts (should return 401 with remaining attempts)
    for attempt in range(1, 5):
        resp = test_client.post('/api/auth/login', json={
            'identifier': test_email,
            'password': 'wrong_password',
            'portal_role': 'student'
        })
        assert resp.status_code == 401
        assert f"{5 - attempt} attempt(s) remaining" in resp.get_json()['message']

    # 3. 5th failed attempt triggers 15-min lockout -> 429 ACCOUNT_LOCKED
    resp_5th = test_client.post('/api/auth/login', json={
        'identifier': test_email,
        'password': 'wrong_password',
        'portal_role': 'student'
    })
    assert resp_5th.status_code == 429
    assert resp_5th.get_json()['error'] == 'ACCOUNT_LOCKED'
    assert 'locked for 15 minutes' in resp_5th.get_json()['message']

    # 4. 6th attempt with CORRECT password is still blocked while locked out -> 429
    resp_6th = test_client.post('/api/auth/login', json={
        'identifier': test_email,
        'password': 'password123',
        'portal_role': 'student'
    })
    assert resp_6th.status_code == 429
    assert resp_6th.get_json()['error'] == 'ACCOUNT_LOCKED'

    # 5. Clean up by resetting failed attempts on user
    with test_client.application.app_context():
        u = db.session.get(User, user_id)
        if u:
            u.reset_failed_attempts()
            db.session.commit()


# ==============================================================================
# 6. SQL INJECTION RESILIENCE
# ==============================================================================

def test_sql_injection_defense_across_attack_vectors(test_client):
    """
    Verify application defenses against SQL injection attacks in login credentials,
    search queries, and parameter inputs.
    """
    initial_user_count = User.query.count()

    # 1. SQL Injection payload in login identifier
    resp_login_sqli = test_client.post('/api/auth/login', json={
        'identifier': "' OR '1'='1' --",
        'password': "random_password",
        'portal_role': 'student'
    })
    assert resp_login_sqli.status_code == 401
    assert resp_login_sqli.get_json()['error'] == 'INVALID_CREDENTIALS'

    # 2. DROP TABLE payload in admin search
    admin_headers = get_admin_auth(test_client)
    resp_search_sqli = test_client.get('/api/admin/users?search=%27%3B+DROP+TABLE+users%3B+--', headers=admin_headers)
    assert resp_search_sqli.status_code == 200
    assert resp_search_sqli.get_json()['success'] is True

    # Verify users table was not dropped
    assert User.query.count() == initial_user_count

    # 3. UNION SELECT in Principal student query
    principal_headers = get_auth_token(test_client, 'principal@pesitm.edu', 'password123', 'principal')
    resp_usn_sqli = test_client.get("/api/principal/students?usn=4PM21CS001'+UNION+SELECT+1,2,3--", headers=principal_headers)
    assert resp_usn_sqli.status_code == 200
    assert resp_usn_sqli.get_json()['success'] is True


# ==============================================================================
# 7. NOTIFICATION OWNERSHIP TAMPER PROTECTION
# ==============================================================================

def test_cross_user_notification_ownership_protection(test_client):
    """
    Ensure Student 2 cannot mark read or delete notifications belonging to Student 1.
    """
    student1_headers = get_auth_token(test_client, '4PM21CS001', 'password123', 'student')
    student2_headers = get_auth_token(test_client, '4PM21CS002', 'password123', 'student')

    # 1. Create a notification for Student 1
    with test_client.application.app_context():
        s1 = Student.query.filter_by(usn='4PM21CS001').first()
        test_notif = Notification(
            sender_id=3,
            recipient_user_id=s1.user_id,
            student_id=s1.student_id,
            title='Confidential Security Notice',
            message='Classified academic communication for Student 1',
            status='sent'
        )
        db.session.add(test_notif)
        db.session.commit()
        notif_id = test_notif.id
        db.session.remove()

    # 2. Student 2 tries to mark Student 1's notification as read -> 403 Forbidden
    resp_read = test_client.patch(f'/api/notifications/{notif_id}/read', headers=student2_headers)
    assert resp_read.status_code == 403
    assert 'You do not own this notification' in resp_read.get_json()['message']

    # 3. Student 2 tries to delete Student 1's notification -> 403 Forbidden
    resp_del = test_client.delete(f'/api/notifications/{notif_id}', headers=student2_headers)
    assert resp_del.status_code == 403
    assert 'You do not own this notification' in resp_del.get_json()['message']

    # 4. Student 1 successfully marks as read -> 200 OK
    resp_own_read = test_client.patch(f'/api/notifications/{notif_id}/read', headers=student1_headers)
    assert resp_own_read.status_code == 200
    assert resp_own_read.get_json()['data']['status'] == 'read'


# ==============================================================================
# 8. MARKS AUDIT TRAIL INTEGRITY & TAMPER PROOF ENFORCEMENT
# ==============================================================================

def test_marks_audit_trail_tamper_proof_enforcement(test_client):
    """
    Ensure academic marks cannot be modified without a mandatory institutional justification,
    and verify that all valid modifications create an immutable audit record in MarkHistory.
    """
    teacher_headers = get_auth_token(test_client, 'anita.rao@pesitm.edu', 'password123', 'teacher')

    # 1. Submitting without reason is rejected with 400 Bad Request
    with test_client.application.app_context():
        s_target = Student.query.filter_by(class_id=2).first()
        target_student_id = s_target.student_id if s_target else 22
        m = Mark.query.filter_by(student_id=target_student_id, subject_id=1).first()
        target_cie1 = 39.5 if m and m.cie1 != 39.5 else 35.0

    resp_no_reason = test_client.post('/api/teacher/marks/bulk', headers=teacher_headers, json={
        'class_id': 2,
        'subject_id': 1,
        'marks': [{'student_id': target_student_id, 'cie1': 38.0}]
    })
    assert resp_no_reason.status_code == 400
    msg = resp_no_reason.get_json()['message'].lower()
    assert 'justification reason' in msg and 'mandatory' in msg

    # 2. Submitting with valid institutional reason succeeds
    audit_reason = f"Phase 13 Security Audit Verification - {uuid.uuid4().hex[:8]}"

    resp_valid = test_client.post('/api/teacher/marks/bulk', headers=teacher_headers, json={
        'class_id': 2,
        'subject_id': 1,
        'reason': audit_reason,
        'marks': [{'student_id': target_student_id, 'cie1': target_cie1}]
    })
    assert resp_valid.status_code == 200
    assert resp_valid.get_json()['success'] is True

    # 3. Verify MarkHistory contains the audit log entry
    with test_client.application.app_context():
        db.session.remove()
        history_entry = MarkHistory.query.filter_by(reason=audit_reason).first()
        assert history_entry is not None
        assert history_entry.field_name == 'cie1'
        assert history_entry.changed_by is not None
        assert float(history_entry.new_value) == target_cie1
        assert history_entry.changed_by is not None
        assert history_entry.field_name == 'cie1'
