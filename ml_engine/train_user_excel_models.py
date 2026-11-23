"""
Centralized Academic Monitoring and Prediction System (CAMPS-ML)
PES Institute of Technology & Management (PESITM), Shivamogga

Multi-Module Machine Learning Training & Evaluation Pipeline
Dataset: Real PESITM Semester 1-6 Student Performance Dataset (131 Students)
"""

import os
import sys
from pathlib import Path
import json
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import joblib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import StratifiedKFold, KFold, cross_validate, train_test_split
from sklearn.preprocessing import StandardScaler, RobustScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report,
    mean_absolute_error, mean_squared_error, r2_score
)

# Classifiers
from sklearn.linear_model import LogisticRegression, RidgeClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, ExtraTreesClassifier
from xgboost import XGBClassifier

# Regressors
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor
from xgboost import XGBRegressor

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "processed" / "pesitm_sem6_students_evaluation.csv"
MODEL_DIR = BASE_DIR / "ml_engine" / "saved_models"
OUTPUT_DIR = BASE_DIR / "reports_output"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_and_preprocess_data():
    """
    Loads and preprocesses student evaluation records.
    Strictly excludes Sem 6 columns from features to prevent data leakage.
    """
    df = pd.read_csv(DATA_PATH)
    print(f"[*] Loaded dataset: {df.shape[0]} students, {df.shape[1]} raw columns.")

    # 1. Feature Engineering
    # Identify lateral entry students (Sem 1 and Sem 2 blank)
    df['is_lateral_entry'] = df['Sem1_SGPA'].isna().astype(int)

    # Impute missing Sem 1 & Sem 2 SGPA with CGPA (their actual cumulative academic level)
    df['Sem1_SGPA_clean'] = df['Sem1_SGPA'].fillna(df['cgpa'])
    df['Sem2_SGPA_clean'] = df['Sem2_SGPA'].fillna(df['cgpa'])

    # Academic trajectory features
    df['sgpa_trend'] = df['Sem5_SGPA'] - df['Sem4_SGPA']
    df['cgpa_deviation'] = df['Sem5_SGPA'] - df['cgpa']
    df['internal_ratio'] = df['Sem5_internal_pct'] / (df['cgpa'] * 10.0 + 1e-5)

    # Feature columns (Past measures up to Sem 5 only)
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

    X = df[feature_cols].copy()

    # Targets:
    # Module 1: Binary Pass/Fail (Sem6 failed subjects == 0 -> 1/PASS, > 0 -> 0/FAIL)
    y_pass_fail = (df['Sem6_failed_subjects'] == 0).astype(int)

    # Module 2: Multi-class Risk Level ('Low': 0, 'Medium': 1, 'High': 2)
    risk_map = {'Low': 0, 'Medium': 1, 'High': 2}
    y_risk = df['risk_level'].map(risk_map)

    # Module 3: Continuous Targets (Sem6 Average Total /100 & Sem6 SGPA)
    y_sem6_total = df['Sem6_avg_total'].astype(float)
    y_sem6_sgpa = df['Sem6_SGPA'].astype(float)

    # Module 4: Binned Marks Range ('50-60', '60-70', '70-80', '80-90', '90-100')
    range_order = ['50-60', '60-70', '70-80', '80-90', '90-100']
    range_map = {k: i for i, k in enumerate(range_order)}
    y_range = df['predicted_next_sem_marks_range'].map(range_map)

    return df, X, feature_cols, y_pass_fail, y_risk, y_sem6_total, y_sem6_sgpa, y_range, risk_map, range_order


