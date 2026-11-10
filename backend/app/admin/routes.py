from datetime import datetime
from flask import Blueprint, jsonify, request
from backend.extensions import db, bcrypt
from backend.app.services.auth_middleware import authenticate, require_role
from backend.app.models import (
    User, Student, Teacher, Parent, ParentStudent,
    Department, Course, AcademicYear, Semester, Section, Class, Subject,
    TeacherAssignment, AuditLog, Fee, Prediction, Alert, Notification
)

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/status', methods=['GET'])
def admin_status():
    return jsonify({
        'module': 'Admin Portal API',
        'status': 'active',
        'endpoints': [
            '/api/admin/stats',
            '/api/admin/users',
            '/api/admin/departments',
            '/api/admin/classes',
            '/api/admin/subjects',
            '/api/admin/assignments',
            '/api/admin/parent-students',
            '/api/admin/audit-logs'
        ]
    }), 200


@admin_bp.route('/stats', methods=['GET'])
@authenticate()
@require_role('admin', 'principal')
def get_system_stats():
    """
    Returns global system metrics and institutional telemetry.
    """
    total_users = User.query.count()
    students_count = Student.query.count()
    teachers_count = Teacher.query.count()
    parents_count = Parent.query.count()
    admins_count = User.query.filter_by(role='admin').count()
    principals_count = User.query.filter_by(role='principal').count()

    active_classes = Class.query.count()
    depts_count = Department.query.count()
    subjects_count = Subject.query.count()
    open_alerts = Alert.query.filter_by(status='open').count()
    audit_logs_count = AuditLog.query.count()

    return jsonify({
        'success': True,
        'data': {
            'users': {
                'total': total_users,
                'students': students_count,
                'teachers': teachers_count,
                'parents': parents_count,
                'admins': admins_count,
                'principals': principals_count,
            },
            'academics': {
                'departments': depts_count,
                'classes': active_classes,
                'subjects': subjects_count,
                'open_alerts': open_alerts,
            },
            'system': {
                'audit_events': audit_logs_count,
                'status': 'healthy',
                'engine': 'Python 3.14 + Flask + SQLAlchemy ORM',
                'database': 'SQLite / MySQL (VTU PESITM Benchmark)'
            }
        }
    }), 200


