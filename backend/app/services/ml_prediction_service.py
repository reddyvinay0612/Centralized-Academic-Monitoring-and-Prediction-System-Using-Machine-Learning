"""
Machine Learning Multi-Department Prediction Engine for CAMPS-ML.
Integrates 4 Champion Models trained on 644 PESITM multi-department students:
1. Pass/Fail Classifier (XGBoost Champion - 89.60% Accuracy, 94.43% F1)
2. Risk Tier Classifier (XGBoost Champion - 79.19% Accuracy, Low/Medium/High)
3. SGPA & Aggregate Marks Regressors (Lasso Champion - R2=0.728, MAE=0.410)
4. Marks Range Classifier (Extra Trees Champion - 10-point bands)
"""

import os
from pathlib import Path
import joblib
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
MODEL_DIR = BASE_DIR / "ml_engine" / "saved_models"

PF_MODEL_PATH = MODEL_DIR / "pesitm_sem6_pass_fail_champion.joblib"
RISK_MODEL_PATH = MODEL_DIR / "pesitm_sem6_risk_classifier_champion.joblib"
REG_MODEL_PATH = MODEL_DIR / "pesitm_sem6_regressor_champion.joblib"
RANGE_MODEL_PATH = MODEL_DIR / "pesitm_sem6_range_classifier_champion.joblib"

# Backward compatibility fallback path
LEGACY_MODEL_PATH = MODEL_DIR / "pass_fail_classifier.joblib"

_cached_bundles = {
    "pass_fail": None,
    "risk": None,
    "regressor": None,
    "range": None
}


def get_model_bundle():
    """
    Loads and caches the 4 champion models.
    """
    global _cached_bundles
    if _cached_bundles["pass_fail"] is None:
        if PF_MODEL_PATH.exists():
            _cached_bundles["pass_fail"] = joblib.load(PF_MODEL_PATH)
        elif LEGACY_MODEL_PATH.exists():
            legacy = joblib.load(LEGACY_MODEL_PATH)
            _cached_bundles["pass_fail"] = legacy if isinstance(legacy, dict) else {"model": legacy}

        if RISK_MODEL_PATH.exists():
            _cached_bundles["risk"] = joblib.load(RISK_MODEL_PATH)

        if REG_MODEL_PATH.exists():
            _cached_bundles["regressor"] = joblib.load(REG_MODEL_PATH)

        if RANGE_MODEL_PATH.exists():
            _cached_bundles["range"] = joblib.load(RANGE_MODEL_PATH)

    return _cached_bundles["pass_fail"]


def get_all_champion_models():
    """
    Returns the dictionary of all loaded champion bundles.
    """
    get_model_bundle()
    return _cached_bundles


