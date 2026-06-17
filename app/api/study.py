from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.study import Subject, Topic, Task, Schedule, Goal, StudySession, Event
from datetime import datetime, time, timedelta
from sqlalchemy import func

study_bp = Blueprint('study', __name__)

# --- Materias ---
@study_bp.route('/subjects')
@login_required
def list_subjects():
    subjects = Subject.query.filter_by(user_id=current_user.id).all()
    return render_template('study/subjects.html', subjects=subjects)

@study_bp.route('/subjects/create', methods=['POST'])
@login_required
def create_subject():
    name = request.form.get('name')
    description = request.form.get('description')
    category = request.form.get('category')
    if not name:
        flash('El nombre es obligatorio', 'error')
        return redirect(url_for('study.list_subjects'))
    new_subj = Subject(name=name, description=description, category=category, user_id=current_user.id)
    db.session.add(new_subj)
    db.session.commit()
    flash('Materia creada', 'success')
    return redirect(url_for('study.list_subjects'))

@study_bp.route('/subjects/edit/<int:id>', methods=['POST'])
@login_required
def edit_subject(id):
    subject = Subject.query.get_or_404(id)
    if subject.user_id != current_user.id:
        flash('No autorizado', 'error')
        return redirect(url_for('study.list_subjects'))
    subject.name = request.form.get('name')
    subject.description = request.form.get('description')
    subject.category = request.form.get('category')
    db.session.commit()
    flash('Materia actualizada', 'success')
    return redirect(url_for('study.list_subjects'))

@study_bp.route('/subjects/delete/<int:id>', methods=['POST'])
@login_required
def delete_subject(id):
    subject = Subject.query.get_or_404(id)
    if subject.user_id != current_user.id:
        flash('No autorizado', 'error')
        return redirect(url_for('study.list_subjects'))
    db.session.delete(subject)
    db.session.commit()
    flash('Materia eliminada', 'success')
    return redirect(url_for('study.list_subjects'))

