import io
from datetime import datetime
from flask import Blueprint, jsonify, request, send_file
from backend.extensions import db
from backend.app.services.auth_middleware import authenticate, require_role
from backend.app.models import (
    User, Parent, Student, ParentStudent, Class, Department, Teacher,
    Attendance, Mark, SemesterResult, Fee, FeePayment,
    Notification, Alert, Remark, Prediction, Explanation
)

# Optional ReportLab imports for child report PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

parents_bp = Blueprint('parents', __name__)

def get_current_parent_record(current_user):
    """Resolve Parent model record for the authenticated user"""
    if current_user.role == 'parent':
        return Parent.query.filter_by(user_id=current_user.user_id).first()
    return None

def verify_child_parent_link(current_user, student_id):
    """
    Ensures that current_user is linked to student_id via parent_students,
    or has administrative/principal privileges.
    Returns: (is_authorized: bool, student_or_error_response)
    """
    student = db.session.get(Student, student_id)
    if not student:
        return False, (jsonify({'success': False, 'error': 'NOT_FOUND', 'message': 'Student record not found.'}), 404)

    # Principal & Admin bypass
    if current_user.role in ('principal', 'admin'):
        return True, student

    # Parent role verification
    if current_user.role == 'parent':
        parent = Parent.query.filter_by(user_id=current_user.user_id).first()
        if not parent:
            return False, (jsonify({'success': False, 'error': 'NOT_FOUND', 'message': 'Parent profile not linked to user account.'}), 404)

        link = ParentStudent.query.filter_by(parent_id=parent.parent_id, student_id=student.student_id).first()
        if not link:
            return False, (jsonify({'success': False, 'error': 'FORBIDDEN', 'message': 'You can only access records of your registered children.'}), 403)

        return True, student

    return False, (jsonify({'success': False, 'error': 'FORBIDDEN', 'message': 'Unauthorized portal access.'}), 403)


@parents_bp.route('/status', methods=['GET'])
def parent_status():
    return jsonify({
        'module': 'Parent Portal API',
        'status': 'active',
        'endpoints': [
            '/api/parent/children',
            '/api/parent/children/<id>/summary',
            '/api/parent/children/<id>/report',
            '/api/parent/messages'
        ]
    }), 200


@parents_bp.route('/children', methods=['GET'])
@authenticate()
@require_role('parent', 'admin', 'principal')
def get_parent_children():
    """
    List all children registered under the authenticated parent account.
    If admin or principal, returns first batch or allows ?parent_id filter.
    """
    parent = get_current_parent_record(request.current_user)

    if not parent and request.current_user.role in ('admin', 'principal'):
        parent_id_param = request.args.get('parent_id', type=int)
        if parent_id_param:
            parent = db.session.get(Parent, parent_id_param)
        else:
            parent = Parent.query.first()

    if not parent:
        return jsonify({'success': False, 'error': 'NOT_FOUND', 'message': 'Parent profile not found.'}), 404

    children_records = parent.children.all()
    children_list = []

    for child in children_records:
        cls = db.session.get(Class, child.class_id) if child.class_id else None
        dept = db.session.get(Department, cls.dept_id) if cls and cls.dept_id else None
        mentor = db.session.get(Teacher, cls.mentor_teacher_id) if cls and cls.mentor_teacher_id else None

        # Attendance calculation
        att_records = Attendance.query.filter_by(student_id=child.student_id).all()
        tot_held = sum(r.total_classes for r in att_records)
        tot_att = sum(r.attended_classes for r in att_records)
        att_pct = round((tot_att / tot_held * 100), 2) if tot_held > 0 else 0.0

        # CGPA calculation
        sem_results = SemesterResult.query.filter_by(student_id=child.student_id).all()
        tot_credits = sum(r.credits_earned for r in sem_results)
        weighted_sgpa = sum(float(r.sgpa) * r.credits_earned for r in sem_results)
        cgpa = round(weighted_sgpa / tot_credits, 2) if tot_credits > 0 else 0.0
        backlogs = sum(r.backlogs for r in sem_results)

        # ML Prediction
        pred = Prediction.query.filter_by(student_id=child.student_id).order_by(Prediction.generated_at.desc()).first()
        risk_level = pred.risk_level if pred else ('high' if att_pct < 65 else ('medium' if att_pct < 75 else 'low'))

        # Parent-Student relationship label
        link = ParentStudent.query.filter_by(parent_id=parent.parent_id, student_id=child.student_id).first()
        relation_title = link.relation if link else 'Child'

        children_list.append({
            'student_id': child.student_id,
            'name': child.name,
            'usn': child.usn,
            'relation': relation_title,
            'class_name': cls.class_name if cls else 'N/A',
            'section': cls.section if cls else 'A',
            'semester': cls.semester if cls else 1,
            'academic_status': child.academic_status,
            'fee_status': child.fee_status,
            'attendance_percentage': att_pct,
            'is_shortage': att_pct < 75.0,
            'cgpa': cgpa,
            'active_backlogs': backlogs,
            'risk_level': risk_level,
            'department': {
                'dept_id': dept.dept_id if dept else None,
                'dept_code': dept.dept_code if dept else 'CSE',
                'dept_name': dept.name if dept else 'Computer Science & Engineering',
            },
            'mentor': {
                'name': mentor.name if mentor else 'Faculty Mentor',
                'phone': mentor.phone if mentor else 'N/A',
                'designation': mentor.designation if mentor else 'Assistant Professor',
            }
        })

    return jsonify({
        'success': True,
        'parent': {
            'parent_id': parent.parent_id,
            'name': parent.name,
            'phone': parent.phone,
            'email': parent.email
        },
        'count': len(children_list),
        'data': children_list
    }), 200


