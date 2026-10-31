"""
Pytest Fixtures and Test Configuration for CAMPS-ML.
Provides in-memory SQLite database and test clients with authenticated roles.
"""

import pytest
from app import create_app, db
from app.models import (
    Role,
    User,
    StudentProfile,
    FacultyProfile,
    Department,
    Course,
    Enrollment,
    AttendanceRecord,
    InternalAssessment,
)


@pytest.fixture
def app():
    """Create Flask test application configured for testing."""
    test_app = create_app("testing")
    
    with test_app.app_context():
        db.create_all()

        # Seed minimal test department and users
        dept = Department(code="CSD", name="Computer Science and Design")
        db.session.add(dept)
        db.session.flush()

        # Admin User
        admin = User(email="test.admin@camps.edu", role=Role.ADMIN)
        admin.set_password("AdminPass@123")
        db.session.add(admin)

        # Faculty User
        faculty_user = User(email="test.faculty@camps.edu", role=Role.FACULTY)
        faculty_user.set_password("FacultyPass@123")
        db.session.add(faculty_user)
        db.session.flush()

        faculty = FacultyProfile(
            user_id=faculty_user.id,
            employee_id="TEST-FAC-01",
            first_name="Test",
            last_name="Professor",
            department_id=dept.id
        )
        db.session.add(faculty)
        db.session.flush()

        # Student User
        student_user = User(email="test.student@camps.edu", role=Role.STUDENT)
        student_user.set_password("StudentPass@123")
        db.session.add(student_user)
        db.session.flush()

        student = StudentProfile(
            user_id=student_user.id,
            usn="1RV21CD999",
            first_name="Test",
            last_name="Student",
            department_id=dept.id,
            batch_year=2021,
            current_semester=5,
            section="A",
            cumulative_cgpa=7.5,
            total_active_backlogs=0,
            fee_status="Cleared",
            mentor_id=faculty.id,
            current_risk_level="Low"
        )
        db.session.add(student)
        db.session.flush()

        # Course & Enrollment
        course = Course(code="21CS51", name="Machine Learning", department_id=dept.id, semester=5, credits=4)
        db.session.add(course)
        db.session.flush()

        enrollment = Enrollment(student_id=student.id, course_id=course.id, academic_year="2024-25", semester=5)
        db.session.add(enrollment)
        db.session.flush()

        att = AttendanceRecord(enrollment_id=enrollment.id, total_classes=40, attended_classes=36, percentage=90.0)
        cie = InternalAssessment(enrollment_id=enrollment.id, ia1_marks=25.0, ia2_marks=26.0, assignment_marks=9.0, lab_marks=8.0)
        cie.compute_total_cie()
        db.session.add_all([att, cie])

        db.session.commit()

        yield test_app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client for HTTP requests."""
    return app.test_client()
