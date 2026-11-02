import pytest
from backend.app import create_app
from backend.extensions import db, bcrypt
from backend.app.models import (
    User, Student, Parent, Teacher, Department, Class,
    ParentStudent, TeacherAssignment, Subject
)
from backend.app.services.auth_middleware import check_student_scope

@pytest.fixture
def test_setup():
    app = create_app('testing')
    with app.app_context():
        db.create_all()

        pwd = bcrypt.generate_password_hash('password123').decode('utf-8')

        # 1. Department
        dept = Department(dept_id=1, dept_code='CSE', name='Computer Science')
        db.session.add(dept)
        db.session.flush()

        # 2. Executive Users
        principal_u = User(user_id=1, username='principal', email='principal@pesitm.edu',
                           password_hash=pwd, role='principal')
        admin_u = User(user_id=2, username='admin', email='admin@pesitm.edu',
                       password_hash=pwd, role='admin')
        db.session.add_all([principal_u, admin_u])

        # 3. Teacher
        teacher_u = User(user_id=3, username='anita.rao', email='anita.rao@pesitm.edu',
                         password_hash=pwd, role='teacher')
        db.session.add(teacher_u)
        db.session.flush()
        teacher = Teacher(teacher_id=1, user_id=teacher_u.user_id, name='Prof. Anita Rao',
                          employee_id='EMP-CSE-01', dept_id=1)
        db.session.add(teacher)

        # 4. Class & Subject
        cls1 = Class(class_id=1, class_name='5th Sem CSE', section='A', semester=5,
                     academic_year='2024-25', dept_id=1, mentor_teacher_id=1)
        cls2 = Class(class_id=2, class_name='5th Sem CSE', section='B', semester=5,
                     academic_year='2024-25', dept_id=1)
        subj = Subject(subject_id=1, subject_code='21CS51', subject_name='Machine Learning',
                       semester=5, credits=4, dept_id=1)
        db.session.add_all([cls1, cls2, subj])
        db.session.flush()

        # Teacher Assignment: Class 1 only
        t_assign = TeacherAssignment(teacher_id=1, class_id=1, subject_id=1)
        db.session.add(t_assign)

        # 5. Parents
        p1_u = User(user_id=4, username='parent_001', email='parent_001@gmail.com',
                    phone='+91 98800 20001', password_hash=pwd, role='parent')
        p2_u = User(user_id=5, username='parent_002', email='parent_002@gmail.com',
                    phone='+91 98800 20002', password_hash=pwd, role='parent')
        db.session.add_all([p1_u, p2_u])
        db.session.flush()

        parent1 = Parent(parent_id=1, user_id=p1_u.user_id, name='Parent One', phone='+91 98800 20001')
        parent2 = Parent(parent_id=2, user_id=p2_u.user_id, name='Parent Two', phone='+91 98800 20002')
        db.session.add_all([parent1, parent2])
        db.session.flush()

        # 6. Students
        s1_u = User(user_id=6, username='4pm21cs001', email='4pm21cs001@pesitm.edu',
                    password_hash=pwd, role='student')
        s2_u = User(user_id=7, username='4pm21cs002', email='4pm21cs002@pesitm.edu',
                    password_hash=pwd, role='student')
        db.session.add_all([s1_u, s2_u])
        db.session.flush()

        student1 = Student(student_id=1, user_id=s1_u.user_id, name='Poorvi V S',
                           usn='4PM21CS001', class_id=1)
        student2 = Student(student_id=2, user_id=s2_u.user_id, name='Rohan Verma',
                           usn='4PM21CS002', class_id=2)
        db.session.add_all([student1, student2])
        db.session.flush()

        # Parent 1 links ONLY to Student 1
        # Parent 2 links ONLY to Student 2
        ps1 = ParentStudent(parent_id=1, student_id=1, relation='Mother')
        ps2 = ParentStudent(parent_id=2, student_id=2, relation='Father')
        db.session.add_all([ps1, ps2])

        db.session.commit()

        with app.test_client() as client:
            yield client, {
                'principal': principal_u,
                'admin': admin_u,
                'teacher': teacher_u,
                'parent1': p1_u,
                'parent2': p2_u,
                'student1': s1_u,
                'student2': s2_u
            }

        db.session.remove()
        db.drop_all()

