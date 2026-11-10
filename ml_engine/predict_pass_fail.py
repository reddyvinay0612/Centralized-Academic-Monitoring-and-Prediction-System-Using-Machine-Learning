"""
Interactive and CLI Predictor for Student Pass/Fail in Semester Examinations.
Analyzes Past IA Marks and Past Semester Results using the trained XGBoost model.
"""

import sys
import argparse
from pathlib import Path
import joblib
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "ml_engine" / "saved_models" / "pass_fail_classifier.joblib"


def load_model():
    if not MODEL_PATH.exists():
        print(f"[!] Error: Model bundle not found at {MODEL_PATH}")
        print("    Please run: py ml_engine/train_pass_fail_classifier.py")
        sys.exit(1)
    return joblib.load(MODEL_PATH)


def predict(
    ia1=20.0, ia2=20.0, ia3=20.0,
    assignment=8.5, lab=18.0,
    sem1_sgpa=7.0, sem2_sgpa=7.2, sem3_sgpa=7.1, sem4_sgpa=7.3,
    cgpa=7.15, backlogs=0, attendance=85.0
):
    bundle = load_model()
    pipeline = bundle["pipeline"]

    # Compute derived features
    ia_avg = (ia1 + ia2 + ia3) / 3.0
    ia_trend = ia3 - ia1
    # VTU CIE calculation: Best 2 of 3 IAs scaled + Assignment + Lab
    # For general evaluation: Total CIE out of 50
    total_cie = min(50.0, (sorted([ia1, ia2, ia3], reverse=True)[0] + sorted([ia1, ia2, ia3], reverse=True)[1]) / 2.0 + assignment + (lab * 0.5))
    cie_deficiency = 1 if total_cie < 20.0 else 0
    past_sem_avg = (sem1_sgpa + sem2_sgpa + sem3_sgpa + sem4_sgpa) / 4.0
    sgpa_trend = sem4_sgpa - sem1_sgpa
    att_shortage = 1 if attendance < 75.0 else 0

    record = pd.DataFrame([{
        "CIE_IA1": float(ia1),
        "CIE_IA2": float(ia2),
        "CIE_IA3": float(ia3),
        "IA_Average": float(ia_avg),
        "IA_Trend": float(ia_trend),
        "Assignment_Score": float(assignment),
        "Lab_Score": float(lab),
        "Total_CIE": float(total_cie),
        "CIE_Deficiency": int(cie_deficiency),
        "Sem1_SGPA": float(sem1_sgpa),
        "Sem2_SGPA": float(sem2_sgpa),
        "Sem3_SGPA": float(sem3_sgpa),
        "Sem4_SGPA": float(sem4_sgpa),
        "Past_Sem_Avg": float(past_sem_avg),
        "SGPA_Trend": float(sgpa_trend),
        "Cumulative_CGPA": float(cgpa),
        "Active_Backlogs": int(backlogs),
        "Attendance_Percentage": float(attendance),
        "Attendance_Shortage": int(att_shortage),
    }])

    # Predict probability
    prob_pass = float(pipeline.predict_proba(record)[0, 1])
    prob_fail = 1.0 - prob_pass
    prediction = "PASS" if prob_pass >= 0.50 else "FAIL"

    # Assess Risk Tier
    if prob_pass >= 0.80:
        risk_tier = "LOW RISK (Safe)"
        badge = "[SAFE - ON TRACK TO CLEAR]"
    elif prob_pass >= 0.50:
        risk_tier = "MODERATE RISK (Borderline Pass)"
        badge = "[CAUTION - REQUIRES INTERVENTION]"
    else:
        risk_tier = "HIGH RISK (Predicted Failure / Backlog Hazard)"
        badge = "[ALERT - CRITICAL REMEDIAL NEEDED]"

    # Generate Top Key Factor Contributions
    factors = []
    if cie_deficiency:
        factors.append("[-] CRITICAL: CIE aggregate below VTU regulatory 20/50 requirement.")
    elif total_cie >= 35:
        factors.append(f"[+] Strong Continuous Internal Assessment (Total CIE: {total_cie:.1f}/50).")
    elif total_cie < 25:
        factors.append(f"[-] Low Continuous Internal Assessment (Total CIE: {total_cie:.1f}/50).")

    if backlogs > 0:
        factors.append(f"[-] Warning: {backlogs} active backlog(s) accumulating academic debt.")
    else:
        factors.append("[+] Zero active backlogs maintaining clean academic trajectory.")

    if att_shortage:
        factors.append(f"[-] Regulatory Shortage: Attendance ({attendance:.1f}%) below VTU 75% bar.")
    elif attendance >= 85:
        factors.append(f"[+] Excellent Attendance ({attendance:.1f}%) supporting classroom readiness.")

    if ia_trend > 2.0:
        factors.append(f"[+] Upward Performance Velocity (IA3 improved by +{ia_trend:.1f} over IA1).")
    elif ia_trend < -2.0:
        factors.append(f"[-] Declining Performance Velocity (IA3 dropped by {abs(ia_trend):.1f} compared to IA1).")

    if cgpa >= 7.5:
        factors.append(f"[+] Strong Historical CGPA base ({cgpa:.2f}).")
    elif cgpa < 5.5:
        factors.append(f"[-] Vulnerable Cumulative CGPA base ({cgpa:.2f}).")

    # Recommendations
    recs = []
    if prediction == "FAIL" or prob_pass < 0.60:
        recs.append("Attend mandatory remedial tutorials for subjects with IA scores < 18.")
        recs.append("Target a minimum of 42/100 in SEE External Exam to compensate for CIE.")
        recs.append("Request faculty mentorship review before final VTU examination hall ticket issuance.")
    else:
        recs.append("Maintain consistent preparation schedule targeting First Class with Distinction (FCD >= 7.75 SGPA).")
        recs.append("Solve previous 3 years VTU question papers to solidify SEE performance.")

    return {
        "prediction": prediction,
        "pass_probability": round(prob_pass * 100, 2),
        "fail_probability": round(prob_fail * 100, 2),
        "risk_tier": risk_tier,
        "badge": badge,
        "total_cie": round(total_cie, 1),
        "factors": factors,
        "recommendations": recs
    }


