"""
Student Controller Blueprint for CAMPS-ML.
Provides Personalized Academic Dashboard, CGPA Trajectory, XAI Explainability Insights,
Personal Improvement Recommendations, and PDF Transcript Downloads.
"""

from flask import Blueprint, render_template, send_file, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import (
    Role,
    StudentProfile,
    Enrollment,
    SemesterResult,
    PredictionLog,
    MentorRemark,
)
from app.blueprints.auth.routes import role_required
from app.services.report_service import generate_student_pdf_report
from app.services.prediction_service import extract_features_from_student, predict_for_student_dict

student_bp = Blueprint("student", __name__, url_prefix="/student")


@student_bp.route("/dashboard")
@login_required
@role_required(Role.STUDENT)
def dashboard():
    """Student Self-Monitoring & AI Advising Dashboard."""
    student = current_user.student_profile
    if not student:
        flash("Student profile not found. Please contact administration.", "danger")
        return redirect(url_for("auth.login"))

    enrollments = Enrollment.query.filter_by(student_id=student.id).all()
    semester_results = SemesterResult.query.filter_by(student_id=student.id).order_by(SemesterResult.semester).all()
    latest_pred = PredictionLog.query.filter_by(student_id=student.id).order_by(PredictionLog.created_at.desc()).first()
    remarks = MentorRemark.query.filter_by(student_id=student.id).order_by(MentorRemark.created_at.desc()).all()

    # Calculate average attendance %
    att_vals = [e.attendance.percentage for e in enrollments if e.attendance]
    avg_att = round(sum(att_vals) / len(att_vals), 1) if att_vals else 100.0

    # Get personalized recommendations from inference engine
    features = extract_features_from_student(student)
    pred_data = predict_for_student_dict(features)
    recommendations = pred_data.get("recommendations", [])

    return render_template(
        "student/dashboard.html",
        student=student,
        enrollments=enrollments,
        semester_results=semester_results,
        latest_pred=latest_pred,
        remarks=remarks,
        avg_att=avg_att,
        recommendations=recommendations,
        pred_data=pred_data
    )


@student_bp.route("/download-transcript")
@login_required
@role_required(Role.STUDENT)
def download_transcript():
    """Download personal academic transcript and audit PDF."""
    student = current_user.student_profile
    pdf_path = generate_student_pdf_report(student.id)
    return send_file(pdf_path, as_attachment=True)
