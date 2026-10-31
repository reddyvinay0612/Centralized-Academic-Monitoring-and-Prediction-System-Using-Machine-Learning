"""
User and Profile ORM Models for CAMPS-ML.
Handles Role-Based Access Control (Admin, HoD, Faculty/Mentor, Student)
and password hashing via Werkzeug / Bcrypt.
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db


class Role:
    """Standardized Role constants for RBAC."""
    ADMIN = "admin"
    HOD = "hod"
    FACULTY = "faculty"
    STUDENT = "student"
    
    CHOICES = [ADMIN, HOD, FACULTY, STUDENT]


class User(UserMixin, db.Model):
    """Core Authentication & Identity Model."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=Role.STUDENT, index=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)

    # 1-to-1 relationships to role-specific profiles
    student_profile = db.relationship("StudentProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    faculty_profile = db.relationship("FacultyProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    notifications = db.relationship("NotificationAlert", back_populates="recipient_user", cascade="all, delete-orphan")

    def set_password(self, password):
        """Hash and set user password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify plain password against hashed password."""
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        """Return full name depending on user role."""
        if self.role == Role.STUDENT and self.student_profile:
            return f"{self.student_profile.first_name} {self.student_profile.last_name}"
        elif self.role in (Role.FACULTY, Role.HOD) and self.faculty_profile:
            return f"{self.faculty_profile.first_name} {self.faculty_profile.last_name}"
        return self.email.split("@")[0].capitalize()

    def has_role(self, *roles):
        """Check if user has any of the requested roles."""
        return self.role in roles

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


class FacultyProfile(db.Model):
    """Profile data for Faculty members, Mentors, and HoDs."""
    __tablename__ = "faculty_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    employee_id = db.Column(db.String(30), unique=True, nullable=False, index=True)
    first_name = db.Column(db.String(60), nullable=False)
    last_name = db.Column(db.String(60), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=False)
    designation = db.Column(db.String(80), default="Assistant Professor")
    phone = db.Column(db.String(15), nullable=True)
    cabin_room = db.Column(db.String(20), nullable=True)

    # Relationships
    user = db.relationship("User", back_populates="faculty_profile")
    department = db.relationship("Department", back_populates="faculty_members")
    mentees = db.relationship("StudentProfile", back_populates="mentor", foreign_keys="StudentProfile.mentor_id")
    remarks_given = db.relationship("MentorRemark", back_populates="faculty", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Faculty {self.first_name} {self.last_name} ({self.employee_id})>"


class StudentProfile(db.Model):
    """Detailed Profile for Students matching Indian College USN schema."""
    __tablename__ = "student_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    usn = db.Column(db.String(20), unique=True, nullable=False, index=True)  # e.g., 1RV21CD001
    first_name = db.Column(db.String(60), nullable=False)
    last_name = db.Column(db.String(60), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=False)
    batch_year = db.Column(db.Integer, nullable=False)  # Admission Year, e.g. 2021
    current_semester = db.Column(db.Integer, nullable=False, default=1)
    section = db.Column(db.String(5), nullable=False, default="A")
    gender = db.Column(db.String(10), nullable=True)  # Male, Female, Other
    category = db.Column(db.String(20), default="General")  # General, OBC, SC, ST, etc.
    parent_phone = db.Column(db.String(15), nullable=True)
    parent_email = db.Column(db.String(120), nullable=True)
    
    # Financial Status
    fee_due_amount = db.Column(db.Float, default=0.0, nullable=False)
    fee_status = db.Column(db.String(20), default="Cleared")  # Cleared, Pending, Defaulter
    scholarship_recipient = db.Column(db.Boolean, default=False)
    
    # Mentorship assignment
    mentor_id = db.Column(db.Integer, db.ForeignKey("faculty_profiles.id"), nullable=True)

    # Overall Academic Standing
    cumulative_cgpa = db.Column(db.Float, default=0.0)
    total_active_backlogs = db.Column(db.Integer, default=0)
    current_risk_level = db.Column(db.String(20), default="Low")  # Low, Medium, High

    # Relationships
    user = db.relationship("User", back_populates="student_profile")
    department = db.relationship("Department", back_populates="students")
    mentor = db.relationship("FacultyProfile", back_populates="mentees", foreign_keys=[mentor_id])
    enrollments = db.relationship("Enrollment", back_populates="student", cascade="all, delete-orphan")
    semester_results = db.relationship("SemesterResult", back_populates="student", cascade="all, delete-orphan")
    predictions = db.relationship("PredictionLog", back_populates="student", cascade="all, delete-orphan")
    mentor_remarks = db.relationship("MentorRemark", back_populates="student", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Student {self.usn} - {self.first_name} {self.last_name}>"
