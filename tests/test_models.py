"""
Unit Tests for SQLAlchemy Models in CAMPS-ML.
Verifies password hashing, attendance percentage calculations, and CIE algorithms.
"""

from app.models import User, StudentProfile, AttendanceRecord, InternalAssessment


def test_user_password_hashing(app):
    """Verify that passwords are securely hashed and validated."""
    user = User(email="unique.tester@camps.edu", role="student")
    user.set_password("MySecurePass#2024")
    
    assert user.password_hash != "MySecurePass#2024"
    assert user.check_password("MySecurePass#2024") is True
    assert user.check_password("WrongPassword") is False


def test_attendance_shortage_calculation():
    """Verify that attendance percentage < 75% correctly triggers shortage flag."""
    att = AttendanceRecord(total_classes=40, attended_classes=28)
    att.calculate_percentage()
    assert att.percentage == 70.0
    assert att.is_shortage is True

    att.attended_classes = 32
    att.calculate_percentage()
    assert att.percentage == 80.0
    assert att.is_shortage is False


def test_cie_score_computation():
    """
    Verify standard CIE computation:
    Average of best 2 out of 3 IAs (max 30) + Assignment (max 10) + Lab (max 10) = Max 50.
    """
    cie = InternalAssessment(
        ia1_marks=22.0,
        ia2_marks=18.0,
        ia3_marks=26.0,
        assignment_marks=9.0,
        lab_marks=8.5
    )
    total = cie.compute_total_cie()
    # Best 2 are 26 and 22 -> Avg = 24.0. Total = 24.0 + 9.0 + 8.5 = 41.5
    assert total == 41.5
