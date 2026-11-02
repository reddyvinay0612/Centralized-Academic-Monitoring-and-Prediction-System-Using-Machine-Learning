from backend.extensions import db

# 1. User & Authentication Models
from backend.app.models.user import User, PasswordReset, RefreshToken

# 2. Academic & Curriculum Models
from backend.app.models.academic import (
    Department,
    Course,
    AcademicYear,
    Semester,
    Section,
    Class,
    Subject,
    Timetable
)

# 3. People & Role Profiles
from backend.app.models.people import (
    Teacher,
    Parent,
    Student,
    ParentStudent,
    TeacherAssignment
)

# 4. Assessment, Attendance & Grading Models
from backend.app.models.grading import (
    Attendance,
    Mark,
    MarkHistory,
    SemesterResult,
    Assignment,
    AssignmentSubmission,
    Examination,
    Participation
)

# 5. Finance & Fees
from backend.app.models.finance import Fee, FeePayment

# 6. Governance, ML, Alerts & Audit Logs
from backend.app.models.system import (
    AuditLog,
    Notification,
    Alert,
    Remark,
    ModelRun,
    Prediction,
    Explanation
)

__all__ = [
    'db',
    'User',
    'PasswordReset',
    'RefreshToken',
    'Department',
    'Course',
    'AcademicYear',
    'Semester',
    'Section',
    'Class',
    'Subject',
    'Timetable',
    'Teacher',
    'Parent',
    'Student',
    'ParentStudent',
    'TeacherAssignment',
    'Attendance',
    'Mark',
    'MarkHistory',
    'SemesterResult',
    'Assignment',
    'AssignmentSubmission',
    'Examination',
    'Participation',
    'Fee',
    'FeePayment',
    'AuditLog',
    'Notification',
    'Alert',
    'Remark',
    'ModelRun',
    'Prediction',
    'Explanation'
]