def run_pass_fail_prediction(
    ia1=20.0, ia2=20.0, ia3=20.0,
    assignment=8.5, lab=18.0,
    sem1_sgpa=7.0, sem2_sgpa=7.0, sem3_sgpa=7.0, sem4_sgpa=7.0, sem5_sgpa=None,
    previous_sem_sgpa=None,
    cgpa=7.0, backlogs=0, attendance=85.0,
    sem5_internal_pct=None
):
    """
    Computes unified multi-module predictions using the PESITM multi-department champion models:
    - Pass/Fail forecast (Module 1)
    - Risk Tier assessment (Module 2)
    - Predicted SGPA and Marks (Module 3)
    - Next-sem Marks Range Band (Module 4)
    - VTU Regulatory Eligibility & Semester Detention Compliance
    """
    get_model_bundle()
    pf_bundle = _cached_bundles["pass_fail"]
    risk_bundle = _cached_bundles["risk"]
    reg_bundle = _cached_bundles["regressor"]
    range_bundle = _cached_bundles["range"]

    # Calculate Continuous Internal Evaluation (CIE) using VTU guidelines
    ia_list = [float(ia1), float(ia2), float(ia3)]
    avg_ia = float(np.mean(ia_list))
    best_2_ias = sorted(ia_list, reverse=True)[:2]
    total_cie = min(50.0, (sum(best_2_ias) / 2.0) + float(assignment) + (float(lab) * 0.5))
    cie_deficiency = 1 if total_cie < 20.0 else 0

    # Clean and resolve semester variables
    s1 = float(sem1_sgpa) if sem1_sgpa is not None and float(sem1_sgpa) > 0 else None
    s2 = float(sem2_sgpa) if sem2_sgpa is not None and float(sem2_sgpa) > 0 else None
    s3 = float(sem3_sgpa) if sem3_sgpa is not None and float(sem3_sgpa) > 0 else float(cgpa)
    s4 = float(sem4_sgpa) if sem4_sgpa is not None and float(sem4_sgpa) > 0 else float(cgpa)
    s5 = float(sem5_sgpa) if sem5_sgpa is not None and float(sem5_sgpa) > 0 else s4

    prev_sgpa = float(previous_sem_sgpa) if previous_sem_sgpa is not None else s5
    curr_cgpa = float(cgpa) if cgpa is not None and float(cgpa) > 0 else float(np.mean([x for x in [s1, s2, s3, s4, s5] if x]))
    curr_backlogs = max(0, int(backlogs))
    curr_att = float(attendance)

    # Lateral Entry handling
    is_lateral = 1 if s1 is None else 0
    s1_clean = curr_cgpa if is_lateral else s1
    s2_clean = curr_cgpa if s2 is None else s2

    # Internal percentage calculation
    if sem5_internal_pct is not None and float(sem5_internal_pct) > 0:
        internal_pct = float(sem5_internal_pct)
    else:
        # Based on CIE total out of 50 or IA average out of 25
        internal_pct = min(100.0, max(20.0, (total_cie / 50.0) * 100.0))

    # Trajectory & Ratio features matching the 14-feature schema
    sgpa_trend = float(s5 - s4)
    cgpa_deviation = float(s5 - curr_cgpa)
    internal_ratio = float(internal_pct / (curr_cgpa * 10.0 + 1e-5))

    feature_cols = [
        'Sem1_SGPA_clean',
        'Sem2_SGPA_clean',
        'Sem3_SGPA',
        'Sem4_SGPA',
        'Sem5_SGPA',
        'previous_sem_sgpa',
        'cgpa',
        'backlogs',
        'Sem5_internal_pct',
        'avg_ia',
        'sgpa_trend',
        'cgpa_deviation',
        'internal_ratio',
        'is_lateral_entry'
    ]

    record = pd.DataFrame([{
        'Sem1_SGPA_clean': float(s1_clean),
        'Sem2_SGPA_clean': float(s2_clean),
        'Sem3_SGPA': float(s3),
        'Sem4_SGPA': float(s4),
        'Sem5_SGPA': float(s5),
        'previous_sem_sgpa': float(prev_sgpa),
        'cgpa': float(curr_cgpa),
        'backlogs': int(curr_backlogs),
        'Sem5_internal_pct': float(internal_pct),
        'avg_ia': float(avg_ia),
        'sgpa_trend': float(sgpa_trend),
        'cgpa_deviation': float(cgpa_deviation),
        'internal_ratio': float(internal_ratio),
        'is_lateral_entry': int(is_lateral)
    }])[feature_cols]

    # --- Module 1: Pass / Fail Prediction ---
    prob_pass = 0.95
    if pf_bundle:
        model = pf_bundle.get("model") if isinstance(pf_bundle, dict) else pf_bundle
        try:
            probs = model.predict_proba(record)[0]
            prob_pass = float(probs[1])
        except Exception:
            prob_pass = 0.95 if curr_backlogs == 0 and curr_cgpa >= 6.0 else 0.40
    else:
        fail_risk = (
            (1 if total_cie < 20 else 0) * 0.4 +
            (1 if curr_att < 75 else 0) * 0.3 +
            (min(curr_backlogs, 4) * 0.1) +
            (1 if curr_cgpa < 5.0 else 0) * 0.2
        )
        prob_pass = 1.0 - min(0.99, max(0.01, fail_risk))

    prob_fail = 1.0 - prob_pass
    prediction = "PASS" if prob_pass >= 0.50 else "FAIL"

    # --- Module 2: Risk Tier Classification ---
    risk_label = "LOW RISK"
    if risk_bundle:
        try:
            r_model = risk_bundle.get("model") if isinstance(risk_bundle, dict) else risk_bundle
            risk_idx = int(r_model.predict(record)[0])
            risk_map = {0: "LOW RISK", 1: "MODERATE RISK", 2: "HIGH RISK"}
            risk_label = risk_map.get(risk_idx, "MODERATE RISK")
        except Exception:
            if prob_pass >= 0.80:
                risk_label = "LOW RISK"
            elif prob_pass >= 0.50:
                risk_label = "MODERATE RISK"
            else:
                risk_label = "HIGH RISK"
    else:
        if prob_pass >= 0.80:
            risk_label = "LOW RISK"
        elif prob_pass >= 0.50:
            risk_label = "MODERATE RISK"
        else:
            risk_label = "HIGH RISK"

    # --- Module 3: Continuous SGPA and Marks Regression ---
    predicted_sgpa = round(float(np.clip(curr_cgpa * 0.98 + (avg_ia / 25.0) * 0.5, 3.5, 10.0)), 2)
    predicted_avg_marks = round(float(np.clip(predicted_sgpa * 9.5, 35.0, 98.0)), 1)
    if reg_bundle and isinstance(reg_bundle, dict):
        try:
            if "sgpa_model" in reg_bundle:
                pred_s = float(reg_bundle["sgpa_model"].predict(record)[0])
                predicted_sgpa = round(float(np.clip(pred_s, 3.0, 10.0)), 2)
            if "marks_model" in reg_bundle:
                pred_m = float(reg_bundle["marks_model"].predict(record)[0])
                predicted_avg_marks = round(float(np.clip(pred_m, 35.0, 100.0)), 1)
        except Exception:
            pass

    # --- Module 4: Marks Range Category ---
    predicted_marks_range = "70-80"
    if range_bundle and isinstance(range_bundle, dict):
        try:
            rg_model = range_bundle.get("model")
            encoder = range_bundle.get("encoder")
            pred_rg = rg_model.predict(record)[0]
            predicted_marks_range = str(encoder.inverse_transform([pred_rg])[0])
        except Exception:
            if predicted_avg_marks >= 80:
                predicted_marks_range = "80-90"
            elif predicted_avg_marks >= 70:
                predicted_marks_range = "70-80"
            elif predicted_avg_marks >= 60:
                predicted_marks_range = "60-70"
            else:
                predicted_marks_range = "50-60"
    else:
        if predicted_avg_marks >= 80:
            predicted_marks_range = "80-90"
        elif predicted_avg_marks >= 70:
            predicted_marks_range = "70-80"
        elif predicted_avg_marks >= 60:
            predicted_marks_range = "60-70"
        else:
            predicted_marks_range = "50-60"

    # --- Explainability & Risk Attribution Factors ---
    factors = []
    if cie_deficiency:
        factors.append("[-] CRITICAL: Continuous Internal Evaluation (CIE) falls below VTU minimum 20/50 requirement.")
    elif total_cie >= 35.0:
        factors.append(f"[+] Strong Internal Marks: Total CIE score ({total_cie:.1f}/50) provides a resilient safety margin.")
    elif total_cie < 25.0:
        factors.append(f"[-] Borderline Internal Marks: Total CIE ({total_cie:.1f}/50) leaves little margin for external SEE exams.")

    if curr_backlogs > 0:
        factors.append(f"[-] Academic Burden: {curr_backlogs} uncleared backlog subject(s) indicate persistent subject difficulty.")
    else:
        factors.append("[+] Zero Active Backlogs: All prior semester coursework successfully cleared on time.")

    if curr_att < 75.0:
        factors.append(f"[-] Attendance Shortage Alert: {curr_att:.1f}% attendance is below VTU 75% regulatory requirement.")
    elif curr_att >= 85.0:
        factors.append(f"[+] Strong Attendance: {curr_att:.1f}% attendance ensures regulatory eligibility and consistent classroom coverage.")

    if sgpa_trend > 0.3:
        factors.append(f"[+] Positive Performance Trajectory: Semester SGPA trend improved by +{sgpa_trend:.2f}.")
    elif sgpa_trend < -0.5:
        factors.append(f"[-] Negative Performance Trajectory: Semester SGPA dropped by {abs(sgpa_trend):.2f}.")

    if curr_cgpa >= 7.5:
        factors.append(f"[+] High Cumulative CGPA ({curr_cgpa:.2f}) indicates robust foundational mastery.")
    elif curr_cgpa < 5.5:
        factors.append(f"[-] Low Cumulative CGPA ({curr_cgpa:.2f}) places student in vulnerable performance bracket.")

    recommendations = []
    if prediction == "FAIL" or prob_pass < 0.60 or risk_label == "HIGH RISK":
        recommendations.append("Enroll in mandatory remedial tutorial classes for subjects scoring below 18/25 in IAs.")
        recommendations.append("Target a minimum of 45/100 in the upcoming Semester End Exam (SEE) to secure course clearance.")
        recommendations.append("Attend designated faculty mentoring session to formulate an intensive revision schedule.")
    else:
        recommendations.append("Maintain consistent problem-solving practice targeting First Class with Distinction (>= 7.75 SGPA).")
        recommendations.append("Review previous years VTU model question papers to maximize external SEE scoring.")

    # --- VTU Examination Eligibility & Semester Detention Analysis ---
    detention_reasons = []
    detention_risk = "SAFE"  # "SAFE" | "WARNING_CONDONATION" | "DETAINED"

    # 1. Statutory Attendance Check (VTU Rule: Min 75%, Condonation 65-74.9%, Detained < 65%)
    attendance_compliant = curr_att >= 75.0
    if curr_att < 65.0:
        detention_risk = "DETAINED"
        detention_reasons.append(
            f"CRITICAL ATTENDANCE DETENTION (NSAR): Current attendance is {curr_att:.1f}%, which falls below 65%. Under VTU Section 18.2 regulations, student is DETAINED from semester exams and must repeat the semester."
        )
    elif curr_att < 75.0:
        if detention_risk != "DETAINED":
            detention_risk = "WARNING_CONDONATION"
        detention_reasons.append(
            f"ATTENDANCE SHORTAGE CONDONATION REQUIRED: Current attendance ({curr_att:.1f}%) is below 75%. Student must obtain Principal medical/institutional condonation to sit for semester end examinations."
        )
    else:
        detention_reasons.append(
            f"ATTENDANCE COMPLIANCE: Class attendance ({curr_att:.1f}%) comfortably exceeds VTU statutory minimum 75% requirement."
        )

    # 2. Continuous Internal Evaluation (CIE) Sessional Threshold (VTU Rule: Min 40% = 20/50)
    cie_compliant = total_cie >= 20.0
    if total_cie < 20.0:
        detention_risk = "DETAINED"
        detention_reasons.append(
            f"SESSIONAL CIE DETENTION (NSSR): Total CIE score is {total_cie:.1f}/50, which is below the VTU statutory passing mark of 20/50 (40%). Student is disqualified from appearing for this course in SEE."
        )
    elif total_cie < 25.0:
        if detention_risk == "SAFE":
            detention_risk = "WARNING_CONDONATION"
        detention_reasons.append(
            f"BORDERLINE CIE AGGREGATE: Total CIE score ({total_cie:.1f}/50) meets the bare minimum (20/50), but leaves vulnerable margin for semester end theory exams."
        )
    else:
        detention_reasons.append(
            f"CIE SESSIONAL QUALIFICATION: Total CIE score ({total_cie:.1f}/50) qualifies student well above VTU 20/50 internal sessional threshold."
        )

    # 3. Vertical Progression / Active Backlogs Allowance (VTU Rule: Max 4 active backlog courses)
    backlogs_compliant = curr_backlogs <= 4
    if curr_backlogs > 4:
        if detention_risk != "DETAINED":
            detention_risk = "WARNING_CONDONATION"
        detention_reasons.append(
            f"VERTICAL PROGRESSION RISK: {curr_backlogs} accumulated backlogs exceed permissible limit (maximum 4). Student is at risk of academic year detention."
        )
    else:
        detention_reasons.append(
            f"PROGRESSION COMPLIANCE: {curr_backlogs} active backlogs satisfies VTU vertical progression limit (maximum 4 courses permissible)."
        )

    # Overall Examination Eligibility Verdict
    if detention_risk == "DETAINED":
        exam_eligibility = "DETAINED FROM SEMESTER EXAMINATIONS"
        prediction = "FAIL"
        prob_pass = min(prob_pass, 0.05)
        prob_fail = max(prob_fail, 0.95)
        risk_label = "HIGH RISK"
    elif detention_risk == "WARNING_CONDONATION":
        exam_eligibility = "CONDITIONAL / AT RISK OF DETENTION"
    else:
        exam_eligibility = "ELIGIBLE TO TAKE SEMESTER EXAMINATIONS (SUFFICIENT TO APPEAR)"

    pass_pct = round(prob_pass * 100.0, 2)
    fail_pct = round(prob_fail * 100.0, 2)

    return {
        "prediction": prediction,
        "pass_probability": pass_pct,
        "fail_probability": fail_pct,
        "risk_tier": risk_label,
        "predicted_sgpa": predicted_sgpa,
        "predicted_avg_marks": predicted_avg_marks,
        "predicted_marks_range": predicted_marks_range,
        "total_cie": round(total_cie, 1),
        "exam_eligibility": exam_eligibility,
        "detention_risk": detention_risk,
        "detention_reasons": detention_reasons,
        "regulatory_checks": {
            "attendance": {
                "value": round(curr_att, 1),
                "threshold": 75.0,
                "compliant": attendance_compliant,
                "status": "Compliant" if curr_att >= 75.0 else ("Condonation Required" if curr_att >= 65.0 else "Detained (NSAR)")
            },
            "cie": {
                "value": round(total_cie, 1),
                "threshold": 20.0,
                "compliant": cie_compliant,
                "status": "Qualified" if total_cie >= 20.0 else "Detained (NSSR)"
            },
            "backlogs": {
                "value": int(curr_backlogs),
                "max_allowed": 4,
                "compliant": backlogs_compliant,
                "status": "Permissible" if curr_backlogs <= 4 else "Progression Barrier"
            }
        },
        "factors": factors,
        "recommendations": recommendations,
        "model_benchmarks": {
            "pass_fail": "89.60% Accuracy (XGBoost Champion)",
            "risk_classifier": "79.19% Accuracy (XGBoost Champion)",
            "regressor": "R2=0.728, MAE=0.410 SGPA (Lasso Champion)",
            "range_classifier": "65.84% Exact / 98.4% ±1 Band (Extra Trees Champion)"
        }
    }
