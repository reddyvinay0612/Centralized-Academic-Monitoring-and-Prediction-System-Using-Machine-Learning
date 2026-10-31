"""
Machine Learning and Explainability ORM Models for CAMPS-ML.
Persists Risk Predictions, Projected SGPA, and SHAP Local Attributions.
"""

from datetime import datetime
from app import db


class PredictionLog(db.Model):
    """Historical audit log of ML inferences per student."""
    __tablename__ = "prediction_logs"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    milestone = db.Column(db.String(30), default="Current")  # e.g., Post-IA1, Post-IA2, End-Sem
    
    # Classification Output (Islam et al. 2024)
    predicted_risk_level = db.Column(db.String(20), nullable=False)  # High, Medium, Low
    risk_probability = db.Column(db.Float, nullable=False)           # 0.0 to 1.0 (probability of high risk/dropout)
    
    # Regression Output (DeJong & Karadogan 2024)
    predicted_sgpa = db.Column(db.Float, nullable=True)              # 0.00 to 10.00 projected next-term SGPA
    
    # Metadata & Auditing
    model_name = db.Column(db.String(60), default="XGBoost + RF Pipeline")
    model_version = db.Column(db.String(20), default="v1.0")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    student = db.relationship("StudentProfile", back_populates="predictions")
    shap_factors = db.relationship("SHAPFactor", back_populates="prediction", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Prediction Student:{self.student_id} Risk:{self.predicted_risk_level} Prob:{self.risk_probability:.2f}>"


class SHAPFactor(db.Model):
    """Top feature attribution factors explaining why a student received a risk rating."""
    __tablename__ = "shap_factors"

    id = db.Column(db.Integer, primary_key=True)
    prediction_id = db.Column(db.Integer, db.ForeignKey("prediction_logs.id", ondelete="CASCADE"), nullable=False)
    feature_name = db.Column(db.String(80), nullable=False)       # e.g., "Attendance Rate", "IA2 Average"
    feature_value = db.Column(db.String(50), nullable=True)      # e.g., "64.2%", "12.5 / 30"
    shap_value = db.Column(db.Float, nullable=False)             # Numerical SHAP attribution value
    impact_direction = db.Column(db.String(20), nullable=False)  # "Increases Risk" or "Decreases Risk"

    # Relationships
    prediction = db.relationship("PredictionLog", back_populates="shap_factors")

    def __repr__(self):
        return f"<SHAPFactor {self.feature_name}: {self.shap_value:+.3f} ({self.impact_direction})>"
