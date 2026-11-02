import io
import csv
from datetime import datetime
from flask import Blueprint, jsonify, request, send_file, Response
from backend.extensions import db
from backend.app.services.auth_middleware import authenticate, require_role
from backend.app.models import (
    User, Teacher, Class, Department, Subject, Student,
    TeacherAssignment, Attendance, Mark, MarkHistory,
    SemesterResult, Notification, Alert, Remark, Prediction, AuditLog
)

teachers_bp = Blueprint('teachers', __name__)

def get_current_teacher_record(current_user):
    """Resolve Teacher model record for the authenticated user"""
    if current_user.role in ('teacher', 'hod'):
        return Teacher.query.filter_by(user_id=current_user.user_id).first()
    return None

def verify_teacher_class_access(current_user, class_id):
    """
    Ensures that current_user has access to the specified class_id:
    - Teacher: must be assigned to this class or be its mentor.
    - HoD: class must belong to their department.
    - Admin/Principal: full college-wide access.
    Returns: (is_authorized: bool, class_or_error_response)
    """
    target_class = db.session.get(Class, class_id)
    if not target_class:
        return False, (jsonify({'success': False, 'error': 'NOT_FOUND', 'message': 'Class not found.'}), 404)

    if current_user.role in ('principal', 'admin'):
        return True, target_class

    teacher = get_current_teacher_record(current_user)
    if not teacher:
        return False, (jsonify({'success': False, 'error': 'NOT_FOUND', 'message': 'Teacher profile not linked.'}), 404)

    # HoD department check
    if current_user.role == 'hod' and target_class.dept_id == teacher.dept_id:
        return True, target_class

    # Check mentor assignment
    if target_class.mentor_teacher_id == teacher.teacher_id:
        return True, target_class

    # Check subject teaching assignment
    assignment = TeacherAssignment.query.filter_by(
        teacher_id=teacher.teacher_id,
        class_id=target_class.class_id
    ).first()

    if assignment:
        return True, target_class

    return False, (jsonify({'success': False, 'error': 'FORBIDDEN', 'message': 'You are not assigned to instruct or mentor this class.'}), 403)


@teachers_bp.route('/status', methods=['GET'])
def teacher_status():
    return jsonify({
        'module': 'Teacher Portal API',
        'status': 'active',
        'endpoints': [
            '/api/teacher/classes',
            '/api/teacher/classes/<id>/students',
            '/api/teacher/marks/<id>',
            '/api/teacher/marks/<id>/history',
            '/api/teacher/attendance',
            '/api/teacher/upload',
            '/api/teacher/notify',
            '/api/teacher/remarks'
        ]
    }), 200