@admin_bp.route('/users', methods=['GET'])
@authenticate()
@require_role('admin', 'principal')
def list_users():
    """
    Paginated and filtered user list.
    """
    role = request.args.get('role')
    search = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 1000, type=int)

    query = User.query

    if role and role.lower() != 'all':
        query = query.filter_by(role=role.lower())

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            db.or_(
                User.username.ilike(search_filter),
                User.email.ilike(search_filter),
                User.phone.ilike(search_filter)
            )
        )

    total = query.count()
    users = query.order_by(User.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    users_list = []
    for u in users:
        item = u.to_dict()
        # Attach role-specific metadata
        if u.role == 'student':
            st = Student.query.filter_by(user_id=u.user_id).first()
            if st:
                item['profile_name'] = st.name
                item['usn'] = st.usn
                item['class_name'] = st.enrolled_class.class_name if st.enrolled_class else None
        elif u.role in ('teacher', 'hod'):
            tc = Teacher.query.filter_by(user_id=u.user_id).first()
            if tc:
                item['profile_name'] = tc.name
                item['employee_id'] = tc.employee_id
                item['designation'] = tc.designation
        elif u.role == 'parent':
            pr = Parent.query.filter_by(user_id=u.user_id).first()
            if pr:
                item['profile_name'] = pr.name
                item['wards_count'] = pr.children.count()

        users_list.append(item)

    return jsonify({
        'success': True,
        'total': total,
        'page': page,
        'limit': limit,
        'data': users_list
    }), 200


@admin_bp.route('/users', methods=['POST'])
@authenticate()
@require_role('admin')
def create_user():
    """
    Create a new user and associated role profile (Student, Teacher, Parent).
    """
    payload = request.get_json() or {}
    username = payload.get('username', '').strip()
    email = payload.get('email', '').strip()
    role = payload.get('role', 'student').strip().lower()
    password = payload.get('password', 'password123')
    phone = payload.get('phone', '').strip()
    name = payload.get('name', username).strip()

    if not username or not email or not role:
        return jsonify({'success': False, 'error': 'BAD_REQUEST', 'message': 'username, email, and role are required.'}), 400

    # Check for uniqueness
    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({'success': False, 'error': 'CONFLICT', 'message': 'A user with this username or email already exists.'}), 409

    pwd_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(
        username=username,
        email=email,
        phone=phone,
        password_hash=pwd_hash,
        role=role,
        active=True
    )
    db.session.add(new_user)
    db.session.flush()

    # Create associated profile record
    if role == 'student':
        usn = payload.get('usn', username).strip().upper()
        class_id = payload.get('class_id', 1)
        st = Student(
            user_id=new_user.user_id,
            name=name,
            usn=usn,
            class_id=class_id,
            academic_status='active',
            fee_status='paid'
        )
        db.session.add(st)

    elif role in ('teacher', 'hod'):
        emp_id = payload.get('employee_id', f"EMP-{new_user.user_id}")
        dept_id = payload.get('dept_id', 1)
        tc = Teacher(
            user_id=new_user.user_id,
            name=name,
            employee_id=emp_id,
            dept_id=dept_id,
            designation=payload.get('designation', 'Assistant Professor'),
            phone=phone
        )
        db.session.add(tc)

    elif role == 'parent':
        pr = Parent(
            user_id=new_user.user_id,
            name=name,
            phone=phone or '+91 90000 00000',
            email=email
        )
        db.session.add(pr)

    # Log to AuditLog
    audit = AuditLog(
        user_id=request.current_user.user_id,
        role=request.current_user.role,
        action='USER_CREATED',
        target_type='User',
        target_id=new_user.user_id,
        ip=request.remote_addr
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f"User account '{username}' ({role}) created successfully.",
        'data': new_user.to_dict()
    }), 201


@admin_bp.route('/users/<int:user_id>', methods=['PATCH'])
@authenticate()
@require_role('admin')
def update_user(user_id):
    """
    Update user profile or toggle activation status (soft activation / deactivation).
    """
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'success': False, 'error': 'NOT_FOUND', 'message': 'User not found.'}), 404

    payload = request.get_json() or {}
    changes = []

    if 'active' in payload and payload['active'] is not None:
        old_val = user.active
        user.active = bool(payload['active'])
        changes.append(f"active: {old_val} -> {user.active}")

    if 'email' in payload and payload['email']:
        user.email = payload['email'].strip()
        changes.append("email updated")

    if 'phone' in payload:
        user.phone = payload['phone'].strip()
        changes.append("phone updated")

    # Audit logging
    audit = AuditLog(
        user_id=request.current_user.user_id,
        role=request.current_user.role,
        action='USER_UPDATED',
        target_type='User',
        target_id=user.user_id,
        ip=request.remote_addr
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f"User {user.username} updated ({', '.join(changes)}).",
        'data': user.to_dict()
    }), 200


@admin_bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
@authenticate()
@require_role('admin')
def admin_reset_password(user_id):
    """
    Administrative password override for an account.
    """
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'success': False, 'error': 'NOT_FOUND', 'message': 'User not found.'}), 404

    payload = request.get_json() or {}
    new_password = payload.get('new_password', '').strip()

    if not new_password or len(new_password) < 6:
        return jsonify({'success': False, 'error': 'BAD_REQUEST', 'message': 'New password must be at least 6 characters.'}), 400

    user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
    user.login_attempts = 0
    user.locked_until = None

    audit = AuditLog(
        user_id=request.current_user.user_id,
        role=request.current_user.role,
        action='PASSWORD_ADMIN_RESET',
        target_type='User',
        target_id=user.user_id,
        ip=request.remote_addr
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f"Password for {user.username} was reset successfully."
    }), 200


