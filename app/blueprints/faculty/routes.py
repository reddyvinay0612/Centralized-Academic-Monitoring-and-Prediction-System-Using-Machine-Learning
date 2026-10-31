"""
Faculty & Mentor Controller Blueprint for CAMPS-ML.
Handles Mentee Monitoring, CIE/Attendance Entry, XAI Diagnostics, and Intervention Logging.
"""

from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from app import db
from app.models import (
    Role,
    StudentProfile,
    FacultyProfile,
    Course,
    Enrollment,
    AttendanceRecord,
    InternalAssessment,
    PredictionLog,
    MentorRemark,
)
from app.blueprints.auth.routes import role_required
from app.services.prediction_service import score_and_update_student
from app.services.report_service import generate_student_pdf_report

faculty_bp = Blueprint("faculty", __name__, url_prefix="/faculty")


@faculty_bp.route("/dashboard")
@login_required
@role_required(Role.FACULTY, Role.HOD, Role.ADMIN)
def dashboard():
    """Faculty Dashboard with Mentee Tracker & Critical Risk Alerts."""
    faculty = current_user.faculty_profile

    # Retrieve mentees
    if faculty:
        mentees = StudentProfile.query.filter_by(mentor_id=faculty.id).all()
    else:
        mentees = StudentProfile.query.limit(20).all()

    # Filter options
    filter_risk = request.args.get("risk")
    if filter_risk:
        mentees = [s for s in mentees if s.current_risk_level == filter_risk]

    # Metrics
    high_risk_mentees = [s for s in mentees if s.current_risk_level == "High"]
    attendance_shortage = [s for s in mentees if any(e.attendance and e.attendance.is_shortage for e in s.enrollments)]

    return render_template(
        "faculty/dashboard.html",
        faculty=faculty,
        mentees=mentees,
        total_mentees=len(mentees),
        high_risk_count=len(high_risk_mentees),
        shortage_count=len(attendance_shortage)
    )


@faculty_bp.route("/student/<int:student_id>")
@login_required
@role_required(Role.FACULTY, Role.HOD, Role.ADMIN)
def student_detail(student_id: int):
    """Detailed Academic & Predictive Diagnostics View for a specific student."""
    student = StudentProfile.query.get_or_404(student_id)
    enrollments = Enrollment.query.filter_by(student_id=student.id).all()
    latest_pred = PredictionLog.query.filter_by(student_id=student.id).order_by(PredictionLog.created_at.desc()).first()
    remarks = MentorRemark.query.filter_by(student_id=student.id).order_by(MentorRemark.created_at.desc()).all()

    # Calculate average attendance %
    att_vals = [e.attendance.percentage for e in enrollments if e.attendance]
    avg_att = round(sum(att_vals) / len(att_vals), 1) if att_vals else 100.0

    return render_template(
        "faculty/student_detail.html",
        student=student,
        enrollments=enrollments,
        latest_pred=latest_pred,
        remarks=remarks,
        avg_att=avg_att
    )


@faculty_bp.route("/student/<int:student_id>/remark", methods=["POST"])
@login_required
@role_required(Role.FACULTY, Role.HOD, Role.ADMIN)
def add_mentor_remark(student_id: int):
    """Log a counselling remark and actionable intervention for a mentee."""
    student = StudentProfile.query.get_or_404(student_id)
    faculty_id = current_user.faculty_profile.id if current_user.faculty_profile else 1

    category = request.form.get("concern_category", "Academic Performance")
    remark_text = request.form.get("remark_text", "").strip()
    action_plan = request.form.get("action_plan", "").strip()
    days_followup = int(request.form.get("follow_up_days", 14))

    if not remark_text:
        flash("Remark notes cannot be empty.", "warning")
        return redirect(url_for("faculty.student_detail", student_id=student.id))

    remark = MentorRemark(
        student_id=student.id,
        faculty_id=faculty_id,
        concern_category=category,
        remark_text=remark_text,
        action_plan=action_plan,
        follow_up_date=date.today() + timedelta(days=days_followup),
        status="Open"
    )
    db.session.add(remark)
    db.session.commit()

    flash("Counselling remark and intervention plan recorded successfully!", "success")
    return redirect(url_for("faculty.student_detail", student_id=student.id))


@faculty_bp.route("/student/<int:student_id>/rescore")
@login_required
@role_required(Role.FACULTY, Role.HOD, Role.ADMIN)
def rescore_student(student_id: int):
    """Trigger on-demand real-time ML inference for the student."""
    res = score_and_update_student(student_id, milestone="Faculty Re-evaluation", commit=True)
    if res:
        flash(f"ML Re-evaluation Complete: Risk Tier is '{res['predicted_risk_level']}' (High Risk Probability: {res['risk_probability']*100:.1f}%).", "info")
    else:
        flash("Failed to run prediction for this student.", "danger")
    return redirect(url_for("faculty.student_detail", student_id=student_id))


@faculty_bp.route("/student/<int:student_id>/download-pdf")
@login_required
def download_pdf(student_id: int):
    """Download official Student Transcript & Predictive Risk Audit PDF."""
    pdf_path = generate_student_pdf_report(student_id)
    return send_file(pdf_path, as_attachment=True)