@teachers_bp.route('/classes', methods=['GET'])
@authenticate()
@require_role('teacher', 'hod', 'admin', 'principal')
def get_teacher_classes():
    """
    Fetch all classes and subjects assigned to this faculty member with live telemetry:
    total students, class average attendance, average CIE, count of at-risk students.
    """
    teacher = get_current_teacher_record(request.current_user)

    if not teacher and request.current_user.role in ('admin', 'principal'):
        teacher = Teacher.query.first()

    if not teacher:
        return jsonify({'success': False, 'error': 'NOT_FOUND', 'message': 'Teacher profile not found.'}), 404

    # Determine assigned units
    assignments = teacher.assignments
    results = []

    for assign in assignments:
        cls = assign.assigned_class
        subj = assign.assigned_subject
        if not cls or not subj:
            continue

        students = cls.students.all()
        total_enrolled = len(students)
        student_ids = [s.student_id for s in students]

        # Calculate subject-specific attendance stats
        att_records = Attendance.query.filter(
            Attendance.subject_id == subj.subject_id,
            Attendance.student_id.in_(student_ids) if student_ids else False
        ).all()

        avg_att = round(sum(float(a.percentage) for a in att_records) / len(att_records), 2) if att_records else 0.0
        shortage_count = sum(1 for a in att_records if float(a.percentage) < 75.0)

        # Calculate CIE stats
        marks_records = Mark.query.filter(
            Mark.subject_id == subj.subject_id,
            Mark.student_id.in_(student_ids) if student_ids else False
        ).all()

        avg_cie = round(sum(float(m.total_cie) for m in marks_records) / len(marks_records), 2) if marks_records else 0.0

        # High/Medium Risk count
        predictions = Prediction.query.filter(
            Prediction.student_id.in_(student_ids) if student_ids else False
        ).all()

        at_risk_count = sum(1 for p in predictions if p.risk_level in ('high', 'medium'))

        results.append({
            'assignment_id': assign.id,
            'class_id': cls.class_id,
            'class_name': cls.class_name,
            'section': cls.section,
            'semester': cls.semester,
            'academic_year': cls.academic_year,
            'subject_id': subj.subject_id,
            'subject_code': subj.subject_code,
            'subject_name': subj.subject_name,
            'credits': subj.credits,
            'is_mentor': cls.mentor_teacher_id == teacher.teacher_id,
            'metrics': {
                'total_students': total_enrolled,
                'average_attendance': avg_att,
                'shortage_count': shortage_count,
                'average_cie': avg_cie,
                'max_cie': 50.0,
                'at_risk_count': at_risk_count
            }
        })

    return jsonify({
        'success': True,
        'teacher': {
            'teacher_id': teacher.teacher_id,
            'name': teacher.name,
            'employee_id': teacher.employee_id,
            'designation': teacher.designation,
            'department_id': teacher.dept_id
        },
        'count': len(results),
        'data': results
    }), 200


@teachers_bp.route('/classes/<int:class_id>/students', methods=['GET'])
@authenticate()
@require_role('teacher', 'hod', 'admin', 'principal')
def get_class_roster(class_id):
    """
    Fetch student roster for a given assigned class with search and risk filters.
    """
    is_auth, cls = verify_teacher_class_access(request.current_user, class_id)
    if not is_auth:
        return cls

    subject_id = request.args.get('subject_id', type=int)
    risk_filter = request.args.get('risk_level')  # 'high', 'medium', 'low'
    search_query = request.args.get('search', '').strip().lower()

    # If subject_id not passed, pick first assigned subject for this class
    teacher = get_current_teacher_record(request.current_user)
    if not subject_id and teacher:
        assign = TeacherAssignment.query.filter_by(teacher_id=teacher.teacher_id, class_id=cls.class_id).first()
        if assign:
            subject_id = assign.subject_id

    query = cls.students
    students = query.all()

    roster = []
    for s in students:
        if search_query and search_query not in s.name.lower() and search_query not in s.usn.lower():
            continue

        # Load subject attendance
        att = Attendance.query.filter_by(student_id=s.student_id, subject_id=subject_id).first() if subject_id else None
        att_pct = float(att.percentage) if att else 0.0

        # Load subject CIE marks
        mark = Mark.query.filter_by(student_id=s.student_id, subject_id=subject_id).first() if subject_id else None

        # Load ML Risk Prediction
        pred = Prediction.query.filter_by(student_id=s.student_id).order_by(Prediction.generated_at.desc()).first()
        r_level = pred.risk_level if pred else ('high' if att_pct < 65 else ('medium' if att_pct < 75 else 'low'))

        if risk_filter and risk_filter.lower() != 'all' and r_level.lower() != risk_filter.lower():
            continue

        roster.append({
            'student_id': s.student_id,
            'name': s.name,
            'usn': s.usn,
            'academic_status': s.academic_status,
            'fee_status': s.fee_status,
            'attendance': {
                'attendance_id': att.attendance_id if att else None,
                'total_classes': att.total_classes if att else 0,
                'attended_classes': att.attended_classes if att else 0,
                'percentage': att_pct,
                'is_shortage': att_pct < 75.0
            },
            'marks': {
                'marks_id': mark.marks_id if mark else None,
                'cie1': float(mark.cie1) if mark else 0.0,
                'cie2': float(mark.cie2) if mark else 0.0,
                'cie3': float(mark.cie3) if mark else 0.0,
                'assignment_marks': float(mark.assignment_marks) if mark else 0.0,
                'quiz_marks': float(mark.quiz_marks) if mark else 0.0,
                'total_cie': float(mark.total_cie) if mark else 0.0,
                'is_passing': float(mark.total_cie or 0) >= 20.0 if mark else False
            },
            'prediction': {
                'risk_level': r_level,
                'risk_score': float(pred.risk_score) if pred else 0.2,
                'predicted_outcome': pred.predicted_outcome if pred else 'Pass',
                'predicted_sgpa': float(pred.predicted_sgpa) if pred and pred.predicted_sgpa else 7.5
            }
        })

    return jsonify({
        'success': True,
        'class_id': cls.class_id,
        'class_name': cls.class_name,
        'section': cls.section,
        'subject_id': subject_id,
        'total_count': len(roster),
        'data': roster
    }), 200


