"""
Realistic Synthetic Dataset Generator for Indian Engineering College Schema.
Generates 1,500 records with realistic multivariate correlations:
- High backlogs + low attendance (<75%) + low CIE -> High Risk / Dropout
- Moderate attendance + average CIE + 1 backlog -> Medium Risk / Probation
- High attendance (>85%) + high CIE + 0 backlogs -> Low Risk / High Honors
"""

import numpy as np
import pandas as pd
from pathlib import Path

# Fix seed for reproducibility
np.random.seed(42)

DATA_DIR = Path(__file__).resolve().parent / "synthetic"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def generate_indian_college_dataset(n_samples=1500):
    """Generate realistic student dataset with correlated academic metrics."""
    records = []

    first_names_male = ["Aarav", "Rohan", "Vikram", "Aditya", "Abhishek", "Nikhil", "Arjun", "Varun", "Rahul", "Karthik", "Siddharth", "Pranav", "Gautam", "Harish", "Manoj"]
    first_names_female = ["Ananya", "Pooja", "Simran", "Megha", "Deepika", "Aditi", "Sneha", "Divya", "Priya", "Kavya", "Shreya", "Rhea", "Nandini", "Aishwarya", "Tanvi"]
    last_names = ["Sharma", "Verma", "Rao", "Nair", "Patel", "Gowda", "Bhat", "Kulkarni", "Reddy", "Menon", "Deshmukh", "Hegde", "Sen", "Joshi", "Iyer"]

    departments = ["CSD", "CSE", "ISE", "ECE"]
    categories = ["General", "OBC", "SC", "ST", "EWS"]

    for i in range(1, n_samples + 1):
        dept = np.random.choice(departments, p=[0.35, 0.35, 0.15, 0.15])
        gender = np.random.choice(["Male", "Female"], p=[0.58, 0.42])
        first_name = np.random.choice(first_names_male if gender == "Male" else first_names_female)
        last_name = np.random.choice(last_names)
        usn = f"1RV21{dept}{i:03d}" if i <= 999 else f"1RV21{dept}{i}"
        category = np.random.choice(categories, p=[0.45, 0.30, 0.10, 0.05, 0.10])

        # Latent academic aptitude factor ~ N(0, 1)
        latent_ability = np.random.normal(0, 1)

        # High school metrics correlated with ability
        pct_10th = np.clip(78 + latent_ability * 8 + np.random.normal(0, 4), 55, 99)
        pct_12th = np.clip(74 + latent_ability * 9 + np.random.normal(0, 5), 50, 98)
        entrance_rank = int(np.clip(25000 - latent_ability * 12000 + np.random.normal(0, 4000), 500, 75000))

        # Attendance strongly correlated with diligence/ability
        attendance = np.clip(78 + latent_ability * 11 + np.random.normal(0, 6), 35, 99)

        # Continuous Internal Evaluation (CIE) out of 30
        ia1 = np.clip(18 + latent_ability * 5 + np.random.normal(0, 2.5), 4, 30)
        ia2 = np.clip(17.5 + latent_ability * 5.2 + np.random.normal(0, 2.8), 3, 30)
        ia3 = np.clip(18.2 + latent_ability * 5.0 + np.random.normal(0, 2.5), 5, 30)
        assignment = np.clip(7.5 + latent_ability * 1.2 + np.random.normal(0, 0.8), 3, 10)
        lab_score = np.clip(8.0 + latent_ability * 1.0 + np.random.normal(0, 0.7), 4, 10)

        # Total CIE (Best 2 IAs avg + Assignment + Lab = max 50)
        best_2_ias = sorted([ia1, ia2, ia3], reverse=True)[:2]
        cie_total = round((sum(best_2_ias) / 2.0) + assignment + lab_score, 2)

        # Historical SGPAs Sem 1-4
        sgpa_s1 = np.clip(7.0 + latent_ability * 1.2 + np.random.normal(0, 0.5), 4.0, 9.9)
        sgpa_s2 = np.clip(6.9 + latent_ability * 1.25 + np.random.normal(0, 0.5), 3.8, 9.9)
        sgpa_s3 = np.clip(6.8 + latent_ability * 1.3 + np.random.normal(0, 0.6), 3.5, 10.0)
        sgpa_s4 = np.clip(6.85 + latent_ability * 1.35 + np.random.normal(0, 0.6), 3.5, 10.0)
        cgpa = round((sgpa_s1 + sgpa_s2 + sgpa_s3 + sgpa_s4) / 4.0, 2)

        # Backlogs
        if cgpa < 5.5 or attendance < 65:
            backlogs = int(np.random.choice([2, 3, 4, 5], p=[0.4, 0.3, 0.2, 0.1]))
        elif cgpa < 6.8 or attendance < 75:
            backlogs = int(np.random.choice([0, 1, 2], p=[0.4, 0.45, 0.15]))
        else:
            backlogs = int(np.random.choice([0, 1], p=[0.95, 0.05]))

        # Financials
        fee_due = 0.0
        fee_status = "Cleared"
        if np.random.rand() < 0.18:
            fee_status = np.random.choice(["Pending", "Defaulter"], p=[0.7, 0.3])
            fee_due = round(float(np.random.choice([15000, 30000, 45000, 60000])), 2)

        scholarship = 1 if (cgpa >= 8.5 and fee_status == "Cleared") else 0

        # Target Risk Classification (Islam et al. 2024: 3-class target)
        # Latent risk score
        risk_score = (
            (75.0 - attendance) * 0.025 +
            (5.5 - cgpa) * 0.35 +
            (backlogs * 0.30) +
            (18.0 - (ia1 + ia2)/2.0) * 0.04 +
            (0.15 if fee_status != "Cleared" else -0.1)
        )

        if risk_score > 0.45 or attendance < 60 or backlogs >= 3:
            target_risk = "High"  # Equivalent to Dropout
        elif risk_score > -0.20 or attendance < 75 or backlogs == 1 or cgpa < 6.5:
            target_risk = "Medium"  # Equivalent to Enrolled / Academic Probation
        else:
            target_risk = "Low"  # Equivalent to Graduate / Good Standing

        # Target Next-Semester SGPA Regression (DeJong & Karadogan 2024)
        next_sgpa = np.clip(
            cgpa + (attendance - 75) * 0.02 + (cie_total - 30) * 0.05 - (backlogs * 0.35) + np.random.normal(0, 0.35),
            3.5, 10.0
        )

        records.append({
            "USN": usn,
            "First_Name": first_name,
            "Last_Name": last_name,
            "Department": dept,
            "Gender": gender,
            "Category": category,
            "10th_Percentage": round(pct_10th, 1),
            "12th_Percentage": round(pct_12th, 1),
            "Entrance_Rank": entrance_rank,
            "Attendance_Percentage": round(attendance, 1),
            "CIE_IA1": round(ia1, 1),
            "CIE_IA2": round(ia2, 1),
            "CIE_IA3": round(ia3, 1),
            "Assignment_Score": round(assignment, 1),
            "Lab_Score": round(lab_score, 1),
            "Total_CIE": cie_total,
            "Sem1_SGPA": round(sgpa_s1, 2),
            "Sem2_SGPA": round(sgpa_s2, 2),
            "Sem3_SGPA": round(sgpa_s3, 2),
            "Sem4_SGPA": round(sgpa_s4, 2),
            "Cumulative_CGPA": cgpa,
            "Active_Backlogs": backlogs,
            "Fee_Due_Amount": fee_due,
            "Fee_Status": fee_status,
            "Scholarship": scholarship,
            "Target_Risk": target_risk,
            "Target_Next_SGPA": round(next_sgpa, 2)
        })

    df = pd.DataFrame(records)
    out_csv = DATA_DIR / "indian_college_student_data.csv"
    df.to_csv(out_csv, index=False)
    print(f"[+] Successfully generated {len(df)} synthetic records -> {out_csv}")
    print("[*] Target Risk Class Distribution:")
    print(df["Target_Risk"].value_counts(normalize=True).round(3))
    return df


if __name__ == "__main__":
    generate_indian_college_dataset(1500)
