from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.extensions import db
from app.models.study import Subject, Topic

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
        flash('El nombre de la materia es obligatorio', 'error')
        return redirect(url_for('study.list_subjects'))
    
    new_subject = Subject(name=name, description=description, category=category, user_id=current_user.id)
    db.session.add(new_subject)
    db.session.commit()
    
    flash('Materia creada con éxito', 'success')
    return redirect(url_for('study.list_subjects'))

@study_bp.route('/subjects/edit/<int:id>', methods=['POST'])
@login_required
def edit_subject(id):
    subject = Subject.query.get_or_404(id)
    if subject.user_id != current_user.id:
        flash('No tienes permiso para editar esta materia', 'error')
        return redirect(url_for('study.list_subjects'))
    
    subject.name = request.form.get('name')
    subject.description = request.form.get('description')
    subject.category = request.form.get('category')
    
    db.session.commit()
    flash('Materia actualizada con éxito', 'success')
    return redirect(url_for('study.list_subjects'))

@study_bp.route('/subjects/delete/<int:id>', methods=['POST'])
@login_required
def delete_subject(id):
    subject = Subject.query.get_or_404(id)
    if subject.user_id != current_user.id:
        flash('No tienes permiso para eliminar esta materia', 'error')
        return redirect(url_for('study.list_subjects'))
    
    db.session.delete(subject)
    db.session.commit()
    flash('Materia eliminada con éxito', 'success')
    return redirect(url_for('study.list_subjects'))

# --- Temas ---

@study_bp.route('/subjects/<int:subject_id>/topics')
@login_required
def list_topics(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    if subject.user_id != current_user.id:
        flash('No tienes permiso para ver esta materia', 'error')
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
    
    flash('Tema registrado con éxito', 'success')
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
        flash('No tienes permiso para eliminar este tema', 'error')
        return redirect(url_for('study.list_subjects'))
    
    db.session.delete(topic)
    db.session.commit()
    flash('Tema eliminado con éxito', 'success')
    return redirect(url_for('study.list_topics', subject_id=subject_id))