# =========================================================================
# MODULE 1: PASS / FAIL PREDICTION (BINARY CLASSIFICATION)
# =========================================================================
def evaluate_module_1(X, y, feature_cols):
    print("\n" + "=" * 70)
    print("MODULE 1: PASS / FAIL CLASSIFIER (5-Fold Stratified Cross Validation)")
    print("=" * 70)
    print(f"Target Distribution: PASS (0 backlogs in Sem 6) = {sum(y == 1)}, FAIL (>=1 backlog) = {sum(y == 0)}")

    models = {
        "XGBoost Classifier": XGBClassifier(
            n_estimators=100, max_depth=4, learning_rate=0.05,
            scale_pos_weight=(sum(y == 0) / max(1, sum(y == 1))),
            random_state=42, eval_metric="logloss"
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=100, max_depth=5, class_weight="balanced", random_state=42
        ),
        "Gradient Boosting": GradientBoostingClassifier(
            n_estimators=100, learning_rate=0.05, max_depth=3, random_state=42
        ),
        "Decision Tree": DecisionTreeClassifier(
            max_depth=4, class_weight="balanced", random_state=42
        ),
        "Logistic Regression": Pipeline([
            ('scaler', StandardScaler()),
            ('clf', LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42))
        ])
    }

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    results = {}

    for name, model in models.items():
        acc_list, prec_list, rec_list, f1_list, auc_list = [], [], [], [], []

        for train_idx, test_idx in skf.split(X, y):
            X_tr, X_te = X.iloc[train_idx], X.iloc[test_idx]
            y_tr, y_te = y.iloc[train_idx], y.iloc[test_idx]

            model.fit(X_tr, y_tr)
            y_pred = model.predict(X_te)

            if hasattr(model, "predict_proba"):
                y_prob = model.predict_proba(X_te)[:, 1]
            elif hasattr(model, "decision_function"):
                y_prob = model.decision_function(X_te)
            else:
                y_prob = y_pred

            acc_list.append(accuracy_score(y_te, y_pred))
            prec_list.append(precision_score(y_te, y_pred, zero_division=0))
            rec_list.append(recall_score(y_te, y_pred, zero_division=0))
            f1_list.append(f1_score(y_te, y_pred, zero_division=0))
            try:
                auc_list.append(roc_auc_score(y_te, y_prob))
            except:
                auc_list.append(0.5)

        results[name] = {
            "Accuracy": np.mean(acc_list),
            "Precision": np.mean(prec_list),
            "Recall": np.mean(rec_list),
            "F1_Score": np.mean(f1_list),
            "ROC_AUC": np.mean(auc_list)
        }

    res_df = pd.DataFrame(results).T.sort_values(by="F1_Score", ascending=False)
    print(res_df.to_string(formatters={
        'Accuracy': '{:.2%}'.format,
        'Precision': '{:.2%}'.format,
        'Recall': '{:.2%}'.format,
        'F1_Score': '{:.2%}'.format,
        'ROC_AUC': '{:.4f}'.format
    }))

    # Fit Champion model on entire dataset for production serving
    champion_name = res_df.index[0]
    champion_model = models[champion_name]
    champion_model.fit(X, y)
    print(f"\n[+] Champion Model Selected: {champion_name} (Accuracy: {res_df.loc[champion_name, 'Accuracy']:.2%}, F1: {res_df.loc[champion_name, 'F1_Score']:.2%})")

    # Save artifact bundle
    bundle = {
        "model": champion_model,
        "feature_cols": feature_cols,
        "champion_name": champion_name,
        "metrics": results[champion_name],
        "all_model_results": results
    }
    joblib.dump(bundle, MODEL_DIR / "pesitm_sem6_pass_fail_champion.joblib")
    return res_df, champion_model


