import hashlib
import secrets
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import create_access_token, create_refresh_token, decode_token
from backend.extensions import db
from backend.app.models import (
    User, Student, Parent, Teacher, AuditLog, RefreshToken, PasswordReset
)
from backend.app.services.auth_middleware import authenticate

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/status', methods=['GET'])
def auth_status():
    """Authentication Service Heartbeat"""
    return jsonify({
        'module': 'Authentication Service',
        'status': 'active',
        'endpoints': [
            '/api/auth/login',
            '/api/auth/refresh',
            '/api/auth/logout',
            '/api/auth/me',
            '/api/auth/forgot-password',
            '/api/auth/reset-password',
            '/api/auth/change-password'
        ],
        'supported_portals': ['student', 'parent', 'teacher', 'admin', 'principal']
    }), 200

def hash_token(token: str) -> str:
    """SHA-256 hash for secure database storage of refresh and reset tokens"""
    return hashlib.sha256(token.encode('utf-8')).hexdigest()

def find_user_by_identifier(identifier: str):
    """
    Finds user by Email, Username, USN (Student), Employee ID (Teacher), or Phone (Parent).
    """
    clean_id = identifier.strip()

    # 1. Match direct User columns: email or username
    user = User.query.filter(
        (db.func.lower(User.email) == clean_id.lower()) |
        (db.func.lower(User.username) == clean_id.lower())
    ).first()
    if user:
        return user

    # 2. Check Student USN (e.g. 4PM21CS001)
    student = Student.query.filter(db.func.lower(Student.usn) == clean_id.lower()).first()
    if student and student.user_account:
        return student.user_account

    # 3. Check Teacher Employee ID (e.g. EMP-CSE-01)
    teacher = Teacher.query.filter(db.func.lower(Teacher.employee_id) == clean_id.lower()).first()
    if teacher and teacher.user_account:
        return teacher.user_account

    # 4. Check Parent Phone Number
    parent = Parent.query.filter(Parent.phone == clean_id).first()
    if parent and parent.user_account:
        return parent.user_account

    # 5. Check User phone
    user_phone = User.query.filter(User.phone == clean_id).first()
    if user_phone:
        return user_phone

    return None