@admin_bp.route('/departments', methods=['GET'])
@authenticate()
@require_role('admin', 'principal')
def get_departments():
    """
    List institutional departments with HoD names and student headcount.
    """
    depts = Department.query.all()
    results = []
    for d in depts:
        hod = db.session.get(Teacher, d.hod_teacher_id) if d.hod_teacher_id else None
        results.append({
            'dept_id': d.dept_id,
            'dept_code': d.dept_code,
            'name': d.name,
            'hod_name': hod.name if hod else 'To Be Assigned',
            'classes_count': len(d.classes),
            'subjects_count': len(d.subjects)
        })

    return jsonify({'success': True, 'data': results}), 200


@admin_bp.route('/classes', methods=['GET'])
@authenticate()
@require_role('admin', 'principal', 'teacher')
def get_classes():
    """
    List all academic classes with assigned mentor and department details.
    """
    classes = Class.query.all()
    results = []
    for c in classes:
        dept = db.session.get(Department, c.dept_id) if c.dept_id else None
        mentor = db.session.get(Teacher, c.mentor_teacher_id) if c.mentor_teacher_id else None
        results.append({
            'class_id': c.class_id,
            'class_name': c.class_name,
            'section': c.section,
            'semester': c.semester,
            'academic_year': c.academic_year,
            'dept_id': c.dept_id,
            'dept_name': dept.name if dept else 'N/A',
            'mentor_id': c.mentor_teacher_id,
            'mentor_name': mentor.name if mentor else 'Unassigned',
            'enrolled_students': c.students.count()
        })

    return jsonify({'success': True, 'data': results}), 200


@admin_bp.route('/classes', methods=['POST'])
@authenticate()
@require_role('admin')
def create_class():
    """
    Create a new class division.
    """
    payload = request.get_json() or {}
    class_name = payload.get('class_name', '').strip()
    section = payload.get('section', 'A').strip().upper()
    semester = payload.get('semester', 1)
    academic_year = payload.get('academic_year', '2024-25').strip()
    dept_id = payload.get('dept_id')
    mentor_teacher_id = payload.get('mentor_teacher_id')

    if not class_name or not dept_id:
        return jsonify({'success': False, 'error': 'BAD_REQUEST', 'message': 'class_name and dept_id are required.'}), 400

    new_class = Class(
        class_name=class_name,
        section=section,
        semester=semester,
        academic_year=academic_year,
        dept_id=dept_id,
        mentor_teacher_id=mentor_teacher_id
    )
    db.session.add(new_class)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Class created successfully.', 'data': new_class.to_dict()}), 201


@admin_bp.route('/subjects', methods=['GET'])
@authenticate()
@require_role('admin', 'principal', 'teacher')
def get_subjects():
    """
    List all curriculum subjects.
    """
    dept_id = request.args.get('dept_id', type=int)
    query = Subject.query
    if dept_id:
        query = query.filter_by(dept_id=dept_id)

    subjects = query.all()
    results = []
    for s in subjects:
        dept = db.session.get(Department, s.dept_id) if s.dept_id else None
        results.append({
            'subject_id': s.subject_id,
            'subject_code': s.subject_code,
            'subject_name': s.subject_name,
            'semester': s.semester,
            'credits': s.credits,
            'dept_name': dept.name if dept else 'N/A'
        })

    return jsonify({'success': True, 'data': results}), 200


@admin_bp.route('/subjects', methods=['POST'])
@authenticate()
@require_role('admin')
def create_subject():
    """
    Create a new syllabus subject.
    """
    payload = request.get_json() or {}
    code = payload.get('subject_code', '').strip().upper()
    name = payload.get('subject_name', '').strip()
    semester = payload.get('semester', 1)
    credits = payload.get('credits', 3)
    dept_id = payload.get('dept_id')

    if not code or not name or not dept_id:
        return jsonify({'success': False, 'error': 'BAD_REQUEST', 'message': 'subject_code, subject_name, dept_id are required.'}), 400

    subj = Subject(
        subject_code=code,
        subject_name=name,
        semester=semester,
        credits=credits,
        dept_id=dept_id
    )
    db.session.add(subj)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Subject created.', 'data': subj.to_dict()}), 201


