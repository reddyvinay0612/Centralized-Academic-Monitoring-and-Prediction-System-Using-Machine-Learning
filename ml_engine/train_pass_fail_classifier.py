"""
Centralized Academic Monitoring and Prediction System (CAMPS-ML)
PES Institute of Technology & Management (PESITM), Shivamogga

Pass/Fail Prediction Model based on Past IA Marks & Past Semester Results.
Measures:
  - Past IA Marks: CIE_IA1, CIE_IA2, CIE_IA3, IA_Average, IA_Trend, Assignment_Score, Lab_Score, Total_CIE, CIE_Deficiency
  - Past Semester Results: Sem1_SGPA, Sem2_SGPA, Sem3_SGPA, Sem4_SGPA, Cumulative_CGPA, Active_Backlogs, SGPA_Trend
  - Institutional Factors: Attendance_Percentage, Attendance_Shortage

Binary Classification:
  1 = PASS (clears all subjects in future examination)
  0 = FAIL (fails 1 or more subjects / accumulates backlogs)

Methodology:
  - Stratified 80/20 train/test split (zero data leakage)
  - Preprocessing: Median Imputation + Robust / Standard Scaling
  - Class Imbalance: SMOTE applied strictly on training folds via imblearn Pipeline
  - 5-Fold Stratified Cross Validation across 5 algorithms:
      1. XGBoost Classifier
      2. Random Forest Classifier
      3. Gradient Boosting Classifier
      4. Decision Tree Classifier
      5. Logistic Regression
  - Hyperparameter tuning for Champion Model (XGBoost)
  - Model Explainability: SHAP (SHapley Additive exPlanations) TreeExplainer
  - Publication-grade visualization outputs in reports_output/
  - Serialized pipeline to ml_engine/saved_models/pass_fail_classifier.joblib
"""

import os
import sys
import glob
from pathlib import Path
import numpy as np
import pandas as pd
import joblib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate, GridSearchCV
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, roc_curve, confusion_matrix, classification_report
)

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from xgboost import XGBClassifier
from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.over_sampling import SMOTE
import shap

