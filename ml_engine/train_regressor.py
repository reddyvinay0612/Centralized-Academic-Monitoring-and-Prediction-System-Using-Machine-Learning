"""
Machine Learning Continuous GPA Regression Pipeline for CAMPS-ML.
Implements DeJong & Karadogan 2024 methodology:
- Predicts next-semester continuous SGPA (3.5 to 10.0 scale)
- Compares Linear Regression, Ridge, Decision Tree, Random Forest, and Gradient Boosting Regressors
- Metrics: MAE, RMSE, R-squared (R2 >= 0.70)
- Serializes final model to ml_engine/saved_models/regressor_pipeline.joblib
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import joblib
from pathlib import Path

from sklearn.model_selection import train_test_split, cross_validate, KFold
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from sklearn.linear_model import LinearRegression, Ridge
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "synthetic" / "indian_college_student_data.csv"
MODEL_DIR = BASE_DIR / "ml_engine" / "saved_models"
OUTPUT_DIR = BASE_DIR / "reports_output"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def train_regressor():
    """Train and evaluate continuous SGPA regression models."""
    df = pd.read_csv(DATA_PATH)

    num_features = [
        "Attendance_Percentage", "CIE_IA1", "CIE_IA2", "CIE_IA3",
        "Assignment_Score", "Lab_Score", "Total_CIE",
        "Sem1_SGPA", "Sem2_SGPA", "Sem3_SGPA", "Sem4_SGPA", "Cumulative_CGPA",
        "Active_Backlogs", "10th_Percentage", "12th_Percentage", "Entrance_Rank"
    ]
    cat_features = ["Department", "Gender", "Category", "Fee_Status", "Scholarship"]

    X = df[num_features + cat_features]
    y = df["Target_Next_SGPA"].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler())
            ]), num_features),
            ("cat", Pipeline([
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
            ]), cat_features)
        ]
    )

    models = {
        "Linear Regression": LinearRegression(),
        "Ridge Regression": Ridge(alpha=1.0),
        "Decision Tree Regressor": DecisionTreeRegressor(max_depth=5, random_state=42),
        "Random Forest Regressor": RandomForestRegressor(n_estimators=120, max_depth=7, random_state=42),
        "Gradient Boosting Regressor": GradientBoostingRegressor(n_estimators=120, learning_rate=0.08, random_state=42)
    }

    print("\n" + "=" * 65)
    print("5-Fold Cross Validation: Next-Semester SGPA Regression")
    print("=" * 65)
    print(f"{'Model':<28} | {'MAE':<10} | {'RMSE':<10} | {'R2 Score'}")
    print("-" * 65)

    cv = KFold(n_splits=5, shuffle=True, random_state=42)
    best_model_name = None
    best_r2 = -float("inf")
    best_pipe = None

    for name, reg in models.items():
        pipe = Pipeline([
            ("preprocessor", preprocessor),
            ("regressor", reg)
        ])

        cv_res = cross_validate(pipe, X_train, y_train, cv=cv, scoring=["neg_mean_absolute_error", "neg_root_mean_squared_error", "r2"])
        mae = -cv_res["test_neg_mean_absolute_error"].mean()
        rmse = -cv_res["test_neg_root_mean_squared_error"].mean()
        r2 = cv_res["test_r2"].mean()

        print(f"{name:<28} | {mae:.4f}     | {rmse:.4f}     | {r2:.4f}")

        if r2 > best_r2:
            best_r2 = r2
            best_model_name = name
            best_pipe = pipe

    print("=" * 65)

    # Train best pipeline on full training set and evaluate on test split
    best_pipe.fit(X_train, y_train)
    y_pred = best_pipe.predict(X_test)

    test_mae = mean_absolute_error(y_test, y_pred)
    test_rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    test_r2 = r2_score(y_test, y_pred)

    print(f"\n[+] Selected Best Regressor: {best_model_name}")
    print(f"[*] Test Set MAE:  {test_mae:.4f} SGPA points")
    print(f"[*] Test Set RMSE: {test_rmse:.4f}")
    print(f"[*] Test Set R2:   {test_r2:.4f} (DeJong et al. achieved R2 ~0.67)")

    # Plot Actual vs Predicted SGPA
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.scatter(y_test, y_pred, alpha=0.6, color="#0d6efd", edgecolors="k", s=40)
    ax.plot([3.5, 10], [3.5, 10], "r--", lw=2, label="Perfect Line of Equality")
    ax.set_title(f"Actual vs Predicted Next-Semester SGPA\n({best_model_name}, R2 = {test_r2:.2f})", fontsize=12, fontweight="bold")
    ax.set_xlabel("Actual SGPA", fontsize=11)
    ax.set_ylabel("Predicted SGPA", fontsize=11)
    ax.legend(loc="upper left")
    plt.tight_layout()
    reg_plot = OUTPUT_DIR / "regression_actual_vs_predicted.png"
    plt.savefig(reg_plot, dpi=300)
    plt.close()
    print(f"[+] Saved Regression Calibration Plot -> {reg_plot.name}")

    # Serialize Regressor Bundle
    bundle = {
        "pipeline": best_pipe,
        "num_features": num_features,
        "cat_features": cat_features,
        "metrics": {
            "test_mae": test_mae,
            "test_rmse": test_rmse,
            "test_r2": test_r2
        }
    }
    model_save_path = MODEL_DIR / "regressor_pipeline.joblib"
    joblib.dump(bundle, model_save_path)
    print(f"[+] Serialized Best Regressor Pipeline -> {model_save_path}")

    return best_pipe


if __name__ == "__main__":
    train_regressor()