@parents_bp.route('/children/<int:child_id>/summary', methods=['GET'])
@authenticate()
@require_role('parent', 'admin', 'principal')
def get_child_summary(child_id):
    """
    Fetch comprehensive academic overview, alerts, marks, attendance,
    and fee details for a specific registered child.
    """
    is_auth, child = verify_child_parent_link(request.current_user, child_id)
    if not is_auth:
        return child

    cls = db.session.get(Class, child.class_id) if child.class_id else None
    dept = db.session.get(Department, cls.dept_id) if cls and cls.dept_id else None
    mentor = db.session.get(Teacher, cls.mentor_teacher_id) if cls and cls.mentor_teacher_id else None

    # 1. Attendance Metrics
    att_records = Attendance.query.filter_by(student_id=child.student_id).all()
    tot_held = sum(r.total_classes for r in att_records)
    tot_att = sum(r.attended_classes for r in att_records)
    overall_att_pct = round((tot_att / tot_held * 100), 2) if tot_held > 0 else 0.0

    subject_att = []
    shortage_warnings = []
    for a in att_records:
        pct = float(a.percentage)
        is_short = pct < 75.0
        classes_needed = max(0, (3 * a.total_classes) - (4 * a.attended_classes)) if is_short else 0

        subject_att.append({
            'attendance_id': a.attendance_id,
            'subject_code': a.subject.subject_code if a.subject else 'SUB',
            'subject_name': a.subject.subject_name if a.subject else 'Subject',
            'total_classes': a.total_classes,
            'attended_classes': a.attended_classes,
            'percentage': pct,
            'is_shortage': is_short,
            'classes_needed': classes_needed
        })
        if is_short:
            shortage_warnings.append(
                f"Shortage in {a.subject.subject_name if a.subject else 'Subject'} ({pct}%). Requires {classes_needed} consecutive classes."
            )

    # 2. CIE Marks & Semester Results
    marks_records = Mark.query.filter_by(student_id=child.student_id).all()
    sem_results = SemesterResult.query.filter_by(student_id=child.student_id).order_by(SemesterResult.semester.asc()).all()

    subjects_marks = []
    for m in marks_records:
        tot = float(m.total_cie)
        subjects_marks.append({
            'marks_id': m.marks_id,
            'subject_code': m.subject.subject_code if m.subject else 'SUB',
            'subject_name': m.subject.subject_name if m.subject else 'Subject',
            'cie1': float(m.cie1),
            'cie2': float(m.cie2),
            'cie3': float(m.cie3),
            'assignment': float(m.assignment_marks),
            'quiz': float(m.quiz_marks),
            'total_cie': tot,
            'max_cie': 50.0,
            'is_passing': tot >= 20.0
        })

    tot_credits = sum(r.credits_earned for r in sem_results)
    weighted_sgpa = sum(float(r.sgpa) * r.credits_earned for r in sem_results)
    cgpa = round(weighted_sgpa / tot_credits, 2) if tot_credits > 0 else 0.0
    active_backlogs = sum(r.backlogs for r in sem_results)

    # 3. Fee Breakdown
    fee_class = Fee.query.filter_by(class_id=child.class_id).first() if child.class_id else None
    payments = FeePayment.query.filter_by(student_id=child.student_id).order_by(FeePayment.payment_date.desc()).all()
    total_fee_amount = float(fee_class.total_amount) if fee_class else 85000.0
    paid_sum = sum(float(p.amount_paid) for p in payments if p.status == 'completed')
    balance_due = max(0.0, total_fee_amount - paid_sum)

    # 4. Remarks & Guidance
    remarks = Remark.query.filter_by(student_id=child.student_id).order_by(Remark.created_at.desc()).all()

    # 5. ML Risk Prediction & SHAP
    pred = Prediction.query.filter_by(student_id=child.student_id).order_by(Prediction.generated_at.desc()).first()
    exps = sorted([e.to_dict() for e in pred.explanations], key=lambda x: x['rank_order']) if pred else []

    risk_level = pred.risk_level if pred else ('high' if overall_att_pct < 65 else ('medium' if overall_att_pct < 75 else 'low'))
    risk_score = float(pred.risk_score) if pred else (0.85 if risk_level == 'high' else (0.55 if risk_level == 'medium' else 0.15))

    # 6. Active Alerts
    alerts = Alert.query.filter_by(student_id=child.student_id, status='open').order_by(Alert.created_at.desc()).all()

    return jsonify({
        'success': True,
        'data': {
            'student': {
                'student_id': child.student_id,
                'name': child.name,
                'usn': child.usn,
                'class_name': cls.class_name if cls else '5th Sem CSE',
                'section': cls.section if cls else 'A',
                'semester': cls.semester if cls else 5,
                'academic_status': child.academic_status,
                'fee_status': child.fee_status,
                'department': dept.name if dept else 'Computer Science & Engineering',
                'mentor': {
                    'name': mentor.name if mentor else 'Faculty Mentor',
                    'designation': mentor.designation if mentor else 'Assistant Professor',
                    'phone': mentor.phone if mentor else '+91 98450 12345',
                    'employee_id': mentor.employee_id if mentor else 'PES-T01'
                }
            },
            'attendance': {
                'overall_percentage': overall_att_pct,
                'total_held': tot_held,
                'total_attended': tot_att,
                'is_shortage': overall_att_pct < 75.0,
                'subjects': subject_att,
                'warnings': shortage_warnings
            },
            'academics': {
                'cgpa': cgpa,
                'total_credits': tot_credits,
                'active_backlogs': active_backlogs,
                'subjects': subjects_marks,
                'progression': [{'semester': r.semester, 'sgpa': float(r.sgpa), 'backlogs': r.backlogs} for r in sem_results]
            },
            'finance': {
                'total_annual_fee': total_fee_amount,
                'amount_paid': paid_sum,
                'balance_due': balance_due,
                'status': 'Paid' if balance_due == 0 else 'Pending',
                'due_date': fee_class.due_date.strftime('%Y-%m-%d') if fee_class else '2025-01-31',
                'payments': [p.to_dict() for p in payments]
            },
            'prediction': {
                'risk_level': risk_level,
                'risk_score': risk_score,
                'predicted_outcome': pred.predicted_outcome if pred else ('Pass' if risk_level == 'low' else 'At-Risk'),
                'predicted_sgpa': float(pred.predicted_sgpa) if pred and pred.predicted_sgpa else 7.50,
                'explanations': exps
            },
            'alerts': [a.to_dict() for a in alerts],
            'remarks': [r.to_dict() for r in remarks]
        }
    }), 200