# =========================================================================
# MODULE 2: ACADEMIC RISK LEVEL CLASSIFIER (MULTI-CLASS)
# =========================================================================
def evaluate_module_2(X, y, feature_cols, risk_map):
    print("\n" + "=" * 70)
    print("MODULE 2: ACADEMIC RISK LEVEL PREDICTOR (Multi-Class: Low, Medium, High)")
    print("=" * 70)
    rev_risk_map = {v: k for k, v in risk_map.items()}
    counts = y.value_counts().to_dict()
    print("Target Counts:", {rev_risk_map[k]: v for k, v in counts.items()})

    models = {
        "XGBoost Multi-Class": XGBClassifier(
            n_estimators=100, max_depth=4, learning_rate=0.05,
            objective="multi:softprob", num_class=3, random_state=42
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=100, max_depth=5, class_weight="balanced", random_state=42
        ),
        "Gradient Boosting": GradientBoostingClassifier(
            n_estimators=80, learning_rate=0.05, max_depth=3, random_state=42
        ),
        "Extra Trees": ExtraTreesClassifier(
            n_estimators=100, max_depth=5, class_weight="balanced", random_state=42
        ),
        "Logistic Regression": Pipeline([
            ('scaler', StandardScaler()),
            ('clf', LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42))
        ])
    }

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    results = {}

    for name, model in models.items():
        acc_list, f1_macro_list, f1_weighted_list = [], [], []

        for train_idx, test_idx in skf.split(X, y):
            X_tr, X_te = X.iloc[train_idx], X.iloc[test_idx]
            y_tr, y_te = y.iloc[train_idx], y.iloc[test_idx]

            model.fit(X_tr, y_tr)
            y_pred = model.predict(X_te)

            acc_list.append(accuracy_score(y_te, y_pred))
            f1_macro_list.append(f1_score(y_te, y_pred, average="macro", zero_division=0))
            f1_weighted_list.append(f1_score(y_te, y_pred, average="weighted", zero_division=0))

        results[name] = {
            "Accuracy": np.mean(acc_list),
            "F1_Macro": np.mean(f1_macro_list),
            "F1_Weighted": np.mean(f1_weighted_list)
        }

    res_df = pd.DataFrame(results).T.sort_values(by="F1_Macro", ascending=False)
    print(res_df.to_string(formatters={
        'Accuracy': '{:.2%}'.format,
        'F1_Macro': '{:.2%}'.format,
        'F1_Weighted': '{:.2%}'.format
    }))

    champion_name = res_df.index[0]
    champion_model = models[champion_name]
    champion_model.fit(X, y)
    print(f"\n[+] Champion Model Selected: {champion_name} (Accuracy: {res_df.loc[champion_name, 'Accuracy']:.2%}, Macro F1: {res_df.loc[champion_name, 'F1_Macro']:.2%})")

    bundle = {
        "model": champion_model,
        "feature_cols": feature_cols,
        "champion_name": champion_name,
        "risk_map": risk_map,
        "metrics": results[champion_name],
        "all_model_results": results
    }
    joblib.dump(bundle, MODEL_DIR / "pesitm_sem6_risk_classifier_champion.joblib")
    return res_df, champion_model


