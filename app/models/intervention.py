"""
Intervention and Alert Notification ORM Models for CAMPS-ML.
Tracks Faculty Mentorship remarks, counseling action plans, and automated early warnings.
"""

from datetime import datetime
from app import db


class MentorRemark(db.Model):
    """Counselling and intervention record logged by a Faculty Mentor."""
    __tablename__ = "mentor_remarks"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey("faculty_profiles.id", ondelete="CASCADE"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    concern_category = db.Column(db.String(50), nullable=False)  # Attendance, CIE Marks, Fee/Financial, Disciplinary
    remark_text = db.Column(db.Text, nullable=False)
    action_plan = db.Column(db.Text, nullable=True)             # e.g., "Assigned peer tutor; 2 remedial tests scheduled"
    follow_up_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default="Open")            # Open, In-Progress, Resolved

    # Relationships
    student = db.relationship("StudentProfile", back_populates="mentor_remarks")
    faculty = db.relationship("FacultyProfile", back_populates="remarks_given")

    def __repr__(self):
        return f"<MentorRemark Student:{self.student_id} Faculty:{self.faculty_id} Category:{self.concern_category}>"


class NotificationAlert(db.Model):
    """In-app and email alert dispatched when academic thresholds are breached."""
    __tablename__ = "notification_alerts"

    id = db.Column(db.Integer, primary_key=True)
    recipient_user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=True)
    
    alert_type = db.Column(db.String(40), nullable=False)  # ATTENDANCE_SHORTAGE, HIGH_RISK, CIE_FAIL, FEE_DUE
    severity = db.Column(db.String(20), default="warning") # info, warning, critical
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    email_dispatched = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    recipient_user = db.relationship("User", back_populates="notifications")
    student = db.relationship("StudentProfile")

    def __repr__(self):
        return f"<Alert User:{self.recipient_user_id} Type:{self.alert_type} Read:{self.is_read}>"
