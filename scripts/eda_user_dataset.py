import pandas as pd
import numpy as np

df = pd.read_csv('data/processed/pesitm_sem6_students_evaluation.csv')
print("Shape:", df.shape)
print("\nColumns:", df.columns.tolist())
print("\nMissing values:")
print(df.isnull().sum())

print("\nRisk Level Distribution:")
print(df['risk_level'].value_counts())

print("\nMarks Range Distribution:")
print(df['predicted_next_sem_marks_range'].value_counts())

print("\nSem6 Failed Subjects Distribution:")
print(df['Sem6 failed subjects'].value_counts())

print("\nHead of data:")
print(df.head(3))
