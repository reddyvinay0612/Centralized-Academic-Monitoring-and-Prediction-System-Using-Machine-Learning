"""
REST API Blueprint for CAMPS-ML.
Exposes async endpoints for live prediction scoring, Chart.js feeds, and notifications.
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models import StudentProfile, SemesterResult, Enrollment, NotificationAlert
from app.services.prediction_service import predict_for_student_dict, score_and_update_student

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/predict", methods=["POST"])
def live_predict():
    """
    Public / Internal REST endpoint for programmatic model scoring.
    Accepts arbitrary student attributes JSON and returns risk classification + TreeSHAP attributions.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON payload provided"}), 400

    try:
        results = predict_for_student_dict(data)
        return jsonify({
            "status": "success",
            "prediction": results
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/student/<int:student_id>/chart-data")
@login_required
def student_chart_data(student_id: int):
    """Feed structured data for Chart.js interactive performance graphs."""
    student = StudentProfile.query.get_or_404(student_id)

    # Historical SGPA trend
    results = SemesterResult.query.filter_by(student_id=student.id).order_by(SemesterResult.semester).all()
    sem_labels = [f"Sem {r.semester}" for r in results]
    sgpa_values = [r.sgpa for r in results]

    # Current Course Attendance & CIE
    enrollments = Enrollment.query.filter_by(student_id=student.id).all()
    course_labels = [e.course.code for e in enrollments]
    att_percentages = [e.attendance.percentage if e.attendance else 0.0 for e in enrollments]
    cie_totals = [e.internal_assessment.total_cie if e.internal_assessment else 0.0 for e in enrollments]

    return jsonify({
        "sgpa_trend": {
            "labels": sem_labels,
            "values": sgpa_values,
            "cgpa": student.cumulative_cgpa
        },
        "course_performance": {
            "labels": course_labels,
            "attendance": att_percentages,
            "cie": cie_totals
        }
    })


@api_bp.route("/notifications/unread")
@login_required
def get_unread_notifications():
    """Return count and list of unread notifications for current user."""
    alerts = NotificationAlert.query.filter_by(
        recipient_user_id=current_user.id, is_read=False
    ).order_by(NotificationAlert.created_at.desc()).limit(10).all()

    return jsonify({
        "count": len(alerts),
        "alerts": [
            {
                "id": a.id,
                "title": a.title,
                "message": a.message,
                "severity": a.severity,
                "created_at": a.created_at.strftime("%d-%b %H:%M")
            } for a in alerts
        ]
    })


@api_bp.route("/notifications/<int:alert_id>/read", methods=["POST"])
@login_required
def mark_notification_read(alert_id: int):
    """Mark a notification alert as read."""
    alert = NotificationAlert.query.filter_by(id=alert_id, recipient_user_id=current_user.id).first()
    if alert:
        alert.is_read = True
        db.session.commit()
        return jsonify({"status": "success"})
    return jsonify({"error": "Alert not found"}), 404
