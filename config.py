"""
Centralized Academic Monitoring and Prediction System (CAMPS-ML)
Configuration Module supporting Development, Testing, and Production environments.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory of the Project
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env if present
load_dotenv(BASE_DIR / ".env")


class Config:
    """Base configuration with shared application parameters."""
    SECRET_KEY = os.getenv("SECRET_KEY", "camps-ml-default-insecure-key-change-me")
    
    # SQLAlchemy ORM Settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'instance' / 'camps.db'}"
    )
    
    # Flask-Mail Settings
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True").lower() in ("true", "1", "t")
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "False").lower() in ("true", "1", "t")
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", None)
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", None)
    MAIL_DEFAULT_SENDER = os.getenv(
        "MAIL_DEFAULT_SENDER", "CAMPS Alerts <alerts@camps-institution.edu>"
    )
    
    # Upload and Report Storage
    UPLOAD_FOLDER = BASE_DIR / "data" / "raw"
    REPORTS_FOLDER = BASE_DIR / "reports_output"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload limit
    
    # ML Engine & Alert Thresholds
    ML_MODEL_DIR = BASE_DIR / "ml_engine" / "saved_models"
    ALERT_ATTENDANCE_THRESHOLD = float(os.getenv("ALERT_ATTENDANCE_THRESHOLD", 75.0))
    ALERT_HIGH_RISK_PROBABILITY = float(os.getenv("ALERT_HIGH_RISK_PROBABILITY", 0.60))


class DevelopmentConfig(Config):
    """Configuration for local development."""
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Configuration for automated test runner (pytest)."""
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    MAIL_SUPPRESS_SEND = True


class ProductionConfig(Config):
    """Configuration for production deployment."""
    DEBUG = False
    TESTING = False
    # In production, require an explicitly defined secret key and database URL
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
