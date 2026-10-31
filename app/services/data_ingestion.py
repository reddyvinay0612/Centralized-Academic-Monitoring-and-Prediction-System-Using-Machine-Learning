"""
Data Ingestion & Bulk ETL Service for CAMPS-ML.
Processes uploaded CSV and Excel files for student records, attendance, and internal marks,
and automatically triggers ML inference pipelines for newly ingested records.
"""

import pandas as pd
from app import db
from app.models import (
    Role,
    User,
    StudentProfile,
    Department,
    Course,
    Enrollment,
    AttendanceRecord,
    InternalAssessment,
)
from app.services.prediction_service import score_and_update_student


def process_bulk_student_upload(file_path: str, department_id: int, current_semester: int = 5):
    """
    Parse uploaded CSV or Excel file containing student records and continuous evaluation data.
    Expected columns: USN, First_Name, Last_Name, Email, Attendance_Percentage, IA1, IA2, IA3, Backlogs, Fee_Status
    """
    if str(file_path).endswith(".csv"):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)

    # Standardize column headers
    df.columns = [c.strip().replace(" ", "_") for c in df.columns]

    processed_count = 0
    updated_count = 0
    errors = []

    courses = Course.query.filter_by(department_id=department_id, semester=current_semester).all()

    for idx, row in df.iterrows():
        try:
            usn = str(row.get("USN", "")).strip().upper()
            if not usn or usn == "NAN":
                continue

            first_name = str(row.get("First_Name", "Student")).strip()
            last_name = str(row.get("Last_Name", "")).strip()
            email = str(row.get("Email", f"student.{usn.lower()}@camps.edu")).strip().lower()
            att_pct = float(row.get("Attendance_Percentage", row.get("Attendance", 85.0)))
            ia1 = float(row.get("IA1", 20.0))
            ia2 = float(row.get("IA2", 20.0))
            ia3 = float(row.get("IA3", 20.0)) if "IA3" in row and pd.notna(row["IA3"]) else None
            cgpa = float(row.get("Cumulative_CGPA", row.get("CGPA", 7.0)))
            backlogs = int(row.get("Active_Backlogs", row.get("Backlogs", 0)))
            fee_status = str(row.get("Fee_Status", "Cleared")).capitalize()

            # Find or create User
            user = User.query.filter_by(email=email).first()
            if not user:
                user = User(email=email, role=Role.STUDENT)
                user.set_password("Student@123")
                db.session.add(user)
                db.session.flush()

            # Find or create StudentProfile
            student = StudentProfile.query.filter_by(usn=usn).first()
            if not student:
                student = StudentProfile(
                    user_id=user.id,
                    usn=usn,
                    first_name=first_name,
                    last_name=last_name,
                    department_id=department_id,
                    batch_year=2021,
                    current_semester=current_semester,
                    section=str(row.get("Section", "A")),
                    cumulative_cgpa=cgpa,
                    total_active_backlogs=backlogs,
                    fee_status=fee_status
                )
                db.session.add(student)
                db.session.flush()
                processed_count += 1
            else:
                student.first_name = first_name
                student.last_name = last_name
                student.cumulative_cgpa = cgpa
                student.total_active_backlogs = backlogs
                student.fee_status = fee_status
                updated_count += 1

            # Update enrollments and marks for active courses
            for course in courses:
                enrollment = Enrollment.query.filter_by(
                    student_id=student.id, course_id=course.id, academic_year="2024-25"
                ).first()

                if not enrollment:
                    enrollment = Enrollment(
                        student_id=student.id,
                        course_id=course.id,
                        academic_year="2024-25",
                        semester=current_semester
                    )
                    db.session.add(enrollment)
                    db.session.flush()

                # Attendance
                total_classes = 40
                attended = int(round((att_pct / 100.0) * total_classes))
                if not enrollment.attendance:
                    att_rec = AttendanceRecord(
                        enrollment_id=enrollment.id,
                        total_classes=total_classes,
                        attended_classes=attended,
                        percentage=att_pct
                    )
                    db.session.add(att_rec)
                else:
                    enrollment.attendance.total_classes = total_classes
                    enrollment.attendance.attended_classes = attended
                    enrollment.attendance.percentage = att_pct

                # CIE
                if not enrollment.internal_assessment:
                    cie = InternalAssessment(
                        enrollment_id=enrollment.id,
                        ia1_marks=ia1,
                        ia2_marks=ia2,
                        ia3_marks=ia3,
                        assignment_marks=8.0,
                        lab_marks=8.0 if course.is_laboratory else 0.0
                    )
                    cie.compute_total_cie()
                    db.session.add(cie)
                else:
                    enrollment.internal_assessment.ia1_marks = ia1
                    enrollment.internal_assessment.ia2_marks = ia2
                    enrollment.internal_assessment.ia3_marks = ia3
                    enrollment.internal_assessment.compute_total_cie()

            db.session.commit()

            # Execute ML scoring immediately
            score_and_update_student(student.id, milestone="Bulk Ingestion", commit=True)

        except Exception as e:
            db.session.rollback()
            errors.append(f"Row {idx+1} ({row.get('USN', 'Unknown')}): {str(e)}")

    return {
        "new_students": processed_count,
        "updated_students": updated_count,
        "errors": errors
    }
