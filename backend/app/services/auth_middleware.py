from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity
from backend.extensions import db
from backend.app.models import User, Student, Parent, Teacher, ParentStudent, TeacherAssignment, Class

def authenticate(optional=False):
    """
    Middleware decorator to verify JWT Bearer token and attach authenticated User object.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                verify_jwt_in_request(optional=optional)
                identity = get_jwt_identity()

                if identity is None and optional:
                    request.current_user = None
                    request.jwt_payload = {}
                    return fn(*args, **kwargs)

                if identity is None:
                    return jsonify({
                        'success': False,
                        'error': 'UNAUTHORIZED',
                        'message': 'Authentication token is required.'
                    }), 401

                user = db.session.get(User, int(identity)) if identity else None
                if not user or not user.active:
                    return jsonify({
                        'success': False,
                        'error': 'ACCOUNT_INACTIVE',
                        'message': 'Account is inactive or has been deactivated. Please contact administration.'
                    }), 401

                request.current_user = user
                request.jwt_payload = get_jwt()
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': 'INVALID_TOKEN',
                    'message': f'Authentication failed: {str(e)}'
                }), 401

            return fn(*args, **kwargs)

        return wrapper
    return decorator

def require_role(*allowed_roles):
    """
    Middleware decorator that restricts access strictly to specified roles.
    Returns 403 Forbidden if user's role does not match.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not hasattr(request, 'current_user') or request.current_user is None:
                return jsonify({
                    'success': False,
                    'error': 'UNAUTHORIZED',
                    'message': 'Authentication required before permission verification.'
                }), 401

            user_role = request.current_user.role

            # Map hod to teacher where applicable
            roles_set = set(allowed_roles)
            if 'teacher' in roles_set and user_role == 'hod':
                roles_set.add('hod')

            if user_role not in roles_set:
                return jsonify({
                    'success': False,
                    'error': 'FORBIDDEN',
                    'message': f'Access restricted. Requires one of roles: {", ".join(allowed_roles)}. Your role is {user_role}.'
                }), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator

def check_student_scope(current_user, student_id: int):
    """
    Evaluates whether current_user is authorized to view or access the given student_id:
      - student: can access only their own record
      - parent: can access only children mapped in parent_students
      - teacher: can access only students in classes assigned to this teacher
      - hod: can access only students in their department
      - principal: can access every student in the college
      - admin: can access every student
    Returns: (is_authorized: bool, student_or_error_message: Student | str)
    """
    student = db.session.get(Student, student_id)
    if not student:
        return False, "Student not found."

    role = current_user.role

    # 1. Principal & Admin: Full college-wide access
    if role in ('principal', 'admin'):
        return True, student

    # 2. Student: Own record only
    if role == 'student':
        if student.user_id == current_user.user_id:
            return True, student
        return False, "You can only view your own student academic records."

    # 3. Parent: Linked children only
    if role == 'parent':
        parent = Parent.query.filter_by(user_id=current_user.user_id).first()
        if not parent:
            return False, "Parent profile not found."

        is_linked = ParentStudent.query.filter_by(
            parent_id=parent.parent_id,
            student_id=student.student_id
        ).first()

        if is_linked:
            return True, student
        return False, "You are only authorized to view records belonging to your registered child."

    # 4. Teacher: Assigned classes only
    if role in ('teacher', 'hod'):
        teacher = Teacher.query.filter_by(user_id=current_user.user_id).first()
        if not teacher:
            return False, "Teacher profile not found."

        # If HoD, can view any student in their department
        if role == 'hod':
            student_class = db.session.get(Class, student.class_id)
            if student_class and student_class.dept_id == teacher.dept_id:
                return True, student

        # Check assigned classes for teacher
        has_class_assignment = TeacherAssignment.query.filter_by(
            teacher_id=teacher.teacher_id,
            class_id=student.class_id
        ).first()

        if has_class_assignment:
            return True, student

        # Check if mentor of class
        student_class = db.session.get(Class, student.class_id)
        if student_class and student_class.mentor_teacher_id == teacher.teacher_id:
            return True, student

        return False, "You can only view students enrolled in classes assigned to you."

    return False, "Unauthorized access."

def scope_student_access(param_name='student_id'):
    """
    Route decorator ensuring student data access conforms to scope constraints.
    Injects authorized `student` object into keyword arguments.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not hasattr(request, 'current_user') or not request.current_user:
                return jsonify({'success': False, 'error': 'UNAUTHORIZED', 'message': 'Authentication required.'}), 401

            student_id = kwargs.get(param_name)
            if student_id is None:
                return jsonify({'success': False, 'error': 'BAD_REQUEST', 'message': 'Missing student ID parameter.'}), 400

            is_authorized, result = check_student_scope(request.current_user, int(student_id))
            if not is_authorized:
                return jsonify({'success': False, 'error': 'FORBIDDEN', 'message': result}), 403

            kwargs['student'] = result
            return fn(*args, **kwargs)
        return wrapper
    return decorator
