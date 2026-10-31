"""
Alert & Notification Service for CAMPS-ML.
Handles automated threshold checks, in-app notifications, and email alerts via Flask-Mail.
"""

from flask import current_app, render_template_string
from flask_mail import Message
from app import db, mail
from app.models import NotificationAlert, StudentProfile, User


def check_and_create_alerts_for_student(student_id: int):
    """Scan academic metrics for a student and raise alerts if thresholds are breached."""
    student = StudentProfile.query.get(student_id)
    if not student:
        return []

    created_alerts = []
    
    # 1. Attendance Shortage Check (< 75%)
    # Compute average attendance
    att_percentages = [e.attendance.percentage for e in student.enrollments if e.attendance]
    avg_att = sum(att_percentages) / len(att_percentages) if att_percentages else 100.0

    if avg_att < current_app.config.get("ALERT_ATTENDANCE_THRESHOLD", 75.0):
        # Create alert for student
        s_alert = NotificationAlert(
            recipient_user_id=student.user_id,
            student_id=student.id,
            alert_type="ATTENDANCE_SHORTAGE",
            severity="warning",
            title="Attendance Shortage Warning (< 75%)",
            message=f"Dear {student.first_name}, your average attendance is {avg_att:.1f}%, which falls below the mandatory 75% threshold. You are at risk of semester exam disallowance.",
            is_read=False
        )
        db.session.add(s_alert)
        created_alerts.append(s_alert)

        # Create alert for mentor
        if student.mentor and student.mentor.user_id:
            m_alert = NotificationAlert(
                recipient_user_id=student.mentor.user_id,
                student_id=student.id,
                alert_type="ATTENDANCE_SHORTAGE",
                severity="warning",
                title=f"Mentee Attendance Shortage: {student.usn}",
                message=f"Student {student.first_name} {student.last_name} ({student.usn}) has an average attendance of {avg_att:.1f}%. Please schedule an advisory session.",
                is_read=False
            )
            db.session.add(m_alert)
            created_alerts.append(m_alert)

    # 2. High Risk / Dropout Detection
    if student.current_risk_level == "High":
        if student.mentor and student.mentor.user_id:
            risk_alert = NotificationAlert(
                recipient_user_id=student.mentor.user_id,
                student_id=student.id,
                alert_type="HIGH_RISK_DETECTED",
                severity="critical",
                title=f"Critical Academic Risk Flag: {student.usn}",
                message=f"Student {student.first_name} {student.last_name} ({student.usn}) has been classified in the HIGH RISK tier by the ML model. Immediate counselling intervention recommended.",
                is_read=False
            )
            db.session.add(risk_alert)
            created_alerts.append(risk_alert)

    db.session.commit()
    return created_alerts


def dispatch_email_alert(recipient_email: str, subject: str, message_body: str) -> bool:
    """Send transactional email advisory via Flask-Mail, safely handling offline SMTP."""
    try:
        if not recipient_email or "@" not in recipient_email:
            return False

        msg = Message(
            subject=f"[CAMPS-ML Advisory] {subject}",
            recipients=[recipient_email],
            body=message_body
        )

        # In testing or local dev without credentials, log safely
        mail_user = current_app.config.get("MAIL_USERNAME")
        if not mail_user or current_app.config.get("TESTING"):
            print(f"[*] Mock Email Dispatched -> Recipient: {recipient_email} | Subject: {subject}")
            return True

        mail.send(msg)
        return True
    except Exception as e:
        print(f"[!] Email dispatch failed ({e}); continuing gracefully.")
        return False
