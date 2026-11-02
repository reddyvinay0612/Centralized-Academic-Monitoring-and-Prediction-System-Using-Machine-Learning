from datetime import datetime
from backend.extensions import db

class Department(db.Model):
    __tablename__ = 'departments'

    dept_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dept_code = db.Column(db.String(10), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    hod_teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.teacher_id', ondelete='SET NULL', use_alter=True), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    teachers = db.relationship('Teacher', backref='department', foreign_keys='Teacher.dept_id')
    courses = db.relationship('Course', backref='department', cascade='all, delete-orphan')
    classes = db.relationship('Class', backref='department')
    subjects = db.relationship('Subject', backref='department')

    def to_dict(self):
        return {
            'dept_id': self.dept_id,
            'dept_code': self.dept_code,
            'name': self.name,
            'hod_teacher_id': self.hod_teacher_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

class Course(db.Model):
    __tablename__ = 'courses'

    course_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    dept_id = db.Column(db.Integer, db.ForeignKey('departments.dept_id', ondelete='CASCADE'), nullable=False)
    duration_years = db.Column(db.Integer, default=4, nullable=False)

    def to_dict(self):
        return {
            'course_id': self.course_id,
            'course_code': self.course_code,
            'name': self.name,
            'dept_id': self.dept_id,
            'duration_years': self.duration_years,
        }

class AcademicYear(db.Model):
    __tablename__ = 'academic_years'

    year_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    year_name = db.Column(db.String(20), unique=True, nullable=False)  # e.g., '2024-25'
    is_current = db.Column(db.Boolean, default=True, nullable=False)

    def to_dict(self):
        return {
            'year_id': self.year_id,
            'year_name': self.year_name,
            'is_current': self.is_current,
        }

class Semester(db.Model):
    __tablename__ = 'semesters'

    semester_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    semester_number = db.Column(db.Integer, nullable=False)  # 1 to 8
    academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_years.year_id', ondelete='CASCADE'), nullable=True)

    def to_dict(self):
        return {
            'semester_id': self.semester_id,
            'semester_number': self.semester_number,
            'academic_year_id': self.academic_year_id,
        }

class Section(db.Model):
    __tablename__ = 'sections'

    section_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    section_name = db.Column(db.String(10), nullable=False)  # 'A', 'B', 'C'

    def to_dict(self):
        return {
            'section_id': self.section_id,
            'section_name': self.section_name,
        }

class Class(db.Model):
    __tablename__ = 'classes'

    class_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    class_name = db.Column(db.String(50), nullable=False)  # e.g. '5th Sem CSE'
    section = db.Column(db.String(5), nullable=False)      # 'A' or 'B'
    semester = db.Column(db.Integer, nullable=False)       # 5
    academic_year = db.Column(db.String(15), nullable=False) # '2024-25'
    dept_id = db.Column(db.Integer, db.ForeignKey('departments.dept_id', ondelete='RESTRICT'), nullable=False)
    mentor_teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.teacher_id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('class_name', 'section', 'academic_year', name='uq_class_sec_year'),
    )

    # Relationships
    students = db.relationship('Student', backref='enrolled_class', lazy='dynamic')
    timetables = db.relationship('Timetable', backref='class_unit', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'class_id': self.class_id,
            'class_name': self.class_name,
            'section': self.section,
            'semester': self.semester,
            'academic_year': self.academic_year,
            'dept_id': self.dept_id,
            'mentor_teacher_id': self.mentor_teacher_id,
        }

class Subject(db.Model):
    __tablename__ = 'subjects'

    subject_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject_code = db.Column(db.String(15), unique=True, nullable=False)
    subject_name = db.Column(db.String(100), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    credits = db.Column(db.Integer, default=3, nullable=False)
    dept_id = db.Column(db.Integer, db.ForeignKey('departments.dept_id', ondelete='RESTRICT'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'subject_id': self.subject_id,
            'subject_code': self.subject_code,
            'subject_name': self.subject_name,
            'semester': self.semester,
            'credits': self.credits,
            'dept_id': self.dept_id,
        }

class Timetable(db.Model):
    __tablename__ = 'timetable'

    timetable_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.class_id', ondelete='CASCADE'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.subject_id', ondelete='CASCADE'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.teacher_id', ondelete='SET NULL'), nullable=True)
    day_of_week = db.Column(db.String(15), nullable=False)  # 'Monday'
    start_time = db.Column(db.String(10), nullable=False)   # '09:00 AM'
    end_time = db.Column(db.String(10), nullable=False)     # '10:00 AM'
    room_number = db.Column(db.String(20), default='LH-101', nullable=False)

    # Relationships
    subject = db.relationship('Subject')
    teacher = db.relationship('Teacher')

    def to_dict(self):
        return {
            'timetable_id': self.timetable_id,
            'class_id': self.class_id,
            'subject_id': self.subject_id,
            'subject_code': self.subject.subject_code if self.subject else None,
            'subject_name': self.subject.subject_name if self.subject else None,
            'teacher_id': self.teacher_id,
            'teacher_name': self.teacher.name if self.teacher else None,
            'day_of_week': self.day_of_week,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'room_number': self.room_number,
        }
