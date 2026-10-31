"""
Sanity & Boundary Tests for Trained Machine Learning Pipelines and XAI Engine.
"""

from app.services.prediction_service import get_models, predict_for_student_dict


def test_models_loaded_successfully():
    """Verify that serialized joblib artifacts load without error."""
    clf_bundle, reg_bundle, shap_bundle = get_models()
    assert clf_bundle is not None
    assert reg_bundle is not None
    assert shap_bundle is not None
    assert "pipeline" in clf_bundle
    assert "pipeline" in reg_bundle


def test_prediction_output_contract():
    """Verify output contract, bounds, and schema of the predict service."""
    dummy_student = {
        "Department": "CSD",
        "Gender": "Male",
        "Category": "General",
        "Fee_Status": "Cleared",
        "Scholarship": 0,
        "Attendance_Percentage": 82.5,
        "CIE_IA1": 22.0,
        "CIE_IA2": 21.0,
        "CIE_IA3": 23.0,
        "Assignment_Score": 8.0,
        "Lab_Score": 8.5,
        "Total_CIE": 39.0,
        "Sem1_SGPA": 7.4,
        "Sem2_SGPA": 7.6,
        "Sem3_SGPA": 7.3,
        "Sem4_SGPA": 7.5,
        "Cumulative_CGPA": 7.45,
        "Active_Backlogs": 0,
        "10th_Percentage": 85.0,
        "12th_Percentage": 82.0,
        "Entrance_Rank": 12000,
        "Fee_Due_Amount": 0.0
    }

    res = predict_for_student_dict(dummy_student)

    assert "predicted_risk_level" in res
    assert res["predicted_risk_level"] in ["Low", "Medium", "High"]
    assert 0.0 <= res["risk_probability"] <= 1.0
    assert 3.5 <= res["predicted_sgpa"] <= 10.0
    assert len(res["shap_factors"]) > 0
    assert "recommendations" in res
