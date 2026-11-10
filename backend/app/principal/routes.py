import io
from datetime import datetime
from flask import Blueprint, jsonify, request, send_file
from backend.extensions import db
from backend.app.services.auth_middleware import authenticate, require_role
from backend.app.models import (
    User, Student, Teacher, Department, Class, Subject,
    Attendance, Mark, SemesterResult, Prediction, Alert, Remark
)

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

principal_bp = Blueprint('principal', __name__)

@principal_bp.route('/status', methods=['GET'])
def principal_status():
    return jsonify({
        'module': 'Principal Portal API',
        'status': 'active',
        'endpoints': [
            '/api/principal/overview',
            '/api/principal/departments',
            '/api/principal/classes',
            '/api/principal/students',
            '/api/principal/report/executive'
        ]
    }), 200


@principal_bp.route('/overview', methods=['GET'])
@authenticate()
@require_role('principal', 'admin')
def get_executive_overview():
    """
    Fetch comprehensive college-wide performance metrics, attendance averages,
    CGPA averages, and overall XGBoost risk distributions.
    """
    total_students = Student.query.count()
    total_faculty = Teacher.query.count()
    total_departments = Department.query.count()
    total_classes = Class.query.count()

    # 1. College-wide Attendance
    all_attendance = Attendance.query.all()
    tot_held = sum(a.total_classes for a in all_attendance)
    tot_att = sum(a.attended_classes for a in all_attendance)
    college_avg_att = round((tot_att / tot_held * 100), 2) if tot_held > 0 else 0.0
    critical_shortage_count = sum(1 for a in all_attendance if float(a.percentage) < 75.0)

    # 2. College-wide CGPA
    all_sem_results = SemesterResult.query.all()
    tot_credits = sum(r.credits_earned for r in all_sem_results)
    weighted_sum = sum(float(r.sgpa) * r.credits_earned for r in all_sem_results)
    college_avg_cgpa = round(weighted_sum / tot_credits, 2) if tot_credits > 0 else 0.0

    # 3. XGBoost Risk Distribution
    predictions = Prediction.query.all()
    risk_counts = {'high': 0, 'medium': 0, 'low': 0}

    if predictions:
        for p in predictions:
            lvl = p.risk_level.lower() if p.risk_level else 'low'
            risk_counts[lvl] = risk_counts.get(lvl, 0) + 1
    else:
        # Fallback heuristic calculation if predictions not run yet
        for s in Student.query.all():
            st_att = [float(a.percentage) for a in s.attendance_records]
            avg = sum(st_att) / len(st_att) if st_att else 85.0
            if avg < 65:
                risk_counts['high'] += 1
            elif avg < 75:
                risk_counts['medium'] += 1
            else:
                risk_counts['low'] += 1

    tot_preds = sum(risk_counts.values()) or 1
    risk_percentages = {
        'high': round((risk_counts['high'] / tot_preds) * 100, 1),
        'medium': round((risk_counts['medium'] / tot_preds) * 100, 1),
        'low': round((risk_counts['low'] / tot_preds) * 100, 1)
    }

    # 4. Alerts
    open_alerts = Alert.query.filter_by(status='open').count()
    resolved_alerts = Alert.query.filter_by(status='resolved').count()

    return jsonify({
        'success': True,
        'data': {
            'headcount': {
                'total_students': total_students,
                'total_faculty': total_faculty,
                'total_departments': total_departments,
                'total_classes': total_classes,
                'student_faculty_ratio': round(total_students / total_faculty, 1) if total_faculty > 0 else 0
            },
            'academic_health': {
                'college_avg_attendance': college_avg_att,
                'college_avg_cgpa': college_avg_cgpa,
                'critical_shortage_records': critical_shortage_count
            },
            'risk_distribution': {
                'counts': risk_counts,
                'percentages': risk_percentages,
                'total_evaluated': tot_preds
            },
            'alerts': {
                'open_alerts': open_alerts,
                'resolved_alerts': resolved_alerts,
                'total_alerts': open_alerts + resolved_alerts
            }
        }
    }), 200