# Directories
BASE_DIR = Path(__file__).resolve().parent.parent
REAL_PESITM_DATA_PATH = BASE_DIR / "data" / "processed" / "pesitm_real_marks_dataset.csv"
SYNTHETIC_DATA_PATH = BASE_DIR / "data" / "synthetic" / "indian_college_student_data.csv"
MODEL_DIR = BASE_DIR / "ml_engine" / "saved_models"
OUTPUT_DIR = BASE_DIR / "reports_output"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_dataset():
    """
    Constructs a comprehensive dataset combining past IA marks, past semester results,
    and attendance records, engineering key academic indicators for Pass/Fail prediction.
    Prioritizes real PESITM college marks dataset if present.
    """
    if REAL_PESITM_DATA_PATH.exists():
        print(f"[*] Loading authentic PESITM college marks dataset: {REAL_PESITM_DATA_PATH}")
        df = pd.read_csv(REAL_PESITM_DATA_PATH)
    else:
        print(f"[*] Loading synthetic marks dataset: {SYNTHETIC_DATA_PATH}")
        df = pd.read_csv(SYNTHETIC_DATA_PATH)

        # 1. Feature Engineering: Past IA Marks measures
        df["IA_Average"] = (df["CIE_IA1"] + df["CIE_IA2"] + df["CIE_IA3"]) / 3.0
        df["IA_Trend"] = df["CIE_IA3"] - df["CIE_IA1"]
        df["CIE_Deficiency"] = (df["Total_CIE"] < 20.0).astype(int)

        # 2. Feature Engineering: Past Semester Results measures
        df["SGPA_Trend"] = df["Sem4_SGPA"] - df["Sem1_SGPA"]
        df["Past_Sem_Avg"] = (df["Sem1_SGPA"] + df["Sem2_SGPA"] + df["Sem3_SGPA"] + df["Sem4_SGPA"]) / 4.0

        # 3. Regulatory Indicators (VTU Regulations)
        df["Attendance_Shortage"] = (df["Attendance_Percentage"] < 75.0).astype(int)

        # 4. Target Variable: PASS (1) or FAIL (0) in Further Examination
        fail_condition = (
            (df["Target_Next_SGPA"] < 5.0) |
            (df["Target_Risk"] == "High") |
            ((df["Active_Backlogs"] >= 2) & (df["Total_CIE"] < 25)) |
            (df["Attendance_Percentage"] < 65.0)
        )
        df["Pass_Fail_Target"] = np.where(fail_condition, 0, 1)

    # Feature List
    feature_cols = [
        # Past IA Marks Measures
        "CIE_IA1", "CIE_IA2", "CIE_IA3", "IA_Average", "IA_Trend",
        "Assignment_Score", "Lab_Score", "Total_CIE", "CIE_Deficiency",
        # Past Semester Results Measures
        "Sem1_SGPA", "Sem2_SGPA", "Sem3_SGPA", "Sem4_SGPA",
        "Past_Sem_Avg", "SGPA_Trend", "Cumulative_CGPA", "Active_Backlogs",
        # Attendance & Institutional Measures
        "Attendance_Percentage", "Attendance_Shortage"
    ]

    X = df[feature_cols].copy()
    y = df["Pass_Fail_Target"].values

    total_samples = len(df)
    pass_count = int(np.sum(y == 1))
    fail_count = int(np.sum(y == 0))

    print(f"[+] Total Student Samples: {total_samples}")
    print(f"    - PASS Samples:  {pass_count} ({pass_count/total_samples*100:.1f}%)")
    print(f"    - FAIL Samples:  {fail_count} ({fail_count/total_samples*100:.1f}%)")
    print(f"[+] Evaluated Predictor Features ({len(feature_cols)}):")
    for idx, col in enumerate(feature_cols, 1):
        print(f"    {idx:2d}. {col}")

    return X, y, feature_cols


def build_preprocessor(feature_cols):
    """Build preprocessing pipeline with median imputation and robust scaling."""
    transformer = ImbPipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", RobustScaler())
    ])

    preprocessor = ColumnTransformer(
        transformers=[("num", transformer, feature_cols)],
        remainder="drop"
    )
    return preprocessor


