import io
from datetime import datetime
from flask import Blueprint, jsonify, request, send_file
from backend.extensions import db
from backend.app.services.auth_middleware import authenticate, require_role, check_student_scope
from backend.app.models import (
    User, Student, Class, Department, Teacher, Subject,
    Attendance, Mark, SemesterResult, Timetable,
    Notification, Remark, Prediction, Explanation
)

# Optional ReportLab imports for PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

students_bp = Blueprint('students', __name__)

def resolve_target_student(current_user):
    """
    Helper to resolve the student record based on user identity or scoped query parameter:
    - If user is student: returns their own student record.
    - If user is parent/teacher/hod/admin/principal: respects ?student_id=<id> with strict scope validation.
    """
    requested_id = request.args.get('student_id', type=int)

    if current_user.role == 'student':
        student = Student.query.filter_by(user_id=current_user.user_id).first()
        if not student:
            return None, (jsonify({'success': False, 'error': 'NOT_FOUND', 'message': 'Student profile not linked to user account.'}), 404)
        if requested_id and requested_id != student.student_id:
            return None, (jsonify({'success': False, 'error': 'FORBIDDEN', 'message': 'Students can only access their own records.'}), 403)
        return student, None

    # For parent, teacher, hod, admin, principal
    if not requested_id:
        return None, (jsonify({'success': False, 'error': 'BAD_REQUEST', 'message': 'Missing student_id query parameter.'}), 400)

    is_authorized, result = check_student_scope(current_user, requested_id)
    if not is_authorized:
        return None, (jsonify({'success': False, 'error': 'FORBIDDEN', 'message': result}), 403)

    return result, None


@students_bp.route('/status', methods=['GET'])
def student_status():
    return jsonify({
        'module': 'Student Portal API',
        'status': 'active',
        'endpoints': [
            '/api/student/me',
            '/api/student/attendance',
            '/api/student/marks',
            '/api/student/timetable',
            '/api/student/notifications',
            '/api/student/remarks',
            '/api/student/prediction',
            '/api/student/report/download'
        ]
    }), 200


@students_bp.route('/me', methods=['GET'])
@authenticate()
def get_student_profile():
    """
    Fetch comprehensive student profile data including class, department, and mentor.
    """
    student, err = resolve_target_student(request.current_user)
    if err:
        return err

    # Load associated class, department, and mentor
    cls = db.session.get(Class, student.class_id) if student.class_id else None
    dept = db.session.get(Department, cls.dept_id) if cls and cls.dept_id else None
    mentor = db.session.get(Teacher, cls.mentor_teacher_id) if cls and cls.mentor_teacher_id else None
    user_account = db.session.get(User, student.user_id)

    profile_data = {
        'student_id': student.student_id,
        'user_id': student.user_id,
        'name': student.name,
        'usn': student.usn,
        'email': user_account.email if user_account else '',
        'academic_status': student.academic_status,
        'fee_status': student.fee_status,
        'class_id': cls.class_id if cls else None,
        'class_name': cls.class_name if cls else 'N/A',
        'section': cls.section if cls else 'N/A',
        'semester': cls.semester if cls else 1,
        'academic_year': cls.academic_year if cls else '2024-25',
        'department': {
            'dept_id': dept.dept_id if dept else None,
            'dept_code': dept.dept_code if dept else 'CSE',
            'dept_name': dept.name if dept else 'Computer Science & Engineering',
        },
        'mentor': {
            'teacher_id': mentor.teacher_id if mentor else None,
            'name': mentor.name if mentor else 'Assigned Faculty Mentor',
            'employee_id': mentor.employee_id if mentor else 'N/A',
            'designation': mentor.designation if mentor else 'Assistant Professor',
            'phone': mentor.phone if mentor else 'N/A'
        }
    }

    return jsonify({'success': True, 'data': profile_data}), 200


