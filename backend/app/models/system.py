from datetime import datetime
from backend.extensions import db

class AuditLog(db.Model):
    __tablename__ = 'audit_log'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True)
    role = db.Column(db.String(20), nullable=True)
    action = db.Column(db.String(100), nullable=False)  # 'LOGIN_SUCCESS', 'MARKS_UPDATE', 'DATA_EXPORT'
    target_type = db.Column(db.String(50), nullable=True)  # 'Student', 'Class', 'Report'
    target_id = db.Column(db.Integer, nullable=True)
    ip = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'role': self.role,
            'action': self.action,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'ip': self.ip,
            'created_at': self.created_at.isoformat(),
        }

class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True)
    recipient_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id', ondelete='SET NULL'), nullable=True)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    channel = db.Column(
        db.Enum('in_app', 'email', 'sms', name='notif_channel_enum'),
        default='in_app',
        nullable=False
    )
    status = db.Column(
        db.Enum('pending', 'sent', 'read', name='notif_status_enum'),
        default='sent',
        nullable=False
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    read_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    sender = db.relationship('User', foreign_keys=[sender_id])
    recipient = db.relationship('User', foreign_keys=[recipient_user_id])
    student = db.relationship('Student', foreign_keys=[student_id])

    def to_dict(self):
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'sender_name': self.sender.username if self.sender else 'System',
            'recipient_user_id': self.recipient_user_id,
            'student_id': self.student_id,
            'student_name': self.student.name if self.student else None,
            'title': self.title,
            'message': self.message,
            'channel': self.channel,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'read_at': self.read_at.isoformat() if self.read_at else None,
        }

class Alert(db.Model):
    __tablename__ = 'alerts'

    alert_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id', ondelete='CASCADE'), nullable=False)
    risk_level = db.Column(
        db.Enum('medium', 'high', name='alert_risk_enum'),
        nullable=False
    )
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(
        db.Enum('open', 'contacted', 'resolved', name='alert_status_enum'),
        default='open',
        nullable=False
    )
    email_sent = db.Column(db.Boolean, default=False, nullable=False)
    sms_sent = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    resolved_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'alert_id': self.alert_id,
            'student_id': self.student_id,
            'student_name': self.student.name if self.student else None,
            'usn': self.student.usn if self.student else None,
            'risk_level': self.risk_level,
            'reason': self.reason,
            'status': self.status,
            'email_sent': self.email_sent,
            'sms_sent': self.sms_sent,
            'created_at': self.created_at.isoformat(),
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
        }

class Remark(db.Model):
    __tablename__ = 'remarks'

    remark_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id', ondelete='CASCADE'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.teacher_id', ondelete='CASCADE'), nullable=False)
    remark_text = db.Column(db.Text, nullable=False)
    action_taken = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'remark_id': self.remark_id,
            'student_id': self.student_id,
            'teacher_id': self.teacher_id,
            'teacher_name': self.author_teacher.name if self.author_teacher else None,
            'remark_text': self.remark_text,
            'action_taken': self.action_taken,
            'created_at': self.created_at.isoformat(),
        }

class ModelRun(db.Model):
    __tablename__ = 'model_runs'

    run_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    model_name = db.Column(db.String(100), nullable=False)
    model_version = db.Column(db.String(20), nullable=False, index=True)
    algorithm = db.Column(db.String(100), nullable=False)
    accuracy = db.Column(db.Numeric(5, 4), nullable=False)
    precision_macro = db.Column(db.Numeric(5, 4), nullable=False)
    recall_macro = db.Column(db.Numeric(5, 4), nullable=False)
    f1_macro = db.Column(db.Numeric(5, 4), nullable=False)
    roc_auc = db.Column(db.Numeric(5, 4), nullable=False)
    regressor_r2 = db.Column(db.Numeric(5, 4), nullable=False)
    trained_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    metrics_json = db.Column(db.JSON, nullable=True)

class Prediction(db.Model):
    __tablename__ = 'predictions'

    prediction_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id', ondelete='CASCADE'), nullable=False)
    model_run_id = db.Column(db.Integer, db.ForeignKey('model_runs.run_id', ondelete='RESTRICT'), nullable=False)
    predicted_outcome = db.Column(
        db.Enum('Pass', 'Fail', 'Dropout', 'Graduate', name='predicted_outcome_enum'),
        nullable=False
    )
    risk_score = db.Column(db.Numeric(5, 4), nullable=False)
    risk_level = db.Column(
        db.Enum('low', 'medium', 'high', name='pred_risk_level_enum'),
        nullable=False,
        index=True
    )
    predicted_sgpa = db.Column(db.Numeric(4, 2), nullable=True)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    explanations = db.relationship('Explanation', backref='prediction', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'prediction_id': self.prediction_id,
            'student_id': self.student_id,
            'predicted_outcome': self.predicted_outcome,
            'risk_score': float(self.risk_score),
            'risk_level': self.risk_level,
            'predicted_sgpa': float(self.predicted_sgpa) if self.predicted_sgpa else None,
            'generated_at': self.generated_at.isoformat(),
            'explanations': [e.to_dict() for e in self.explanations],
        }

class Explanation(db.Model):
    __tablename__ = 'explanations'

    explanation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    prediction_id = db.Column(db.Integer, db.ForeignKey('predictions.prediction_id', ondelete='CASCADE'), nullable=False)
    feature_name = db.Column(db.String(100), nullable=False)
    feature_value = db.Column(db.String(50), nullable=False)
    shap_value = db.Column(db.Numeric(6, 4), nullable=False)
    rank_order = db.Column(db.Integer, default=1, nullable=False)

    def to_dict(self):
        return {
            'explanation_id': self.explanation_id,
            'feature': self.feature_name,
            'displayValue': self.feature_value,
            'shap': float(self.shap_value),
            'rank_order': self.rank_order,
        }
