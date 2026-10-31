"""
SQLAlchemy ORM Model Registry and Flask-Login User Loader for CAMPS-ML.
"""

from app import login_manager
from app.models.user import Role, User, StudentProfile, FacultyProfile
from app.models.academic import Department, Course, Enrollment
from app.models.assessment import AttendanceRecord, InternalAssessment, SemesterResult
from app.models.prediction import PredictionLog, SHAPFactor
from app.models.intervention import MentorRemark, NotificationAlert


@login_manager.user_loader
def load_user(user_id):
    """Flask-Login callback to reload the user object from the user ID stored in the session."""
    return User.query.get(int(user_id))


__all__ = [
    "Role",
    "User",
    "StudentProfile",
    "FacultyProfile",
    "Department",
    "Course",
    "Enrollment",
    "AttendanceRecord",
    "InternalAssessment",
    "SemesterResult",
    "PredictionLog",
    "SHAPFactor",
    "MentorRemark",
    "NotificationAlert",
]
