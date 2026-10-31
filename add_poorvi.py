"""
Add student account for Poorvi V S in CAMPS-ML.
"""

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
    SemesterResult,
)
from app.services.prediction_service import score_and_update_student

app = create_app("development")

with app.app_context():
    dept = Department.query.filter_by(code="CSD").first()
    faculty = FacultyProfile.query.first()
    courses = Course.query.filter_by(department_id=dept.id, semester=5).all()

    # Check if user already exists
    user = User.query.filter(User.email.in_(["poorvi@camps.edu", "poorvivs@camps.edu"])).first()
    if not user:
        user = User(email="poorvi@camps.edu", role=Role.STUDENT)
        user.set_password("Student@123")
        db.session.add(user)
        db.session.flush()
    else:
        user.set_password("Student@123")

    profile = StudentProfile.query.filter(
        (StudentProfile.first_name == "Poorvi") | (StudentProfile.usn == "1RV21CD000")
    ).first()

    if not profile:
        profile = StudentProfile(
            user_id=user.id,
            usn="1RV21CD000",
            first_name="Poorvi",
            last_name="V S",
            department_id=dept.id,
            batch_year=2021,
            current_semester=5,
            section="A",
            gender="Female",
            category="General",
            parent_phone="+91-9880011223",
            parent_email="parent.poorvi@gmail.com",
            fee_due_amount=0.0,
            fee_status="Cleared",
            scholarship_recipient=True,
            mentor_id=faculty.id if faculty else None,
            cumulative_cgpa=8.95,
            total_active_backlogs=0,
            current_risk_level="Low"
        )
        db.session.add(profile)
        db.session.flush()

        # Semester 1-4 history
        for sem in range(1, 5):
            res = SemesterResult(
                student_id=profile.id,
                semester=sem,
                sgpa=8.80 + (sem * 0.05),
                cgpa_after_sem=8.90,
                credits_registered=20,
                credits_earned=20,
                backlogs_count=0,
                result_status="Pass"
            )
            db.session.add(res)

        # Sem 5 course enrollments
        for course in courses:
            enr = Enrollment(student_id=profile.id, course_id=course.id, academic_year="2024-25", semester=5)
            db.session.add(enr)
            db.session.flush()

            att = AttendanceRecord(enrollment_id=enr.id, total_classes=40, attended_classes=37, percentage=92.5)
            cie = InternalAssessment(
                enrollment_id=enr.id,
                ia1_marks=27.5,
                ia2_marks=28.0,
                assignment_marks=9.5,
                lab_marks=9.5 if course.is_laboratory else 0.0
            )
            cie.compute_total_cie()
            db.session.add_all([att, cie])

        db.session.commit()
        print(f"[+] Successfully registered Poorvi V S (USN: {profile.usn}, Email: {user.email})")

        # Run ML scoring
        score_and_update_student(profile.id, milestone="Initial Profile", commit=True)
    else:
        print(f"[*] Poorvi V S already exists with USN {profile.usn}")
