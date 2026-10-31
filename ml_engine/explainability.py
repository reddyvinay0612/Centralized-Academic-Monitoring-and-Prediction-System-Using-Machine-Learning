"""
TreeSHAP Explainable AI (XAI) Engine for CAMPS-ML.
Computes Shapley Additive exPlanations for XGBoost risk classifier.
Provides:
- Global feature importance (SHAP summary plot & bar plot)
- Local per-student explanations (top drivers increasing or decreasing risk)
- Serializes explainer to ml_engine/saved_models/shap_explainer.joblib
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
import joblib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "ml_engine" / "saved_models"
OUTPUT_DIR = BASE_DIR / "reports_output"
DATA_PATH = BASE_DIR / "data" / "synthetic" / "indian_college_student_data.csv"


def build_and_save_shap_explainer():
    """Extract fitted tree classifier, compute TreeSHAP values, and generate summary plots."""
    print("=" * 65)
    print("CAMPS-ML: Initializing TreeSHAP Explainability Engine")
    print("=" * 65)

    bundle = joblib.load(MODEL_DIR / "classifier_pipeline.joblib")
    pipeline = bundle["pipeline"]
    preprocessor = pipeline.named_steps["preprocessor"]
    xgb_clf = pipeline.named_steps["classifier"]

    df = pd.read_csv(DATA_PATH)
    features = bundle["num_features"] + bundle["cat_features"]
    X = df[features]

    # Transform feature matrix using fitted preprocessor
    X_transformed = preprocessor.transform(X)

    # Get feature names from ColumnTransformer
    cat_encoder = preprocessor.named_transformers_["cat"].named_steps["encoder"]
    encoded_cat_names = list(cat_encoder.get_feature_names_out(bundle["cat_features"]))
    feature_names = bundle["num_features"] + encoded_cat_names

    # Sample background dataset for TreeSHAP
    bg_sample = X_transformed[:300]
    explainer = shap.TreeExplainer(xgb_clf, data=bg_sample)

    print("[*] Computing SHAP values across test cohort...")
    test_sample = X_transformed[300:600]
    shap_values = explainer(test_sample)

    # 1. SHAP Summary Plot (For High Risk Class = index 2)
    # If multiclass, shap_values has shape (samples, features, classes)
    high_risk_shap = shap_values[:, :, 2] if len(shap_values.shape) == 3 else shap_values

    fig, ax = plt.subplots(figsize=(10, 6))
    shap.summary_plot(high_risk_shap.values, test_sample, feature_names=feature_names, show=False, max_display=12)
    plt.title("TreeSHAP Global Feature Attributions (High-Risk Dropout Class)", fontsize=13, fontweight="bold", pad=15)
    plt.tight_layout()
    summary_plot = OUTPUT_DIR / "shap_summary_plot.png"
    plt.savefig(summary_plot, dpi=300)
    plt.close()
    print(f"[+] Saved SHAP Summary Plot -> {summary_plot.name}")

    # 2. SHAP Global Bar Plot
    fig, ax = plt.subplots(figsize=(9, 5))
    shap.plots.bar(high_risk_shap, show=False, max_display=10)
    plt.title("Top 10 Global Academic Risk Factors (TreeSHAP Mean |Impact|)", fontsize=13, fontweight="bold", pad=15)
    plt.tight_layout()
    bar_plot = OUTPUT_DIR / "shap_bar_plot.png"
    plt.savefig(bar_plot, dpi=300)
    plt.close()
    print(f"[+] Saved SHAP Bar Plot -> {bar_plot.name}")

    # Save Explainer and Metadata
    explainer_bundle = {
        "explainer": explainer,
        "feature_names": feature_names,
        "preprocessor": preprocessor,
        "features": features
    }
    save_path = MODEL_DIR / "shap_explainer.joblib"
    joblib.dump(explainer_bundle, save_path)
    print(f"[+] Serialized TreeSHAP Explainer Bundle -> {save_path}")
    print("=" * 65)
    return explainer_bundle


def explain_student(student_dict):
    """
    Given a single student's dictionary of attributes, compute exact SHAP attributions
    and return human-readable top drivers explaining their academic risk level.
    """
    bundle = joblib.load(MODEL_DIR / "shap_explainer.joblib")
    preprocessor = bundle["preprocessor"]
    explainer = bundle["explainer"]
    feature_names = bundle["feature_names"]
    expected_features = bundle["features"]

    df_student = pd.DataFrame([student_dict])
    X_trans = preprocessor.transform(df_student[expected_features])
    sv = explainer(X_trans)

    # For high risk class (index 2)
    sv_high = sv.values[0, :, 2] if len(sv.values.shape) == 3 else sv.values[0]

    # Pair features with their SHAP contribution
    drivers = []
    for fname, val in zip(feature_names, sv_high):
        # Clean feature name
        clean_name = fname.replace("num__", "").replace("cat__", "").replace("_", " ")
        if abs(val) > 0.01:
            drivers.append({
                "feature": clean_name,
                "raw_value": str(student_dict.get(fname.split("__")[-1], "N/A")),
                "shap_impact": round(float(val), 4),
                "direction": "Increases Risk" if val > 0 else "Decreases Risk"
            })

    # Sort by absolute SHAP impact
    drivers.sort(key=lambda x: abs(x["shap_impact"]), reverse=True)
    return drivers[:5]


if __name__ == "__main__":
    build_and_save_shap_explainer()
