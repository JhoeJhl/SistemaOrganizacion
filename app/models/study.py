from app.extensions import db
from datetime import datetime

class Subject(db.Model):
    __tablename__ = "subjects"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    tasks = db.relationship('Task', backref='subject', lazy=True, cascade="all, delete-orphan")

    user = db.relationship('User', backref=db.backref('subjects', lazy=True))

class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='pending') # pending, in_progress, completed
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