@teachers_bp.route('/marks/<int:marks_id>', methods=['PATCH'])
@authenticate()
@require_role('teacher', 'hod', 'admin', 'principal')
def update_student_marks(marks_id):
    """
    Update CIE marks with mandatory audit logging to mark_history.
    Requires 'reason' in JSON payload.
    """
    mark = db.session.get(Mark, marks_id)
    if not mark:
        return jsonify({'success': False, 'error': 'NOT_FOUND', 'message': 'Marks record not found.'}), 404

    payload = request.get_json() or {}
    reason = payload.get('reason', '').strip()

    if not reason:
        return jsonify({
            'success': False,
            'error': 'VALIDATION_ERROR',
            'message': 'A reason for marks alteration is strictly mandatory for institutional audit compliance.'
        }), 400

    student = db.session.get(Student, mark.student_id)
    is_auth, cls = verify_teacher_class_access(request.current_user, student.class_id)
    if not is_auth:
        return cls

    # Track fields to update
    fields = ['cie1', 'cie2', 'cie3', 'assignment_marks', 'quiz_marks']
    audit_entries = []

    for f in fields:
        if f in payload and payload[f] is not None:
            new_val = round(float(payload[f]), 1)
            old_val = float(getattr(mark, f) or 0.0)

            if new_val != old_val:
                setattr(mark, f, new_val)
                # Create MarkHistory record
                h = MarkHistory(
                    marks_id=mark.marks_id,
                    field_name=f,
                    old_value=old_val,
                    new_value=new_val,
                    changed_by=request.current_user.user_id,
                    reason=reason
                )
                db.session.add(h)
                audit_entries.append({'field': f, 'old': old_val, 'new': new_val})

    # Recalculate total CIE
    old_tot = float(mark.total_cie or 0.0)
    new_tot = mark.calculate_total()

    if new_tot != old_tot:
        h_tot = MarkHistory(
            marks_id=mark.marks_id,
            field_name='total_cie',
            old_value=old_tot,
            new_value=new_tot,
            changed_by=request.current_user.user_id,
            reason=f"Recalculated VTU CIE aggregate: {reason}"
        )
        db.session.add(h_tot)
        audit_entries.append({'field': 'total_cie', 'old': old_tot, 'new': new_tot})

    # Log to System AuditLog
    audit_sys = AuditLog(
        user_id=request.current_user.user_id,
        role=request.current_user.role,
        action='MARKS_UPDATE',
        target_type='Student',
        target_id=student.student_id,
        ip=request.remote_addr
    )
    db.session.add(audit_sys)

    mark.last_updated = datetime.utcnow()
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f"Marks successfully updated with {len(audit_entries)} audit trail entries recorded.",
        'data': mark.to_dict(),
        'audit_trail': audit_entries
    }), 200


@teachers_bp.route('/marks/<int:marks_id>/history', methods=['GET'])
@authenticate()
@require_role('teacher', 'hod', 'admin', 'principal')
def get_marks_history(marks_id):
    """
    Fetch the complete audit log of modifications made to a mark entry.
    """
    mark = db.session.get(Mark, marks_id)
    if not mark:
        return jsonify({'success': False, 'error': 'NOT_FOUND', 'message': 'Marks record not found.'}), 404

    history = MarkHistory.query.filter_by(marks_id=marks_id).order_by(MarkHistory.changed_at.desc()).all()

    return jsonify({
        'success': True,
        'marks_id': marks_id,
        'data': [h.to_dict() for h in history]
    }), 200