@principal_bp.route('/departments', methods=['GET'])
@authenticate()
@require_role('principal', 'admin')
def get_department_comparative_matrix():
    """
    Department-by-department comparative benchmarking.
    """
    depts = Department.query.all()
    matrix = []

    for d in depts:
        hod = db.session.get(Teacher, d.hod_teacher_id) if d.hod_teacher_id else None
        classes = d.classes
        class_ids = [c.class_id for c in classes]

        students = Student.query.filter(Student.class_id.in_(class_ids)).all() if class_ids else []
        student_count = len(students)
        faculty_count = len(d.teachers)
        student_ids = [s.student_id for s in students]

        # Department Attendance
        att_records = Attendance.query.filter(Attendance.student_id.in_(student_ids)).all() if student_ids else []
        tot_h = sum(a.total_classes for a in att_records)
        tot_a = sum(a.attended_classes for a in att_records)
        dept_avg_att = round((tot_a / tot_h * 100), 2) if tot_h > 0 else 0.0

        # Department CGPA
        sem_records = SemesterResult.query.filter(SemesterResult.student_id.in_(student_ids)).all() if student_ids else []
        tot_c = sum(r.credits_earned for r in sem_records)
        dept_cgpa = round(sum(float(r.sgpa) * r.credits_earned for r in sem_records) / tot_c, 2) if tot_c > 0 else 0.0

        # Department Risk counts
        preds = Prediction.query.filter(Prediction.student_id.in_(student_ids)).all() if student_ids else []
        high_risk = sum(1 for p in preds if p.risk_level == 'high')
        med_risk = sum(1 for p in preds if p.risk_level == 'medium')
        low_risk = sum(1 for p in preds if p.risk_level == 'low')

        matrix.append({
            'dept_id': d.dept_id,
            'dept_code': d.dept_code,
            'name': d.name,
            'hod_name': hod.name if hod else 'To Be Appointed',
            'headcount': {
                'students': student_count,
                'faculty': faculty_count,
                'ratio': round(student_count / faculty_count, 1) if faculty_count > 0 else 0
            },
            'performance': {
                'avg_attendance': dept_avg_att,
                'avg_cgpa': dept_cgpa,
                'risk_breakdown': {
                    'high': high_risk,
                    'medium': med_risk,
                    'low': low_risk
                }
            }
        })

    return jsonify({'success': True, 'data': matrix}), 200


@principal_bp.route('/classes', methods=['GET'])
@authenticate()
@require_role('principal', 'admin')
def get_class_cohort_performance():
    """
    Cohort-level drilldown list across departments.
    """
    dept_id = request.args.get('dept_id', type=int)
    query = Class.query
    if dept_id:
        query = query.filter_by(dept_id=dept_id)

    classes = query.all()
    results = []

    for c in classes:
        dept = db.session.get(Department, c.dept_id) if c.dept_id else None
        mentor = db.session.get(Teacher, c.mentor_teacher_id) if c.mentor_teacher_id else None
        students = c.students.all()
        student_ids = [s.student_id for s in students]

        att_records = Attendance.query.filter(Attendance.student_id.in_(student_ids)).all() if student_ids else []
        tot_h = sum(a.total_classes for a in att_records)
        tot_a = sum(a.attended_classes for a in att_records)
        avg_att = round((tot_a / tot_h * 100), 2) if tot_h > 0 else 0.0

        marks_records = Mark.query.filter(Mark.student_id.in_(student_ids)).all() if student_ids else []
        avg_cie = round(sum(float(m.total_cie) for m in marks_records) / len(marks_records), 2) if marks_records else 0.0

        preds = Prediction.query.filter(Prediction.student_id.in_(student_ids)).all() if student_ids else []
        high_risk_count = sum(1 for p in preds if p.risk_level in ('high', 'medium'))

        results.append({
            'class_id': c.class_id,
            'class_name': c.class_name,
            'section': c.section,
            'semester': c.semester,
            'academic_year': c.academic_year,
            'department_code': dept.dept_code if dept else 'N/A',
            'mentor_name': mentor.name if mentor else 'Unassigned',
            'student_count': len(students),
            'avg_attendance': avg_att,
            'avg_cie': avg_cie,
            'at_risk_students': high_risk_count
        })

    return jsonify({'success': True, 'data': results}), 200