# =========================================================================
# MODULE 3: CONTINUOUS PERFORMANCE REGRESSOR (SEM6 AVERAGE TOTAL & SGPA)
# =========================================================================
def evaluate_module_3(X, y_total, y_sgpa, feature_cols):
    print("\n" + "=" * 70)
    print("MODULE 3: NEXT-SEMESTER CONTINUOUS MARKS & SGPA REGRESSOR (5-Fold CV)")
    print("=" * 70)

    models_total = {
        "Ridge Regressor": Pipeline([('scaler', StandardScaler()), ('reg', Ridge(alpha=1.0))]),
        "Random Forest Regressor": RandomForestRegressor(n_estimators=100, max_depth=5, random_state=42),
        "Gradient Boosting Regressor": GradientBoostingRegressor(n_estimators=80, learning_rate=0.05, max_depth=3, random_state=42),
        "XGBoost Regressor": XGBRegressor(n_estimators=100, max_depth=3, learning_rate=0.05, random_state=42),
        "Linear Regression": Pipeline([('scaler', StandardScaler()), ('reg', LinearRegression())])
    }

    kf = KFold(n_splits=5, shuffle=True, random_state=42)

    # 1. Predicting Sem 6 Average Total (/100)
    print("\n--- Sub-Module 3A: Predicting Sem 6 Average Total Score (/100) ---")
    results_total = {}
    for name, model in models_total.items():
        r2_list, mae_list, rmse_list = [], [], []
        for train_idx, test_idx in kf.split(X):
            X_tr, X_te = X.iloc[train_idx], X.iloc[test_idx]
            y_tr, y_te = y_total.iloc[train_idx], y_total.iloc[test_idx]

            model.fit(X_tr, y_tr)
            y_pred = model.predict(X_te)

            r2_list.append(r2_score(y_te, y_pred))
            mae_list.append(mean_absolute_error(y_te, y_pred))
            rmse_list.append(np.sqrt(mean_squared_error(y_te, y_pred)))

        results_total[name] = {
            "R2_Score": np.mean(r2_list),
            "MAE (Marks)": np.mean(mae_list),
            "RMSE (Marks)": np.mean(rmse_list)
        }

    res_total_df = pd.DataFrame(results_total).T.sort_values(by="R2_Score", ascending=False)
    print(res_total_df.to_string(formatters={
        'R2_Score': '{:.4f}'.format,
        'MAE (Marks)': '{:.2f}'.format,
        'RMSE (Marks)': '{:.2f}'.format
    }))

    # 2. Predicting Sem 6 SGPA (0.0 to 10.0 scale)
    print("\n--- Sub-Module 3B: Predicting Sem 6 SGPA (10-Point Scale) ---")
    results_sgpa = {}
    for name, model in models_total.items():
        r2_list, mae_list, rmse_list = [], [], []
        for train_idx, test_idx in kf.split(X):
            X_tr, X_te = X.iloc[train_idx], X.iloc[test_idx]
            y_tr, y_te = y_sgpa.iloc[train_idx], y_sgpa.iloc[test_idx]

            model.fit(X_tr, y_tr)
            y_pred = model.predict(X_te)

            r2_list.append(r2_score(y_te, y_pred))
            mae_list.append(mean_absolute_error(y_te, y_pred))
            rmse_list.append(np.sqrt(mean_squared_error(y_te, y_pred)))

        results_sgpa[name] = {
            "R2_Score": np.mean(r2_list),
            "MAE (SGPA)": np.mean(mae_list),
            "RMSE (SGPA)": np.mean(rmse_list)
        }

    res_sgpa_df = pd.DataFrame(results_sgpa).T.sort_values(by="R2_Score", ascending=False)
    print(res_sgpa_df.to_string(formatters={
        'R2_Score': '{:.4f}'.format,
        'MAE (SGPA)': '{:.3f}'.format,
        'RMSE (SGPA)': '{:.3f}'.format
    }))

    # Fit Champion for Sem6 Total
    champ_total_name = res_total_df.index[0]
    champ_total_model = models_total[champ_total_name]
    champ_total_model.fit(X, y_total)

    bundle = {
        "model_total": champ_total_model,
        "feature_cols": feature_cols,
        "metrics_total": results_total[champ_total_name],
        "metrics_sgpa": results_sgpa[champ_total_name]
    }
    joblib.dump(bundle, MODEL_DIR / "pesitm_sem6_regressor_champion.joblib")
    return res_total_df, res_sgpa_df, champ_total_model


