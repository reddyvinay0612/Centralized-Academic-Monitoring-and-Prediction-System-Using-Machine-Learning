"""
Exploratory Data Analysis (EDA) & Profiling Engine for CAMPS-ML.
Generates statistical distributions, correlation heatmaps, and feature diagnostics.
"""

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for headless execution
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "reports_output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def run_eda(dataset_path=None):
    """Analyze student dataset distributions, correlations, and outliers."""
    if dataset_path is None:
        dataset_path = BASE_DIR / "data" / "synthetic" / "indian_college_student_data.csv"

    print("=" * 65)
    print(f"Running Exploratory Data Analysis on: {dataset_path.name}")
    print("=" * 65)

    df = pd.read_csv(dataset_path)
    print(f"Dataset Shape: {df.shape[0]} rows, {df.shape[1]} columns")

    # 1. Target Distribution Plot
    fig, ax = plt.subplots(figsize=(7, 4.5))
    palette = {"Low": "#28a745", "Medium": "#ffc107", "High": "#dc3545"}
    sns.countplot(x="Target_Risk", data=df, palette=palette, order=["Low", "Medium", "High"], ax=ax)
    ax.set_title("Target Risk Class Distribution (CAMPS-ML)", fontsize=13, fontweight="bold")
    ax.set_xlabel("Predicted Academic Risk Tier", fontsize=11)
    ax.set_ylabel("Student Count", fontsize=11)
    for p in ax.patches:
        ax.annotate(f"{int(p.get_height())} ({p.get_height()/len(df)*100:.1f}%)",
                    (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center', xytext=(0, 7), textcoords='offset points', fontweight="bold")
    plt.tight_layout()
    dist_plot = OUTPUT_DIR / "eda_class_distribution.png"
    plt.savefig(dist_plot, dpi=300)
    plt.close()
    print(f"[+] Saved Class Distribution -> {dist_plot.name}")

    # 2. Correlation Heatmap
    num_cols = [
        "Attendance_Percentage", "CIE_IA1", "CIE_IA2", "CIE_IA3",
        "Total_CIE", "Cumulative_CGPA", "Active_Backlogs",
        "10th_Percentage", "12th_Percentage", "Target_Next_SGPA"
    ]
    corr_df = df[num_cols].corr()

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr_df, annot=True, fmt=".2f", cmap="coolwarm", cbar=True, ax=ax, linewidths=0.5)
    ax.set_title("Multivariate Academic Correlation Matrix", fontsize=14, fontweight="bold")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    corr_plot = OUTPUT_DIR / "eda_correlation_heatmap.png"
    plt.savefig(corr_plot, dpi=300)
    plt.close()
    print(f"[+] Saved Correlation Heatmap -> {corr_plot.name}")

    # 3. Attendance vs Cumulative CGPA by Risk Level
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.scatterplot(
        x="Attendance_Percentage", y="Cumulative_CGPA",
        hue="Target_Risk", hue_order=["Low", "Medium", "High"],
        palette=palette, alpha=0.75, s=60, data=df, ax=ax
    )
    ax.axvline(75.0, color="red", linestyle="--", label="Mandatory 75% Attendance")
    ax.set_title("Attendance % vs Cumulative CGPA by Risk Classification", fontsize=13, fontweight="bold")
    ax.legend(loc="upper left")
    plt.tight_layout()
    scatter_plot = OUTPUT_DIR / "eda_risk_factors.png"
    plt.savefig(scatter_plot, dpi=300)
    plt.close()
    print(f"[+] Saved Risk Factors Scatter Plot -> {scatter_plot.name}")

    # 4. Statistical Summary Report
    summary_txt = OUTPUT_DIR / "eda_summary_report.txt"
    with open(summary_txt, "w") as f:
        f.write("CAMPS-ML EXPLORATORY DATA ANALYSIS SUMMARY\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Total Rows: {len(df)}\n")
        f.write(f"Features: {list(df.columns)}\n\n")
        f.write("TARGET DISTRIBUTION:\n")
        f.write(str(df['Target_Risk'].value_counts()) + "\n\n")
        f.write("NUMERICAL FEATURES DESCRIPTIVE STATISTICS:\n")
        f.write(str(df[num_cols].describe().round(2)) + "\n")
    print(f"[+] Saved EDA Summary Text Report -> {summary_txt.name}")
    print("=" * 65)


if __name__ == "__main__":
    run_eda()
