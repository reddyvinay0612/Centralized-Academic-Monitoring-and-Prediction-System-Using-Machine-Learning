"""
Academic Structure ORM Models for CAMPS-ML.
Handles Departments, Courses/Subjects, and Semester Course Enrollments.
"""

from app import db


class Department(db.Model):
    """Academic Department (e.g., Computer Science & Design)."""
    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False, index=True)  # CSD, CSE, ISE
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)

    # Relationships
    faculty_members = db.relationship("FacultyProfile", back_populates="department")
    students = db.relationship("StudentProfile", back_populates="department")
    courses = db.relationship("Course", back_populates="department", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Department {self.code} - {self.name}>"


class Course(db.Model):
    """Curriculum Subject / Course offering."""
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)  # e.g., 21CS51
    name = db.Column(db.String(120), nullable=False)  # e.g., Machine Learning
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=False)
    semester = db.Column(db.Integer, nullable=False)  # 1 to 8
    credits = db.Column(db.Integer, default=3, nullable=False)
    is_laboratory = db.Column(db.Boolean, default=False, nullable=False)
    syllabus_scheme = db.Column(db.String(20), default="2021 Scheme")

    # Relationships
    department = db.relationship("Department", back_populates="courses")
    enrollments = db.relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Course {self.code} - {self.name} (Sem {self.semester})>"


class Enrollment(db.Model):
    """Student registration for a specific course in a specific term."""
    __tablename__ = "enrollments"
    __table_args__ = (
        db.UniqueConstraint("student_id", "course_id", "academic_year", name="uq_student_course_year"),
    )

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    academic_year = db.Column(db.String(10), nullable=False)  # e.g., '2024-25'
    semester = db.Column(db.Integer, nullable=False)

    # Relationships
    student = db.relationship("StudentProfile", back_populates="enrollments")
    course = db.relationship("Course", back_populates="enrollments")
    attendance = db.relationship("AttendanceRecord", back_populates="enrollment", uselist=False, cascade="all, delete-orphan")
    internal_assessment = db.relationship("InternalAssessment", back_populates="enrollment", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Enrollment Student:{self.student_id} Course:{self.course_id} Sem:{self.semester}>"
