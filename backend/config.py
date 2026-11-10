import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Load environment settings from root .env and backend/.env
load_dotenv(os.path.join(BASE_DIR, '..', '.env'), override=True)
load_dotenv(os.path.join(BASE_DIR, '.env'), override=True)

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
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '3306')
    DB_NAME = os.environ.get('DB_NAME', 'camps_db')
    
    # Primary MySQL Connection String
    MYSQL_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    
    # SQLite Path
    SQLITE_PATH = os.path.join(BASE_DIR, 'camps_smart_college.db').replace('\\', '/')
    SQLITE_URI = f"sqlite:///{SQLITE_PATH}"
    
    # Check MySQL connectivity before deciding URI
    _target_mysql_uri = None
    if os.environ.get('DATABASE_URL') and not os.environ.get('DATABASE_URL').startswith('sqlite:///camps'):
        _target_mysql_uri = os.environ.get('DATABASE_URL')
    elif os.environ.get('USE_MYSQL', 'false').lower() == 'true':
        _target_mysql_uri = MYSQL_URI

    _mysql_connected = False
    if _target_mysql_uri and 'mysql' in _target_mysql_uri:
        try:
            import pymysql
            from urllib.parse import urlparse
            _p = urlparse(_target_mysql_uri)
            _c = pymysql.connect(
                host=_p.hostname or 'localhost',
                user=_p.username or 'root',
                password=_p.password or '',
                port=_p.port or 3306,
                connect_timeout=2
            )
            _c.close()
            _mysql_connected = True
        except Exception:
            _mysql_connected = False

    if _mysql_connected and _target_mysql_uri:
        SQLALCHEMY_DATABASE_URI = _target_mysql_uri
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
            'isolation_level': 'READ COMMITTED',
        }
    else:
        SQLALCHEMY_DATABASE_URI = SQLITE_URI
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_pre_ping': True,
        }

    SQLALCHEMY_TRACK_MODIFICATIONS = False

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
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=5)

config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