def print_report(res, inputs):
    print("\n" + "=" * 76)
    print("      PESITM SHIVAMOGGA - ACADEMIC MONITORING & PREDICTION SYSTEM")
    print("               VTU EXAMINATION PASS/FAIL FORECAST")
    print("=" * 76)
    print(f" PREDICTED OUTCOME:    >>>  {res['prediction']}  <<<   {res['badge']}")
    print(f" Pass Probability:     {res['pass_probability']}%")
    print(f" Failure Risk:         {res['fail_probability']}%")
    print(f" Institutional Risk:   {res['risk_tier']}")
    print("-" * 76)
    print(" INPUT MEASURES SUMMARY:")
    print(f"   * Internal Assessment (IA): IA-1: {inputs['ia1']} | IA-2: {inputs['ia2']} | IA-3: {inputs['ia3']}")
    print(f"   * Internal Total (CIE):     {res['total_cie']} / 50")
    print(f"   * Past Semester SGPA:       Sem1: {inputs['sem1']} | Sem2: {inputs['sem2']} | Sem3: {inputs['sem3']} | Sem4: {inputs['sem4']}")
    print(f"   * Cumulative CGPA:          {inputs['cgpa']} / 10.0")
    print(f"   * Active Backlogs:          {inputs['backlogs']}")
    print(f"   * Attendance:               {inputs['att']}%")
    print("-" * 76)
    print(" KEY ACADEMIC ATTRIBUTION FACTORS:")
    for f in res["factors"]:
        print(f"   {f}")
    print("-" * 76)
    print(" ACTIONABLE RECOMMENDATIONS:")
    for r in res["recommendations"]:
        print(f"   -> {r}")
    print("=" * 76 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Predict Student Pass/Fail in Future VTU Examination")
    parser.add_argument("--ia1", type=float, default=None, help="CIE IA-1 Marks (out of 25/50)")
    parser.add_argument("--ia2", type=float, default=None, help="CIE IA-2 Marks (out of 25/50)")
    parser.add_argument("--ia3", type=float, default=None, help="CIE IA-3 Marks (out of 25/50)")
    parser.add_argument("--assignment", type=float, default=8.5, help="Assignment Marks (out of 10)")
    parser.add_argument("--lab", type=float, default=18.0, help="Lab Internal Marks (out of 20)")
    parser.add_argument("--sem1", type=float, default=7.0, help="Semester 1 SGPA")
    parser.add_argument("--sem2", type=float, default=7.2, help="Semester 2 SGPA")
    parser.add_argument("--sem3", type=float, default=7.1, help="Semester 3 SGPA")
    parser.add_argument("--sem4", type=float, default=7.3, help="Semester 4 SGPA")
    parser.add_argument("--cgpa", type=float, default=None, help="Cumulative CGPA")
    parser.add_argument("--backlogs", type=int, default=0, help="Active Backlogs Count")
    parser.add_argument("--att", type=float, default=85.0, help="Attendance Percentage")

    args = parser.parse_args()

    # Interactive Prompt if arguments omitted
    if args.ia1 is None:
        print("\n=== PESITM Academic Predictor (Interactive Mode) ===")
        print("Please enter the student's past marks and semester results:")
        try:
            ia1 = float(input("  CIE IA-1 Marks (e.g., 22): ") or 20.0)
            ia2 = float(input("  CIE IA-2 Marks (e.g., 20): ") or 20.0)
            ia3 = float(input("  CIE IA-3 Marks (e.g., 24): ") or 20.0)
            sem1 = float(input("  Semester 1 SGPA (e.g., 7.5): ") or 7.0)
            sem2 = float(input("  Semester 2 SGPA (e.g., 7.2): ") or 7.0)
            sem3 = float(input("  Semester 3 SGPA (e.g., 7.4): ") or 7.0)
            sem4 = float(input("  Semester 4 SGPA (e.g., 7.6): ") or 7.0)
            cgpa = float(input("  Cumulative CGPA (e.g., 7.4): ") or (sem1 + sem2 + sem3 + sem4)/4.0)
            backlogs = int(input("  Active Backlogs (e.g., 0): ") or 0)
            att = float(input("  Attendance % (e.g., 85.0): ") or 85.0)
        except (ValueError, KeyboardInterrupt):
            print("\nExiting.")
            sys.exit(0)
    else:
        ia1 = args.ia1
        ia2 = args.ia2 or args.ia1
        ia3 = args.ia3 or args.ia1
        sem1 = args.sem1
        sem2 = args.sem2
        sem3 = args.sem3
        sem4 = args.sem4
        cgpa = args.cgpa or (sem1 + sem2 + sem3 + sem4) / 4.0
        backlogs = args.backlogs
        att = args.att

    inputs = {
        "ia1": ia1, "ia2": ia2, "ia3": ia3,
        "sem1": sem1, "sem2": sem2, "sem3": sem3, "sem4": sem4,
        "cgpa": cgpa, "backlogs": backlogs, "att": att
    }

    result = predict(
        ia1=ia1, ia2=ia2, ia3=ia3,
        assignment=args.assignment, lab=args.lab,
        sem1_sgpa=sem1, sem2_sgpa=sem2, sem3_sgpa=sem3, sem4_sgpa=sem4,
        cgpa=cgpa, backlogs=backlogs, attendance=att
    )

    print_report(result, inputs)


if __name__ == "__main__":
    main()
