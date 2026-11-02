from datetime import datetime
from backend.extensions import db

class Fee(db.Model):
    __tablename__ = 'fees'

    fee_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.class_id', ondelete='CASCADE'), nullable=False)
    academic_year = db.Column(db.String(15), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    enrolled_class = db.relationship('Class')

    def to_dict(self):
        return {
            'fee_id': self.fee_id,
            'class_id': self.class_id,
            'class_name': self.enrolled_class.class_name if self.enrolled_class else None,
            'academic_year': self.academic_year,
            'total_amount': float(self.total_amount),
            'due_date': self.due_date.isoformat(),
        }

class FeePayment(db.Model):
    __tablename__ = 'fee_payments'

    payment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id', ondelete='CASCADE'), nullable=False)
    amount_paid = db.Column(db.Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    payment_mode = db.Column(db.String(50), default='Online/UPI', nullable=False)
    transaction_reference = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(
        db.Enum('completed', 'pending', 'failed', name='payment_status_enum'),
        default='completed',
        nullable=False
    )

    def to_dict(self):
        return {
            'payment_id': self.payment_id,
            'student_id': self.student_id,
            'amount_paid': float(self.amount_paid),
            'payment_date': self.payment_date.isoformat(),
            'payment_mode': self.payment_mode,
            'transaction_reference': self.transaction_reference,
            'status': self.status,
        }
