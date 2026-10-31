"""
Head of Department (HoD) Blueprint for CAMPS-ML.
Provides Departmental Cohort Analytics, Risk Breakdown, and Excel Audit Reports.
"""

from flask import Blueprint, render_template, send_file, flash, request
from flask_login import login_required, current_user
from app.models import Role, StudentProfile, FacultyProfile, Department, Course, PredictionLog
from app.blueprints.auth.routes import role_required
from app.services.report_service import generate_class_excel_report

hod_bp = Blueprint("hod", __name__, url_prefix="/hod")


@hod_bp.route("/dashboard")
@login_required
@role_required(Role.HOD, Role.ADMIN)
def dashboard():
    """Departmental Performance & Risk Overview."""
    dept_id = current_user.faculty_profile.department_id if current_user.faculty_profile else 1
    department = Department.query.get(dept_id)

    students = StudentProfile.query.filter_by(department_id=dept_id).all()
    faculty_list = FacultyProfile.query.filter_by(department_id=dept_id).all()

    high_risk_students = [s for s in students if s.current_risk_level == "High"]
    med_risk_students = [s for s in students if s.current_risk_level == "Medium"]
    low_risk_students = [s for s in students if s.current_risk_level == "Low"]

    # Calculate average CGPA
    avg_cgpa = round(sum(s.cumulative_cgpa for s in students) / len(students), 2) if students else 0.0

    return render_template(
        "hod/dashboard.html",
        department=department,
        total_students=len(students),
        total_faculty=len(faculty_list),
        avg_cgpa=avg_cgpa,
        high_risk_count=len(high_risk_students),
        med_risk_count=len(med_risk_students),
        low_risk_count=len(low_risk_students),
        high_risk_students=high_risk_students,
        faculty_list=faculty_list
    )


@hod_bp.route("/export-excel")
@login_required
@role_required(Role.HOD, Role.ADMIN)
def export_excel():
    """Download department-wide Excel performance and risk audit."""
    dept_code = current_user.faculty_profile.department.code if current_user.faculty_profile and current_user.faculty_profile.department else "CSD"
    excel_path = generate_class_excel_report(department_code=dept_code, semester=5)
    return send_file(excel_path, as_attachment=True)
