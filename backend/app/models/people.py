from datetime import datetime
from backend.extensions import db

class Teacher(db.Model):
    __tablename__ = 'teachers'

    teacher_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    employee_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    designation = db.Column(db.String(60), default='Assistant Professor', nullable=False)
    dept_id = db.Column(db.Integer, db.ForeignKey('departments.dept_id', ondelete='RESTRICT'), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Scoped class-subject assignments
    assignments = db.relationship('TeacherAssignment', backref='teacher', cascade='all, delete-orphan')
    mentored_classes = db.relationship('Class', backref='mentor_teacher', foreign_keys='Class.mentor_teacher_id')
    remarks_logged = db.relationship('Remark', backref='author_teacher')

    def to_dict(self):
        return {
            'teacher_id': self.teacher_id,
            'user_id': self.user_id,
            'name': self.name,
            'employee_id': self.employee_id,
            'designation': self.designation,
            'dept_id': self.dept_id,
            'phone': self.phone,
        }

class Parent(db.Model):
    __tablename__ = 'parents'

    parent_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False, index=True)
    email = db.Column(db.String(100), nullable=True)
    address = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Many-to-Many with Student via parent_students
    children = db.relationship(
        'Student',
        secondary='parent_students',
        back_populates='parents',
        lazy='dynamic'
    )

    def to_dict(self):
        return {
            'parent_id': self.parent_id,
            'user_id': self.user_id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
        }

class Student(db.Model):
    __tablename__ = 'students'

    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    usn = db.Column(db.String(20), unique=True, nullable=False, index=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.class_id', ondelete='RESTRICT'), nullable=False)
    academic_status = db.Column(
        db.Enum('active', 'detained', 'graduated', 'dropped', name='student_status_enum'),
        default='active',
        nullable=False
    )
    fee_status = db.Column(
        db.Enum('paid', 'pending', name='student_fee_enum'),
        default='paid',
        nullable=False
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    parents = db.relationship(
        'Parent',
        secondary='parent_students',
        back_populates='children',
        lazy='dynamic'
    )
    attendance_records = db.relationship('Attendance', backref='student', cascade='all, delete-orphan', lazy='dynamic')
    marks_records = db.relationship('Mark', backref='student', cascade='all, delete-orphan', lazy='dynamic')
    semester_results = db.relationship('SemesterResult', backref='student', cascade='all, delete-orphan', lazy='dynamic')
    predictions = db.relationship('Prediction', backref='student', cascade='all, delete-orphan', lazy='dynamic')
    alerts = db.relationship('Alert', backref='student', cascade='all, delete-orphan', lazy='dynamic')
    remarks = db.relationship('Remark', backref='student', cascade='all, delete-orphan', lazy='dynamic')
    fee_payments = db.relationship('FeePayment', backref='student', cascade='all, delete-orphan', lazy='dynamic')

    def to_dict(self):
        return {
            'student_id': self.student_id,
            'user_id': self.user_id,
            'name': self.name,
            'usn': self.usn,
            'class_id': self.class_id,
            'class_name': self.enrolled_class.class_name if self.enrolled_class else None,
            'section': self.enrolled_class.section if self.enrolled_class else None,
            'semester': self.enrolled_class.semester if self.enrolled_class else None,
            'academic_status': self.academic_status,
            'fee_status': self.fee_status,
        }

class ParentStudent(db.Model):
    __tablename__ = 'parent_students'

    parent_id = db.Column(db.Integer, db.ForeignKey('parents.parent_id', ondelete='CASCADE'), primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id', ondelete='CASCADE'), primary_key=True)
    relation = db.Column(db.String(50), default='Parent', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class TeacherAssignment(db.Model):
    __tablename__ = 'teacher_classes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.teacher_id', ondelete='CASCADE'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.class_id', ondelete='CASCADE'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.subject_id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('teacher_id', 'class_id', 'subject_id', name='uq_teacher_class_subject'),
    )

    # Relationships
    assigned_class = db.relationship('Class')
    assigned_subject = db.relationship('Subject')

    def to_dict(self):
        return {
            'id': self.id,
            'teacher_id': self.teacher_id,
            'class_id': self.class_id,
            'class_name': self.assigned_class.class_name if self.assigned_class else None,
            'section': self.assigned_class.section if self.assigned_class else None,
            'subject_id': self.subject_id,
            'subject_code': self.assigned_subject.subject_code if self.assigned_subject else None,
            'subject_name': self.assigned_subject.subject_name if self.assigned_subject else None,
        }