@teachers_bp.route('/attendance', methods=['POST'])
@authenticate()
@require_role('teacher', 'hod', 'admin', 'principal')
def log_session_attendance():
    """
    Log attendance for an academic lecture session.
    Payload: { class_id: int, subject_id: int, date: str, attendance_list: [{ student_id: int, is_present: bool }] }
    """
    payload = request.get_json() or {}
    class_id = payload.get('class_id')
    subject_id = payload.get('subject_id')
    att_list = payload.get('attendance_list', [])

    if not class_id or not subject_id or not att_list:
        return jsonify({
            'success': False,
            'error': 'BAD_REQUEST',
            'message': 'class_id, subject_id, and attendance_list are required.'
        }), 400

    is_auth, cls = verify_teacher_class_access(request.current_user, class_id)
    if not is_auth:
        return cls

    subj = db.session.get(Subject, subject_id)
    if not subj:
        return jsonify({'success': False, 'error': 'NOT_FOUND', 'message': 'Subject not found.'}), 404

    updated_count = 0
    shortage_alerts_triggered = 0

    for item in att_list:
        s_id = item.get('student_id')
        is_present = item.get('is_present', False)

        record = Attendance.query.filter_by(student_id=s_id, subject_id=subject_id).first()
        if not record:
            record = Attendance(
                student_id=s_id,
                subject_id=subject_id,
                total_classes=0,
                attended_classes=0,
                percentage=0.0
            )
            db.session.add(record)

        record.total_classes += 1
        if is_present:
            record.attended_classes += 1

        new_pct = record.calculate_percentage()
        record.last_updated = datetime.utcnow()
        updated_count += 1

        # Check if dropped into shortage (<75%)
        if new_pct < 75.0:
            existing_alert = Alert.query.filter_by(student_id=s_id, status='open').first()
            if not existing_alert:
                alert = Alert(
                    student_id=s_id,
                    risk_level='medium' if new_pct >= 65 else 'high',
                    reason=f"Attendance in {subj.subject_name} is below 75% ({new_pct}%).",
                    status='open'
                )
                db.session.add(alert)
                shortage_alerts_triggered += 1

    db.session.commit()

    return jsonify({
        'success': True,
        'message': f"Session attendance successfully recorded for {updated_count} students.",
        'shortage_alerts_triggered': shortage_alerts_triggered
    }), 200


@teachers_bp.route('/upload', methods=['POST'])
@authenticate()
@require_role('teacher', 'hod', 'admin', 'principal')
def batch_upload_data():
    """
    Ingest marks or attendance data via CSV upload with row-by-row validation.
    """
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'BAD_REQUEST', 'message': 'No CSV file uploaded.'}), 400

    file = request.files['file']
    upload_type = request.form.get('upload_type', 'marks')  # 'marks' or 'attendance'
    class_id = request.form.get('class_id', type=int)
    subject_id = request.form.get('subject_id', type=int)

    if not class_id or not subject_id:
        return jsonify({'success': False, 'error': 'BAD_REQUEST', 'message': 'class_id and subject_id are required.'}), 400

    is_auth, cls = verify_teacher_class_access(request.current_user, class_id)
    if not is_auth:
        return cls

    try:
        stream = io.StringIO(file.stream.read().decode('utf-8-sig'), newline=None)
        reader = csv.DictReader(stream)
    except Exception as e:
        return jsonify({'success': False, 'error': 'PARSE_ERROR', 'message': f'Failed to parse CSV: {str(e)}'}), 400

    processed_count = 0
    errors = []

    for row_idx, row in enumerate(reader, start=2):
        # Normalize keys to lower case
        row_clean = {k.strip().lower(): v.strip() for k, v in row.items() if k}
        usn = row_clean.get('usn')

        if not usn:
            errors.append({'row': row_idx, 'error': 'Missing USN.'})
            continue

        student = Student.query.filter_by(usn=usn).first()
        if not student or student.class_id != class_id:
            errors.append({'row': row_idx, 'usn': usn, 'error': 'Student not found in this class.'})
            continue

        if upload_type == 'marks':
            try:
                cie1 = float(row_clean.get('cie1', 0))
                cie2 = float(row_clean.get('cie2', 0))
                cie3 = float(row_clean.get('cie3', 0))
                assign = float(row_clean.get('assignment', row_clean.get('assign', 0)))
                quiz = float(row_clean.get('quiz', 0))

                mark = Mark.query.filter_by(student_id=student.student_id, subject_id=subject_id).first()
                if not mark:
                    mark = Mark(student_id=student.student_id, subject_id=subject_id)
                    db.session.add(mark)

                mark.cie1 = cie1
                mark.cie2 = cie2
                mark.cie3 = cie3
                mark.assignment_marks = assign
                mark.quiz_marks = quiz
                mark.calculate_total()
                mark.last_updated = datetime.utcnow()
                processed_count += 1
            except ValueError as ve:
                errors.append({'row': row_idx, 'usn': usn, 'error': f'Invalid numeric mark: {str(ve)}'})

        elif upload_type == 'attendance':
            try:
                total_cls = int(row_clean.get('total_classes', 0))
                att_cls = int(row_clean.get('attended_classes', 0))

                record = Attendance.query.filter_by(student_id=student.student_id, subject_id=subject_id).first()
                if not record:
                    record = Attendance(student_id=student.student_id, subject_id=subject_id)
                    db.session.add(record)

                record.total_classes = total_cls
                record.attended_classes = att_cls
                record.calculate_percentage()
                record.last_updated = datetime.utcnow()
                processed_count += 1
            except ValueError as ve:
                errors.append({'row': row_idx, 'usn': usn, 'error': f'Invalid attendance integer: {str(ve)}'})

    db.session.commit()

    return jsonify({
        'success': True,
        'message': f"Batch upload completed: {processed_count} records processed successfully.",
        'processed_count': processed_count,
        'error_count': len(errors),
        'errors': errors
    }), 200


@teachers_bp.route('/notify', methods=['POST'])
@authenticate()
@require_role('teacher', 'hod', 'admin', 'principal')
def notify_students_and_parents():
    """
    Transmit academic notices or alerts to individual students, selected students, or whole classes,
    with automatic forwarding to registered parents.
    """
    payload = request.get_json() or {}
    class_id = payload.get('class_id')
    student_ids = payload.get('student_ids', [])
    subject = payload.get('subject', 'Faculty Academic Notice').strip()
    message_text = payload.get('message', '').strip()
    notify_parents = payload.get('send_to_parent', True)

    if not class_id or not message_text:
        return jsonify({'success': False, 'error': 'BAD_REQUEST', 'message': 'class_id and message are required.'}), 400

    is_auth, cls = verify_teacher_class_access(request.current_user, class_id)
    if not is_auth:
        return cls

    # If student_ids is empty or 'all', select all students in the class
    if not student_ids or student_ids == 'all':
        target_students = cls.students.all()
    else:
        target_students = Student.query.filter(Student.student_id.in_(student_ids), Student.class_id == class_id).all()

    teacher = get_current_teacher_record(request.current_user)
    teacher_name = teacher.name if teacher else 'Faculty'
    dispatched_count = 0

    for s in target_students:
        # 1. Notify Student
        notif_student = Notification(
            sender_id=request.current_user.user_id,
            recipient_user_id=s.user_id,
            student_id=s.student_id,
            title=f"Faculty Notice: {subject}",
            message=f"From {teacher_name} ({cls.class_name}):\n\n{message_text}",
            channel='in_app',
            status='sent'
        )
        db.session.add(notif_student)
        dispatched_count += 1

        # 2. Forward to Parent(s) if enabled
        if notify_parents:
            for p in s.parents:
                notif_parent = Notification(
                    sender_id=request.current_user.user_id,
                    recipient_user_id=p.user_id,
                    student_id=s.student_id,
                    title=f"Academic Notice regarding {s.name} ({s.usn}): {subject}",
                    message=f"Dear Parent,\n\nFrom {teacher_name}:\n{message_text}",
                    channel='in_app',
                    status='sent'
                )
                db.session.add(notif_parent)
                dispatched_count += 1

    db.session.commit()

    return jsonify({
        'success': True,
        'message': f"Successfully transmitted notice to {len(target_students)} student(s) with {dispatched_count} total messages generated.",
        'dispatched_count': dispatched_count
    }), 201


@teachers_bp.route('/remarks', methods=['POST'])
@authenticate()
@require_role('teacher', 'hod', 'admin', 'principal')
def create_teacher_remark():
    """
    Log an official academic remark or mentorship observation on a student.
    """
    payload = request.get_json() or {}
    student_id = payload.get('student_id')
    remark_text = payload.get('remark_text', '').strip()
    action_taken = payload.get('action_taken', '').strip()

    if not student_id or not remark_text:
        return jsonify({'success': False, 'error': 'BAD_REQUEST', 'message': 'student_id and remark_text are required.'}), 400

    student = db.session.get(Student, student_id)
    if not student:
        return jsonify({'success': False, 'error': 'NOT_FOUND', 'message': 'Student not found.'}), 404

    is_auth, cls = verify_teacher_class_access(request.current_user, student.class_id)
    if not is_auth:
        return cls

    teacher = get_current_teacher_record(request.current_user)
    if not teacher and request.current_user.role in ('admin', 'principal'):
        teacher = Teacher.query.first()

    rem = Remark(
        student_id=student.student_id,
        teacher_id=teacher.teacher_id,
        remark_text=remark_text,
        action_taken=action_taken or None
    )
    db.session.add(rem)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Mentorship remark successfully recorded.',
        'data': rem.to_dict()
    }), 201


@teachers_bp.route('/marks/bulk', methods=['POST'])
@authenticate()
@require_role('teacher', 'hod', 'admin', 'principal')
def bulk_update_student_marks():
    """
    Bulk/Matrix CIE Marks Entry across an entire class cohort with VTU best-of-2
    aggregation and mandatory institutional audit reason.
    """
    payload = request.get_json() or {}
    class_id = payload.get('class_id')
    subject_id = payload.get('subject_id')
    reason = payload.get('reason', '').strip()
    marks_list = payload.get('marks', [])

    if not class_id or not subject_id or not marks_list:
        return jsonify({
            'success': False,
            'error': 'BAD_REQUEST',
            'message': 'class_id, subject_id, and marks array are required.'
        }), 400

    if not reason:
        return jsonify({
            'success': False,
            'error': 'VALIDATION_ERROR',
            'message': 'A justification reason for bulk marks modification is mandatory for institutional audit compliance.'
        }), 400

    is_auth, cls = verify_teacher_class_access(request.current_user, class_id)
    if not is_auth:
        return cls

    subj = db.session.get(Subject, subject_id)
    if not subj:
        return jsonify({'success': False, 'error': 'NOT_FOUND', 'message': 'Subject not found.'}), 404

    updated_students = 0
    total_audit_entries = 0
    fields = ['cie1', 'cie2', 'cie3', 'assignment_marks', 'quiz_marks']

    for item in marks_list:
        student_id = item.get('student_id')
        if not student_id:
            continue

        student = db.session.get(Student, student_id)
        if not student or student.class_id != class_id:
            continue

        mark = Mark.query.filter_by(student_id=student_id, subject_id=subject_id).first()
        if not mark:
            mark = Mark(
                student_id=student_id,
                subject_id=subject_id,
                cie1=0.0,
                cie2=0.0,
                cie3=0.0,
                assignment_marks=0.0,
                quiz_marks=0.0,
                total_cie=0.0
            )
            db.session.add(mark)

        student_modified = False
        for f in fields:
            if f in item and item[f] is not None:
                try:
                    val = round(float(item[f]), 1)
                    # Clamping
                    if f in ('cie1', 'cie2', 'cie3'):
                        val = max(0.0, min(50.0, val))
                    else:
                        val = max(0.0, min(10.0, val))

                    old_val = float(getattr(mark, f) or 0.0)
                    if val != old_val:
                        setattr(mark, f, val)
                        h = MarkHistory(
                            marks_id=mark.marks_id,
                            field_name=f,
                            old_value=old_val,
                            new_value=val,
                            changed_by=request.current_user.user_id,
                            reason=reason
                        )
                        db.session.add(h)
                        total_audit_entries += 1
                        student_modified = True
                except (ValueError, TypeError):
                    continue

        if student_modified:
            old_tot = float(mark.total_cie or 0.0)
            new_tot = mark.calculate_total()
            if new_tot != old_tot:
                h_tot = MarkHistory(
                    marks_id=mark.marks_id,
                    field_name='total_cie',
                    old_value=old_tot,
                    new_value=new_tot,
                    changed_by=request.current_user.user_id,
                    reason=f"Bulk recalculated VTU CIE: {reason}"
                )
                db.session.add(h_tot)
                total_audit_entries += 1
            mark.last_updated = datetime.utcnow()
        updated_students += 1

    # Log to System AuditLog
    audit_sys = AuditLog(
        user_id=request.current_user.user_id,
        role=request.current_user.role,
        action='BULK_MARKS_UPDATE',
        target_type='Class',
        target_id=class_id,
        ip=request.remote_addr
    )
    db.session.add(audit_sys)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f"Bulk CIE assessment saved for {updated_students} students with {total_audit_entries} audit entries.",
        'updated_students': updated_students,
        'audit_entries': total_audit_entries
    }), 200


@teachers_bp.route('/classes/<int:class_id>/subjects/<int:subject_id>/marks/template', methods=['GET'])
@authenticate()
@require_role('teacher', 'hod', 'admin', 'principal')
def download_marks_csv_template(class_id, subject_id):
    """
    Generate and stream a pre-populated CSV template with the class roster for bulk offline entry.
    """
    is_auth, cls = verify_teacher_class_access(request.current_user, class_id)
    if not is_auth:
        return cls

    subj = db.session.get(Subject, subject_id)
    if not subj:
        return jsonify({'success': False, 'error': 'NOT_FOUND', 'message': 'Subject not found.'}), 404

    students = Student.query.filter_by(class_id=class_id).order_by(Student.usn).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['USN', 'Student_Name', 'CIE1_Out_Of_50', 'CIE2_Out_Of_50', 'CIE3_Out_Of_50', 'Assignment_Out_Of_10', 'Quiz_Out_Of_10'])

    for s in students:
        mark = Mark.query.filter_by(student_id=s.student_id, subject_id=subject_id).first()
        writer.writerow([
            s.usn,
            s.name,
            float(mark.cie1) if mark else 0.0,
            float(mark.cie2) if mark else 0.0,
            float(mark.cie3) if mark else 0.0,
            float(mark.assignment_marks) if mark else 0.0,
            float(mark.quiz_marks) if mark else 0.0
        ])

    csv_data = output.getvalue()
    filename = f"Marks_Template_Class_{cls.class_name.replace(' ', '_')}_{subj.subject_code}.csv"
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'}
    )


@teachers_bp.route('/classes/<int:class_id>/subjects/<int:subject_id>/attendance/template', methods=['GET'])
@authenticate()
@require_role('teacher', 'hod', 'admin', 'principal')
def download_attendance_csv_template(class_id, subject_id):
    """
    Generate and stream an attendance CSV template for bulk offline logging.
    """
    is_auth, cls = verify_teacher_class_access(request.current_user, class_id)
    if not is_auth:
        return cls

    subj = db.session.get(Subject, subject_id)
    if not subj:
        return jsonify({'success': False, 'error': 'NOT_FOUND', 'message': 'Subject not found.'}), 404

    students = Student.query.filter_by(class_id=class_id).order_by(Student.usn).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['USN', 'Student_Name', 'Classes_Held', 'Classes_Attended'])

    for s in students:
        att = Attendance.query.filter_by(student_id=s.student_id, subject_id=subject_id).first()
        writer.writerow([
            s.usn,
            s.name,
            att.total_classes if att else 0,
            att.attended_classes if att else 0
        ])

    csv_data = output.getvalue()
    filename = f"Attendance_Template_Class_{cls.class_name.replace(' ', '_')}_{subj.subject_code}.csv"
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'}
    )


@teachers_bp.route('/classes/<int:class_id>/subjects/<int:subject_id>/audit-history', methods=['GET'])
@authenticate()
@require_role('teacher', 'hod', 'admin', 'principal')
def get_class_subject_audit_history(class_id, subject_id):
    """
    Fetch comprehensive chronological audit trail of all mark changes in this class and subject.
    """
    is_auth, cls = verify_teacher_class_access(request.current_user, class_id)
    if not is_auth:
        return cls

    # Get all marks for students in this class and subject
    students = Student.query.filter_by(class_id=class_id).all()
    s_ids = [s.student_id for s in students]

    marks = Mark.query.filter(Mark.student_id.in_(s_ids), Mark.subject_id == subject_id).all()
    m_ids = [m.marks_id for m in marks]

    if not m_ids:
        return jsonify({'success': True, 'data': []}), 200

    history_records = MarkHistory.query.filter(MarkHistory.marks_id.in_(m_ids)).order_by(MarkHistory.changed_at.desc()).limit(150).all()

    results = []
    # Map for fast lookup
    mark_map = {m.marks_id: m for m in marks}
    student_map = {s.student_id: s for s in students}

    for h in history_records:
        mark = mark_map.get(h.marks_id)
        student = student_map.get(mark.student_id) if mark else None
        modifier = db.session.get(User, h.changed_by) if h.changed_by else None

        results.append({
            'history_id': h.id,
            'marks_id': h.marks_id,
            'student_name': student.name if student else 'Unknown',
            'usn': student.usn if student else 'N/A',
            'field_name': h.field_name,
            'old_value': float(h.old_value) if h.old_value is not None else 0.0,
            'new_value': float(h.new_value) if h.new_value is not None else 0.0,
            'changed_by': modifier.username if modifier else 'System',
            'changed_by_role': modifier.role if modifier else 'N/A',
            'reason': h.reason,
            'changed_at': h.changed_at.isoformat() if h.changed_at else None
        })

    return jsonify({'success': True, 'count': len(results), 'data': results}), 200


@teachers_bp.route('/attendance/<int:attendance_id>', methods=['PATCH'])
@authenticate()
@require_role('teacher', 'hod', 'admin', 'principal')
def update_student_attendance_record(attendance_id):
    """
    Directly update attendance figures (e.g. condonation, medical leave) with mandatory audit reason.
    """
    record = db.session.get(Attendance, attendance_id)
    if not record:
        return jsonify({'success': False, 'error': 'NOT_FOUND', 'message': 'Attendance record not found.'}), 404

    student = db.session.get(Student, record.student_id)
    is_auth, cls = verify_teacher_class_access(request.current_user, student.class_id)
    if not is_auth:
        return cls

    payload = request.get_json() or {}
    reason = payload.get('reason', '').strip()
    if not reason:
        return jsonify({
            'success': False,
            'error': 'VALIDATION_ERROR',
            'message': 'A reason for attendance adjustment is strictly required.'
        }), 400

    tot = payload.get('total_classes')
    att = payload.get('attended_classes')

    if tot is not None:
        record.total_classes = max(0, int(tot))
    if att is not None:
        record.attended_classes = max(0, min(record.total_classes, int(att)))

    new_pct = record.calculate_percentage()
    record.last_updated = datetime.utcnow()

    # Log to AuditLog
    audit_sys = AuditLog(
        user_id=request.current_user.user_id,
        role=request.current_user.role,
        action='ATTENDANCE_OVERRIDE',
        target_type='Attendance',
        target_id=record.attendance_id,
        ip=request.remote_addr
    )
    db.session.add(audit_sys)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f"Attendance successfully updated: {record.attended_classes}/{record.total_classes} ({new_pct}%).",
        'data': record.to_dict()
    }), 200

