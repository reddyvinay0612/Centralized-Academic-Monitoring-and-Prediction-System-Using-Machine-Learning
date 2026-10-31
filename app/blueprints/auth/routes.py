"""
Authentication & Authorization Blueprint for CAMPS-ML.
Handles Login, Logout, RBAC Decorators, and Password updates.
"""

from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Role

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def role_required(*allowed_roles):
    """Decorator to enforce strict Role-Based Access Control on endpoints."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth.login", next=request.url))
            if current_user.role not in allowed_roles:
                flash("Access Denied: You do not possess the required clearance for this resource.", "danger")
                # Redirect to appropriate home dashboard according to role
                if current_user.role == Role.ADMIN:
                    return redirect(url_for("admin.dashboard"))
                elif current_user.role == Role.HOD:
                    return redirect(url_for("hod.dashboard"))
                elif current_user.role == Role.FACULTY:
                    return redirect(url_for("faculty.dashboard"))
                else:
                    return redirect(url_for("student.dashboard"))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Handle user sign-in and redirect to appropriate role portal."""
    if current_user.is_authenticated:
        if current_user.role == Role.ADMIN:
            return redirect(url_for("admin.dashboard"))
        elif current_user.role == Role.HOD:
            return redirect(url_for("hod.dashboard"))
        elif current_user.role == Role.FACULTY:
            return redirect(url_for("faculty.dashboard"))
        else:
            return redirect(url_for("student.dashboard"))

    if request.method == "POST":
        identifier = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        user = None
        if identifier:
            # 1. Search by exact email (case-insensitive)
            user = User.query.filter(User.email.ilike(identifier)).first()

            # 2. Search by USN if student
            if not user:
                from app.models import StudentProfile, FacultyProfile
                student_by_usn = StudentProfile.query.filter(StudentProfile.usn.ilike(identifier)).first()
                if student_by_usn:
                    user = student_by_usn.user

            # 3. Search by Student First Name / Full Name
            if not user:
                from app.models import StudentProfile
                for s in StudentProfile.query.all():
                    full_name = f"{s.first_name} {s.last_name}".strip().lower()
                    id_lower = identifier.lower().replace(".", " ").strip()
                    fn_lower = s.first_name.strip().lower()
                    # Check partial or exact match
                    if id_lower in full_name or full_name in id_lower or id_lower == fn_lower:
                        user = s.user
                        break

            # 4. Search by Faculty First Name / Full Name
            if not user:
                from app.models import FacultyProfile
                for f in FacultyProfile.query.all():
                    full_name = f"{f.first_name} {f.last_name}".strip().lower()
                    id_lower = identifier.lower().strip()
                    if id_lower in full_name or full_name in id_lower:
                        user = f.user
                        break

            # 5. Search by Role shorthand
            if not user:
                if identifier.lower() == "admin":
                    user = User.query.filter_by(role=Role.ADMIN).first()
                elif identifier.lower() in ("hod", "hod csd"):
                    user = User.query.filter_by(role=Role.HOD).first()

        if user and user.check_password(password):
            if not user.is_active:
                flash("Your account has been deactivated. Please contact the system administrator.", "danger")
                return render_template("auth/login.html")

            login_user(user, remember=remember)
            flash(f"Welcome back, {user.full_name}!", "success")

            next_page = request.args.get("next")
            if next_page and next_page.startswith("/"):
                return redirect(next_page)

            if user.role == Role.ADMIN:
                return redirect(url_for("admin.dashboard"))
            elif user.role == Role.HOD:
                return redirect(url_for("hod.dashboard"))
            elif user.role == Role.FACULTY:
                return redirect(url_for("faculty.dashboard"))
            else:
                return redirect(url_for("student.dashboard"))
        else:
            flash("Invalid email credentials or password. Please try again.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    """Sign user out and clear active session."""
    logout_user()
    flash("You have been signed out successfully.", "info")
    return redirect(url_for("auth.login"))
