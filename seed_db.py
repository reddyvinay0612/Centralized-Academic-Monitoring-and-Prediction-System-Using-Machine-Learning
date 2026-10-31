"""
Database Seeder for CAMPS-ML.
Initializes SQLite database with production-representative academic records matching
Indian engineering college schemas (USN, CIE tests, attendance %, SGPA/CGPA, fee status).
"""

import sys
from datetime import datetime, date, timedelta
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
    PredictionLog,
    SHAPFactor,
    MentorRemark,
    NotificationAlert,
)

app = create_app("development")


def seed_database():
    """Wipe and recreate database schema with realistic multi-role data."""
    print("=" * 70)
    print("CAMPS-ML: Initializing & Seeding Relational Database")
    print("=" * 70)

    with app.app_context():
        print("[1/7] Dropping old tables and creating clean schema...")
        db.drop_all()
        db.create_all()

        print("[2/7] Seeding Departments...")
        dept_csd = Department(code="CSD", name="Computer Science and Design", description="AI, Design Thinking & Full-Stack Systems")
        dept_cse = Department(code="CSE", name="Computer Science and Engineering", description="Core Computing, Systems & Algorithms")
        dept_ise = Department(code="ISE", name="Information Science and Engineering", description="Data Science, Networking & Information Systems")
        dept_ece = Department(code="ECE", name="Electronics and Communication Engineering", description="VLSI, Embedded Systems & Signal Processing")
        
        db.session.add_all([dept_csd, dept_cse, dept_ise, dept_ece])
        db.session.flush()

        print("[3/7] Seeding Administrative, HoD & Faculty Accounts...")
        # 1. Admin
        admin_user = User(email="admin@camps.edu", role=Role.ADMIN)
        admin_user.set_password("Admin@123")
        db.session.add(admin_user)

        # 2. HoD (Computer Science & Design)
        hod_user = User(email="hod.csd@camps.edu", role=Role.HOD)
        hod_user.set_password("Hod@123")
        db.session.add(hod_user)
        db.session.flush()

        hod_profile = FacultyProfile(
            user_id=hod_user.id,
            employee_id="EMP-CSD-001",
            first_name="Dr. S. K.",
            last_name="Ramesh",
            department_id=dept_csd.id,
            designation="Professor & Head of Department",
            phone="+91-9845012345",
            cabin_room="CSD-301"
        )
        db.session.add(hod_profile)

        # 3. Faculty / Mentor 1 (Prof. Anita Rao)
        f1_user = User(email="prof.anita@camps.edu", role=Role.FACULTY)
        f1_user.set_password("Faculty@123")
        db.session.add(f1_user)
        db.session.flush()

        f1_profile = FacultyProfile(
            user_id=f1_user.id,
            employee_id="EMP-CSD-012",
            first_name="Prof. Anita",
            last_name="Rao",
            department_id=dept_csd.id,
            designation="Associate Professor",
            phone="+91-9845023456",
            cabin_room="CSD-304"
        )
        db.session.add(f1_profile)

        # 4. Faculty / Mentor 2 (Prof. Karthik Nair)
        f2_user = User(email="prof.karthik@camps.edu", role=Role.FACULTY)
        f2_user.set_password("Faculty@123")
        db.session.add(f2_user)
        db.session.flush()

        f2_profile = FacultyProfile(
            user_id=f2_user.id,
            employee_id="EMP-CSD-018",
            first_name="Prof. Karthik",
            last_name="Nair",
            department_id=dept_csd.id,
            designation="Assistant Professor",
            phone="+91-9845034567",
            cabin_room="CSD-308"
        )
        db.session.add(f2_profile)
        db.session.flush()

        print("[4/7] Seeding Semester 5 Curriculum Courses...")
        c1 = Course(code="21CS51", name="Machine Learning & Applications", department_id=dept_csd.id, semester=5, credits=4, is_laboratory=True)
        c2 = Course(code="21CS52", name="Database Management Systems", department_id=dept_csd.id, semester=5, credits=4, is_laboratory=True)
        c3 = Course(code="21CS53", name="Computer Networks & Cloud Computing", department_id=dept_csd.id, semester=5, credits=3, is_laboratory=False)
        c4 = Course(code="21CD54", name="Interactive UI/UX & Design Thinking", department_id=dept_csd.id, semester=5, credits=3, is_laboratory=True)
        c5 = Course(code="21CD55", name="Research Methodology & Intellectual Property", department_id=dept_csd.id, semester=5, credits=2, is_laboratory=False)

        courses = [c1, c2, c3, c4, c5]
        db.session.add_all(courses)
        db.session.flush()

        print("[5/7] Seeding Student Cohort with High, Medium & Low Risk Profiles...")
        
        # Student Definitions: (USN, First, Last, Gender, Mentor, PrevCGPA, Backlogs, FeeStatus, FeeDue, RiskLevel, BaseAtt, BaseIA)
        student_data = [
            # High Risk Profiles (Attendance < 75%, failing IAs, backlogs, fee dues)
            ("1RV21CD001", "Rohan", "Verma", "Male", f1_profile.id, 5.12, 3, "Defaulter", 45000.0, "High", 58.0, 11.0),
            ("1RV21CD002", "Pooja", "Hegde", "Female", f1_profile.id, 5.45, 2, "Pending", 15000.0, "High", 64.0, 13.0),
            ("1RV21CD003", "Vikram", "Aditya", "Male", f2_profile.id, 4.88, 4, "Defaulter", 60000.0, "High", 52.0, 9.5),
            ("1RV21CD004", "Simran", "Kaur", "Female", f2_profile.id, 5.60, 2, "Cleared", 0.0, "High", 68.0, 12.5),
            
            # Medium Risk Profiles (Borderline attendance 72-78%, average IAs, 1 backlog)
            ("1RV21CD005", "Abhishek", "Kumar", "Male", f1_profile.id, 6.42, 1, "Cleared", 0.0, "Medium", 74.0, 17.0),
            ("1RV21CD006", "Megha", "Shastry", "Female", f1_profile.id, 6.78, 1, "Cleared", 0.0, "Medium", 76.5, 18.0),
            ("1RV21CD007", "Nikhil", "Gowda", "Male", f2_profile.id, 6.20, 1, "Pending", 8000.0, "Medium", 73.0, 16.0),
            ("1RV21CD008", "Deepika", "Patel", "Female", f2_profile.id, 6.95, 0, "Cleared", 0.0, "Medium", 78.0, 19.5),
            ("1RV21CD009", "Arjun", "Reddy", "Male", f1_profile.id, 6.35, 1, "Cleared", 0.0, "Medium", 71.0, 16.5),

            # Low Risk / Good Standing Profiles (High attendance > 85%, high IAs > 23/30, 0 backlogs)
            ("1RV21CD010", "Aditi", "Bhat", "Female", f1_profile.id, 8.85, 0, "Cleared", 0.0, "Low", 94.0, 26.5),
            ("1RV21CD011", "Varun", "Sharma", "Male", f1_profile.id, 8.40, 0, "Cleared", 0.0, "Low", 89.0, 24.5),
            ("1RV21CD012", "Sneha", "Kulkarni", "Female", f2_profile.id, 9.15, 0, "Cleared", 0.0, "Low", 96.0, 28.5),
            ("1RV21CD013", "Kiran", "Prasad", "Male", f2_profile.id, 7.95, 0, "Cleared", 0.0, "Low", 86.0, 23.0),
            ("1RV21CD014", "Divya", "Menon", "Female", f1_profile.id, 8.70, 0, "Cleared", 0.0, "Low", 92.0, 25.0),
            ("1RV21CD015", "Rahul", "Deshmukh", "Male", f2_profile.id, 9.30, 0, "Cleared", 0.0, "Low", 98.0, 29.0),
            ("1RV21CD016", "Ananya", "Sen", "Female", f1_profile.id, 8.15, 0, "Cleared", 0.0, "Low", 88.0, 24.0),
        ]

        seeded_students = []

        for item in student_data:
            usn, fname, lname, gender, mentor_id, cgpa, backlogs, fee_status, fee_due, risk, att_base, ia_base = item
            email = f"student.{usn.lower()}@camps.edu"
            
            # Create User
            s_user = User(email=email, role=Role.STUDENT)
            s_user.set_password("Student@123")
            db.session.add(s_user)
            db.session.flush()

            # Create StudentProfile
            s_profile = StudentProfile(
                user_id=s_user.id,
                usn=usn,
                first_name=fname,
                last_name=lname,
                department_id=dept_csd.id,
                batch_year=2021,
                current_semester=5,
                section="A",
                gender=gender,
                category="General",
                parent_phone="+91-9988776655",
                parent_email=f"parent.{usn.lower()}@gmail.com",
                fee_due_amount=fee_due,
                fee_status=fee_status,
                scholarship_recipient=(cgpa > 8.5),
                mentor_id=mentor_id,
                cumulative_cgpa=cgpa,
                total_active_backlogs=backlogs,
                current_risk_level=risk
            )
            db.session.add(s_profile)
            db.session.flush()
            seeded_students.append((s_profile, s_user, risk, att_base, ia_base, cgpa, backlogs, fee_due))

            # Add Historical Semesters 1 to 4
            for sem in range(1, 5):
                sem_sgpa = max(4.0, min(10.0, round(cgpa + (sem * 0.1 - 0.25), 2)))
                sem_res = SemesterResult(
                    student_id=s_profile.id,
                    semester=sem,
                    sgpa=sem_sgpa,
                    cgpa_after_sem=round((cgpa + sem_sgpa) / 2.0, 2),
                    credits_registered=20,
                    credits_earned=20 if backlogs == 0 or sem <= 2 else 16,
                    backlogs_count=0 if backlogs == 0 or sem <= 2 else 1,
                    result_status="Pass" if backlogs == 0 or sem <= 2 else "Arrears"
                )
                db.session.add(sem_res)

            # Enroll in the 5 courses of Sem 5
            for idx, course in enumerate(courses):
                enrollment = Enrollment(
                    student_id=s_profile.id,
                    course_id=course.id,
                    academic_year="2024-25",
                    semester=5
                )
                db.session.add(enrollment)
                db.session.flush()

                # Attendance (simulate variance per course)
                course_att = max(35.0, min(100.0, att_base + (idx * 2.5 - 5.0)))
                total_cls = 40
                attended = int(round((course_att / 100.0) * total_cls))
                att_record = AttendanceRecord(
                    enrollment_id=enrollment.id,
                    total_classes=total_cls,
                    attended_classes=attended,
                    percentage=round((attended / total_cls) * 100.0, 2)
                )
                db.session.add(att_record)

                # Internal Assessments (IA1, IA2, Assignment, Lab)
                ia1 = max(5.0, min(30.0, round(ia_base + (idx * 1.0 - 2.0), 1)))
                ia2 = max(4.0, min(30.0, round(ia_base + (idx * 0.5 - 1.5), 1)))
                assign = 8.5 if risk == "Low" else (6.5 if risk == "Medium" else 4.0)
                lab_sc = 9.0 if risk == "Low" else (7.0 if risk == "Medium" else 5.0)

                cie = InternalAssessment(
                    enrollment_id=enrollment.id,
                    ia1_marks=ia1,
                    ia2_marks=ia2,
                    ia3_marks=None,  # Not conducted yet at milestone
                    assignment_marks=assign,
                    lab_marks=lab_sc if course.is_laboratory else 0.0
                )
                cie.compute_total_cie()
                db.session.add(cie)

        print("[6/7] Seeding ML Predictions, TreeSHAP Attributions & Alerts...")
        for s_profile, s_user, risk, att_base, ia_base, cgpa, backlogs, fee_due in seeded_students:
            # Model prediction log
            if risk == "High":
                risk_prob = round(0.78 + (backlogs * 0.04), 2)
                pred_sgpa = round(max(4.2, cgpa - 0.6), 2)
            elif risk == "Medium":
                risk_prob = 0.46
                pred_sgpa = round(cgpa - 0.1, 2)
            else:
                risk_prob = 0.12
                pred_sgpa = round(min(9.8, cgpa + 0.3), 2)

            pred_log = PredictionLog(
                student_id=s_profile.id,
                semester=5,
                milestone="Post-IA2",
                predicted_risk_level=risk,
                risk_probability=risk_prob,
                predicted_sgpa=pred_sgpa,
                model_name="XGBoost Classifier + RF Regressor",
                model_version="v1.0"
            )
            db.session.add(pred_log)
            db.session.flush()

            # SHAP Local Factors
            if risk == "High":
                f1 = SHAPFactor(prediction_id=pred_log.id, feature_name="Lecture Attendance %", feature_value=f"{att_base}%", shap_value=+0.42, impact_direction="Increases Risk")
                f2 = SHAPFactor(prediction_id=pred_log.id, feature_name="CIE IA2 Average", feature_value=f"{ia_base}/30", shap_value=+0.31, impact_direction="Increases Risk")
                f3 = SHAPFactor(prediction_id=pred_log.id, feature_name="Active Arrears / Backlogs", feature_value=f"{backlogs} courses", shap_value=+0.28, impact_direction="Increases Risk")
                db.session.add_all([f1, f2, f3])

                # Trigger early warning alert
                alert = NotificationAlert(
                    recipient_user_id=s_profile.mentor.user_id,
                    student_id=s_profile.id,
                    alert_type="HIGH_RISK_DETECTED",
                    severity="critical",
                    title=f"Critical Academic Risk: {s_profile.usn}",
                    message=f"Student {s_profile.first_name} {s_profile.last_name} ({s_profile.usn}) has breached risk threshold (Risk: {risk_prob*100:.0f}%, Attendance: {att_base}%). Immediate counselling required.",
                    is_read=False,
                    email_dispatched=True
                )
                db.session.add(alert)

                # Student in-app alert
                s_alert = NotificationAlert(
                    recipient_user_id=s_user.id,
                    student_id=s_profile.id,
                    alert_type="ATTENDANCE_SHORTAGE",
                    severity="warning",
                    title="Attendance & Performance Advisory",
                    message=f"Your overall attendance is currently {att_base}%, which is below the mandatory 75% VTU threshold. Please meet your mentor Prof. {s_profile.mentor.last_name}.",
                    is_read=False,
                    email_dispatched=True
                )
                db.session.add(s_alert)

            elif risk == "Medium":
                f1 = SHAPFactor(prediction_id=pred_log.id, feature_name="Lecture Attendance %", feature_value=f"{att_base}%", shap_value=+0.18, impact_direction="Increases Risk")
                f2 = SHAPFactor(prediction_id=pred_log.id, feature_name="Continuous Assessment Score", feature_value=f"{ia_base}/30", shap_value=-0.12, impact_direction="Decreases Risk")
                f3 = SHAPFactor(prediction_id=pred_log.id, feature_name="Previous Cumulative CGPA", feature_value=f"{cgpa}", shap_value=-0.15, impact_direction="Decreases Risk")
                db.session.add_all([f1, f2, f3])
            else:
                f1 = SHAPFactor(prediction_id=pred_log.id, feature_name="Lecture Attendance %", feature_value=f"{att_base}%", shap_value=-0.38, impact_direction="Decreases Risk")
                f2 = SHAPFactor(prediction_id=pred_log.id, feature_name="Previous Cumulative CGPA", feature_value=f"{cgpa}", shap_value=-0.44, impact_direction="Decreases Risk")
                f3 = SHAPFactor(prediction_id=pred_log.id, feature_name="CIE IA2 Average", feature_value=f"{ia_base}/30", shap_value=-0.29, impact_direction="Decreases Risk")
                db.session.add_all([f1, f2, f3])

        print("[7/7] Seeding Mentor Intervention Records...")
        # Mentor Remark for Rohan Verma (1RV21CD001)
        rohan = StudentProfile.query.filter_by(usn="1RV21CD001").first()
        remark1 = MentorRemark(
            student_id=rohan.id,
            faculty_id=f1_profile.id,
            concern_category="Attendance & CIE Marks",
            remark_text="Student cited transportation hurdles and health issues during IA2 week. Missing lab sessions in Machine Learning.",
            action_plan="1. Mandatory attendance in 2 Saturday remedial lab sessions. 2. Contacted parents regarding fee payment plan. 3. Target IA3 score: > 18/30.",
            follow_up_date=date.today() + timedelta(days=14),
            status="In-Progress"
        )
        db.session.add(remark1)

        # Mentor Remark for Vikram Aditya (1RV21CD003)
        vikram = StudentProfile.query.filter_by(usn="1RV21CD003").first()
        remark2 = MentorRemark(
            student_id=vikram.id,
            faculty_id=f2_profile.id,
            concern_category="Academic Arrears & Fee Due",
            remark_text="Student has 4 backlogs in foundational math and circuits. Low motivation and poor assignment completion.",
            action_plan="Referred to departmental student counsellor. Assigned peer study partner from 7th semester for Mathematics.",
            follow_up_date=date.today() + timedelta(days=7),
            status="Open"
        )
        db.session.add(remark2)

        db.session.commit()
        print("=" * 70)
        print("[+] DATABASE SUCCESSFULLY SEEDED & COMMITTED!")
        print("=" * 70)


def print_credential_sheet():
    """Print role-based credentials for testing all views."""
    print("\n" + "=" * 70)
    print("CAMPS-ML DEMO LOGIN CREDENTIALS")
    print("=" * 70)
    print(f"{'Role':<12} | {'Email Address':<28} | {'Default Password'}")
    print("-" * 70)
    print(f"{'Admin':<12} | {'admin@camps.edu':<28} | {'Admin@123'}")
    print(f"{'HoD (CSD)':<12} | {'hod.csd@camps.edu':<28} | {'Hod@123'}")
    print(f"{'Faculty 1':<12} | {'prof.anita@camps.edu':<28} | {'Faculty@123'}")
    print(f"{'Faculty 2':<12} | {'prof.karthik@camps.edu':<28} | {'Faculty@123'}")
    print(f"{'Student High':<12} | {'student.1rv21cd001@camps.edu':<28} | {'Student@123'}")
    print(f"{'Student Med':<12} | {'student.1rv21cd005@camps.edu':<28} | {'Student@123'}")
    print(f"{'Student Low':<12} | {'student.1rv21cd010@camps.edu':<28} | {'Student@123'}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    seed_database()
    print_credential_sheet()
