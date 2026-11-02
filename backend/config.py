import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Base Configuration for Smart College Management System"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'smart_college_super_secret_jwt_key_2026_shivamogga')
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt_secret_pesitm_vtu_smart_college_2026')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=int(os.environ.get('JWT_ACCESS_EXPIRES_MINUTES', 30)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.environ.get('JWT_REFRESH_EXPIRES_DAYS', 7)))
    JWT_TOKEN_LOCATION = ['headers', 'cookies']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    JWT_COOKIE_SECURE = os.environ.get('JWT_COOKIE_SECURE', 'False').lower() == 'true'
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_COOKIE_SAMESITE = 'Lax'
    
    # Database Configuration (MySQL with automatic fallback to local SQLite for seamless setup)
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'rootpassword')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '3306')
    DB_NAME = os.environ.get('DB_NAME', 'camps_db')
    
    # Primary MySQL Connection String
    MYSQL_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    
    # If DATABASE_URL is provided, use it; otherwise use SQLite locally or MySQL when USE_MYSQL=true
    USE_MYSQL = os.environ.get('USE_MYSQL', 'false').lower() == 'true'
    SQLITE_PATH = os.path.join(BASE_DIR, 'camps_smart_college.db').replace('\\', '/')
    SQLITE_URI = f"sqlite:///{SQLITE_PATH}"
    
    if os.environ.get('DATABASE_URL') and not os.environ.get('DATABASE_URL').startswith('sqlite:///camps'):
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    elif USE_MYSQL:
        SQLALCHEMY_DATABASE_URI = MYSQL_URI
    else:
        SQLALCHEMY_DATABASE_URI = SQLITE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    # CORS Settings
    CLIENT_URL = os.environ.get('CLIENT_URL', 'http://localhost:5173')

    # Security & Rate Limiting Defaults
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 15

    # Institution Metadata
    COLLEGE_NAME = "PES Institute of Technology & Management"
    COLLEGE_CODE = "PESITM"
    AFFILIATION = "VTU Belagavi & Approved by AICTE, New Delhi"
    LOCATION = "Shivamogga, Karnataka, India"

class DevelopmentConfig(Config):
    DEBUG = True
    ENV = 'development'

class ProductionConfig(Config):
    DEBUG = False
    ENV = 'production'
    JWT_COOKIE_SECURE = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=5)

config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
