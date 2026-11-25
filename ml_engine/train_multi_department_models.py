"""
Centralized Academic Monitoring and Prediction System (CAMPS-ML)
PES Institute of Technology & Management (PESITM), Shivamogga

Multi-Department Machine Learning Training & Evaluation Pipeline
Dataset: Real & Calibrated PESITM Semester 1-6 Master Dataset (644 Students across 9 Departments)
Departments: CSE, ISE, ECE, EEE, ME, CV, CSD, CE, AIML
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

from sklearn.model_selection import StratifiedKFold, KFold, cross_validate, train_test_split
from sklearn.preprocessing import StandardScaler, RobustScaler, LabelEncoder
from sklearn.impute import SimpleImputer
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
DATA_PATH = BASE_DIR / "data" / "processed" / "pesitm_multi_department_master.csv"
MODEL_DIR = BASE_DIR / "ml_engine" / "saved_models"
OUTPUT_DIR = BASE_DIR / "reports_output"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_and_preprocess_master():
    df = pd.read_csv(DATA_PATH)
    print(f"[*] Loaded Master Multi-Department Dataset: {df.shape[0]} students across {df['department'].nunique()} departments.")

    # 1. Feature Engineering
    df['is_lateral_entry'] = df['Sem1_SGPA'].isna().astype(int)
    df['Sem1_SGPA_clean'] = df['Sem1_SGPA'].fillna(df['cgpa'])
    df['Sem2_SGPA_clean'] = df['Sem2_SGPA'].fillna(df['cgpa'])

    # Trajectory features
    df['sgpa_trend'] = df['Sem5_SGPA'] - df['Sem4_SGPA']
    df['cgpa_deviation'] = df['Sem5_SGPA'] - df['cgpa']
    df['internal_ratio'] = df['Sem5_internal_pct'] / (df['cgpa'] * 10.0 + 1e-5)

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
    # Module 1: Pass/Fail (Sem6 failed subjects == 0 -> 1/PASS, >0 -> 0/FAIL)
    y_pass_fail = (df['Sem6_failed_subjects'] == 0).astype(int)

    # Module 2: Risk Level (0: Low, 1: Medium, 2: High)
    risk_mapping = {'Low': 0, 'Medium': 1, 'High': 2}
    y_risk = df['risk_level'].map(risk_mapping)

    # Module 3: Continuous Regression (Sem6 SGPA & Sem6 Avg Total Marks)
    y_sgpa = df['Sem6_SGPA'].astype(float)
    y_marks = df['Sem6_avg_total'].astype(float)

    # Module 4: Marks Range Category
    range_encoder = LabelEncoder()
    y_range = range_encoder.fit_transform(df['predicted_next_sem_marks_range'])

    return {
        'df': df,
        'X': X,
        'feature_cols': feature_cols,
        'y_pass_fail': y_pass_fail,
        'y_risk': y_risk,
        'y_sgpa': y_sgpa,
        'y_marks': y_marks,
        'y_range': y_range,
        'range_encoder': range_encoder
    }

def train_module_1_pass_fail(X, y):
    print("\n" + "="*80)
    print(" MODULE 1: PASS / FAIL CLASSIFIER BENCHMARK (5-FOLD STRATIFIED CV)")
    print("="*80)

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    models = {
        'Logistic Regression': Pipeline([
            ('scaler', StandardScaler()),
            ('clf', LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42))
        ]),
        'Decision Tree': DecisionTreeClassifier(max_depth=5, class_weight='balanced', random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=150, max_depth=6, class_weight='balanced', random_state=42),
        'Extra Trees': ExtraTreesClassifier(n_estimators=150, max_depth=6, class_weight='balanced', random_state=42),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, learning_rate=0.08, max_depth=3, random_state=42),
        'XGBoost': XGBClassifier(
            n_estimators=120, learning_rate=0.08, max_depth=4,
            scale_pos_weight=len(y[y==1])/max(1, len(y[y==0])),
            eval_metric='logloss', random_state=42
        )
    }

    results = {}
    best_name = None
    best_f1 = -1

    for name, model in models.items():
        scoring = ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']
        cv_res = cross_validate(model, X, y, cv=skf, scoring=scoring)

        acc = cv_res['test_accuracy'].mean()
        prec = cv_res['test_precision'].mean()
        rec = cv_res['test_recall'].mean()
        f1 = cv_res['test_f1'].mean()
        auc = cv_res['test_roc_auc'].mean()

        results[name] = {
            'accuracy': round(acc * 100, 2),
            'precision': round(prec * 100, 2),
            'recall': round(rec * 100, 2),
            'f1_score': round(f1 * 100, 2),
            'roc_auc': round(auc, 4)
        }

        print(f"  {name:<22} | Acc: {acc*100:6.2f}% | Prec: {prec*100:6.2f}% | Rec: {rec*100:6.2f}% | F1: {f1*100:6.2f}% | AUC: {auc:6.4f}")

        if f1 > best_f1:
            best_f1 = f1
            best_name = name

    print(f"\n[★] Champion Pass/Fail Model: {best_name} (F1 Score: {best_f1*100:.2f}%)")

    # Fit champion on full dataset and save
    champion = models[best_name]
    champion.fit(X, y)
    save_path = MODEL_DIR / "pesitm_sem6_pass_fail_champion.joblib"
    joblib.dump({
        'model': champion,
        'model_name': best_name,
        'metrics': results[best_name],
        'feature_names': list(X.columns)
    }, save_path)

    # Legacy fallback save
    joblib.dump(champion, MODEL_DIR / "pass_fail_classifier.joblib")
    print(f"    Saved champion model to: {save_path}")

    return best_name, results

def train_module_2_risk_level(X, y):
    print("\n" + "="*80)
    print(" MODULE 2: ACADEMIC RISK LEVEL CLASSIFIER (LOW / MEDIUM / HIGH)")
    print("="*80)

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    models = {
        'Random Forest': RandomForestClassifier(n_estimators=150, max_depth=6, class_weight='balanced', random_state=42),
        'Extra Trees': ExtraTreesClassifier(n_estimators=150, max_depth=6, class_weight='balanced', random_state=42),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, learning_rate=0.08, max_depth=3, random_state=42),
        'XGBoost': XGBClassifier(n_estimators=120, learning_rate=0.08, max_depth=4, eval_metric='mlogloss', random_state=42)
    }

    results = {}
    best_name = None
    best_acc = -1

    for name, model in models.items():
        scoring = ['accuracy', 'f1_macro', 'f1_weighted']
        cv_res = cross_validate(model, X, y, cv=skf, scoring=scoring)

        acc = cv_res['test_accuracy'].mean()
        f1_mac = cv_res['test_f1_macro'].mean()
        f1_wgt = cv_res['test_f1_weighted'].mean()

        results[name] = {
            'accuracy': round(acc * 100, 2),
            'macro_f1': round(f1_mac * 100, 2),
            'weighted_f1': round(f1_wgt * 100, 2)
        }

        print(f"  {name:<22} | Accuracy: {acc*100:6.2f}% | Macro F1: {f1_mac*100:6.2f}% | Weighted F1: {f1_wgt*100:6.2f}%")

        if acc > best_acc:
            best_acc = acc
            best_name = name

    print(f"\n[★] Champion Risk Model: {best_name} (Accuracy: {best_acc*100:.2f}%)")

    champion = models[best_name]
    champion.fit(X, y)
    save_path = MODEL_DIR / "pesitm_sem6_risk_classifier_champion.joblib"
    joblib.dump({
        'model': champion,
        'model_name': best_name,
        'metrics': results[best_name],
        'feature_names': list(X.columns),
        'target_classes': ['Low', 'Medium', 'High']
    }, save_path)
    joblib.dump(champion, MODEL_DIR / "classifier_pipeline.joblib")
    print(f"    Saved champion model to: {save_path}")

    return best_name, results

def train_module_3_sgpa_regressor(X, y_sgpa, y_marks):
    print("\n" + "="*80)
    print(" MODULE 3: SEMESTER SGPA & TOTAL MARKS REGRESSOR")
    print("="*80)

    kf = KFold(n_splits=5, shuffle=True, random_state=42)

    models = {
        'Ridge Regressor': Pipeline([('scaler', StandardScaler()), ('reg', Ridge(alpha=1.0))]),
        'Lasso Regressor': Pipeline([('scaler', StandardScaler()), ('reg', Lasso(alpha=0.01))]),
        'Random Forest': RandomForestRegressor(n_estimators=150, max_depth=6, random_state=42),
        'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, learning_rate=0.08, max_depth=3, random_state=42),
        'XGBoost Regressor': XGBRegressor(n_estimators=120, learning_rate=0.08, max_depth=4, random_state=42)
    }

    results = {}
    best_name = None
    best_r2 = -999

    for name, model in models.items():
        scoring = ['r2', 'neg_mean_absolute_error', 'neg_root_mean_squared_error']
        cv_res = cross_validate(model, X, y_sgpa, cv=kf, scoring=scoring)

        r2 = cv_res['test_r2'].mean()
        mae = -cv_res['test_neg_mean_absolute_error'].mean()
        rmse = -cv_res['test_neg_root_mean_squared_error'].mean()

        results[name] = {
            'r2_score': round(r2, 4),
            'mae': round(mae, 4),
            'rmse': round(rmse, 4)
        }

        print(f"  {name:<22} | R² Score: {r2:6.4f} | MAE: ±{mae:5.3f} SGPA | RMSE: {rmse:5.3f}")

        if r2 > best_r2:
            best_r2 = r2
            best_name = name

    print(f"\n[★] Champion SGPA Regressor: {best_name} (R²: {best_r2:.4f})")

    # Fit champions
    champion_sgpa = models[best_name]
    champion_sgpa.fit(X, y_sgpa)

    # Train marks regressor using same champion architecture
    champion_marks = Pipeline([('scaler', StandardScaler()), ('reg', Ridge(alpha=1.0))]) if 'Ridge' in best_name else RandomForestRegressor(n_estimators=150, max_depth=6, random_state=42)
    champion_marks.fit(X, y_marks)

    save_path = MODEL_DIR / "pesitm_sem6_regressor_champion.joblib"
    joblib.dump({
        'sgpa_model': champion_sgpa,
        'marks_model': champion_marks,
        'model_name': best_name,
        'metrics': results[best_name],
        'feature_names': list(X.columns)
    }, save_path)
    joblib.dump(champion_sgpa, MODEL_DIR / "regressor_pipeline.joblib")
    print(f"    Saved champion model to: {save_path}")

    return best_name, results

def train_module_4_marks_range(X, y_range, encoder):
    print("\n" + "="*80)
    print(" MODULE 4: SEMESTER MARKS RANGE BAND CLASSIFIER")
    print("="*80)

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    models = {
        'Random Forest': RandomForestClassifier(n_estimators=150, max_depth=6, random_state=42),
        'Extra Trees': ExtraTreesClassifier(n_estimators=150, max_depth=6, random_state=42),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, learning_rate=0.08, max_depth=3, random_state=42),
        'XGBoost': XGBClassifier(n_estimators=120, learning_rate=0.08, max_depth=4, eval_metric='mlogloss', random_state=42)
    }

    results = {}
    best_name = None
    best_acc = -1

    for name, model in models.items():
        scoring = ['accuracy', 'f1_weighted']
        cv_res = cross_validate(model, X, y_range, cv=skf, scoring=scoring)

        acc = cv_res['test_accuracy'].mean()
        f1 = cv_res['test_f1_weighted'].mean()

        results[name] = {
            'accuracy': round(acc * 100, 2),
            'weighted_f1': round(f1 * 100, 2)
        }

        print(f"  {name:<22} | Band Accuracy: {acc*100:6.2f}% | Weighted F1: {f1*100:6.2f}%")

        if acc > best_acc:
            best_acc = acc
            best_name = name

    print(f"\n[★] Champion Marks Range Model: {best_name} (Accuracy: {best_acc*100:.2f}%)")

    champion = models[best_name]
    champion.fit(X, y_range)
    save_path = MODEL_DIR / "pesitm_sem6_range_classifier_champion.joblib"
    joblib.dump({
        'model': champion,
        'model_name': best_name,
        'encoder': encoder,
        'metrics': results[best_name],
        'feature_names': list(X.columns),
        'classes': list(encoder.classes_)
    }, save_path)
    print(f"    Saved champion model to: {save_path}")

    return best_name, results

def run_all_training():
    print("="*80)
    print(" PESITM MULTI-DEPARTMENT ML MODEL TRAINING ENGINE")
    print("="*80)

    data = load_and_preprocess_master()
    X = data['X']

    m1_name, m1_res = train_module_1_pass_fail(X, data['y_pass_fail'])
    m2_name, m2_res = train_module_2_risk_level(X, data['y_risk'])
    m3_name, m3_res = train_module_3_sgpa_regressor(X, data['y_sgpa'], data['y_marks'])
    m4_name, m4_res = train_module_4_marks_range(X, data['y_range'], data['range_encoder'])

    summary = {
        'total_samples': len(X),
        'total_departments': int(data['df']['department'].nunique()),
        'departments': list(data['df']['department'].unique()),
        'module_1_pass_fail': {'champion': m1_name, 'benchmarks': m1_res},
        'module_2_risk_level': {'champion': m2_name, 'benchmarks': m2_res},
        'module_3_sgpa_regressor': {'champion': m3_name, 'benchmarks': m3_res},
        'module_4_marks_range': {'champion': m4_name, 'benchmarks': m4_res}
    }

    report_path = OUTPUT_DIR / "pesitm_multi_department_ml_benchmarks.json"
    with open(report_path, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"\n[✓] Complete multi-department training benchmarks exported to: {report_path}")

if __name__ == '__main__':
    run_all_training()
