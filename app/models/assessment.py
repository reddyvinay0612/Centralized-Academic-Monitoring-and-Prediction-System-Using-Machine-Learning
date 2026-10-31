"""
Assessment ORM Models for CAMPS-ML.
Handles Attendance Tracking, Continuous Internal Evaluation (IA1-IA3, CIE),
and End-Semester Exam Results (SGPA, CGPA, Backlogs).
"""

from datetime import datetime
from app import db


class AttendanceRecord(db.Model):
    """Attendance log per enrolled course."""
    __tablename__ = "attendance_records"

    id = db.Column(db.Integer, primary_key=True)
    enrollment_id = db.Column(db.Integer, db.ForeignKey("enrollments.id", ondelete="CASCADE"), unique=True, nullable=False)
    total_classes = db.Column(db.Integer, default=0, nullable=False)
    attended_classes = db.Column(db.Integer, default=0, nullable=False)
    percentage = db.Column(db.Float, default=100.0, nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    enrollment = db.relationship("Enrollment", back_populates="attendance")

    def calculate_percentage(self):
        """Update attendance percentage with boundary checking."""
        if self.total_classes > 0:
            self.percentage = round((self.attended_classes / self.total_classes) * 100.0, 2)
        else:
            self.percentage = 100.0
        return self.percentage

    @property
    def is_shortage(self):
        """Returns True if attendance falls below mandatory 75% AICTE/VTU threshold."""
        return self.percentage < 75.0

    def __repr__(self):
        return f"<Attendance Enrollment:{self.enrollment_id} - {self.percentage}%>"


class InternalAssessment(db.Model):
    """Continuous Internal Evaluation (CIE) record per enrolled course."""
    __tablename__ = "internal_assessments"

    id = db.Column(db.Integer, primary_key=True)
    enrollment_id = db.Column(db.Integer, db.ForeignKey("enrollments.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Standard Indian Engineering CIE Scale (IA Tests out of 30, Assignments out of 10, Lab out of 10)
    ia1_marks = db.Column(db.Float, nullable=True)  # Max 30
    ia2_marks = db.Column(db.Float, nullable=True)  # Max 30
    ia3_marks = db.Column(db.Float, nullable=True)  # Max 30
    assignment_marks = db.Column(db.Float, default=0.0)  # Max 10
    lab_marks = db.Column(db.Float, default=0.0)         # Max 10 (or 20 for lab integrated courses)
    total_cie = db.Column(db.Float, default=0.0)        # Best 2 IAs + Assignment + Lab -> Scaled to 50

    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    enrollment = db.relationship("Enrollment", back_populates="internal_assessment")

    def compute_total_cie(self):
        """
        Compute total continuous internal marks.
        Standard convention: Average of best 2 out of 3 IAs (max 30) + Assignment (max 10) + Lab/Seminar (max 10) = Max 50.
        """
        ia_scores = [m for m in [self.ia1_marks, self.ia2_marks, self.ia3_marks] if m is not None]
        if len(ia_scores) >= 2:
            ia_scores.sort(reverse=True)
            best_two_avg = (ia_scores[0] + ia_scores[1]) / 2.0
        elif len(ia_scores) == 1:
            best_two_avg = ia_scores[0]
        else:
            best_two_avg = 0.0

        assignment = self.assignment_marks or 0.0
        lab = self.lab_marks or 0.0
        self.total_cie = round(best_two_avg + assignment + lab, 2)
        return self.total_cie

    def __repr__(self):
        return f"<CIE Enrollment:{self.enrollment_id} - Total:{self.total_cie}/50>"


class SemesterResult(db.Model):
    """End-Semester Performance Ledger (SGPA, CGPA, Backlogs)."""
    __tablename__ = "semester_results"
    __table_args__ = (
        db.UniqueConstraint("student_id", "semester", name="uq_student_semester_result"),
    )

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    semester = db.Column(db.Integer, nullable=False)  # Semester 1 through 8
    sgpa = db.Column(db.Float, nullable=False)        # 0.00 to 10.00
    cgpa_after_sem = db.Column(db.Float, nullable=False)
    credits_registered = db.Column(db.Integer, default=20, nullable=False)
    credits_earned = db.Column(db.Integer, default=20, nullable=False)
    backlogs_count = db.Column(db.Integer, default=0, nullable=False)
    result_status = db.Column(db.String(20), default="Pass")  # Pass, Arrears, Withheld

    # Relationships
    student = db.relationship("StudentProfile", back_populates="semester_results")

    def __repr__(self):
        return f"<Result Student:{self.student_id} Sem:{self.semester} SGPA:{self.sgpa}>"
