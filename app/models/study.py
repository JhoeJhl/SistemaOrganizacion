from app.extensions import db
from datetime import datetime

class Subject(db.Model):
    __tablename__ = "subjects"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=True) # ej: Programación, Inglés, etc.
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    tasks = db.relationship('Task', backref='subject', lazy=True, cascade="all, delete-orphan")
    topics = db.relationship('Topic', backref='subject', lazy=True, cascade="all, delete-orphan")

class Topic(db.Model):
    __tablename__ = "topics"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_completed = db.Column(db.Boolean, default=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    priority = db.Column(db.String(20), default='media') # low, medium, high
    status = db.Column(db.String(20), default='pending') # pending, in_progress, completed
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Schedule(db.Model):
    __tablename__ = "schedules"
    id = db.Column(db.Integer, primary_key=True)
    day_of_week = db.Column(db.Integer, nullable=False) # 0=Monday, 6=Sunday
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    subject = db.relationship('Subject', backref=db.backref('schedules', lazy=True))
    user = db.relationship('User', backref=db.backref('schedules', lazy=True))

class Goal(db.Model):
    __tablename__ = "goals"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    target_date = db.Column(db.DateTime, nullable=True)
    progress = db.Column(db.Integer, default=0) # 0-100
    is_completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('goals', lazy=True))

class StudySession(db.Model):
    __tablename__ = "study_sessions"
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    duration = db.Column(db.Integer, nullable=True) # duration in minutes
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    subject = db.relationship('Subject', backref=db.backref('study_sessions', lazy=True))
    topic = db.relationship('Topic', backref=db.backref('study_sessions', lazy=True))
    user = db.relationship('User', backref=db.backref('study_sessions', lazy=True))

class Event(db.Model):
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=True)
    event_type = db.Column(db.String(50), nullable=False) # examen, entrega, practica, otro
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    subject = db.relationship('Subject', backref=db.backref('events', lazy=True))
    user = db.relationship('User', backref=db.backref('events', lazy=True))