@principal_bp.route('/students', methods=['GET'])
@authenticate()
@require_role('principal', 'admin')
def get_college_students():
    """
    College-wide multi-attribute student drilldown with search and risk filters.
    """
    dept_id = request.args.get('dept_id', type=int)
    class_id = request.args.get('class_id', type=int)
    risk_level = request.args.get('risk_level')
    search = request.args.get('search', '').strip()
    limit = request.args.get('limit', 1000, type=int)

    query = Student.query
    if class_id:
        query = query.filter_by(class_id=class_id)
    elif dept_id:
        classes = Class.query.filter_by(dept_id=dept_id).all()
        class_ids = [c.class_id for c in classes]
        query = query.filter(Student.class_id.in_(class_ids))

    if search:
        s_pat = f"%{search}%"
        query = query.filter(db.or_(Student.name.ilike(s_pat), Student.usn.ilike(s_pat)))

    students = query.limit(limit).all()
    results = []

    for s in students:
        # Attendance
        att_records = s.attendance_records.all()
        tot_h = sum(a.total_classes for a in att_records)
        tot_a = sum(a.attended_classes for a in att_records)
        att_pct = round((tot_a / tot_h * 100), 2) if tot_h > 0 else 0.0

        # CGPA
        sem_records = s.semester_results.all()
        tot_c = sum(r.credits_earned for r in sem_records)
        cgpa = round(sum(float(r.sgpa) * r.credits_earned for r in sem_records) / tot_c, 2) if tot_c > 0 else 0.0

        # Risk
        pred = Prediction.query.filter_by(student_id=s.student_id).order_by(Prediction.generated_at.desc()).first()
        r_level = pred.risk_level if pred else ('high' if att_pct < 65 else ('medium' if att_pct < 75 else 'low'))

        if risk_level and risk_level.lower() != 'all' and r_level.lower() != risk_level.lower():
            continue

        cls = s.enrolled_class
        results.append({
            'student_id': s.student_id,
            'name': s.name,
            'usn': s.usn,
            'class_name': cls.class_name if cls else 'N/A',
            'section': cls.section if cls else 'A',
            'semester': cls.semester if cls else 1,
            'department_code': cls.department.dept_code if cls and cls.department else 'N/A',
            'attendance_percentage': att_pct,
            'cgpa': cgpa,
            'risk_level': r_level,
            'risk_score': float(pred.risk_score) if pred else 0.15
        })

    return jsonify({'success': True, 'count': len(results), 'data': results}), 200


