from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class Parent(db.Model):
    __tablename__ = 'parents'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)  # For future auth
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    children = db.relationship('Child', backref='parent', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'children': [child.to_dict() for child in self.children]
        }

class Child(db.Model):
    __tablename__ = 'children'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    avatar = db.Column(db.String(36), nullable=True)  # Avatar ID
    parent_id = db.Column(db.String(36), db.ForeignKey('parents.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    brushing_records = db.relationship('BrushingRecord', backref='child', lazy=True, cascade='all, delete-orphan')
    reminder_settings = db.relationship('ReminderSetting', backref='child', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'avatar': self.avatar,
            'parentId': self.parent_id,
            'createdAt': self.created_at.isoformat()
        }

class BrushingRecord(db.Model):
    __tablename__ = 'brushing_records'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    child_id = db.Column(db.String(36), db.ForeignKey('children.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Enum('morning', 'evening', name='brushing_time'), nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # seconds
    completed = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Composite unique constraint to prevent duplicate records
    __table_args__ = (db.UniqueConstraint('child_id', 'date', 'time', name='unique_brushing_session'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'childId': self.child_id,
            'date': self.date.isoformat(),
            'time': self.time,
            'duration': self.duration,
            'completed': self.completed,
            'timestamp': self.timestamp.isoformat()
        }

class ReminderSetting(db.Model):
    __tablename__ = 'reminder_settings'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    child_id = db.Column(db.String(36), db.ForeignKey('children.id'), nullable=False)
    morning_time = db.Column(db.String(5), nullable=False, default='08:00')  # HH:MM format
    evening_time = db.Column(db.String(5), nullable=False, default='20:00')  # HH:MM format
    enabled = db.Column(db.Boolean, default=True)
    sound_enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'childId': self.child_id,
            'morningTime': self.morning_time,
            'eveningTime': self.evening_time,
            'enabled': self.enabled,
            'soundEnabled': self.sound_enabled,
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat()
        }

class Avatar(db.Model):
    __tablename__ = 'avatars'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.Text, nullable=False)  # Can be emoji or URL
    description = db.Column(db.Text, nullable=True)
    required_months = db.Column(db.Integer, nullable=False, default=1)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(100), default='admin')  # Who created this avatar
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'imageUrl': self.image_url,
            'description': self.description,
            'requiredMonths': self.required_months,
            'isActive': self.is_active,
            'createdAt': self.created_at.isoformat(),
            'createdBy': self.created_by
        }

class AppUsage(db.Model):
    __tablename__ = 'app_usage'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    child_id = db.Column(db.String(36), db.ForeignKey('children.id'), nullable=False)
    session_start = db.Column(db.DateTime, default=datetime.utcnow)
    session_end = db.Column(db.DateTime, nullable=True)
    duration_minutes = db.Column(db.Integer, nullable=True)
    actions_performed = db.Column(db.JSON, nullable=True)  # Store user actions as JSON
    device_info = db.Column(db.JSON, nullable=True)  # Store device/browser info
    
    def to_dict(self):
        return {
            'id': self.id,
            'childId': self.child_id,
            'sessionStart': self.session_start.isoformat(),
            'sessionEnd': self.session_end.isoformat() if self.session_end else None,
            'durationMinutes': self.duration_minutes,
            'actionsPerformed': self.actions_performed,
            'deviceInfo': self.device_info
        }