# =========================================================================
# MODULE 4: PREDICTED NEXT-SEMESTER MARKS RANGE (10-MARK BANDS)
# =========================================================================
def evaluate_module_4(X, y, feature_cols, range_order):
    print("\n" + "=" * 70)
    print("MODULE 4: PREDICTED NEXT-SEMESTER MARKS RANGE (50-60, 60-70, 70-80, 80-90, 90-100)")
    print("=" * 70)
    print("Marks Range Distribution:", dict(pd.Series([range_order[i] for i in y]).value_counts()))

    models = {
        "XGBoost Classifier": XGBClassifier(
            n_estimators=100, max_depth=3, learning_rate=0.05,
            objective="multi:softprob", num_class=len(range_order), random_state=42
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=100, max_depth=5, class_weight="balanced", random_state=42
        ),
        "Gradient Boosting": GradientBoostingClassifier(
            n_estimators=80, learning_rate=0.05, max_depth=3, random_state=42
        ),
        "Logistic Regression": Pipeline([
            ('scaler', StandardScaler()),
            ('clf', LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42))
        ])
    }

    # Stratified KFold requires at least 2 samples per class, class 90-100 has 1 sample
    # We use StratifiedKFold with k=3 or standard KFold with k=5
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    results = {}

    for name, model in models.items():
        exact_acc_list, adjacent_acc_list, f1_list = [], [], []

        for train_idx, test_idx in kf.split(X):
            X_tr, X_te = X.iloc[train_idx], X.iloc[test_idx]
            y_tr, y_te = y.iloc[train_idx], y.iloc[test_idx]

            model.fit(X_tr, y_tr)
            y_pred = model.predict(X_te)

            # Exact match accuracy
            exact_acc_list.append(accuracy_score(y_te, y_pred))

            # Adjacent band accuracy (tolerates off-by-one 10-mark band)
            adj_acc = np.mean(np.abs(y_te - y_pred) <= 1)
            adjacent_acc_list.append(adj_acc)

            f1_list.append(f1_score(y_te, y_pred, average="weighted", zero_division=0))

        results[name] = {
            "Exact_Accuracy": np.mean(exact_acc_list),
            "Adjacent_Band_Acc (±1 Band)": np.mean(adjacent_acc_list),
            "F1_Weighted": np.mean(f1_list)
        }

    res_df = pd.DataFrame(results).T.sort_values(by="Exact_Accuracy", ascending=False)
    print(res_df.to_string(formatters={
        'Exact_Accuracy': '{:.2%}'.format,
        'Adjacent_Band_Acc (±1 Band)': '{:.2%}'.format,
        'F1_Weighted': '{:.2%}'.format
    }))

    champion_name = res_df.index[0]
    champion_model = models[champion_name]
    champion_model.fit(X, y)

    bundle = {
        "model": champion_model,
        "feature_cols": feature_cols,
        "range_order": range_order,
        "metrics": results[champion_name]
    }
    joblib.dump(bundle, MODEL_DIR / "pesitm_sem6_range_classifier_champion.joblib")
    return res_df, champion_model


def main():
    print("=" * 80)
    print("CAMPS-ML: PESITM INSTITUTIONAL DATASET MULTI-MODULE TRAINING & BENCHMARKING")
    print("=" * 80)

    df, X, feature_cols, y_pass_fail, y_risk, y_sem6_total, y_sem6_sgpa, y_range, risk_map, range_order = load_and_preprocess_data()

    # Module 1: Pass/Fail Classifier
    m1_df, m1_model = evaluate_module_1(X, y_pass_fail, feature_cols)

    # Module 2: Academic Risk Level
    m2_df, m2_model = evaluate_module_2(X, y_risk, feature_cols, risk_map)

    # Module 3: Continuous Marks & SGPA Regressor
    m3a_df, m3b_df, m3_model = evaluate_module_3(X, y_sem6_total, y_sem6_sgpa, feature_cols)

    # Module 4: Marks Range Predictor
    m4_df, m4_model = evaluate_module_4(X, y_range, feature_cols, range_order)

    # Compile comprehensive summary report
    summary = {
        "dataset": {
            "total_students": len(df),
            "semesters_analyzed": "Sem 1 to Sem 6",
            "features_used": feature_cols
        },
        "module_1_pass_fail": m1_df.to_dict(orient="index"),
        "module_2_risk_level": m2_df.to_dict(orient="index"),
        "module_3a_sem6_total_marks": m3a_df.to_dict(orient="index"),
        "module_3b_sem6_sgpa": m3b_df.to_dict(orient="index"),
        "module_4_marks_range": m4_df.to_dict(orient="index")
    }

    with open(OUTPUT_DIR / "pesitm_multi_module_benchmark_metrics.json", "w") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 80)
    print("ALL MODULES SUCCESSFULLY TRAINED, EVALUATED, AND SERIALIZED!")
    print(f"Metrics saved to: {OUTPUT_DIR / 'pesitm_multi_module_benchmark_metrics.json'}")
    print("=" * 80)

if __name__ == "__main__":
    main()