@parents_bp.route('/messages', methods=['POST'])
@authenticate()
@require_role('parent', 'admin', 'principal')
def send_parent_message():
    """
    Dispatch an in-portal communication message from the parent to the child's faculty mentor.
    """
    payload = request.get_json() or {}
    student_id = payload.get('student_id')
    subject = payload.get('subject', '').strip()
    message_text = payload.get('message', '').strip()

    if not student_id or not message_text:
        return jsonify({
            'success': False,
            'error': 'BAD_REQUEST',
            'message': 'Student ID and message text are required.'
        }), 400

    is_auth, child = verify_child_parent_link(request.current_user, int(student_id))
    if not is_auth:
        return child

    cls = db.session.get(Class, child.class_id) if child.class_id else None
    mentor = db.session.get(Teacher, cls.mentor_teacher_id) if cls and cls.mentor_teacher_id else None
    recipient_user_id = mentor.user_id if mentor else None

    # Create Notification record directed to teacher
    notif = Notification(
        sender_id=request.current_user.user_id,
        recipient_user_id=recipient_user_id,
        student_id=child.student_id,
        title=f"Parent Inquiry: {subject or 'Academic Discussion'}",
        message=f"From: {request.current_user.username} (Parent of {child.name}, USN {child.usn})\n\n{message_text}",
        channel='in_app',
        status='sent'
    )
    db.session.add(notif)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f"Inquiry successfully transmitted to mentor {mentor.name if mentor else 'Faculty'}."
    }), 201