def build_user_claims(user: User):
    """Extracts role-specific context IDs into JWT claims for backend authorization"""
    claims = {
        'user_id': user.user_id,
        'username': user.username,
        'email': user.email,
        'role': user.role,
        'must_change_password': user.must_change_password,
    }

    if user.role == 'student' and user.student_profile:
        claims['student_id'] = user.student_profile.student_id
        claims['usn'] = user.student_profile.usn
        claims['class_id'] = user.student_profile.class_id

    elif user.role == 'parent' and user.parent_profile:
        claims['parent_id'] = user.parent_profile.parent_id

    elif user.role in ('teacher', 'hod') and user.teacher_profile:
        claims['teacher_id'] = user.teacher_profile.teacher_id
        claims['dept_id'] = user.teacher_profile.dept_id
        claims['employee_id'] = user.teacher_profile.employee_id

    return claims

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Unified multi-role login with role verification, brute-force lockout, and audit logging.
    Payload: { "identifier": "...", "password": "...", "expectedRole": "..." }
    """
    data = request.get_json() or {}
    identifier = data.get('identifier', '').strip() or data.get('username', '').strip() or data.get('email', '').strip()
    password = data.get('password', '')
    expected_role = data.get('expectedRole', '').strip().lower()
    client_ip = request.remote_addr

    if not identifier or not password:
        return jsonify({
            'success': False,
            'error': 'VALIDATION_ERROR',
            'message': 'Please enter both your identifier (Email/USN/ID/Phone) and password.'
        }), 400

    user = find_user_by_identifier(identifier)

    if not user:
        # Generic authentication failure to prevent username enumeration
        AuditLog.query.session.add(AuditLog(
            action='LOGIN_FAILED_UNKNOWN_USER',
            target_type='User',
            ip=client_ip
        ))
        db.session.commit()
        return jsonify({
            'success': False,
            'error': 'INVALID_CREDENTIALS',
            'message': 'Invalid credentials. Please verify your identifier and password.'
        }), 401

    # Check account active status
    if not user.active:
        AuditLog.query.session.add(AuditLog(
            user_id=user.user_id,
            role=user.role,
            action='LOGIN_BLOCKED_INACTIVE',
            ip=client_ip
        ))
        db.session.commit()
        return jsonify({
            'success': False,
            'error': 'ACCOUNT_DEACTIVATED',
            'message': 'This account has been deactivated. Please contact the college administrator.'
        }), 403

    # Check account lockout
    if user.is_locked():
        remaining = int((user.locked_until - datetime.utcnow()).total_seconds() / 60) + 1
        AuditLog.query.session.add(AuditLog(
            user_id=user.user_id,
            role=user.role,
            action='LOGIN_BLOCKED_LOCKED',
            ip=client_ip
        ))
        db.session.commit()
        return jsonify({
            'success': False,
            'error': 'ACCOUNT_LOCKED',
            'message': f'Account is temporarily locked due to repeated failed logins. Please try again in {remaining} minutes.'
        }), 429

    # Verify password
    if not user.check_password(password):
        user.record_failed_login(max_attempts=5, lockout_minutes=15)
        remaining_attempts = max(0, 5 - user.failed_attempts)
        AuditLog.query.session.add(AuditLog(
            user_id=user.user_id,
            role=user.role,
            action='LOGIN_FAILED_WRONG_PASSWORD',
            ip=client_ip
        ))
        db.session.commit()

        if user.is_locked():
            return jsonify({
                'success': False,
                'error': 'ACCOUNT_LOCKED',
                'message': 'Account has been locked for 15 minutes due to 5 consecutive failed login attempts.'
            }), 429

        return jsonify({
            'success': False,
            'error': 'INVALID_CREDENTIALS',
            'message': f'Invalid password. {remaining_attempts} attempt(s) remaining before temporary lockout.'
        }), 401

    # Verify expectedRole if signing in on a role-specific login portal
    if expected_role:
        user_role = user.role
        role_matches = (user_role == expected_role) or (expected_role == 'teacher' and user_role == 'hod')
        if not role_matches:
            AuditLog.query.session.add(AuditLog(
                user_id=user.user_id,
                role=user.role,
                action='LOGIN_FAILED_ROLE_MISMATCH',
                ip=client_ip
            ))
            db.session.commit()
            return jsonify({
                'success': False,
                'error': 'ROLE_MISMATCH',
                'message': f'These credentials are not for a {expected_role} account. Please use the appropriate portal.'
            }), 401

    # Successful Login: Reset attempts and generate tokens
    user.reset_failed_attempts()
    claims = build_user_claims(user)

    access_token = create_access_token(identity=str(user.user_id), additional_claims=claims)
    refresh_token_raw = create_refresh_token(identity=str(user.user_id))

    # Store refresh token hash in database for secure rotation
    token_db_hash = hash_token(refresh_token_raw)
    db_refresh = RefreshToken(
        user_id=user.user_id,
        token_hash=token_db_hash,
        expires_at=datetime.utcnow() + timedelta(days=7),
        revoked=False
    )
    db.session.add(db_refresh)

    # Log audit event
    AuditLog.query.session.add(AuditLog(
        user_id=user.user_id,
        role=user.role,
        action='LOGIN_SUCCESS',
        ip=client_ip
    ))
    db.session.commit()

    # Determine redirect route by role
    redirect_routes = {
        'student': '/student/dashboard',
        'parent': '/parent/dashboard',
        'teacher': '/teacher/dashboard',
        'hod': '/teacher/dashboard',
        'admin': '/admin/dashboard',
        'principal': '/principal/dashboard'
    }

    response_data = {
        'success': True,
        'message': f'Welcome back, {user.username}!',
        'access_token': access_token,
        'user': user.to_dict(),
        'claims': claims,
        'redirectTo': redirect_routes.get(user.role, '/overview'),
        'mustChangePassword': user.must_change_password
    }

    # Set httpOnly, secure, SameSite refresh cookie
    response = make_response(jsonify(response_data), 200)
    response.set_cookie(
        'camps_refresh_token',
        refresh_token_raw,
        httponly=True,
        secure=False,  # Set True in production HTTPS
        samesite='Lax',
        max_age=7 * 24 * 3600,
        path='/api/auth'
    )
    return response

@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    """
    Refreshes short-lived JWT access token using the httpOnly cookie refresh token.
    """
    token_raw = request.cookies.get('camps_refresh_token')
    if not token_raw:
        # Fallback check JSON body
        data = request.get_json(silent=True) or {}
        token_raw = data.get('refresh_token')

    if not token_raw:
        return jsonify({
            'success': False,
            'error': 'REFRESH_TOKEN_MISSING',
            'message': 'Refresh token missing.'
        }), 401

    try:
        decoded = decode_token(token_raw)
        user_id = int(decoded['sub'])
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'INVALID_REFRESH_TOKEN',
            'message': 'Refresh token is expired or invalid.'
        }), 401

    token_hash = hash_token(token_raw)
    db_token = RefreshToken.query.filter_by(token_hash=token_hash, revoked=False).first()

    if not db_token or not db_token.is_valid():
        return jsonify({
            'success': False,
            'error': 'REVOKED_REFRESH_TOKEN',
            'message': 'Refresh token has been revoked or expired. Please sign in again.'
        }), 401

    user = db.session.get(User, user_id)
    if not user or not user.active:
        return jsonify({
            'success': False,
            'error': 'ACCOUNT_INACTIVE',
            'message': 'User account is inactive.'
        }), 401

    claims = build_user_claims(user)
    new_access_token = create_access_token(identity=str(user.user_id), additional_claims=claims)

    return jsonify({
        'success': True,
        'access_token': new_access_token,
        'claims': claims,
    }), 200

@auth_bp.route('/logout', methods=['POST'])
@authenticate(optional=True)
def logout():
    """
    Revokes refresh token and clears session cookies.
    """
    token_raw = request.cookies.get('camps_refresh_token')
    if token_raw:
        token_hash = hash_token(token_raw)
        db_token = RefreshToken.query.filter_by(token_hash=token_hash).first()
        if db_token:
            db_token.revoked = True

    if hasattr(request, 'current_user') and request.current_user:
        AuditLog.query.session.add(AuditLog(
            user_id=request.current_user.user_id,
            role=request.current_user.role,
            action='LOGOUT',
            ip=request.remote_addr
        ))
    db.session.commit()

    response = make_response(jsonify({
        'success': True,
        'message': 'Successfully signed out.'
    }), 200)

    response.delete_cookie('camps_refresh_token', path='/api/auth')
    return response

@auth_bp.route('/me', methods=['GET'])
@authenticate()
def get_current_user_profile():
    """
    Returns authenticated user profile, claims, and role-specific context.
    """
    user = request.current_user
    data = user.to_dict()

    # Attach profile details
    if user.role == 'student' and user.student_profile:
        data['student'] = user.student_profile.to_dict()
    elif user.role == 'parent' and user.parent_profile:
        data['parent'] = user.parent_profile.to_dict()
        data['children'] = [c.to_dict() for c in user.parent_profile.children.all()]
    elif user.role in ('teacher', 'hod') and user.teacher_profile:
        data['teacher'] = user.teacher_profile.to_dict()
        data['assignments'] = [a.to_dict() for a in user.teacher_profile.assignments]

    return jsonify({
        'success': True,
        'user': data,
        'claims': getattr(request, 'jwt_payload', {})
    }), 200

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """
    Generates single-use cryptographic token with 1 hour expiry for password reset.
    Payload: { "identifier": "..." }
    """
    data = request.get_json() or {}
    identifier = data.get('identifier', '').strip()

    if not identifier:
        return jsonify({'success': False, 'message': 'Identifier is required.'}), 400

    user = find_user_by_identifier(identifier)
    # Always return 200 to prevent user enumeration
    if not user:
        return jsonify({
            'success': True,
            'message': 'If an active account exists for this identifier, reset instructions have been sent.'
        }), 200

    reset_token = secrets.token_urlsafe(32)
    token_hash = hash_token(reset_token)

    pw_reset = PasswordReset(
        user_id=user.user_id,
        token_hash=token_hash,
        expires_at=datetime.utcnow() + timedelta(hours=1),
        used=False
    )
    db.session.add(pw_reset)
    AuditLog.query.session.add(AuditLog(
        user_id=user.user_id,
        role=user.role,
        action='PASSWORD_RESET_REQUESTED',
        ip=request.remote_addr
    ))
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Password reset link has been dispatched to your registered email address.',
        'dev_reset_token': reset_token  # Provided for local testing
    }), 200

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """
    Resets password using single-use cryptographic token.
    Payload: { "token": "...", "newPassword": "..." }
    """
    data = request.get_json() or {}
    token = data.get('token', '').strip()
    new_password = data.get('newPassword', '')

    if not token or not new_password or len(new_password) < 6:
        return jsonify({
            'success': False,
            'error': 'VALIDATION_ERROR',
            'message': 'Valid token and new password (min 6 characters) are required.'
        }), 400

    token_hash = hash_token(token)
    reset_entry = PasswordReset.query.filter_by(token_hash=token_hash).first()

    if not reset_entry or not reset_entry.is_valid():
        return jsonify({
            'success': False,
            'error': 'INVALID_TOKEN',
            'message': 'Reset link is invalid, expired, or has already been used.'
        }), 400

    user = db.session.get(User, reset_entry.user_id)
    if not user:
        return jsonify({'success': False, 'error': 'USER_NOT_FOUND'}), 404

    user.set_password(new_password)
    user.must_change_password = False
    user.reset_failed_attempts()
    reset_entry.used = True

    AuditLog.query.session.add(AuditLog(
        user_id=user.user_id,
        role=user.role,
        action='PASSWORD_RESET_SUCCESS',
        ip=request.remote_addr
    ))
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Your password has been successfully reset. You may now sign in with your new password.'
    }), 200

@auth_bp.route('/change-password', methods=['POST'])
@authenticate()
def change_password():
    """
    Allows authenticated users to rotate password. Forces rotation on first login.
    Payload: { "currentPassword": "...", "newPassword": "..." }
    """
    user = request.current_user
    data = request.get_json() or {}
    current_password = data.get('currentPassword', '')
    new_password = data.get('newPassword', '')

    if not current_password or not new_password or len(new_password) < 6:
        return jsonify({
            'success': False,
            'error': 'VALIDATION_ERROR',
            'message': 'Current password and new password (minimum 6 characters) are required.'
        }), 400

    if not user.check_password(current_password):
        return jsonify({
            'success': False,
            'error': 'INCORRECT_PASSWORD',
            'message': 'The current password you provided is incorrect.'
        }), 400

    user.set_password(new_password)
    user.must_change_password = False
    AuditLog.query.session.add(AuditLog(
        user_id=user.user_id,
        role=user.role,
        action='PASSWORD_CHANGED',
        ip=request.remote_addr
    ))
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Password updated successfully.'
    }), 200