@principal_bp.route('/report/executive', methods=['GET'])
@authenticate()
@require_role('principal', 'admin')
def generate_executive_institutional_report():
    """
    Generate and stream an Executive Institutional Academic Audit PDF for governing councils.
    """
    all_students = Student.query.count()
    all_faculty = Teacher.query.count()
    all_departments = Department.query.all()
    all_attendance = Attendance.query.all()

    tot_held = sum(a.total_classes for a in all_attendance)
    tot_att = sum(a.attended_classes for a in all_attendance)
    college_avg_att = round((tot_att / tot_held * 100), 2) if tot_held > 0 else 0.0

    all_sem = SemesterResult.query.all()
    tot_c = sum(r.credits_earned for r in all_sem)
    college_avg_cgpa = round(sum(float(r.sgpa) * r.credits_earned for r in all_sem) / tot_c, 2) if tot_c > 0 else 0.0

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
        spaceBefore=14,
        spaceAfter=6
    )
    cell_style = ParagraphStyle('Cell', parent=styles['Normal'], fontSize=8.5, leading=11)
    bold_cell_style = ParagraphStyle('BoldCell', parent=styles['Normal'], fontSize=8.5, leading=11, fontName='Helvetica-Bold')

    story = []

    # 1. Institutional Letterhead
    story.append(Paragraph("<b>PES INSTITUTE OF TECHNOLOGY & MANAGEMENT</b>", title_style))
    story.append(Paragraph("Affiliated to VTU Belagavi | Approved by AICTE, New Delhi | Accredited Institution", subtitle_style))
    story.append(Paragraph("NH 206, Sagar Road, Shivamogga - 577204, Karnataka", subtitle_style))
    story.append(Paragraph("<b>OFFICE OF THE PRINCIPAL &bull; EXECUTIVE INSTITUTIONAL ACADEMIC REPORT</b>", ParagraphStyle('ReportName', parent=subtitle_style, fontSize=11, fontName='Helvetica-Bold', textColor=colors.HexColor('#14213d'), spaceBefore=4)))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2f6bff'), spaceAfter=10))

    # 2. Executive KPI Overview Table
    kpi_data = [
        [
            Paragraph("<b>Total Student Enrollment:</b>", bold_cell_style),
            Paragraph(str(all_students), cell_style),
            Paragraph("<b>Total Faculty Strength:</b>", bold_cell_style),
            Paragraph(str(all_faculty), cell_style)
        ],
        [
            Paragraph("<b>Student-to-Faculty Ratio:</b>", bold_cell_style),
            Paragraph(f"{round(all_students / all_faculty, 1)} : 1" if all_faculty > 0 else "N/A", cell_style),
            Paragraph("<b>Academic Programs:</b>", bold_cell_style),
            Paragraph(f"{len(all_departments)} Engineering Branches", cell_style)
        ],
        [
            Paragraph("<b>College Average Attendance:</b>", bold_cell_style),
            Paragraph(f"<b>{college_avg_att}%</b>", bold_cell_style),
            Paragraph("<b>Cumulative College CGPA:</b>", bold_cell_style),
            Paragraph(f"<b>{college_avg_cgpa} / 10.0</b>", bold_cell_style)
        ]
    ]

    t_kpi = Table(kpi_data, colWidths=[130, 140, 130, 140])
    t_kpi.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_kpi)
    story.append(Spacer(1, 14))

    # 3. Departmental Comparative Matrix
    story.append(Paragraph("I. DEPARTMENTAL ACADEMIC COMPARISON & HEADCOUNT MATRIX", h2_style))

    dept_table_data = [
        [
            Paragraph("<b>Branch Code</b>", bold_cell_style),
            Paragraph("<b>Department Name</b>", bold_cell_style),
            Paragraph("<b>Head of Department</b>", bold_cell_style),
            Paragraph("<b>Students</b>", bold_cell_style),
            Paragraph("<b>Avg Att. %</b>", bold_cell_style),
            Paragraph("<b>Avg CGPA</b>", bold_cell_style)
        ]
    ]

    for d in all_departments:
        hod = db.session.get(Teacher, d.hod_teacher_id) if d.hod_teacher_id else None
        cls_ids = [c.class_id for c in d.classes]
        st_count = Student.query.filter(Student.class_id.in_(cls_ids)).count() if cls_ids else 0

        dept_table_data.append([
            Paragraph(d.dept_code, bold_cell_style),
            Paragraph(d.name, cell_style),
            Paragraph(hod.name if hod else 'To Be Assigned', cell_style),
            Paragraph(str(st_count), cell_style),
            Paragraph(f"{college_avg_att}%", cell_style),
            Paragraph(f"{college_avg_cgpa}", cell_style)
        ])

    t_dept = Table(dept_table_data, colWidths=[65, 175, 130, 55, 60, 55])
    t_dept.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e2e8f0')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_dept)
    story.append(Spacer(1, 14))

    # 4. Machine Learning & Predictive Risk Findings
    story.append(Paragraph("II. PREDICTIVE ACADEMIC MONITORING & INTERVENTION SUMMARY", h2_style))
    story.append(Paragraph(
        "Based on institutional XGBoost classification models evaluating continuous internal evaluation scores, "
        "historical SGPA progression, and attendance patterns, students identified at High and Medium risk levels "
        "have been mapped to designated faculty mentors for proactive peer remediation.",
        cell_style
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("• <b>Action Directive 1:</b> All students with attendance below 75% require mandatory mentor intervention before VTU exam form validation.", cell_style))
    story.append(Paragraph("• <b>Action Directive 2:</b> Remedial tutorial sessions for critical internal assessments are operationalized across all engineering programs.", cell_style))

    story.append(Spacer(1, 40))

    # 5. Principal's Institutional Seal & Signature
    sig_data = [
        [
            Paragraph("____________________________<br/><b>Dean of Academics</b>", cell_style),
            Paragraph("____________________________<br/><b>Controller of Examinations</b>", cell_style),
            Paragraph("____________________________<br/><b>Principal & Director, PESITM</b>", cell_style)
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

    filename = "PESITM_Executive_Institutional_Report.pdf"
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )
