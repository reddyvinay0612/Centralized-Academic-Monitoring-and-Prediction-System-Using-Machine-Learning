from datetime import datetime
from backend.extensions import db

class Attendance(db.Model):
    __tablename__ = 'attendance'

    attendance_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id', ondelete='CASCADE'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.subject_id', ondelete='CASCADE'), nullable=False)
    total_classes = db.Column(db.Integer, default=0, nullable=False)
    attended_classes = db.Column(db.Integer, default=0, nullable=False)
    percentage = db.Column(db.Numeric(5, 2), default=0.0, nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('student_id', 'subject_id', name='uq_student_subject_att'),
    )

    # Relationships
    subject = db.relationship('Subject')

    def calculate_percentage(self):
        if self.total_classes > 0:
            self.percentage = round((self.attended_classes / self.total_classes) * 100, 2)
        else:
            self.percentage = 0.0
        return self.percentage

    def to_dict(self):
        return {
            'attendance_id': self.attendance_id,
            'student_id': self.student_id,
            'subject_id': self.subject_id,
            'subject_code': self.subject.subject_code if self.subject else None,
            'subject_name': self.subject.subject_name if self.subject else None,
            'total_classes': self.total_classes,
            'attended_classes': self.attended_classes,
            'percentage': float(self.percentage) if self.percentage is not None else 0.0,
            'is_shortage': float(self.percentage or 0) < 75.0,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
        }

class Mark(db.Model):
    __tablename__ = 'marks'

    marks_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id', ondelete='CASCADE'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.subject_id', ondelete='CASCADE'), nullable=False)
    cie1 = db.Column(db.Numeric(4, 1), default=0.0, nullable=False)
    cie2 = db.Column(db.Numeric(4, 1), default=0.0, nullable=False)
    cie3 = db.Column(db.Numeric(4, 1), default=0.0, nullable=False)
    assignment_marks = db.Column(db.Numeric(4, 1), default=0.0, nullable=False)
    quiz_marks = db.Column(db.Numeric(4, 1), default=0.0, nullable=False)
    total_cie = db.Column(db.Numeric(5, 2), default=0.0, nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('student_id', 'subject_id', name='uq_student_subject_marks'),
    )

    # Relationships
    subject = db.relationship('Subject')
    history_entries = db.relationship('MarkHistory', backref='mark_record', cascade='all, delete-orphan')

    def calculate_total(self):
        """Standard VTU CIE aggregate: Average of top 2 CIEs + Assignments + Quizzes"""
        tests = sorted([float(self.cie1 or 0), float(self.cie2 or 0), float(self.cie3 or 0)], reverse=True)
        top2_avg = (tests[0] + tests[1]) / 2.0 if len(tests) >= 2 else 0.0
        self.total_cie = round(top2_avg + float(self.assignment_marks or 0) + float(self.quiz_marks or 0), 2)
        return self.total_cie

    def to_dict(self):
        return {
            'marks_id': self.marks_id,
            'student_id': self.student_id,
            'subject_id': self.subject_id,
            'subject_code': self.subject.subject_code if self.subject else None,
            'subject_name': self.subject.subject_name if self.subject else None,
            'cie1': float(self.cie1) if self.cie1 is not None else 0.0,
            'cie2': float(self.cie2) if self.cie2 is not None else 0.0,
            'cie3': float(self.cie3) if self.cie3 is not None else 0.0,
            'assignment_marks': float(self.assignment_marks) if self.assignment_marks is not None else 0.0,
            'quiz_marks': float(self.quiz_marks) if self.quiz_marks is not None else 0.0,
            'total_cie': float(self.total_cie) if self.total_cie is not None else 0.0,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
        }

class MarkHistory(db.Model):
    __tablename__ = 'mark_history'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    marks_id = db.Column(db.Integer, db.ForeignKey('marks.marks_id', ondelete='CASCADE'), nullable=False)
    field_name = db.Column(db.String(50), default='total_cie', nullable=False)
    old_value = db.Column(db.Numeric(5, 2), nullable=False)
    new_value = db.Column(db.Numeric(5, 2), nullable=False)
    changed_by = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='RESTRICT'), nullable=False)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    reason = db.Column(db.Text, nullable=False)

    # Relationship to user who altered marks
    editor = db.relationship('User')

    def to_dict(self):
        return {
            'id': self.id,
            'marks_id': self.marks_id,
            'field_name': self.field_name,
            'old_value': float(self.old_value),
            'new_value': float(self.new_value),
            'changed_by': self.changed_by,
            'editor_name': self.editor.username if self.editor else None,
            'changed_at': self.changed_at.isoformat(),
            'reason': self.reason,
        }

class SemesterResult(db.Model):
    __tablename__ = 'semester_results'

    result_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id', ondelete='CASCADE'), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    sgpa = db.Column(db.Numeric(4, 2), nullable=False)
    credits_earned = db.Column(db.Integer, default=20, nullable=False)
    backlogs = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('student_id', 'semester', name='uq_student_semester'),
    )

    def to_dict(self):
        return {
            'result_id': self.result_id,
            'student_id': self.student_id,
            'semester': self.semester,
            'sgpa': float(self.sgpa),
            'credits_earned': self.credits_earned,
            'backlogs': self.backlogs,
        }

class Assignment(db.Model):
    __tablename__ = 'assignments'

    assignment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.subject_id', ondelete='CASCADE'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.class_id', ondelete='CASCADE'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.teacher_id', ondelete='SET NULL'), nullable=True)
    due_date = db.Column(db.DateTime, nullable=False)
    max_marks = db.Column(db.Numeric(4, 1), default=10.0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    subject = db.relationship('Subject')
    submissions = db.relationship('AssignmentSubmission', backref='assignment', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'assignment_id': self.assignment_id,
            'title': self.title,
            'description': self.description,
            'subject_id': self.subject_id,
            'subject_code': self.subject.subject_code if self.subject else None,
            'class_id': self.class_id,
            'due_date': self.due_date.isoformat(),
            'max_marks': float(self.max_marks),
        }

class AssignmentSubmission(db.Model):
    __tablename__ = 'assignment_submissions'

    submission_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.assignment_id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id', ondelete='CASCADE'), nullable=False)
    submission_file = db.Column(db.String(255), nullable=True)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    marks_obtained = db.Column(db.Numeric(4, 1), nullable=True)
    status = db.Column(
        db.Enum('submitted', 'graded', 'late', name='submission_status_enum'),
        default='submitted',
        nullable=False
    )

    def to_dict(self):
        return {
            'submission_id': self.submission_id,
            'assignment_id': self.assignment_id,
            'student_id': self.student_id,
            'submitted_at': self.submitted_at.isoformat(),
            'marks_obtained': float(self.marks_obtained) if self.marks_obtained is not None else None,
            'status': self.status,
        }

class Examination(db.Model):
    __tablename__ = 'examinations'

    exam_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    exam_name = db.Column(db.String(100), nullable=False)  # e.g., 'CIE Test 1', 'Semester End Exam'
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.subject_id', ondelete='CASCADE'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.class_id', ondelete='CASCADE'), nullable=False)
    exam_date = db.Column(db.DateTime, nullable=False)
    start_time = db.Column(db.String(10), nullable=True)
    end_time = db.Column(db.String(10), nullable=True)
    max_marks = db.Column(db.Numeric(5, 2), default=50.0, nullable=False)

    subject = db.relationship('Subject')

    def to_dict(self):
        return {
            'exam_id': self.exam_id,
            'exam_name': self.exam_name,
            'subject_id': self.subject_id,
            'subject_code': self.subject.subject_code if self.subject else None,
            'class_id': self.class_id,
            'exam_date': self.exam_date.isoformat(),
            'start_time': self.start_time,
            'end_time': self.end_time,
            'max_marks': float(self.max_marks),
        }

class Participation(db.Model):
    __tablename__ = 'participation'

    participation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id', ondelete='CASCADE'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.subject_id', ondelete='CASCADE'), nullable=False)
    score = db.Column(db.Numeric(4, 1), default=5.0, nullable=False)
    month = db.Column(db.String(15), nullable=False)
    remarks = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