def test_multi_role_login_success(test_setup):
    client, _ = test_setup

    # 1. Student login using USN
    res = client.post('/api/auth/login', json={
        'identifier': '4PM21CS001',
        'password': 'password123',
        'expectedRole': 'student'
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert 'access_token' in data
    assert data['redirectTo'] == '/student/dashboard'
    assert data['claims']['student_id'] == 1

    # 2. Parent login using Phone
    res = client.post('/api/auth/login', json={
        'identifier': '+91 98800 20001',
        'password': 'password123',
        'expectedRole': 'parent'
    })
    assert res.status_code == 200
    assert res.get_json()['redirectTo'] == '/parent/dashboard'

    # 3. Teacher login using Employee ID
    res = client.post('/api/auth/login', json={
        'identifier': 'EMP-CSE-01',
        'password': 'password123',
        'expectedRole': 'teacher'
    })
    assert res.status_code == 200
    assert res.get_json()['redirectTo'] == '/teacher/dashboard'

    # 4. Admin login
    res = client.post('/api/auth/login', json={
        'identifier': 'admin@pesitm.edu',
        'password': 'password123',
        'expectedRole': 'admin'
    })
    assert res.status_code == 200
    assert res.get_json()['redirectTo'] == '/admin/dashboard'

    # 5. Principal login
    res = client.post('/api/auth/login', json={
        'identifier': 'principal@pesitm.edu',
        'password': 'password123',
        'expectedRole': 'principal'
    })
    assert res.status_code == 200
    assert res.get_json()['redirectTo'] == '/principal/dashboard'

def test_wrong_portal_role_rejection(test_setup):
    """
    Ensure users cannot log in through the wrong portal.
    Example: Parent signing in on teacher portal must be rejected.
    """
    client, _ = test_setup

    res = client.post('/api/auth/login', json={
        'identifier': '+91 98800 20001', # Parent Phone
        'password': 'password123',
        'expectedRole': 'teacher' # Attempting to log into Teacher Portal
    })
    assert res.status_code == 401
    data = res.get_json()
    assert data['error'] == 'ROLE_MISMATCH'
    assert 'These credentials are not for a teacher account' in data['message']

def test_login_brute_force_lockout(test_setup):
    client, _ = test_setup

    # 5 failed attempts with wrong password
    for _ in range(5):
        res = client.post('/api/auth/login', json={
            'identifier': 'admin@pesitm.edu',
            'password': 'WrongPassword123'
        })
        assert res.status_code in (401, 429)

    # 6th attempt should be blocked by account lockout
    blocked_res = client.post('/api/auth/login', json={
        'identifier': 'admin@pesitm.edu',
        'password': 'password123' # Even with right password, account is locked!
    })
    assert blocked_res.status_code == 429
    assert blocked_res.get_json()['error'] == 'ACCOUNT_LOCKED'

def test_protected_me_endpoint_and_cookie_refresh(test_setup):
    client, _ = test_setup

    # Login as student
    login_res = client.post('/api/auth/login', json={
        'identifier': '4PM21CS001',
        'password': 'password123'
    })
    token = login_res.get_json()['access_token']

    # GET /api/auth/me without token -> 401
    unauth = client.get('/api/auth/me')
    assert unauth.status_code == 401

    # GET /api/auth/me with Bearer token -> 200
    auth = client.get('/api/auth/me', headers={'Authorization': f'Bearer {token}'})
    assert auth.status_code == 200
    me_data = auth.get_json()
    assert me_data['user']['username'] == '4pm21cs001'
    assert me_data['user']['student']['usn'] == '4PM21CS001'

    # POST /api/auth/refresh using cookie
    refresh_res = client.post('/api/auth/refresh')
    assert refresh_res.status_code == 200
    assert 'access_token' in refresh_res.get_json()

    # Logout
    logout_res = client.post('/api/auth/logout', headers={'Authorization': f'Bearer {token}'})
    assert logout_res.status_code == 200

def test_scoped_student_access_authorization_matrix(test_setup):
    """
    Validates check_student_scope logic:
    - Student: only own record
    - Parent: only linked child
    - Teacher: only students in assigned classes
    - Principal: all students
    """
    _, users = test_setup

    # Student 1 accessing Student 1 -> Allowed
    allowed, _ = check_student_scope(users['student1'], student_id=1)
    assert allowed is True

    # Student 1 accessing Student 2 -> Denied (403)
    allowed, err = check_student_scope(users['student1'], student_id=2)
    assert allowed is False
    assert "only view your own student academic records" in err

    # Parent 1 accessing Student 1 (their child) -> Allowed
    allowed, _ = check_student_scope(users['parent1'], student_id=1)
    assert allowed is True

    # Parent 1 accessing Student 2 (another family's child) -> Denied (403)
    allowed, err = check_student_scope(users['parent1'], student_id=2)
    assert allowed is False
    assert "only authorized to view records belonging to your registered child" in err

    # Teacher assigned to Class 1 (Student 1 is in Class 1) -> Allowed
    allowed, _ = check_student_scope(users['teacher'], student_id=1)
    assert allowed is True

    # Teacher accessing Student 2 (Student 2 is in Class 2, not assigned to this teacher) -> Denied (403)
    allowed, err = check_student_scope(users['teacher'], student_id=2)
    assert allowed is False
    assert "only view students enrolled in classes assigned to you" in err

    # Principal accessing Student 1 & Student 2 -> Both Allowed
    allowed1, _ = check_student_scope(users['principal'], student_id=1)
    allowed2, _ = check_student_scope(users['principal'], student_id=2)
    assert allowed1 is True and allowed2 is True

def test_password_forgot_and_reset_flow(test_setup):
    client, _ = test_setup

    # Request reset
    req_res = client.post('/api/auth/forgot-password', json={
        'identifier': 'admin@pesitm.edu'
    })
    assert req_res.status_code == 200
    token = req_res.get_json()['dev_reset_token']

    # Reset with new password
    reset_res = client.post('/api/auth/reset-password', json={
        'token': token,
        'newPassword': 'NewSecurePassword@2026'
    })
    assert reset_res.status_code == 200

    # Token cannot be re-used
    reuse_res = client.post('/api/auth/reset-password', json={
        'token': token,
        'newPassword': 'AnotherPassword@2026'
    })
    assert reuse_res.status_code == 400

    # Old password fails
    fail_login = client.post('/api/auth/login', json={
        'identifier': 'admin@pesitm.edu',
        'password': 'password123'
    })
    assert fail_login.status_code == 401

    # New password succeeds
    success_login = client.post('/api/auth/login', json={
        'identifier': 'admin@pesitm.edu',
        'password': 'NewSecurePassword@2026'
    })
    assert success_login.status_code == 200