@parents_bp.route('/messages', methods=['GET'])
@authenticate()
@require_role('parent', 'admin', 'principal')
def get_parent_messages():
    """
    Retrieve message communication log sent by this parent or notifications relating to their children.
    """
    parent = get_current_parent_record(request.current_user)
    if not parent and request.current_user.role == 'parent':
        return jsonify({'success': False, 'error': 'NOT_FOUND', 'message': 'Parent profile not found.'}), 404

    child_ids = [s.student_id for s in parent.children] if parent else []

    messages = Notification.query.filter(
        db.or_(
            Notification.sender_id == request.current_user.user_id,
            Notification.recipient_user_id == request.current_user.user_id,
            Notification.student_id.in_(child_ids) if child_ids else False
        )
    ).order_by(Notification.created_at.desc()).limit(40).all()

    return jsonify({
        'success': True,
        'data': [m.to_dict() for m in messages]
    }), 200


@parents_bp.route('/children/<int:child_id>/report', methods=['GET'])
@authenticate()
@require_role('parent', 'admin', 'principal')
def download_child_report(child_id):
    """
    Generate and stream VTU Academic Performance Report PDF for the parent's child.
    """
    is_auth, child = verify_child_parent_link(request.current_user, child_id)
    if not is_auth:
        return child

    # Retrieve child academic details
    cls = db.session.get(Class, child.class_id) if child.class_id else None
    dept = db.session.get(Department, cls.dept_id) if cls and cls.dept_id else None
    mentor = db.session.get(Teacher, cls.mentor_teacher_id) if cls and cls.mentor_teacher_id else None
    attendance_records = Attendance.query.filter_by(student_id=child.student_id).all()
    marks_records = Mark.query.filter_by(student_id=child.student_id).all()
    sem_results = SemesterResult.query.filter_by(student_id=child.student_id).order_by(SemesterResult.semester.asc()).all()
    remarks = Remark.query.filter_by(student_id=child.student_id).all()

    tot_classes = sum(r.total_classes for r in attendance_records)
    tot_att = sum(r.attended_classes for r in attendance_records)
    overall_att_pct = round((tot_att / tot_classes * 100), 2) if tot_classes > 0 else 0.0

    tot_credits = sum(r.credits_earned for r in sem_results)
    weighted_sgpa = sum(float(r.sgpa) * r.credits_earned for r in sem_results)
    cgpa = round(weighted_sgpa / tot_credits, 2) if tot_credits > 0 else 0.0

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
        alignment=1,
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

    # Header
    story.append(Paragraph("<b>PES INSTITUTE OF TECHNOLOGY & MANAGEMENT</b>", title_style))
    story.append(Paragraph("Affiliated to VTU Belagavi | Approved by AICTE, New Delhi", subtitle_style))
    story.append(Paragraph("NH 206, Sagar Road, Shivamogga - 577204, Karnataka", subtitle_style))
    story.append(Paragraph("<b>PARENT COPY &bull; STUDENT ACADEMIC PERFORMANCE REPORT</b>", ParagraphStyle('ReportName', parent=subtitle_style, fontSize=11, fontName='Helvetica-Bold', textColor=colors.HexColor('#14213d'), spaceBefore=4)))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2f6bff'), spaceAfter=10))

    # Profile Table
    student_table_data = [
        [
            Paragraph("<b>Ward Name:</b>", bold_cell_style),
            Paragraph(child.name, cell_style),
            Paragraph("<b>USN:</b>", bold_cell_style),
            Paragraph(child.usn, bold_cell_style)
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
            Paragraph(f"{mentor.name if mentor else 'Faculty'} ({mentor.phone if mentor else 'N/A'})", cell_style)
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

    # CIE & Attendance
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

    # Progression
    story.append(Paragraph("II. SEMESTER SGPA PROGRESSION", h2_style))
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

    # Remarks
    story.append(Paragraph("III. MENTOR OBSERVATIONS & ACTION RECOMMENDATIONS", h2_style))
    if remarks:
        for rem in remarks:
            story.append(Paragraph(f"• <b>{rem.author_teacher.name if rem.author_teacher else 'Mentor'}:</b> {rem.remark_text}", cell_style))
            if rem.action_taken:
                story.append(Paragraph(f"   <i>Action Initiated:</i> {rem.action_taken}", cell_style))
    else:
        story.append(Paragraph("• Student is progressing on track. Parents are requested to ensure regular attendance.", cell_style))

    story.append(Spacer(1, 35))

    # Signatures
    sig_data = [
        [
            Paragraph("____________________________<br/><b>Parent Signature</b>", cell_style),
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

    doc.build(story)
    pdf_buffer.seek(0)

    filename = f"PESITM_ParentCopy_{child.usn}.pdf"
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )
