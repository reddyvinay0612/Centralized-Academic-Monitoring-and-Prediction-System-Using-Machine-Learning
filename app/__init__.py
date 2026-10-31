"""
Flask Application Factory for CAMPS-ML.
Initializes extensions (SQLAlchemy, LoginManager, Mail) and registers all modular Blueprints.
"""

import os
from flask import Flask, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_mail import Mail
from config import config_by_name

# Initialize Flask extensions
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()


def create_app(config_name=None):
    """Application factory pattern to instantiate and configure Flask app."""
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")
        
    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name["default"]))
    
    # Ensure instance and storage folders exist
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["REPORTS_FOLDER"], exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["ML_MODEL_DIR"], exist_ok=True)

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    
    # Configure Flask-Login defaults
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please sign in to access this page."
    login_manager.login_message_category = "warning"

    # Register models with metadata
    from . import models

    # Register Blueprints
    from app.blueprints.auth.routes import auth_bp
    from app.blueprints.admin.routes import admin_bp
    from app.blueprints.hod.routes import hod_bp
    from app.blueprints.faculty.routes import faculty_bp
    from app.blueprints.student.routes import student_bp
    from app.blueprints.api.routes import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(hod_bp)
    app.register_blueprint(faculty_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(api_bp)

    # Root route: intelligent redirection based on authentication and role
    @app.route("/")
    def index():
        if current_user.is_authenticated:
            if current_user.role == "admin":
                return redirect(url_for("admin.dashboard"))
            elif current_user.role == "hod":
                return redirect(url_for("hod.dashboard"))
            elif current_user.role == "faculty":
                return redirect(url_for("faculty.dashboard"))
            else:
                return redirect(url_for("student.dashboard"))
        return redirect(url_for("auth.login"))

    # Base Health Check Route
    @app.route("/health")
    def health_check():
        return jsonify({
            "status": "healthy",
            "project": "Centralized Academic Monitoring and Prediction System",
            "version": "1.0.0",
            "environment": config_name
        })

    return app
