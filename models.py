from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Parent(db.Model):
    __tablename__ = 'parents'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # İlişki: Bir ebeveynin birden fazla çocuğu olabilir
    children = db.relationship('Child', backref='parent', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'children_count': len(self.children)
        }

class Child(db.Model):
    __tablename__ = 'children'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('parents.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # İlişki: Bir çocuğun birden fazla fırçalama kaydı olabilir
    brushing_records = db.relationship('BrushingRecord', backref='child', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'parent_id': self.parent_id,
            'created_at': self.created_at.isoformat(),
            'total_brushings': len(self.brushing_records)
        }

class BrushingRecord(db.Model):
    __tablename__ = 'brushing_records'
    
    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.Integer, db.ForeignKey('children.id'), nullable=False)
    brushed_at = db.Column(db.DateTime, default=datetime.utcnow)
    duration = db.Column(db.Integer, default=120)  # Saniye cinsinden (varsayılan 2 dakika)
    quality_score = db.Column(db.Integer, default=5)  # 1-10 arası kalite puanı
    notes = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'child_id': self.child_id,
            'brushed_at': self.brushed_at.isoformat(),
            'duration': self.duration,
            'quality_score': self.quality_score,
            'notes': self.notes
        }

class Reward(db.Model):
    __tablename__ = 'rewards'
    
    id = db.Column(db.Integer, primary_key=True)
    child_id = db.Column(db.Integer, db.ForeignKey('children.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    points_required = db.Column(db.Integer, default=10)
    is_earned = db.Column(db.Boolean, default=False)
    earned_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # İlişki
    child = db.relationship('Child', backref='rewards')
    
    def to_dict(self):
        return {
            'id': self.id,
            'child_id': self.child_id,
            'title': self.title,
            'description': self.description,
            'points_required': self.points_required,
            'is_earned': self.is_earned,
            'earned_at': self.earned_at.isoformat() if self.earned_at else None,
            'created_at': self.created_at.isoformat()
        }
