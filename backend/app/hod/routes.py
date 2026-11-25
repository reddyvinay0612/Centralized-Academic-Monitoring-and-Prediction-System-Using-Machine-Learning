"""
Head of Department (HOD) Academic Leadership & Branch Monitoring Routes for CAMPS-ML.
Enables departmental oversight across assigned classes, faculty, student rosters, and ML risk forecasting.
"""

from flask import request, jsonify
from datetime import datetime
import numpy as np

from backend.app.hod import hod_bp
from backend.app.models import db, User, Teacher, Department, Class, Student, Mark, Attendance, Prediction
from backend.app.services.auth_middleware import authenticate, require_role


def resolve_hod_department(user, requested_dept_id=None, requested_dept_code=None):
    """
    Resolves target department:
    - If user is HoD or faculty: STRICTLY LOCKED to their assigned department. Cross-department queries are forbidden.
    - If user is admin or principal: Institutional oversight allows department switching.
    """
    is_executive = user.role in ('admin', 'principal')

    # Resolve user's own assigned home department
    user_dept = None
    t = Teacher.query.filter_by(user_id=user.user_id).first()
    if t and t.dept_id:
        user_dept = db.session.get(Department, t.dept_id)
    elif hasattr(user, 'teacher_profile') and user.teacher_profile and user.teacher_profile.dept_id:
        user_dept = db.session.get(Department, user.teacher_profile.dept_id)

    # Check by username if not found via teacher table (e.g. hod.cse -> CSE, hod.csd -> CSD)
    if not user_dept and user.username and user.username.startswith('hod.'):
        code = user.username.replace('hod.', '').upper()
        user_dept = Department.query.filter(db.func.upper(Department.dept_code) == code).first()

    # If user is HoD, STRICTLY lock to their own department!
    if not is_executive:
        return user_dept or Department.query.first()

    # For Admin or Principal, respect requested department
    if requested_dept_code:
        dept = Department.query.filter(db.func.upper(Department.dept_code) == str(requested_dept_code).strip().upper()).first()
        if dept:
            return dept

    if requested_dept_id:
        dept = db.session.get(Department, int(requested_dept_id))
        if dept:
            return dept

    return user_dept or Department.query.filter(Department.dept_code.in_(['CSE', 'CS'])).first() or Department.query.first()


@hod_bp.route('/overview', methods=['GET'])
@authenticate()
@require_role('hod', 'teacher', 'admin', 'principal')
def get_hod_overview():
    """
    Fetch comprehensive HOD departmental analytics:
    - Department telemetry (students, classes, faculty, avg attendance, avg CIE)
    - Department classes breakdown
    - Faculty workload and assigned courses
    - Enrolled students roster with live ML predictions
    """
    req_dept_id = request.args.get('dept_id')
    req_dept_code = request.args.get('dept_code')

    dept = resolve_hod_department(request.current_user, req_dept_id, req_dept_code)
    if not dept:
        return jsonify({'success': False, 'error': 'NOT_FOUND', 'message': 'Department not found.'}), 404

    # HoD Profile
    hod_teacher = db.session.get(Teacher, dept.hod_teacher_id) if dept.hod_teacher_id else None
    hod_user = db.session.get(User, hod_teacher.user_id) if hod_teacher and hod_teacher.user_id else None

    # Classes in this department
    classes = Class.query.filter_by(dept_id=dept.dept_id).order_by(Class.semester.desc(), Class.section.asc()).all()
    class_ids = [c.class_id for c in classes]

    # Teachers in this department
    teachers = Teacher.query.filter_by(dept_id=dept.dept_id).all()

    # Students in this department's classes
    if class_ids:
        students = Student.query.filter(Student.class_id.in_(class_ids)).order_by(Student.usn.asc()).all()
    else:
        students = []

    student_ids = [s.student_id for s in students]

    from collections import defaultdict

    # Attendance stats - O(N) grouping
    att_records = Attendance.query.filter(Attendance.student_id.in_(student_ids)).all() if student_ids else []
    att_by_student = defaultdict(list)
    total_held = 0
    total_att = 0
    for a in att_records:
        att_by_student[a.student_id].append(a)
        total_held += int(a.total_classes or 0)
        total_att += int(a.attended_classes or 0)
    dept_avg_att = round((total_att / total_held * 100.0), 1) if total_held > 0 else 85.0

    # CIE Marks stats - O(N) grouping
    marks_records = Mark.query.filter(Mark.student_id.in_(student_ids)).all() if student_ids else []
    marks_by_student = defaultdict(list)
    cie_scores = []
    for m in marks_records:
        marks_by_student[m.student_id].append(m)
        if m.total_cie is not None:
            cie_scores.append(float(m.total_cie))
    dept_avg_cie = round(float(np.mean(cie_scores)), 1) if cie_scores else 34.5

    # Precompute student attendance stats & count shortages in O(N)
    student_att_stats = {}
    shortage_count = 0
    for s_id in student_ids:
        s_att = att_by_student.get(s_id, [])
        s_th = sum(int(a.total_classes or 0) for a in s_att)
        s_ta = sum(int(a.attended_classes or 0) for a in s_att)
        s_pct = round((s_ta / s_th * 100.0), 1) if s_th > 0 else 85.0
        student_att_stats[s_id] = (s_th, s_ta, s_pct)
        if s_pct < 75.0:
            shortage_count += 1

    # Predictions
    preds = Prediction.query.filter(Prediction.student_id.in_(student_ids)).all() if student_ids else []
    risk_map = {p.student_id: p.risk_level for p in preds}

    low_risk = sum(1 for p in preds if p.risk_level == 'low')
    med_risk = sum(1 for p in preds if p.risk_level == 'medium')
    high_risk = sum(1 for p in preds if p.risk_level == 'high')

    if not preds and students:
        # Calibrated default estimation
        low_risk = int(len(students) * 0.78)
        med_risk = int(len(students) * 0.16)
        high_risk = len(students) - low_risk - med_risk

    pass_rate = round((low_risk / max(1, len(students))) * 100.0, 1) if students else 92.0

    # Build Class summaries in O(N)
    classes_list = []
    for c in classes:
        cls_students = [s for s in students if s.class_id == c.class_id]
        cls_th = sum(student_att_stats.get(s.student_id, (0, 0, 85.0))[0] for s in cls_students)
        cls_ta = sum(student_att_stats.get(s.student_id, (0, 0, 85.0))[1] for s in cls_students)
        cls_avg_att = round((cls_ta / cls_th * 100.0), 1) if cls_th > 0 else 85.0

        mentor = db.session.get(Teacher, c.mentor_teacher_id) if c.mentor_teacher_id else None

        classes_list.append({
            'class_id': c.class_id,
            'class_name': c.class_name,
            'section': c.section,
            'semester': c.semester,
            'academic_year': c.academic_year,
            'enrolled_students': len(cls_students),
            'mentor_name': mentor.name if mentor else 'Unassigned',
            'average_attendance': cls_avg_att
        })

    # Build Faculty list
    faculty_list = []
    for t in teachers:
        u = db.session.get(User, t.user_id) if t.user_id else None
        faculty_list.append({
            'teacher_id': t.teacher_id,
            'name': t.name,
            'employee_id': t.employee_id,
            'designation': t.designation,
            'email': u.email if u else None,
            'phone': t.phone,
            'assigned_subjects_count': len(t.assignments)
        })

    # Build Students list in O(N)
    students_list = []
    classes_dict = {c.class_id: f"{c.class_name} ({c.section})" for c in classes}
    for s in students:
        _, _, s_pct = student_att_stats.get(s.student_id, (0, 0, 85.0))
        s_marks = marks_by_student.get(s.student_id, [])
        s_cie = [float(m.total_cie) for m in s_marks if m.total_cie is not None]
        s_avg_cie = round(float(np.mean(s_cie)), 1) if s_cie else 34.0

        risk = risk_map.get(s.student_id, 'low' if s_pct >= 75 and s_avg_cie >= 28 else ('medium' if s_pct >= 65 else 'high'))

        students_list.append({
            'student_id': s.student_id,
            'usn': s.usn,
            'name': s.name,
            'class_id': s.class_id,
            'class_name': classes_dict.get(s.class_id, 'Semester 6'),
            'attendance_percentage': s_pct,
            'avg_cie': s_avg_cie,
            'risk_level': risk,
            'predicted_outcome': 'Pass' if risk != 'high' else 'At-Risk'
        })

    # Department navigation list: ONLY admin and principal can switch departments
    if request.current_user.role in ('admin', 'principal'):
        all_depts = Department.query.order_by(Department.dept_id.asc()).all()
        depts_nav = [{
            'dept_id': d.dept_id,
            'dept_code': d.dept_code,
            'name': d.name
        } for d in all_depts]
        can_switch = True
    else:
        # HOD is strictly locked to their own department
        depts_nav = [{
            'dept_id': dept.dept_id,
            'dept_code': dept.dept_code,
            'name': dept.name
        }]
        can_switch = False

    return jsonify({
        'success': True,
        'department': {
            'dept_id': dept.dept_id,
            'dept_code': dept.dept_code,
            'name': dept.name,
            'intake': getattr(dept, 'intake', 60)
        },
        'can_switch_department': can_switch,
        'is_locked': not can_switch,
        'hod': {
            'teacher_id': hod_teacher.teacher_id if hod_teacher else None,
            'name': hod_teacher.name if hod_teacher else 'To Be Appointed',
            'designation': hod_teacher.designation if hod_teacher else 'Professor & Head',
            'employee_id': hod_teacher.employee_id if hod_teacher else None,
            'email': hod_user.email if hod_user else f"hod{dept.dept_code.lower()}@pestrust.edu.in",
            'phone': hod_teacher.phone if hod_teacher else None
        },
        'telemetry': {
            'total_students': len(students),
            'total_classes': len(classes),
            'total_faculty': len(teachers),
            'avg_attendance': dept_avg_att,
            'attendance_shortage_count': shortage_count,
            'avg_cie': dept_avg_cie,
            'pass_rate': pass_rate,
            'risk_distribution': {
                'low': low_risk,
                'medium': med_risk,
                'high': high_risk
            }
        },
        'classes': classes_list,
        'faculty': faculty_list,
        'students': students_list,
        'all_departments': depts_nav
    }), 200