@admin_bp.route('/assignments', methods=['GET'])
@authenticate()
@require_role('admin', 'principal')
def get_teaching_assignments():
    """
    List all faculty-class-subject mappings.
    """
    assignments = TeacherAssignment.query.all()
    results = []
    for a in assignments:
        t = a.teacher
        c = a.assigned_class
        s = a.assigned_subject
        results.append({
            'id': a.id,
            'teacher_id': a.teacher_id,
            'teacher_name': t.name if t else 'N/A',
            'employee_id': t.employee_id if t else 'N/A',
            'class_id': a.class_id,
            'class_name': c.class_name if c else 'N/A',
            'section': c.section if c else 'A',
            'subject_id': a.subject_id,
            'subject_code': s.subject_code if s else 'N/A',
            'subject_name': s.subject_name if s else 'N/A'
        })

    return jsonify({'success': True, 'data': results}), 200


@admin_bp.route('/assignments', methods=['POST'])
@authenticate()
@require_role('admin')
def create_teaching_assignment():
    """
    Map a teacher to a class and subject.
    """
    payload = request.get_json() or {}
    teacher_id = payload.get('teacher_id')
    class_id = payload.get('class_id')
    subject_id = payload.get('subject_id')

    if not teacher_id or not class_id or not subject_id:
        return jsonify({'success': False, 'error': 'BAD_REQUEST', 'message': 'teacher_id, class_id, and subject_id are required.'}), 400

    existing = TeacherAssignment.query.filter_by(
        teacher_id=teacher_id,
        class_id=class_id,
        subject_id=subject_id
    ).first()

    if existing:
        return jsonify({'success': False, 'error': 'CONFLICT', 'message': 'Teacher is already assigned to this subject and class.'}), 409

    assign = TeacherAssignment(
        teacher_id=teacher_id,
        class_id=class_id,
        subject_id=subject_id
    )
    db.session.add(assign)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Instructional allocation created successfully.', 'data': assign.to_dict()}), 201


@admin_bp.route('/assignments/<int:assignment_id>', methods=['DELETE'])
@authenticate()
@require_role('admin')
def delete_teaching_assignment(assignment_id):
    """
    Delete a faculty teaching allocation.
    """
    assign = db.session.get(TeacherAssignment, assignment_id)
    if not assign:
        return jsonify({'success': False, 'error': 'NOT_FOUND', 'message': 'Assignment not found.'}), 404

    db.session.delete(assign)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Assignment deallocated successfully.'}), 200


@admin_bp.route('/parent-students', methods=['POST'])
@authenticate()
@require_role('admin')
def link_parent_student():
    """
    Create a Parent-to-Child mapping in parent_students.
    """
    payload = request.get_json() or {}
    parent_id = payload.get('parent_id')
    student_id = payload.get('student_id')
    relation = payload.get('relation', 'Parent').strip()

    if not parent_id or not student_id:
        return jsonify({'success': False, 'error': 'BAD_REQUEST', 'message': 'parent_id and student_id are required.'}), 400

    existing = ParentStudent.query.filter_by(parent_id=parent_id, student_id=student_id).first()
    if existing:
        return jsonify({'success': False, 'error': 'CONFLICT', 'message': 'Parent is already linked to this student.'}), 409

    link = ParentStudent(parent_id=parent_id, student_id=student_id, relation=relation)
    db.session.add(link)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Parent-Student mapping registered successfully.'}), 201


@admin_bp.route('/audit-logs', methods=['GET'])
@authenticate()
@require_role('admin', 'principal')
def get_audit_logs():
    """
    Retrieve security audit trail events.
    """
    limit = request.args.get('limit', 1000, type=int)
    action = request.args.get('action')

    query = AuditLog.query
    if action:
        query = query.filter_by(action=action)

    logs = query.order_by(AuditLog.created_at.desc()).limit(limit).all()

    return jsonify({
        'success': True,
        'count': len(logs),
        'data': [log.to_dict() for log in logs]
    }), 200