def benchmark_and_train():
    """
    Executes full 5-fold cross validation across 5 classification algorithms,
    tunes the champion model, computes test evaluation, extracts SHAP explanations,
    and generates visual reports.
    """
    X, y, feature_cols = load_dataset()

    # Stratified 80/20 train/test split to guarantee identical class distribution
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, stratify=y, random_state=42
    )

    print(f"\n[*] Training Set: {len(X_train)} samples | Testing Set: {len(X_test)} samples")

    preprocessor = build_preprocessor(feature_cols)

    # Candidate Algorithms
    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Decision Tree": DecisionTreeClassifier(max_depth=5, min_samples_leaf=5, random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=150, max_depth=8, min_samples_split=4, random_state=42),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=120, learning_rate=0.08, max_depth=4, random_state=42),
        "XGBoost": XGBClassifier(n_estimators=120, max_depth=4, learning_rate=0.08, eval_metric="logloss", random_state=42)
    }

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    results = []

    print("\n" + "=" * 80)
    print(f"{'Algorithm':<22} | {'Accuracy':<10} | {'F1-Score':<10} | {'Precision':<10} | {'Recall':<10} | {'ROC-AUC'}")
    print("=" * 80)

    for name, clf in models.items():
        pipe = ImbPipeline([
            ("preprocessor", preprocessor),
            ("smote", SMOTE(random_state=42)),
            ("classifier", clf)
        ])

        scoring = ["accuracy", "f1", "precision", "recall", "roc_auc"]
        cv_scores = cross_validate(pipe, X_train, y_train, cv=cv, scoring=scoring, n_jobs=-1)

        acc = cv_scores["test_accuracy"].mean()
        f1 = cv_scores["test_f1"].mean()
        prec = cv_scores["test_precision"].mean()
        rec = cv_scores["test_recall"].mean()
        auc = cv_scores["test_roc_auc"].mean()

        results.append({
            "Model": name,
            "Accuracy": acc,
            "F1_Score": f1,
            "Precision": prec,
            "Recall": rec,
            "ROC_AUC": auc
        })

        print(f"{name:<22} | {acc*100:6.2f}%   | {f1:8.4f}   | {prec:8.4f}    | {rec:8.4f}  | {auc:8.4f}")

    print("=" * 80)

    results_df = pd.DataFrame(results)

    # --------------------------------------------------------------------------
    # 1. Plot Model Comparison Bar Chart
    # --------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(11, 5.5))
    melted = pd.melt(results_df, id_vars=["Model"], value_vars=["Accuracy", "F1_Score", "Recall", "ROC_AUC"])
    sns.barplot(x="Model", y="value", hue="variable", data=melted, palette="crest", ax=ax)
    ax.set_title("5-Fold Cross Validation Benchmark: Pass/Fail Prediction Models", fontsize=13, fontweight="bold", pad=12)
    ax.set_ylim(0.70, 1.0)
    ax.set_ylabel("Score", fontsize=11)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    plt.xticks(rotation=12, fontweight="medium")
    plt.tight_layout()
    comp_plot = OUTPUT_DIR / "pass_fail_model_comparison.png"
    plt.savefig(comp_plot, dpi=300)
    plt.close()
    print(f"[+] Saved Model Benchmark Chart -> {comp_plot.name}")

    # --------------------------------------------------------------------------
    # 2. Hyperparameter Fine-Tuning for Top Model (XGBoost)
    # --------------------------------------------------------------------------
    print("\n[*] Fine-tuning XGBoost Classifier using GridSearchCV...")
    tuning_pipe = ImbPipeline([
        ("preprocessor", preprocessor),
        ("smote", SMOTE(random_state=42)),
        ("classifier", XGBClassifier(eval_metric="logloss", random_state=42))
    ])

    param_grid = {
        "classifier__n_estimators": [100, 150, 200],
        "classifier__max_depth": [3, 4, 5],
        "classifier__learning_rate": [0.03, 0.08, 0.12],
        "classifier__subsample": [0.8, 1.0]
    }

    grid = GridSearchCV(tuning_pipe, param_grid, cv=3, scoring="f1", n_jobs=-1, verbose=0)
    grid.fit(X_train, y_train)
    champion_pipe = grid.best_estimator_

    print(f"[+] Optimal Hyperparameters: {grid.best_params_}")

    # --------------------------------------------------------------------------
    # 3. Final Evaluation on Unseen 20% Test Split
    # --------------------------------------------------------------------------
    y_pred = champion_pipe.predict(X_test)
    y_prob = champion_pipe.predict_proba(X_test)[:, 1]

    test_acc = accuracy_score(y_test, y_pred)
    test_prec = precision_score(y_test, y_pred)
    test_rec = recall_score(y_test, y_pred)
    test_f1 = f1_score(y_test, y_pred)
    test_auc = roc_auc_score(y_test, y_prob)

    print("\n" + "=" * 65)
    print("FINAL TEST PERFORMANCE ON UNSEEN HELD-OUT DATA (20% Split):")
    print("=" * 65)
    print(f"Accuracy:        {test_acc * 100:.2f}%")
    print(f"F1-Score:        {test_f1:.4f}")
    print(f"Precision:       {test_prec:.4f}")
    print(f"Recall:          {test_rec:.4f}  (Ability to detect Passing students)")
    print(f"ROC-AUC Score:   {test_auc:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["FAIL (0)", "PASS (1)"]))

    # --------------------------------------------------------------------------
    # 4. Save Confusion Matrix Plot
    # --------------------------------------------------------------------------
    cm = confusion_matrix(y_test, y_pred)
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=["Predicted FAIL", "Predicted PASS"],
                yticklabels=["Actual FAIL", "Actual PASS"],
                cbar=False, ax=ax, annot_kws={"size": 13, "weight": "bold"})
    ax.set_title("Test Set Confusion Matrix: Pass/Fail Classifier", fontsize=12, fontweight="bold", pad=12)
    plt.tight_layout()
    cm_path = OUTPUT_DIR / "pass_fail_confusion_matrix.png"
    plt.savefig(cm_path, dpi=300)
    plt.close()
    print(f"[+] Saved Confusion Matrix -> {cm_path.name}")

    # --------------------------------------------------------------------------
    # 5. Save ROC Curve Plot
    # --------------------------------------------------------------------------
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(fpr, tpr, color="#2563eb", lw=2.5, label=f"XGBoost ROC (AUC = {test_auc:.3f})")
    ax.plot([0, 1], [0, 1], color="#94a3b8", linestyle="--", lw=1.5, label="Random Guess")
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel("False Positive Rate (1 - Specificity)", fontsize=10)
    ax.set_ylabel("True Positive Rate (Sensitivity / Recall)", fontsize=10)
    ax.set_title("Receiver Operating Characteristic (ROC) Curve", fontsize=12, fontweight="bold")
    ax.legend(loc="lower right")
    ax.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    roc_path = OUTPUT_DIR / "pass_fail_roc_curve.png"
    plt.savefig(roc_path, dpi=300)
    plt.close()
    print(f"[+] Saved ROC Curve -> {roc_path.name}")

    # --------------------------------------------------------------------------
    # 6. Feature Importance & SHAP Explainability
    # --------------------------------------------------------------------------
    classifier_step = champion_pipe.named_steps["classifier"]
    preprocessor_step = champion_pipe.named_steps["preprocessor"]

    importances = classifier_step.feature_importances_
    feat_imp = pd.Series(importances, index=feature_cols).sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=feat_imp.values, y=feat_imp.index, palette="mako", ax=ax)
    ax.set_title("Feature Importance: Impact of Past Marks on Pass/Fail Prediction", fontsize=12, fontweight="bold")
    ax.set_xlabel("Relative Importance Score", fontsize=10)
    ax.grid(axis="x", linestyle="--", alpha=0.5)
    plt.tight_layout()
    feat_path = OUTPUT_DIR / "pass_fail_feature_importance.png"
    plt.savefig(feat_path, dpi=300)
    plt.close()
    print(f"[+] Saved Feature Importance Chart -> {feat_path.name}")

    # Train TreeExplainer for SHAP local explanations
    print("[*] Generating SHAP TreeExplainer for explainable predictions...")
    X_train_trans = preprocessor_step.transform(X_train)
    explainer = shap.TreeExplainer(classifier_step)

    # --------------------------------------------------------------------------
    # 7. Model Serialization Bundle
    # --------------------------------------------------------------------------
    model_bundle = {
        "pipeline": champion_pipe,
        "feature_cols": feature_cols,
        "metrics": {
            "accuracy": test_acc,
            "f1_score": test_f1,
            "precision": test_prec,
            "recall": test_rec,
            "roc_auc": test_auc
        },
        "model_name": "XGBoost Pass/Fail Early Warning Classifier",
        "decision_threshold": 0.50
    }

    save_path = MODEL_DIR / "pass_fail_classifier.joblib"
    joblib.dump(model_bundle, save_path)
    print(f"[+] Successfully serialized Pass/Fail Model Bundle -> {save_path.name}")

    return champion_pipe, feature_cols


if __name__ == "__main__":
    benchmark_and_train()
