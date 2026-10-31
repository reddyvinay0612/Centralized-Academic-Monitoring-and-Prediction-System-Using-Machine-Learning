"""
Unified Machine Learning & XAI Inference Service for CAMPS-ML.
Bridges trained XGBoost, Random Forest Regressor, and TreeSHAP explainer
with the Flask application and SQLAlchemy database.
"""

import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from app import db
from app.models import (
    StudentProfile,
    PredictionLog,
    SHAPFactor,
    NotificationAlert,
    AttendanceRecord,
    InternalAssessment,
    Enrollment,
    SemesterResult,
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_DIR = BASE_DIR / "ml_engine" / "saved_models"

# Global memory cache for serialized ML pipelines
_CLASSIFIER_CACHE = None
_REGRESSOR_CACHE = None
_SHAP_CACHE = None


def get_models():
    """Load and cache serialized model pipelines in memory."""
    global _CLASSIFIER_CACHE, _REGRESSOR_CACHE, _SHAP_CACHE

    if _CLASSIFIER_CACHE is None:
        _CLASSIFIER_CACHE = joblib.load(MODEL_DIR / "classifier_pipeline.joblib")
    if _REGRESSOR_CACHE is None:
        _REGRESSOR_CACHE = joblib.load(MODEL_DIR / "regressor_pipeline.joblib")
    if _SHAP_CACHE is None:
        _SHAP_CACHE = joblib.load(MODEL_DIR / "shap_explainer.joblib")

    return _CLASSIFIER_CACHE, _REGRESSOR_CACHE, _SHAP_CACHE


def extract_features_from_student(student: StudentProfile):
    """
    Extract standardized feature vector for a student from their relational database records.
    """
    # 1. Aggregate attendance across active enrollments
    enrollments = Enrollment.query.filter_by(student_id=student.id).all()
    att_records = [e.attendance for e in enrollments if e.attendance is not None]
    
    if att_records:
        avg_attendance = round(sum(a.percentage for a in att_records) / len(att_records), 1)
    else:
        avg_attendance = 80.0

    # 2. Aggregate CIE marks
    cie_records = [e.internal_assessment for e in enrollments if e.internal_assessment is not None]
    if cie_records:
        valid_ia1 = [c.ia1_marks for c in cie_records if c.ia1_marks is not None]
        valid_ia2 = [c.ia2_marks for c in cie_records if c.ia2_marks is not None]
        valid_ia3 = [c.ia3_marks for c in cie_records if c.ia3_marks is not None]
        valid_assign = [c.assignment_marks for c in cie_records if c.assignment_marks is not None]
        valid_lab = [c.lab_marks for c in cie_records if c.lab_marks is not None]
        valid_total = [c.total_cie for c in cie_records if c.total_cie is not None]

        ia1 = round(sum(valid_ia1) / len(valid_ia1), 1) if valid_ia1 else 18.0
        ia2 = round(sum(valid_ia2) / len(valid_ia2), 1) if valid_ia2 else 17.5
        ia3 = round(sum(valid_ia3) / len(valid_ia3), 1) if valid_ia3 else 18.0
        assign = round(sum(valid_assign) / len(valid_assign), 1) if valid_assign else 7.5
        lab = round(sum(valid_lab) / len(valid_lab), 1) if valid_lab else 8.0
        total_cie = round(sum(valid_total) / len(valid_total), 1) if valid_total else 34.0
    else:
        ia1, ia2, ia3, assign, lab, total_cie = 18.0, 17.5, 18.0, 7.5, 8.0, 34.0

    # 3. Semester SGPA history
    sem_results = {r.semester: r.sgpa for r in student.semester_results}
    s1 = sem_results.get(1, student.cumulative_cgpa or 7.0)
    s2 = sem_results.get(2, student.cumulative_cgpa or 7.0)
    s3 = sem_results.get(3, student.cumulative_cgpa or 7.0)
    s4 = sem_results.get(4, student.cumulative_cgpa or 7.0)

    feature_dict = {
        "Department": student.department.code if student.department else "CSD",
        "Gender": student.gender or "Male",
        "Category": student.category or "General",
        "Fee_Status": student.fee_status or "Cleared",
        "Scholarship": 1 if student.scholarship_recipient else 0,
        "Attendance_Percentage": avg_attendance,
        "CIE_IA1": ia1,
        "CIE_IA2": ia2,
        "CIE_IA3": ia3,
        "Assignment_Score": assign,
        "Lab_Score": lab,
        "Total_CIE": total_cie,
        "Sem1_SGPA": s1,
        "Sem2_SGPA": s2,
        "Sem3_SGPA": s3,
        "Sem4_SGPA": s4,
        "Cumulative_CGPA": student.cumulative_cgpa or 7.0,
        "Active_Backlogs": student.total_active_backlogs or 0,
        "10th_Percentage": 80.0,
        "12th_Percentage": 78.0,
        "Entrance_Rank": 15000,
        "Fee_Due_Amount": student.fee_due_amount or 0.0
    }
    return feature_dict


def predict_for_student_dict(feature_dict):
    """Execute classification, regression, and TreeSHAP inference on feature dictionary."""
    clf_bundle, reg_bundle, shap_bundle = get_models()

    clf_pipeline = clf_bundle["pipeline"]
    reverse_mapping = clf_bundle["reverse_mapping"]
    reg_pipeline = reg_bundle["pipeline"]
    shap_explainer = shap_bundle["explainer"]
    preprocessor = shap_bundle["preprocessor"]
    feature_names = shap_bundle["feature_names"]
    expected_features = shap_bundle["features"]

    df_input = pd.DataFrame([feature_dict])

    # 1. Classification (Risk Tier)
    pred_class_idx = clf_pipeline.predict(df_input)[0]
    pred_risk_level = reverse_mapping[pred_class_idx]
    pred_probs = clf_pipeline.predict_proba(df_input)[0]
    high_risk_prob = float(pred_probs[2])  # index 2 is High Risk

    # 2. Continuous Next-Semester SGPA Regression
    pred_sgpa = float(reg_pipeline.predict(df_input)[0])
    pred_sgpa = max(3.5, min(10.0, round(pred_sgpa, 2)))

    # 3. TreeSHAP Local Attributions
    X_trans = preprocessor.transform(df_input[expected_features])
    sv = shap_explainer(X_trans)
    sv_high = sv.values[0, :, 2] if len(sv.values.shape) == 3 else sv.values[0]

    shap_factors = []
    for fname, val in zip(feature_names, sv_high):
        clean_name = fname.replace("num__", "").replace("cat__", "").replace("_", " ")
        if abs(val) > 0.005:
            shap_factors.append({
                "feature_name": clean_name,
                "feature_value": str(feature_dict.get(fname.split("__")[-1], "")),
                "shap_value": round(float(val), 4),
                "impact_direction": "Increases Risk" if val > 0 else "Decreases Risk"
            })

    shap_factors.sort(key=lambda x: abs(x["shap_value"]), reverse=True)
    top_shap = shap_factors[:4]

    # 4. Generate Actionable Recommendations based on SHAP drivers
    recommendations = []
    if feature_dict.get("Attendance_Percentage", 100) < 75.0:
        recommendations.append("Attendance is below 75%: prioritize daily lecture attendance and complete compensatory lab makeup sessions.")
    if feature_dict.get("CIE_IA2", 30) < 15.0 or feature_dict.get("Total_CIE", 50) < 25.0:
        recommendations.append("Continuous internal assessment marks are slipping: attend faculty remedial problem-solving clinics before IA3.")
    if feature_dict.get("Active_Backlogs", 0) > 0:
        recommendations.append(f"Clear active backlogs ({feature_dict.get('Active_Backlogs')} courses) via university fast-track supplementary coaching.")
    if feature_dict.get("Fee_Status") != "Cleared":
        recommendations.append("Administrative: Resolve pending fee dues at the accounts desk to prevent exam hall-ticket retention.")
    if not recommendations:
        recommendations.append("Excellent academic standing: maintain current attendance consistency and explore advanced honors electives/research.")

    return {
        "predicted_risk_level": pred_risk_level,
        "risk_probability": round(high_risk_prob, 3),
        "predicted_sgpa": pred_sgpa,
        "shap_factors": top_shap,
        "recommendations": recommendations
    }


def score_and_update_student(student_id: int, milestone="Live Inference", commit=True):
    """
    Score a student profile, persist prediction log, update current risk status,
    and trigger automated early-warning alerts if threshold breached.
    """
    student = StudentProfile.query.get(student_id)
    if not student:
        return None

    features = extract_features_from_student(student)
    result = predict_for_student_dict(features)

    # Update student profile
    student.current_risk_level = result["predicted_risk_level"]

    # Log prediction to database
    pred_log = PredictionLog(
        student_id=student.id,
        semester=student.current_semester,
        milestone=milestone,
        predicted_risk_level=result["predicted_risk_level"],
        risk_probability=result["risk_probability"],
        predicted_sgpa=result["predicted_sgpa"],
        model_name="XGBoost Classifier + GB Regressor",
        model_version="v1.0"
    )
    db.session.add(pred_log)
    db.session.flush()

    # Save top SHAP factors
    for factor in result["shap_factors"]:
        sf = SHAPFactor(
            prediction_id=pred_log.id,
            feature_name=factor["feature_name"],
            feature_value=factor["feature_value"],
            shap_value=factor["shap_value"],
            impact_direction=factor["impact_direction"]
        )
        db.session.add(sf)

    # Check alert thresholds
    att_pct = features.get("Attendance_Percentage", 100.0)
    if result["predicted_risk_level"] == "High" or att_pct < 75.0:
        # Alert to Mentor
        if student.mentor and student.mentor.user_id:
            alert = NotificationAlert(
                recipient_user_id=student.mentor.user_id,
                student_id=student.id,
                alert_type="HIGH_RISK_DETECTED" if result["predicted_risk_level"] == "High" else "ATTENDANCE_SHORTAGE",
                severity="critical" if result["predicted_risk_level"] == "High" else "warning",
                title=f"Early Warning: {student.usn} ({student.first_name})",
                message=f"Student {student.first_name} {student.last_name} flagged with {result['predicted_risk_level']} risk (Prob: {result['risk_probability']*100:.1f}%, Attendance: {att_pct}%). Top driver: {result['shap_factors'][0]['feature_name'] if result['shap_factors'] else 'Academic History'}.",
                is_read=False,
                email_dispatched=False
            )
            db.session.add(alert)

    if commit:
        db.session.commit()

    return result
