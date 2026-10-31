"""
Comprehensive Machine Learning Classification Pipeline for CAMPS-ML.
Implements Islam et al. 2024 methodology:
- Stratified 80/20 train/test split (no data leakage)
- Quantile / Robust normalization & OneHotEncoding
- Imbalance handling: SMOTE strictly on training fold via imblearn Pipeline
- 5-Fold Cross Validation comparing LR, DT, RF, GB, and XGBoost
- Evaluation: Accuracy, Macro Precision, Macro Recall, Macro F1, ROC-AUC
- Hyperparameter tuning for XGBoost
- Serialization to ml_engine/saved_models/classifier_pipeline.joblib
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import joblib
from pathlib import Path

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate, GridSearchCV
from sklearn.preprocessing import StandardScaler, QuantileTransformer, OneHotEncoder, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, accuracy_score, f1_score

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from xgboost import XGBClassifier
from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.over_sampling import SMOTE

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "synthetic" / "indian_college_student_data.csv"
MODEL_DIR = BASE_DIR / "ml_engine" / "saved_models"
OUTPUT_DIR = BASE_DIR / "reports_output"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_and_prepare_data():
    """Load dataset and separate features and target."""
    df = pd.read_csv(DATA_PATH)

    # Feature definitions
    num_features = [
        "Attendance_Percentage", "CIE_IA1", "CIE_IA2", "CIE_IA3",
        "Assignment_Score", "Lab_Score", "Total_CIE",
        "Sem1_SGPA", "Sem2_SGPA", "Sem3_SGPA", "Sem4_SGPA", "Cumulative_CGPA",
        "Active_Backlogs", "10th_Percentage", "12th_Percentage", "Entrance_Rank",
        "Fee_Due_Amount"
    ]
    cat_features = ["Department", "Gender", "Category", "Fee_Status", "Scholarship"]

    X = df[num_features + cat_features]
    y_raw = df["Target_Risk"]

    # Target Label Encoding: Low -> 0, Medium -> 1, High -> 2
    label_mapping = {"Low": 0, "Medium": 1, "High": 2}
    reverse_mapping = {0: "Low", 1: "Medium", 2: "High"}
    y = y_raw.map(label_mapping).values

    return X, y, num_features, cat_features, label_mapping, reverse_mapping


def build_preprocessor(num_features, cat_features):
    """Construct ColumnTransformer for numerical scaling and categorical encoding."""
    num_transformer = ImbPipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", QuantileTransformer(output_distribution="normal", random_state=42))
    ])

    cat_transformer = ImbPipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", num_transformer, num_features),
            ("cat", cat_transformer, cat_features)
        ]
    )
    return preprocessor


def train_and_compare_models():
    """Run 5-Fold Stratified Cross Validation across 5 classification algorithms."""
    X, y, num_features, cat_features, label_mapping, reverse_mapping = load_and_prepare_data()

    # Stratified 80/20 train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, stratify=y, random_state=42
    )
    print(f"[*] Training samples: {len(X_train)} | Testing samples: {len(X_test)}")

    preprocessor = build_preprocessor(num_features, cat_features)

    # Candidate models to benchmark
    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Decision Tree": DecisionTreeClassifier(max_depth=6, random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, random_state=42),
        "XGBoost": XGBClassifier(n_estimators=100, max_depth=5, learning_rate=0.1, eval_metric="mlogloss", random_state=42)
    }

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    comparison_results = []

    print("\n" + "=" * 75)
    print(f"{'Model':<22} | {'Accuracy':<10} | {'Macro F1':<10} | {'Macro Prec':<10} | {'Macro Rec'}")
    print("=" * 75)

    for name, clf in models.items():
        # Scikit-learn Pipeline with SMOTE on train split ONLY
        pipe = ImbPipeline([
            ("preprocessor", preprocessor),
            ("smote", SMOTE(random_state=42)),
            ("classifier", clf)
        ])

        scoring = ["accuracy", "f1_macro", "precision_macro", "recall_macro"]
        cv_scores = cross_validate(pipe, X_train, y_train, cv=cv, scoring=scoring)

        acc = cv_scores["test_accuracy"].mean()
        f1 = cv_scores["test_f1_macro"].mean()
        prec = cv_scores["test_precision_macro"].mean()
        rec = cv_scores["test_recall_macro"].mean()

        comparison_results.append({
            "Model": name,
            "Accuracy": acc,
            "Macro_F1": f1,
            "Precision": prec,
            "Recall": rec
        })
        print(f"{name:<22} | {acc:.4f}     | {f1:.4f}     | {prec:.4f}     | {rec:.4f}")

    print("=" * 75)

    comp_df = pd.DataFrame(comparison_results)

    # Plot Model Comparison Bar Chart
    fig, ax = plt.subplots(figsize=(10, 5))
    comp_df_melted = pd.melt(comp_df, id_vars=["Model"], value_vars=["Accuracy", "Macro_F1", "Recall"])
    sns.barplot(x="Model", y="value", hue="variable", data=comp_df_melted, palette="Set2", ax=ax)
    ax.set_title("5-Fold Cross Validation Benchmark: Risk Classifier Comparison", fontsize=13, fontweight="bold")
    ax.set_ylim(0.70, 1.0)
    ax.set_ylabel("Score", fontsize=11)
    plt.xticks(rotation=15)
    plt.tight_layout()
    comp_plot = OUTPUT_DIR / "model_comparison_barchart.png"
    plt.savefig(comp_plot, dpi=300)
    plt.close()
    print(f"[+] Saved Model Comparison Plot -> {comp_plot.name}")

    # Hyperparameter Tuning for the Top Performer (XGBoost)
    print("\n[*] Fine-tuning XGBoost with GridSearch...")
    xgb_pipe = ImbPipeline([
        ("preprocessor", preprocessor),
        ("smote", SMOTE(random_state=42)),
        ("classifier", XGBClassifier(eval_metric="mlogloss", random_state=42))
    ])

    param_grid = {
        "classifier__max_depth": [4, 5, 6],
        "classifier__n_estimators": [100, 150],
        "classifier__learning_rate": [0.05, 0.1],
        "classifier__subsample": [0.8, 1.0]
    }

    grid = GridSearchCV(xgb_pipe, param_grid, cv=3, scoring="f1_macro", n_jobs=-1)
    grid.fit(X_train, y_train)
    best_pipe = grid.best_estimator_
    print(f"[+] Best Parameters: {grid.best_params_}")

    # Final Evaluation on the Unseen 20% Test Split
    y_pred = best_pipe.predict(X_test)
    y_prob = best_pipe.predict_proba(X_test)

    final_acc = accuracy_score(y_test, y_pred)
    final_f1 = f1_score(y_test, y_pred, average="macro")
    final_roc = roc_auc_score(y_test, y_prob, multi_class="ovr")

    print("\n" + "=" * 55)
    print("FINAL TEST SET PERFORMANCE (Unseen Test Data):")
    print("=" * 55)
    print(f"Accuracy:  {final_acc*100:.2f}%")
    print(f"Macro F1:  {final_f1:.4f}")
    print(f"ROC-AUC:   {final_roc:.4f}")
    print("\nClassification Report:\n", classification_report(y_test, y_pred, target_names=["Low", "Medium", "High"]))

    # Save Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=["Low", "Medium", "High"], yticklabels=["Low", "Medium", "High"], ax=ax)
    ax.set_title("Confusion Matrix on Test Split (XGBoost)", fontsize=13, fontweight="bold")
    ax.set_xlabel("Predicted Risk Tier", fontsize=11)
    ax.set_ylabel("True Academic Tier", fontsize=11)
    plt.tight_layout()
    cm_plot = OUTPUT_DIR / "confusion_matrix.png"
    plt.savefig(cm_plot, dpi=300)
    plt.close()
    print(f"[+] Saved Confusion Matrix -> {cm_plot.name}")

    # Save the serialized model bundle
    bundle = {
        "pipeline": best_pipe,
        "num_features": num_features,
        "cat_features": cat_features,
        "label_mapping": label_mapping,
        "reverse_mapping": reverse_mapping,
        "metrics": {
            "accuracy": final_acc,
            "macro_f1": final_f1,
            "roc_auc": final_roc
        }
    }
    model_save_path = MODEL_DIR / "classifier_pipeline.joblib"
    joblib.dump(bundle, model_save_path)
    print(f"[+] Serialized Best Classifier Pipeline -> {model_save_path}")

    return best_pipe, X_train, y_train, X_test, y_test


if __name__ == "__main__":
    train_and_compare_models()
