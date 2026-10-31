"""
Flask Application Factory for CAMPS-ML.
Initializes extensions (SQLAlchemy, LoginManager, Mail) and registers blueprints.
"""

import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from config import config_by_name

# Initialize Flask extensions (unbound to app yet)
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

    # Base Health Check Route (Verifies environment and app status)
    @app.route("/health")
    def health_check():
        return jsonify({
            "status": "healthy",
            "project": "Centralized Academic Monitoring and Prediction System",
            "version": "1.0.0",
            "environment": config_name
        })

    return app
