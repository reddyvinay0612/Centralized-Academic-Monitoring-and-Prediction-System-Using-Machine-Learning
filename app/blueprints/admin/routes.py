"""
Admin Controller Blueprint for CAMPS-ML.
Handles System Overview, User Management, Department Setup, and Bulk Data Ingestion.
"""

import os
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required
from app import db
from app.models import Role, User, StudentProfile, FacultyProfile, Department, Course, PredictionLog
from app.blueprints.auth.routes import role_required
from app.services.data_ingestion import process_bulk_student_upload

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/dashboard")
@login_required
@role_required(Role.ADMIN)
def dashboard():
    """System Administrator High-Level Analytics Dashboard."""
    total_users = User.query.count()
    total_students = StudentProfile.query.count()
    total_faculty = FacultyProfile.query.count()
    departments = Department.query.all()
    
    # Calculate cohort risk distribution
    high_risk_count = StudentProfile.query.filter_by(current_risk_level="High").count()
    med_risk_count = StudentProfile.query.filter_by(current_risk_level="Medium").count()
    low_risk_count = StudentProfile.query.filter_by(current_risk_level="Low").count()

    recent_predictions = PredictionLog.query.order_by(PredictionLog.created_at.desc()).limit(8).all()

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_students=total_students,
        total_faculty=total_faculty,
        departments=departments,
        high_risk_count=high_risk_count,
        med_risk_count=med_risk_count,
        low_risk_count=low_risk_count,
        recent_predictions=recent_predictions
    )


@admin_bp.route("/users")
@login_required
@role_required(Role.ADMIN)
def manage_users():
    """List all user accounts with pagination and role filters."""
    role_filter = request.args.get("role")
    query = User.query
    if role_filter:
        query = query.filter_by(role=role_filter)
    users = query.order_by(User.created_at.desc()).all()
    departments = Department.query.all()
    return render_template("admin/manage_users.html", users=users, departments=departments)


@admin_bp.route("/upload", methods=["GET", "POST"])
@login_required
@role_required(Role.ADMIN)
def bulk_upload():
    """Upload CSV or Excel dataset to ingest student records and trigger ML inference."""
    departments = Department.query.all()
    
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part provided in upload form.", "danger")
            return redirect(request.url)

        file = request.files["file"]
        dept_id = request.form.get("department_id", type=int)
        sem = request.form.get("semester", 5, type=int)

        if file.filename == "":
            flash("Please choose a valid CSV or Excel file to upload.", "warning")
            return redirect(request.url)

        filename = secure_filename(file.filename)
        save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        file.save(save_path)

        res = process_bulk_student_upload(save_path, department_id=dept_id, current_semester=sem)
        
        if res["errors"]:
            flash(f"Processed {res['new_students']} new, {res['updated_students']} updated with {len(res['errors'])} warnings.", "warning")
        else:
            flash(f"Successfully processed {res['new_students']} new students and updated {res['updated_students']} records with ML predictions!", "success")
        
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/bulk_upload.html", departments=departments)