# --- Temas ---
@study_bp.route('/subjects/<int:subject_id>/topics')
@login_required
def list_topics(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    if subject.user_id != current_user.id:
        flash('No autorizado', 'error')
        return redirect(url_for('study.list_subjects'))
    topics = Topic.query.filter_by(subject_id=subject_id).all()
    return render_template('study/topics.html', subject=subject, topics=topics)

@study_bp.route('/topics/create', methods=['POST'])
@login_required
def create_topic():
    title = request.form.get('title')
    description = request.form.get('description')
    subject_id = request.form.get('subject_id')
    subject = Subject.query.get_or_404(subject_id)
    if subject.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    new_topic = Topic(title=title, description=description, subject_id=subject_id)
    db.session.add(new_topic)
    db.session.commit()
    flash('Tema registrado', 'success')
    return redirect(url_for('study.list_topics', subject_id=subject_id))

@study_bp.route('/topics/toggle/<int:id>', methods=['POST'])
@login_required
def toggle_topic(id):
    topic = Topic.query.get_or_404(id)
    if topic.subject.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    topic.is_completed = not topic.is_completed
    db.session.commit()
    return jsonify({'success': True, 'is_completed': topic.is_completed})

@study_bp.route('/topics/delete/<int:id>', methods=['POST'])
@login_required
def delete_topic(id):
    topic = Topic.query.get_or_404(id)
    subject_id = topic.subject_id
    if topic.subject.user_id != current_user.id:
        flash('No autorizado', 'error')
        return redirect(url_for('study.list_subjects'))
    db.session.delete(topic)
    db.session.commit()
    flash('Tema eliminado', 'success')
    return redirect(url_for('study.list_topics', subject_id=subject_id))

# --- Tareas ---
@study_bp.route('/tasks')
@login_required
def list_tasks():
    subjects = Subject.query.filter_by(user_id=current_user.id).all()
    status_filter = request.args.get('status')
    priority_filter = request.args.get('priority')
    query = Task.query.join(Subject).filter(Subject.user_id == current_user.id)
    if status_filter: query = query.filter(Task.status == status_filter)
    if priority_filter: query = query.filter(Task.priority == priority_filter)
    tasks = query.order_by(Task.due_date.asc()).all()
    return render_template('study/tasks.html', tasks=tasks, subjects=subjects, now=datetime.utcnow())

@study_bp.route('/tasks/create', methods=['POST'])
@login_required
def create_task():
    title = request.form.get('title')
    description = request.form.get('description')
    due_date_str = request.form.get('due_date')
    priority = request.form.get('priority', 'media')
    subject_id = request.form.get('subject_id')
    due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M') if due_date_str else None
    new_task = Task(title=title, description=description, due_date=due_date, priority=priority, subject_id=subject_id)
    db.session.add(new_task)
    db.session.commit()
    flash('Tarea creada', 'success')
    return redirect(url_for('study.list_tasks'))

@study_bp.route('/tasks/update_status/<int:id>', methods=['POST'])
@login_required
def update_task_status(id):
    task = Task.query.get_or_404(id)
    if task.subject.user_id != current_user.id: return jsonify({'error': 'Unauthorized'}), 403
    task.status = request.json.get('status')
    db.session.commit()
    return jsonify({'success': True})

@study_bp.route('/tasks/delete/<int:id>', methods=['POST'])
@login_required
def delete_task(id):
    task = Task.query.get_or_404(id)
    if task.subject.user_id != current_user.id:
        flash('No autorizado', 'error')
        return redirect(url_for('study.list_tasks'))
    db.session.delete(task)
    db.session.commit()
    flash('Tarea eliminada', 'success')
    return redirect(url_for('study.list_tasks'))

# --- Planificador ---
@study_bp.route('/planner')
@login_required
def planner():
    subjects = Subject.query.filter_by(user_id=current_user.id).all()
    schedules = Schedule.query.filter_by(user_id=current_user.id).all()
    agenda = {i: [] for i in range(7)}
    for s in schedules: agenda[s.day_of_week].append(s)
    for day in agenda: agenda[day].sort(key=lambda x: x.start_time)
    days_names = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    return render_template('study/planner.html', agenda=agenda, subjects=subjects, days_names=days_names)

@study_bp.route('/planner/add', methods=['POST'])
@login_required
def add_schedule():
    day = int(request.form.get('day_of_week'))
    start_str = request.form.get('start_time')
    end_str = request.form.get('end_time')
    subject_id = request.form.get('subject_id')
    start_time = datetime.strptime(start_str, '%H:%M').time()
    end_time = datetime.strptime(end_str, '%H:%M').time()
    new_sch = Schedule(day_of_week=day, start_time=start_time, end_time=end_time, subject_id=subject_id, user_id=current_user.id)
    db.session.add(new_sch)
    db.session.commit()
    flash('Sesión programada', 'success')
    return redirect(url_for('study.planner'))

@study_bp.route('/planner/delete/<int:id>', methods=['POST'])
@login_required
def delete_schedule(id):
    sch = Schedule.query.get_or_404(id)
    if sch.user_id != current_user.id: return jsonify({'error': 'Unauthorized'}), 403
    db.session.delete(sch)
    db.session.commit()
    flash('Sesión eliminada', 'success')
    return redirect(url_for('study.planner'))

# --- Metas ---
@study_bp.route('/goals')
@login_required
def list_goals():
    goals = Goal.query.filter_by(user_id=current_user.id).order_by(Goal.target_date.asc()).all()
    return render_template('study/goals.html', goals=goals)

@study_bp.route('/goals/create', methods=['POST'])
@login_required
def create_goal():
    title = request.form.get('title')
    description = request.form.get('description')
    date_str = request.form.get('target_date')
    date = datetime.strptime(date_str, '%Y-%m-%d') if date_str else None
    new_goal = Goal(title=title, description=description, target_date=date, user_id=current_user.id)
    db.session.add(new_goal)
    db.session.commit()
    flash('Meta establecida', 'success')
    return redirect(url_for('study.list_goals'))

@study_bp.route('/goals/update_progress/<int:id>', methods=['POST'])
@login_required
def update_goal_progress(id):
    goal = Goal.query.get_or_404(id)
    if goal.user_id != current_user.id: return jsonify({'error': 'Unauthorized'}), 403
    progress = int(request.json.get('progress', 0))
    goal.progress = progress
    goal.is_completed = (progress == 100)
    db.session.commit()
    return jsonify({'success': True})

@study_bp.route('/goals/delete/<int:id>', methods=['POST'])
@login_required
def delete_goal(id):
    goal = Goal.query.get_or_404(id)
    if goal.user_id != current_user.id: flash('No autorizado', 'error'); return redirect(url_for('study.list_goals'))
    db.session.delete(goal)
    db.session.commit()
    flash('Meta eliminada', 'success')
    return redirect(url_for('study.list_goals'))

# --- Sesiones ---
@study_bp.route('/sessions')
@login_required
def list_sessions():
    sessions = StudySession.query.filter_by(user_id=current_user.id).order_by(StudySession.start_time.desc()).all()
    subjects = Subject.query.filter_by(user_id=current_user.id).all()
    return render_template('study/sessions.html', sessions=sessions, subjects=subjects)

@study_bp.route('/sessions/start', methods=['POST'])
@login_required
def start_session():
    sid = request.form.get('subject_id')
    tid = request.form.get('topic_id')
    if StudySession.query.filter_by(user_id=current_user.id, end_time=None).first():
        flash('Sesión activa existente', 'error'); return redirect(url_for('study.list_sessions'))
    new_sess = StudySession(subject_id=sid, topic_id=tid if tid else None, user_id=current_user.id, start_time=datetime.utcnow())
    db.session.add(new_sess)
    db.session.commit()
    flash('Estudio iniciado', 'success')
    return redirect(url_for('study.list_sessions'))

@study_bp.route('/sessions/stop/<int:id>', methods=['POST'])
@login_required
def stop_session(id):
    sess = StudySession.query.get_or_404(id)
    if sess.user_id != current_user.id: return jsonify({'error': 'Unauthorized'}), 403
    sess.end_time = datetime.utcnow()
    diff = sess.end_time - sess.start_time
    sess.duration = int(diff.total_seconds() / 60)
    db.session.commit()
    flash('Sesión finalizada', 'success')
    return redirect(url_for('study.list_sessions'))

@study_bp.route('/sessions/delete/<int:id>', methods=['POST'])
@login_required
def delete_session(id):
    sess = StudySession.query.get_or_404(id)
    if sess.user_id != current_user.id: return jsonify({'error': 'Unauthorized'}), 403
    db.session.delete(sess)
    db.session.commit()
    flash('Sesión eliminada', 'success')
    return redirect(url_for('study.list_sessions'))

# --- Calendario ---
@study_bp.route('/calendar')
@login_required
def view_calendar():
    subjects = Subject.query.filter_by(user_id=current_user.id).all()
    return render_template('study/calendar.html', subjects=subjects)

@study_bp.route('/api/events')
@login_required
def get_events():
    events = Event.query.filter_by(user_id=current_user.id).all()
    tasks = Task.query.join(Subject).filter(Subject.user_id == current_user.id).all()
    event_list = []
    for e in events:
        event_list.append({
            'title': f"[{e.event_type.upper()}] {e.title}",
            'start': e.start_date.isoformat(),
            'end': e.end_date.isoformat() if e.end_date else None,
            'color': '#6366f1' if e.event_type == 'examen' else '#14b8a6'
        })
    for t in tasks:
        if t.due_date:
            event_list.append({
                'title': f"📋 {t.title}",
                'start': t.due_date.isoformat(),
                'color': '#f59e0b' if t.status != 'completed' else '#10b981'
            })
    return jsonify(event_list)

@study_bp.route('/events/create', methods=['POST'])
@login_required
def create_event():
    title = request.form.get('title')
    etype = request.form.get('event_type')
    start = datetime.strptime(request.form.get('start_date'), '%Y-%m-%dT%H:%M')
    new_event = Event(title=title, event_type=etype, start_date=start, user_id=current_user.id, subject_id=request.form.get('subject_id') or None)
    db.session.add(new_event)
    db.session.commit()
    flash('Evento de calendario creado', 'success')
    return redirect(url_for('study.view_calendar'))

# --- Analíticas ---
@study_bp.route('/analytics')
@login_required
def view_analytics():
    total_min = db.session.query(func.sum(StudySession.duration)).filter(StudySession.user_id == current_user.id).scalar() or 0
    total_hours = round(total_min / 60, 1)
    completed_topics = Topic.query.join(Subject).filter(Subject.user_id == current_user.id, Topic.is_completed == True).count()
    total_topics = Topic.query.join(Subject).filter(Subject.user_id == current_user.id).count()
    progress_percent = round((completed_topics / total_topics * 100), 1) if total_topics > 0 else 0
    
    sessions_by_subject = db.session.query(Subject.name, func.sum(StudySession.duration))\
        .join(StudySession).filter(StudySession.user_id == current_user.id)\
        .group_by(Subject.name).all()
    
    chart_labels = [s[0] for s in sessions_by_subject]
    chart_data = [round(s[1]/60, 1) for s in sessions_by_subject]

    weekly_hours = [0] * 7
    today = datetime.utcnow().date()
    start_of_week = today - timedelta(days=today.weekday())
    for i in range(7):
        day = start_of_week + timedelta(days=i)
        day_min = db.session.query(func.sum(StudySession.duration)).filter(StudySession.user_id == current_user.id, func.date(StudySession.start_time) == day).scalar() or 0
        weekly_hours[i] = round(day_min / 60, 1)

    # Cálculo de racha de estudio (días consecutivos)
    study_streak = 0
    curr_date = today
    while True:
        has_session = StudySession.query.filter(
            StudySession.user_id == current_user.id,
            func.date(StudySession.start_time) == curr_date
        ).first()
        if has_session:
            study_streak += 1
            curr_date -= timedelta(days=1)
        else:
            break

    return render_template('study/analytics.html', 
                           total_hours=total_hours, 
                           completed_topics=completed_topics, 
                           total_topics=total_topics, 
                           progress_percent=progress_percent, 
                           chart_labels=chart_labels, 
                           chart_data=chart_data, 
                           weekly_hours=weekly_hours, 
                           study_streak=study_streak)

@study_bp.route('/api/topics/<int:subject_id>')
@login_required
def get_topics(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    if subject.user_id != current_user.id: return jsonify([]), 403
    return jsonify([{'id': t.id, 'title': t.title} for t in subject.topics])
