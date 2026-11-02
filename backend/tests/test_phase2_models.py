import pytest
from backend.app import create_app
from backend.extensions import db
from backend.app.models import (
    User, Department, Teacher, Parent, Student,
    ParentStudent, TeacherAssignment, Class, Subject,
    Attendance, Mark, MarkHistory
)

@pytest.fixture
def app_ctx():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

def test_user_password_hashing_and_lockout(app_ctx):
    user = User(
        username='test_user',
        email='test_user@pesitm.edu',
        role='student',
        active=True
    )
    user.set_password('Password@123')
    db.session.add(user)
    db.session.commit()

    # Password check
    assert user.check_password('Password@123') is True
    assert user.check_password('WrongPassword') is False
    assert user.is_locked() is False

    # Simulate 5 failed login attempts
    for _ in range(5):
        user.record_failed_login(max_attempts=5, lockout_minutes=15)
    db.session.commit()

    assert user.failed_attempts == 5
    assert user.is_locked() is True

    # Reset failed attempts
    user.reset_failed_attempts()
    db.session.commit()
    assert user.failed_attempts == 0
    assert user.is_locked() is False

def test_parent_child_many_to_many_relationship(app_ctx):
    # Create parent user and profile
    p_user = User(username='par_user', email='parent@gmail.com', role='parent')
    p_user.set_password('password123')
    db.session.add(p_user)
    db.session.flush()

    parent = Parent(user_id=p_user.user_id, name='Parent One', phone='+91 98800 11111')
    db.session.add(parent)
    db.session.flush()

    # Create Department and Class
    dept = Department(dept_code='CSE', name='Computer Science')
    db.session.add(dept)
    db.session.flush()

    cls = Class(class_name='5th Sem CSE', section='A', semester=5, academic_year='2024-25', dept_id=dept.dept_id)
    db.session.add(cls)
    db.session.flush()

    # Create 2 student children for this parent
    s1_u = User(username='stu1', email='stu1@pesitm.edu', role='student')
    s1_u.set_password('password123')
    s2_u = User(username='stu2', email='stu2@pesitm.edu', role='student')
    s2_u.set_password('password123')
    db.session.add_all([s1_u, s2_u])
    db.session.flush()

    s1 = Student(user_id=s1_u.user_id, name='Child One', usn='4PM21CS001', class_id=cls.class_id)
    s2 = Student(user_id=s2_u.user_id, name='Child Two', usn='4PM21CS002', class_id=cls.class_id)
    db.session.add_all([s1, s2])
    db.session.flush()

    # Link parent to both children
    link1 = ParentStudent(parent_id=parent.parent_id, student_id=s1.student_id, relation='Father')
    link2 = ParentStudent(parent_id=parent.parent_id, student_id=s2.student_id, relation='Father')
    db.session.add_all([link1, link2])
    db.session.commit()

    # Assert parent can retrieve only their 2 children
    children = parent.children.all()
    assert len(children) == 2
    assert {c.usn for c in children} == {'4PM21CS001', '4PM21CS002'}

def test_teacher_assignment_and_mark_audit_history(app_ctx):
    # Setup teacher and user
    t_user = User(username='teacher_user', email='teacher@pesitm.edu', role='teacher')
    t_user.set_password('password123')
    db.session.add(t_user)
    db.session.flush()

    dept = Department(dept_code='CSE', name='Computer Science')
    db.session.add(dept)
    db.session.flush()

    teacher = Teacher(user_id=t_user.user_id, name='Prof. Rao', employee_id='EMP-CSE-01', dept_id=dept.dept_id)
    db.session.add(teacher)
    db.session.flush()

    cls = Class(class_name='5th Sem CSE', section='A', semester=5, academic_year='2024-25', dept_id=dept.dept_id)
    subj = Subject(subject_code='21CS51', subject_name='Machine Learning', semester=5, credits=4, dept_id=dept.dept_id)
    db.session.add_all([cls, subj])
    db.session.flush()

    # Assign teacher to class & subject
    assignment = TeacherAssignment(teacher_id=teacher.teacher_id, class_id=cls.class_id, subject_id=subj.subject_id)
    db.session.add(assignment)
    db.session.flush()

    # Student and initial mark
    s_user = User(username='stu_aud', email='stu_aud@pesitm.edu', role='student')
    s_user.set_password('password123')
    db.session.add(s_user)
    db.session.flush()

    student = Student(user_id=s_user.user_id, name='Rohan', usn='4PM21CS050', class_id=cls.class_id)
    db.session.add(student)
    db.session.flush()

    mark = Mark(student_id=student.student_id, subject_id=subj.subject_id, cie1=15.0, cie2=14.0, assignment_marks=4.0, quiz_marks=4.0)
    mark.calculate_total()
    db.session.add(mark)
    db.session.flush()

    initial_cie = float(mark.total_cie)

    # Teacher updates mark and logs reason in MarkHistory
    new_cie1 = 18.0
    mark.cie1 = new_cie1
    updated_cie = float(mark.calculate_total())

    history = MarkHistory(
        marks_id=mark.marks_id,
        field_name='cie1',
        old_value=15.0,
        new_value=new_cie1,
        changed_by=t_user.user_id,
        reason='Re-evaluation after grievance verification'
    )
    db.session.add(history)
    db.session.commit()

    # Assertions
    assert updated_cie > initial_cie
    retrieved_history = MarkHistory.query.filter_by(marks_id=mark.marks_id).first()
    assert retrieved_history is not None
    assert float(retrieved_history.old_value) == 15.0
    assert float(retrieved_history.new_value) == 18.0
    assert retrieved_history.reason == 'Re-evaluation after grievance verification'
    assert retrieved_history.changed_by == t_user.user_id
