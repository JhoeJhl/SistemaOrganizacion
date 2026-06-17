from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models.study import Subject, Task, StudySession, Schedule
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def landing():
    if current_user.is_authenticated:
        return redirect(url_for('main.inicio'))
    return render_template('main/landing.html')

@main_bp.route('/dashboard')
@login_required
def inicio():
    # Calcular estadísticas reales para el dashboard
    total_subjects = Subject.query.filter_by(user_id=current_user.id).count()
    total_tasks = Task.query.join(Subject).filter(Subject.user_id == current_user.id).count()
    pending_tasks = Task.query.join(Subject).filter(Subject.user_id == current_user.id, Task.status != 'completed').count()
    total_sessions = StudySession.query.filter_by(user_id=current_user.id).count()
    
    recent_tasks = Task.query.join(Subject).filter(Subject.user_id == current_user.id).order_by(Task.created_at.desc()).limit(5).all()
    
    # Próximas sesiones (del planificador)
    upcoming_sessions = Schedule.query.filter_by(user_id=current_user.id).limit(5).all()
    
    days_names = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

    return render_template('main/index.html', 
                           total_subjects=total_subjects,
                           total_tasks=total_tasks,
                           pending_tasks=pending_tasks,
                           total_sessions=total_sessions,
                           recent_tasks=recent_tasks,
                           upcoming_sessions=upcoming_sessions,
                           days_names=days_names,
                           now=datetime.utcnow())
