from datetime import datetime, timedelta
from backend.extensions import db, bcrypt

class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(60), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(
        db.Enum('student', 'parent', 'teacher', 'admin', 'principal', 'hod', name='user_role_enum'),
        nullable=False,
        index=True
    )
    active = db.Column(db.Boolean, default=True, nullable=False)
    must_change_password = db.Column(db.Boolean, default=False, nullable=False)
    failed_attempts = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime, nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    student_profile = db.relationship('Student', backref='user_account', uselist=False, cascade='all, delete-orphan')
    parent_profile = db.relationship('Parent', backref='user_account', uselist=False, cascade='all, delete-orphan')
    teacher_profile = db.relationship('Teacher', backref='user_account', uselist=False, cascade='all, delete-orphan')
    refresh_tokens = db.relationship('RefreshToken', backref='user', cascade='all, delete-orphan')
    password_resets = db.relationship('PasswordReset', backref='user', cascade='all, delete-orphan')
    audit_logs = db.relationship('AuditLog', backref='actor_user')

    def set_password(self, password: str):
        """Hash and set user password using bcrypt"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password: str) -> bool:
        """Verify plain password against hashed password"""
        return bcrypt.check_password_hash(self.password_hash, password)

    def is_locked(self) -> bool:
        """Check if account is temporarily locked due to failed attempts"""
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False

    def record_failed_login(self, max_attempts=5, lockout_minutes=15):
        """Increment failed attempts and lock account if threshold reached"""
        self.failed_attempts += 1
        if self.failed_attempts >= max_attempts:
            self.locked_until = datetime.utcnow() + timedelta(minutes=lockout_minutes)

    def reset_failed_attempts(self):
        """Reset failed login counter upon successful authentication"""
        self.failed_attempts = 0
        self.locked_until = None
        self.last_login = datetime.utcnow()

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'active': self.active,
            'must_change_password': self.must_change_password,
            'is_locked': self.is_locked(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

class PasswordReset(db.Model):
    __tablename__ = 'password_resets'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    token_hash = db.Column(db.String(255), nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def is_valid(self) -> bool:
        return not self.used and self.expires_at > datetime.utcnow()

class RefreshToken(db.Model):
    __tablename__ = 'refresh_tokens'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    token_hash = db.Column(db.String(255), nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    revoked = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def is_valid(self) -> bool:
        return not self.revoked and self.expires_at > datetime.utcnow()
