import os
from flask import Flask, jsonify
from backend.config import config_by_name
from backend.extensions import db, jwt, cors, bcrypt, migrate

def create_app(config_name=None):
    """
    Application Factory for Smart College Management System
    Supports Student, Parent, Teacher, Admin, and Principal portals.
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    
    # Configure CORS for frontend access
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config.get('CLIENT_URL', 'http://localhost:5173')}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    )
    
    jwt.init_app(app)

    # JWT Error Handling Handlers
    @jwt.unauthorized_loader
    def custom_unauthorized_response(callback):
        return jsonify({
            'success': False,
            'error': 'UNAUTHORIZED',
            'message': 'Missing authorization token. Please sign in to access this portal.'
        }), 401

    @jwt.invalid_token_loader
    def custom_invalid_token_response(callback):
        return jsonify({
            'success': False,
            'error': 'INVALID_TOKEN',
            'message': 'The authorization token is invalid or has been tampered with.'
        }), 401

    @jwt.expired_token_loader
    def custom_expired_token_response(jwt_header, jwt_payload):
        return jsonify({
            'success': False,
            'error': 'TOKEN_EXPIRED',
            'message': 'Your session has expired. Please sign in again to refresh your session.'
        }), 401

    # Global HTTP Error Handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'success': False, 'error': 'BAD_REQUEST', 'message': str(error)}), 400

    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'success': False, 'error': 'FORBIDDEN', 'message': 'You do not have permission to access this resource.'}), 403

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'success': False, 'error': 'NOT_FOUND', 'message': 'Requested API endpoint or resource was not found.'}), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({'success': False, 'error': 'INTERNAL_SERVER_ERROR', 'message': 'An internal error occurred on the server.'}), 500

    # System Health & Diagnostic Endpoints
    @app.route('/api/health', methods=['GET'])
    def health_check():
        db_status = "connected"
        try:
            db.session.execute(db.text("SELECT 1"))
        except Exception as e:
            db_status = f"unreachable ({str(e)})"

        return jsonify({
            'status': 'healthy',
            'system': 'Smart College Management System API',
            'institution': app.config.get('COLLEGE_NAME'),
            'database': db_status,
            'portals': ['student', 'parent', 'teacher', 'admin', 'principal'],
            'version': '1.0.0-phase1'
        }), 200

    @app.route('/api/system/info', methods=['GET'])
    def system_info():
        return jsonify({
            'college_name': app.config.get('COLLEGE_NAME'),
            'college_code': app.config.get('COLLEGE_CODE'),
            'affiliation': app.config.get('AFFILIATION'),
            'location': app.config.get('LOCATION'),
            'available_roles': ['student', 'parent', 'teacher', 'admin', 'principal'],
            'rbac_enabled': True
        }), 200

    # Register Blueprints
    from backend.app.authentication.routes import auth_bp
    from backend.app.students.routes import students_bp
    from backend.app.parents.routes import parents_bp
    from backend.app.teachers.routes import teachers_bp
    from backend.app.admin.routes import admin_bp
    from backend.app.principal.routes import principal_bp
    from backend.app.notifications.routes import notifications_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(students_bp, url_prefix='/api/student')
    app.register_blueprint(parents_bp, url_prefix='/api/parent')
    app.register_blueprint(teachers_bp, url_prefix='/api/teacher')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(principal_bp, url_prefix='/api/principal')
    app.register_blueprint(notifications_bp, url_prefix='/api/notifications')

    return app
