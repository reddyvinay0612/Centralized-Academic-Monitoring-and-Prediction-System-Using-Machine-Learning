import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from pathlib import Path

OUTPUT_DIR = Path("reports_output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Set styling
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'

# 1. Module 1: Pass/Fail Comparison Bar Chart
models_m1 = ['Random Forest', 'Gradient Boosting', 'XGBoost', 'Logistic Regression', 'Decision Tree']
acc_m1 = [90.83, 90.03, 88.52, 87.04, 83.99]
f1_m1 = [94.80, 94.39, 93.39, 92.19, 90.54]

x = np.arange(len(models_m1))
width = 0.35

fig, ax = plt.subplots(figsize=(9, 5))
rects1 = ax.bar(x - width/2, acc_m1, width, label='Accuracy (%)', color='#2563eb')
rects2 = ax.bar(x + width/2, f1_m1, width, label='F1-Score (%)', color='#10b981')

ax.set_ylabel('Score (%)', fontsize=12, fontweight='bold')
ax.set_title('Module 1: Pass / Fail Prediction Model Comparison (5-Fold Stratified CV)', fontsize=13, fontweight='bold', pad=15)
ax.set_xticks(x)
ax.set_xticklabels(models_m1, fontsize=10, rotation=15)
ax.legend(frameon=True)
ax.set_ylim(70, 100)

for rect in rects1 + rects2:
    h = rect.get_height()
    ax.annotate(f'{h:.1f}%', xy=(rect.get_x() + rect.get_width()/2, h),
                xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'module1_pass_fail_comparison.png', dpi=300)
plt.close()

# 2. Module 3: Regression Predicted vs Actual Scatter Plot
df = pd.read_csv('data/processed/pesitm_sem6_students_evaluation.csv')
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

feature_cols = [
    'Sem1_SGPA_clean', 'Sem2_SGPA_clean', 'Sem3_SGPA', 'Sem4_SGPA', 'Sem5_SGPA',
    'previous_sem_sgpa', 'cgpa', 'backlogs', 'Sem5_internal_pct', 'avg_ia',
    'sgpa_trend', 'cgpa_deviation', 'internal_ratio', 'is_lateral_entry'
]
df['is_lateral_entry'] = df['Sem1_SGPA'].isna().astype(int)
df['Sem1_SGPA_clean'] = df['Sem1_SGPA'].fillna(df['cgpa'])
df['Sem2_SGPA_clean'] = df['Sem2_SGPA'].fillna(df['cgpa'])
df['sgpa_trend'] = df['Sem5_SGPA'] - df['Sem4_SGPA']
df['cgpa_deviation'] = df['Sem5_SGPA'] - df['cgpa']
df['internal_ratio'] = df['Sem5_internal_pct'] / (df['cgpa'] * 10.0 + 1e-5)

X = df[feature_cols]
y_actual = df['Sem6_avg_total']

ridge = Pipeline([('scaler', StandardScaler()), ('reg', Ridge(alpha=1.0))])
ridge.fit(X, y_actual)
y_pred = ridge.predict(X)

fig, ax = plt.subplots(figsize=(7, 6))
ax.scatter(y_actual, y_pred, color='#4f46e5', alpha=0.7, edgecolors='white', s=60, label='Student Predictions')
min_val = min(y_actual.min(), y_pred.min()) - 2
max_val = max(y_actual.max(), y_pred.max()) + 2
ax.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='Perfect Fit ($y = x$)')

ax.set_xlabel('Actual Sem 6 Average Total Score (/100)', fontsize=11, fontweight='bold')
ax.set_ylabel('Predicted Sem 6 Average Total Score (/100)', fontsize=11, fontweight='bold')
ax.set_title(f'Module 3: Continuous Score Prediction (R² = 0.8031, MAE = 2.75 Marks)', fontsize=12, fontweight='bold', pad=15)
ax.legend(frameon=True)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / 'module3_regression_actual_vs_pred.png', dpi=300)
plt.close()

print("[+] Visual performance charts saved to reports_output/")
