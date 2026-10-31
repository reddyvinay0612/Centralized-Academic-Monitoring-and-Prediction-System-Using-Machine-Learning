"""
Reporting Service for CAMPS-ML.
Generates:
1. Professional Student Transcript & Risk Audit PDF via ReportLab
2. Class & Department Performance / Risk Matrix Excel via openpyxl
"""

import os
from datetime import datetime
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

from app.models import StudentProfile, PredictionLog, SHAPFactor, MentorRemark, Enrollment

BASE_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = BASE_DIR / "reports_output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def generate_student_pdf_report(student_id: int) -> str:
    """Generate comprehensive student academic transcript and risk audit PDF."""
    student = StudentProfile.query.get(student_id)
    if not student:
        raise ValueError(f"Student ID {student_id} not found.")

    filename = f"Transcript_{student.usn}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    pdf_path = OUTPUT_DIR / filename

    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "DocTitle", parent=styles["Heading1"], fontSize=18, leading=22, textColor=colors.HexColor("#0d6efd"), alignment=1
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle", parent=styles["Normal"], fontSize=10, leading=14, textColor=colors.HexColor("#6c757d"), alignment=1
    )
    heading2_style = ParagraphStyle(
        "SectionHeading", parent=styles["Heading2"], fontSize=12, leading=16, textColor=colors.HexColor("#212529"), spaceBefore=10, spaceAfter=6
    )
    normal_style = ParagraphStyle("Body", parent=styles["Normal"], fontSize=9, leading=12)

    elements = []

    # Header
    elements.append(Paragraph("CENTRALIZED ACADEMIC MONITORING AND PREDICTION SYSTEM", title_style))
    elements.append(Paragraph("Confidential Student Academic Progress & Predictive Risk Audit", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0d6efd"), spaceAfter=12, spaceBefore=6))

    # Student Demographics Table
    mentor_name = f"{student.mentor.first_name} {student.mentor.last_name}" if student.mentor else "Not Assigned"
    demo_data = [
        [Paragraph(f"<b>USN:</b> {student.usn}", normal_style), Paragraph(f"<b>Student Name:</b> {student.first_name} {student.last_name}", normal_style)],
        [Paragraph(f"<b>Department:</b> {student.department.name if student.department else 'N/A'}", normal_style), Paragraph(f"<b>Current Semester:</b> {student.current_semester} (Sec {student.section})", normal_style)],
        [Paragraph(f"<b>Cumulative CGPA:</b> {student.cumulative_cgpa:.2f}", normal_style), Paragraph(f"<b>Active Backlogs:</b> {student.total_active_backlogs}", normal_style)],
        [Paragraph(f"<b>Fee Status:</b> {student.fee_status}", normal_style), Paragraph(f"<b>Faculty Mentor:</b> {mentor_name}", normal_style)],
    ]
    t_demo = Table(demo_data, colWidths=[270, 270])
    t_demo.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8f9fa")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e9ecef")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(t_demo)
    elements.append(Spacer(1, 10))

    # Machine Learning Early-Warning Prediction Card
    elements.append(Paragraph("Machine Learning Predictive Assessment (XAI Engine)", heading2_style))
    latest_pred = PredictionLog.query.filter_by(student_id=student.id).order_by(PredictionLog.created_at.desc()).first()

    if latest_pred:
        risk_color = colors.HexColor("#dc3545") if latest_pred.predicted_risk_level == "High" else (
            colors.HexColor("#ffc107") if latest_pred.predicted_risk_level == "Medium" else colors.HexColor("#198754")
        )
        ml_data = [
            [
                Paragraph(f"<b>Predicted Academic Risk Tier:</b> <font color='{risk_color.hexval()}'><b>{latest_pred.predicted_risk_level.upper()} RISK</b></font>", normal_style),
                Paragraph(f"<b>Dropout / Failure Probability:</b> {latest_pred.risk_probability*100:.1f}%", normal_style)
            ],
            [
                Paragraph(f"<b>Forecasted Next-Sem SGPA:</b> {latest_pred.predicted_sgpa or 'N/A'}", normal_style),
                Paragraph(f"<b>Model Engine:</b> {latest_pred.model_name} ({latest_pred.model_version})", normal_style)
            ]
        ]
        t_ml = Table(ml_data, colWidths=[270, 270])
        t_ml.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
            ("BOX", (0, 0), (-1, -1), 1, risk_color),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        elements.append(t_ml)
        elements.append(Spacer(1, 8))

        # Top SHAP Explainability Factors
        if latest_pred.shap_factors:
            elements.append(Paragraph("<b>Top Local Contributing Risk Factors (TreeSHAP Attributions):</b>", normal_style))
            shap_rows = [["Risk Factor Name", "Observed Value", "SHAP Impact", "Effect on Student"]]
            for sf in latest_pred.shap_factors:
                shap_rows.append([
                    sf.feature_name,
                    sf.feature_value or "N/A",
                    f"{sf.shap_value:+.3f}",
                    sf.impact_direction
                ])
            t_shap = Table(shap_rows, colWidths=[180, 110, 110, 140])
            t_shap.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d6efd")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]))
            elements.append(t_shap)
            elements.append(Spacer(1, 10))

    # Current Semester Course & Attendance Breakdown
    elements.append(Paragraph(f"Current Semester ({student.current_semester}) Continuous Assessment & Attendance", heading2_style))
    enrollments = Enrollment.query.filter_by(student_id=student.id).all()
    course_rows = [["Course Code", "Course Title", "Credits", "Attendance %", "IA1 (30)", "IA2 (30)", "CIE (50)"]]

    for e in enrollments:
        att = f"{e.attendance.percentage:.1f}%" if e.attendance else "N/A"
        ia1 = f"{e.internal_assessment.ia1_marks}" if e.internal_assessment and e.internal_assessment.ia1_marks is not None else "-"
        ia2 = f"{e.internal_assessment.ia2_marks}" if e.internal_assessment and e.internal_assessment.ia2_marks is not None else "-"
        cie = f"{e.internal_assessment.total_cie}" if e.internal_assessment and e.internal_assessment.total_cie is not None else "-"
        course_rows.append([
            e.course.code,
            e.course.name[:32],
            str(e.course.credits),
            att,
            ia1,
            ia2,
            cie
        ])

    t_course = Table(course_rows, colWidths=[75, 185, 45, 75, 50, 50, 60])
    t_course.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#343a40")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
        ("ALIGN", (2, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    elements.append(t_course)
    elements.append(Spacer(1, 12))

    # Mentor Remarks & Counseling Section
    elements.append(Paragraph("Mentor Counseling & Intervention History", heading2_style))
    remarks = MentorRemark.query.filter_by(student_id=student.id).order_by(MentorRemark.created_at.desc()).all()
    if remarks:
        rem_rows = [["Date", "Mentor", "Category", "Action Plan / Remedial Measure", "Status"]]
        for r in remarks:
            rem_rows.append([
                r.created_at.strftime("%d-%b-%Y"),
                f"Prof. {r.faculty.last_name}",
                r.concern_category,
                Paragraph(r.action_plan or r.remark_text, normal_style),
                r.status
            ])
        t_rem = Table(rem_rows, colWidths=[70, 85, 95, 230, 60])
        t_rem.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#6c757d")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(t_rem)
    else:
        elements.append(Paragraph("<i>No formal counseling interventions recorded to date.</i>", normal_style))

    # Signatures
    elements.append(Spacer(1, 25))
    sig_data = [
        [Paragraph("____________________________<br/><b>Student Signature</b>", normal_style),
         Paragraph("____________________________<br/><b>Faculty Mentor Signature</b>", normal_style),
         Paragraph("____________________________<br/><b>HoD / Dean Academics</b>", normal_style)]
    ]
    t_sig = Table(sig_data, colWidths=[180, 180, 180])
    t_sig.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER")]))
    elements.append(t_sig)

    doc.build(elements)
    return str(pdf_path)


def generate_class_excel_report(department_code="CSD", semester=5) -> str:
    """Generate Excel workbook summarizing all students in a department/semester."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"{department_code}_Sem{semester}_Audit"

    # Styling
    header_fill = PatternFill(start_color="0D6EFD", end_color="0D6EFD", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    bold_font = Font(name="Calibri", size=10, bold=True)
    regular_font = Font(name="Calibri", size=10)

    # Title Block
    ws.merge_cells("A1:K1")
    title_cell = ws["A1"]
    title_cell.value = f"CAMPS-ML ACADEMIC MONITORING REPORT - DEPT OF {department_code} (SEMESTER {semester})"
    title_cell.font = Font(name="Calibri", size=14, bold=True, color="0D6EFD")
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 28

    headers = [
        "USN", "Student Name", "Section", "Avg Attendance %", "Total CIE (50)",
        "Cumulative CGPA", "Backlogs", "Fee Status", "Predicted Risk Tier",
        "Risk Probability", "Projected Next SGPA"
    ]

    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=3, column=col_idx, value=h)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[3].height = 24

    # Fetch students
    students = StudentProfile.query.filter_by(current_semester=semester).all()
    row_idx = 4
    for s in students:
        # compute attendance and CIE averages
        enrollments = Enrollment.query.filter_by(student_id=s.id).all()
        att_pct = round(sum(e.attendance.percentage for e in enrollments if e.attendance) / len(enrollments), 1) if enrollments else 0.0
        cie_avg = round(sum(e.internal_assessment.total_cie for e in enrollments if e.internal_assessment) / len(enrollments), 1) if enrollments else 0.0
        
        pred = PredictionLog.query.filter_by(student_id=s.id).order_by(PredictionLog.created_at.desc()).first()
        risk_tier = pred.predicted_risk_level if pred else s.current_risk_level
        risk_prob = f"{pred.risk_probability*100:.1f}%" if pred else "N/A"
        pred_sgpa = pred.predicted_sgpa if pred else s.cumulative_cgpa

        ws.cell(row=row_idx, column=1, value=s.usn).font = bold_font
        ws.cell(row=row_idx, column=2, value=f"{s.first_name} {s.last_name}").font = regular_font
        ws.cell(row=row_idx, column=3, value=s.section).font = regular_font
        ws.cell(row=row_idx, column=4, value=att_pct).font = regular_font
        ws.cell(row=row_idx, column=5, value=cie_avg).font = regular_font
        ws.cell(row=row_idx, column=6, value=s.cumulative_cgpa).font = regular_font
        ws.cell(row=row_idx, column=7, value=s.total_active_backlogs).font = regular_font
        ws.cell(row=row_idx, column=8, value=s.fee_status).font = regular_font
        
        risk_cell = ws.cell(row=row_idx, column=9, value=risk_tier)
        risk_cell.font = bold_font
        if risk_tier == "High":
            risk_cell.font = Font(name="Calibri", size=10, bold=True, color="DC3545")
        elif risk_tier == "Medium":
            risk_cell.font = Font(name="Calibri", size=10, bold=True, color="FFC107")
        else:
            risk_cell.font = Font(name="Calibri", size=10, bold=True, color="198754")

        ws.cell(row=row_idx, column=10, value=risk_prob).font = regular_font
        ws.cell(row=row_idx, column=11, value=pred_sgpa).font = regular_font

        row_idx += 1

    # Adjust column widths
    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = openpyxl.utils.get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

    filename = f"Class_Risk_Audit_{department_code}_Sem{semester}_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
    excel_path = OUTPUT_DIR / filename
    wb.save(excel_path)
    return str(excel_path)