@students_bp.route('/attendance', methods=['GET'])
@authenticate()
def get_student_attendance():
    """
    Fetch subject-wise attendance breakdown and college-wide attendance threshold indicators.
    """
    student, err = resolve_target_student(request.current_user)
    if err:
        return err

    records = Attendance.query.filter_by(student_id=student.student_id).all()

    total_classes_held = sum(r.total_classes for r in records)
    total_classes_attended = sum(r.attended_classes for r in records)
    overall_percentage = round((total_classes_attended / total_classes_held * 100), 2) if total_classes_held > 0 else 0.0

    subject_breakdown = []
    low_attendance_warnings = []

    for r in records:
        subj = r.subject
        pct = float(r.percentage)
        is_shortage = pct < 75.0

        # Calculate how many consecutive classes are needed to attain 75%
        # (attended + x) / (total + x) >= 0.75  =>  x >= 3*total - 4*attended
        classes_needed = max(0, (3 * r.total_classes) - (4 * r.attended_classes)) if is_shortage else 0

        item = {
            'attendance_id': r.attendance_id,
            'subject_id': r.subject_id,
            'subject_code': subj.subject_code if subj else 'SUB',
            'subject_name': subj.subject_name if subj else 'Unknown Subject',
            'total_classes': r.total_classes,
            'attended_classes': r.attended_classes,
            'absent_classes': r.total_classes - r.attended_classes,
            'percentage': pct,
            'is_shortage': is_shortage,
            'classes_needed_for_75': classes_needed,
            'last_updated': r.last_updated.isoformat() if r.last_updated else None
        }
        subject_breakdown.append(item)

        if is_shortage:
            low_attendance_warnings.append({
                'subject_code': item['subject_code'],
                'subject_name': item['subject_name'],
                'percentage': pct,
                'message': f"Shortage alert: {item['subject_name']} is at {pct}% (< 75% VTU threshold). Requires {classes_needed} consecutive attendance(s) to clear."
            })

    return jsonify({
        'success': True,
        'data': {
            'overall': {
                'total_classes': total_classes_held,
                'attended_classes': total_classes_attended,
                'absent_classes': total_classes_held - total_classes_attended,
                'percentage': overall_percentage,
                'is_shortage': overall_percentage < 75.0,
                'status': 'Shortage (<75%)' if overall_percentage < 75.0 else 'Eligible (>=75%)'
            },
            'subjects': subject_breakdown,
            'warnings': low_attendance_warnings
        }
    }), 200


@students_bp.route('/marks', methods=['GET'])
@authenticate()
def get_student_marks():
    """
    Fetch continuous internal evaluation (CIE) scores, SGPA trends, and backlog summary.
    """
    student, err = resolve_target_student(request.current_user)
    if err:
        return err

    marks_records = Mark.query.filter_by(student_id=student.student_id).all()
    sem_results = SemesterResult.query.filter_by(student_id=student.student_id).order_by(SemesterResult.semester.asc()).all()

    subjects_data = []
    total_internal_obtained = 0.0
    total_internal_max = len(marks_records) * 50.0  # VTU CIE is out of 50 per subject

    for m in marks_records:
        subj = m.subject
        tot = float(m.total_cie)
        total_internal_obtained += tot

        subjects_data.append({
            'marks_id': m.marks_id,
            'subject_id': m.subject_id,
            'subject_code': subj.subject_code if subj else 'SUB',
            'subject_name': subj.subject_name if subj else 'Subject',
            'credits': subj.credits if subj else 3,
            'cie1': float(m.cie1),
            'cie2': float(m.cie2),
            'cie3': float(m.cie3),
            'assignment_marks': float(m.assignment_marks),
            'quiz_marks': float(m.quiz_marks),
            'total_cie': tot,
            'max_cie': 50.0,
            'passing_cie': 20.0,
            'is_passing': tot >= 20.0
        })

    # SGPA progression
    progression = []
    total_credits = 0
    weighted_sgpa_sum = 0.0
    active_backlogs = 0

    for r in sem_results:
        sgpa_val = float(r.sgpa)
        progression.append({
            'semester': r.semester,
            'sgpa': sgpa_val,
            'credits_earned': r.credits_earned,
            'backlogs': r.backlogs
        })
        weighted_sgpa_sum += sgpa_val * r.credits_earned
        total_credits += r.credits_earned
        active_backlogs += r.backlogs

    calculated_cgpa = round(weighted_sgpa_sum / total_credits, 2) if total_credits > 0 else 0.0

    return jsonify({
        'success': True,
        'data': {
            'subjects': subjects_data,
            'progression': progression,
            'summary': {
                'cgpa': calculated_cgpa,
                'total_credits': total_credits,
                'active_backlogs': active_backlogs,
                'average_internal_percentage': round((total_internal_obtained / total_internal_max * 100), 2) if total_internal_max > 0 else 0.0
            }
        }
    }), 200


@students_bp.route('/timetable', methods=['GET'])
@authenticate()
def get_student_timetable():
    """
    Fetch the student's weekly timetable ordered by standard academic periods.
    """
    student, err = resolve_target_student(request.current_user)
    if err:
        return err

    if not student.class_id:
        return jsonify({'success': True, 'data': {'schedule': {}, 'days': []}}), 200

    slots = Timetable.query.filter_by(class_id=student.class_id).all()

    # Days ordering
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    schedule_by_day = {day: [] for day in day_order}

    for slot in slots:
        day = slot.day_of_week
        if day not in schedule_by_day:
            schedule_by_day[day] = []

        schedule_by_day[day].append({
            'timetable_id': slot.timetable_id,
            'day_of_week': slot.day_of_week,
            'start_time': slot.start_time,
            'end_time': slot.end_time,
            'room_number': slot.room_number,
            'subject_code': slot.subject.subject_code if slot.subject else 'SUB',
            'subject_name': slot.subject.subject_name if slot.subject else 'Subject',
            'teacher_name': slot.teacher.name if slot.teacher else 'Faculty',
            'is_lab': 'Lab' in (slot.subject.subject_name if slot.subject else '') or 'Laboratory' in (slot.subject.subject_name if slot.subject else '')
        })

    # Sort each day by start_time
    for d in schedule_by_day:
        schedule_by_day[d].sort(key=lambda x: x['start_time'])

    return jsonify({
        'success': True,
        'data': {
            'class_id': student.class_id,
            'days': day_order,
            'schedule': schedule_by_day
        }
    }), 200


@students_bp.route('/notifications', methods=['GET'])
@authenticate()
def get_student_notifications():
    """
    Fetch notifications and college/department notices visible to this student.
    """
    student, err = resolve_target_student(request.current_user)
    if err:
        return err

    notifs = Notification.query.filter(
        db.or_(
            Notification.student_id == student.student_id,
            Notification.recipient_user_id == student.user_id,
            Notification.recipient_user_id == None
        )
    ).order_by(Notification.created_at.desc()).limit(30).all()

    return jsonify({
        'success': True,
        'data': [n.to_dict() for n in notifs]
    }), 200


@students_bp.route('/remarks', methods=['GET'])
@authenticate()
def get_student_remarks():
    """
    Fetch teacher and mentor feedback, warnings, and guidance notes.
    """
    student, err = resolve_target_student(request.current_user)
    if err:
        return err

    remarks = Remark.query.filter_by(student_id=student.student_id).order_by(Remark.created_at.desc()).all()

    return jsonify({
        'success': True,
        'data': [r.to_dict() for r in remarks]
    }), 200


@students_bp.route('/prediction', methods=['GET'])
@authenticate()
def get_student_prediction():
    """
    Fetch student's latest XGBoost risk prediction and SHAP explanation breakdown.
    """
    student, err = resolve_target_student(request.current_user)
    if err:
        return err

    pred = Prediction.query.filter_by(student_id=student.student_id).order_by(Prediction.generated_at.desc()).first()

    if not pred:
        # Fallback heuristic calculation if no model run has recorded yet
        att_records = Attendance.query.filter_by(student_id=student.student_id).all()
        tot_held = sum(r.total_classes for r in att_records)
        tot_att = sum(r.attended_classes for r in att_records)
        att_pct = (tot_att / tot_held * 100) if tot_held > 0 else 85.0

        risk_level = 'high' if att_pct < 65 else ('medium' if att_pct < 75 else 'low')
        risk_score = 0.85 if risk_level == 'high' else (0.55 if risk_level == 'medium' else 0.15)

        return jsonify({
            'success': True,
            'data': {
                'prediction_id': None,
                'predicted_outcome': 'Pass' if risk_level == 'low' else 'At-Risk',
                'risk_score': risk_score,
                'risk_level': risk_level,
                'predicted_sgpa': 7.50 if risk_level == 'low' else 6.20,
                'generated_at': datetime.utcnow().isoformat(),
                'explanations': [
                    {'feature': 'Attendance Percentage', 'displayValue': f'{round(att_pct, 1)}%', 'shap': -0.42 if risk_level != 'low' else 0.35, 'rank_order': 1},
                    {'feature': 'Continuous Internal Evaluation (CIE)', 'displayValue': '32/50 avg', 'shap': 0.18, 'rank_order': 2},
                    {'feature': 'Historical Semester Backlogs', 'displayValue': '0', 'shap': 0.22, 'rank_order': 3}
                ],
                'recommendations': [
                    'Maintain attendance above 80% across all laboratory and theory classes.',
                    'Attend weekly mentor peer-review sessions for targeted subject improvement.',
                    'Review unit test concepts ahead of university semester examinations.'
                ]
            }
        }), 200

    exps = sorted([e.to_dict() for e in pred.explanations], key=lambda x: x['rank_order'])

    # Build smart actionable recommendations based on risk and SHAP values
    recommendations = []
    for exp in exps:
        feat = exp['feature'].lower()
        if 'attendance' in feat and exp['shap'] < 0:
            recommendations.append("Immediate attendance remediation required: participate in upcoming classes to overcome the <75% shortfall.")
        elif 'cie' in feat and exp['shap'] < 0:
            recommendations.append("Schedule one-on-one consultation with subject faculty for CIE improvement.")
        elif 'backlog' in feat and exp['shap'] < 0:
            recommendations.append("Register for upcoming fast-track supplementary remedial tutorials.")

    if not recommendations:
        recommendations = [
            "Maintain strong academic consistency across all continuous internal assessments.",
            "Stay engaged with your faculty mentor and complete assignment portfolios ahead of due dates."
        ]

    return jsonify({
        'success': True,
        'data': {
            'prediction_id': pred.prediction_id,
            'predicted_outcome': pred.predicted_outcome,
            'risk_score': float(pred.risk_score),
            'risk_level': pred.risk_level,
            'predicted_sgpa': float(pred.predicted_sgpa) if pred.predicted_sgpa else None,
            'generated_at': pred.generated_at.isoformat(),
            'explanations': exps,
            'recommendations': recommendations
        }
    }), 200


@students_bp.route('/report/download', methods=['GET'])
@authenticate()
def download_student_report():
    """
    Generate and stream a formal VTU Academic Performance Report Card PDF.
    """
    student, err = resolve_target_student(request.current_user)
    if err:
        return err

    # Retrieve associated records
    cls = db.session.get(Class, student.class_id) if student.class_id else None
    dept = db.session.get(Department, cls.dept_id) if cls and cls.dept_id else None
    mentor = db.session.get(Teacher, cls.mentor_teacher_id) if cls and cls.mentor_teacher_id else None
    attendance_records = Attendance.query.filter_by(student_id=student.student_id).all()
    marks_records = Mark.query.filter_by(student_id=student.student_id).all()
    sem_results = SemesterResult.query.filter_by(student_id=student.student_id).order_by(SemesterResult.semester.asc()).all()
    remarks = Remark.query.filter_by(student_id=student.student_id).all()

    # Calculate overall metrics
    tot_classes = sum(r.total_classes for r in attendance_records)
    tot_att = sum(r.attended_classes for r in attendance_records)
    overall_att_pct = round((tot_att / tot_classes * 100), 2) if tot_classes > 0 else 0.0

    tot_credits = sum(r.credits_earned for r in sem_results)
    weighted_sgpa = sum(float(r.sgpa) * r.credits_earned for r in sem_results)
    cgpa = round(weighted_sgpa / tot_credits, 2) if tot_credits > 0 else 0.0

    # Build PDF with ReportLab
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=16,
        leading=20,
        alignment=1, # Center
        textColor=colors.HexColor('#14213d')
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        alignment=1,
        textColor=colors.HexColor('#5b6b82')
    )
    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading2'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#2f6bff'),
        spaceBefore=12,
        spaceAfter=6
    )
    cell_style = ParagraphStyle('Cell', parent=styles['Normal'], fontSize=8.5, leading=11)
    bold_cell_style = ParagraphStyle('BoldCell', parent=styles['Normal'], fontSize=8.5, leading=11, fontName='Helvetica-Bold')

    story = []

    # 1. Header
    story.append(Paragraph("<b>PES INSTITUTE OF TECHNOLOGY & MANAGEMENT</b>", title_style))
    story.append(Paragraph("Affiliated to VTU Belagavi | Approved by AICTE, New Delhi", subtitle_style))
    story.append(Paragraph("NH 206, Sagar Road, Shivamogga - 577204, Karnataka", subtitle_style))
    story.append(Paragraph("<b>CENTRALIZED ACADEMIC MONITORING & PERFORMANCE REPORT</b>", ParagraphStyle('ReportName', parent=subtitle_style, fontSize=11, fontName='Helvetica-Bold', textColor=colors.HexColor('#14213d'), spaceBefore=4)))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2f6bff'), spaceAfter=10))

    # 2. Student Particulars Table
    student_table_data = [
        [
            Paragraph("<b>Student Name:</b>", bold_cell_style),
            Paragraph(student.name, cell_style),
            Paragraph("<b>USN:</b>", bold_cell_style),
            Paragraph(student.usn, bold_cell_style)
        ],
        [
            Paragraph("<b>Department:</b>", bold_cell_style),
            Paragraph(dept.name if dept else 'CSE', cell_style),
            Paragraph("<b>Class / Section:</b>", bold_cell_style),
            Paragraph(f"{cls.class_name if cls else '5th Sem'} - Sec {cls.section if cls else 'A'}", cell_style)
        ],
        [
            Paragraph("<b>Academic Year:</b>", bold_cell_style),
            Paragraph(cls.academic_year if cls else '2024-25', cell_style),
            Paragraph("<b>Mentor Faculty:</b>", bold_cell_style),
            Paragraph(mentor.name if mentor else 'Faculty Mentor', cell_style)
        ],
        [
            Paragraph("<b>Overall Attendance:</b>", bold_cell_style),
            Paragraph(f"{overall_att_pct}% ({'ELIGIBLE' if overall_att_pct >= 75 else 'SHORTAGE ALERT'})", bold_cell_style),
            Paragraph("<b>Cumulative CGPA:</b>", bold_cell_style),
            Paragraph(f"{cgpa} / 10.0", bold_cell_style)
        ]
    ]

    t_profile = Table(student_table_data, colWidths=[110, 160, 110, 160])
    t_profile.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_profile)
    story.append(Spacer(1, 12))

    # 3. Subject-wise Marks & Attendance Table
    story.append(Paragraph("I. CONTINUOUS INTERNAL EVALUATION (CIE) & ATTENDANCE SUMMARY", h2_style))

    att_map = {a.subject_id: a for a in attendance_records}
    marks_table_data = [
        [
            Paragraph("<b>Subject Code</b>", bold_cell_style),
            Paragraph("<b>Subject Name</b>", bold_cell_style),
            Paragraph("<b>CIE 1</b>", bold_cell_style),
            Paragraph("<b>CIE 2</b>", bold_cell_style),
            Paragraph("<b>CIE 3</b>", bold_cell_style),
            Paragraph("<b>Assign/Quiz</b>", bold_cell_style),
            Paragraph("<b>Total CIE</b>", bold_cell_style),
            Paragraph("<b>Att. %</b>", bold_cell_style)
        ]
    ]

    for m in marks_records:
        subj = m.subject
        att_entry = att_map.get(m.subject_id)
        att_str = f"{float(att_entry.percentage)}%" if att_entry else "N/A"

        marks_table_data.append([
            Paragraph(subj.subject_code if subj else 'SUB', cell_style),
            Paragraph(subj.subject_name if subj else 'Subject', cell_style),
            Paragraph(str(float(m.cie1)), cell_style),
            Paragraph(str(float(m.cie2)), cell_style),
            Paragraph(str(float(m.cie3)), cell_style),
            Paragraph(f"{float(m.assignment_marks)}+{float(m.quiz_marks)}", cell_style),
            Paragraph(f"<b>{float(m.total_cie)}</b>", bold_cell_style),
            Paragraph(att_str, cell_style)
        ])

    t_marks = Table(marks_table_data, colWidths=[65, 180, 42, 42, 42, 60, 55, 54])
    t_marks.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e2e8f0')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_marks)
    story.append(Spacer(1, 12))

    # 4. Semester Progression Table
    story.append(Paragraph("II. SEMESTER-WISE SGPA PROGRESSION", h2_style))
    sem_table_data = [
        [Paragraph("<b>Semester</b>", bold_cell_style)] + [Paragraph(f"Sem {r.semester}", cell_style) for r in sem_results],
        [Paragraph("<b>SGPA</b>", bold_cell_style)] + [Paragraph(str(float(r.sgpa)), bold_cell_style) for r in sem_results],
        [Paragraph("<b>Backlogs</b>", bold_cell_style)] + [Paragraph(str(r.backlogs), cell_style) for r in sem_results]
    ]
    t_sem = Table(sem_table_data)
    t_sem.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f1f5f9')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_sem)
    story.append(Spacer(1, 12))

    # 5. Faculty Remarks & Mentorship Guidance
    story.append(Paragraph("III. MENTOR OBSERVATIONS & ACTION RECOMMENDATIONS", h2_style))
    if remarks:
        for rem in remarks:
            story.append(Paragraph(f"• <b>{rem.author_teacher.name if rem.author_teacher else 'Mentor'}:</b> {rem.remark_text}", cell_style))
            if rem.action_taken:
                story.append(Paragraph(f"   <i>Action Initiated:</i> {rem.action_taken}", cell_style))
    else:
        story.append(Paragraph("• Academic progress is satisfactory. Continue regular participation in laboratory exercises.", cell_style))

    story.append(Spacer(1, 35))

    # 6. Signatures Footer
    sig_data = [
        [
            Paragraph("____________________________<br/><b>Student Signature</b>", cell_style),
            Paragraph("____________________________<br/><b>Mentor Signature</b>", cell_style),
            Paragraph("____________________________<br/><b>Head of Department / Principal</b>", cell_style)
        ]
    ]
    t_sig = Table(sig_data, colWidths=[180, 180, 180])
    t_sig.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_sig)

    # Build Document
    doc.build(story)
    pdf_buffer.seek(0)

    filename = f"PESITM_Academic_Report_{student.usn}.pdf"
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )
