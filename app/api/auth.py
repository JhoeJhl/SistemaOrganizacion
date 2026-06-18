from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from app.extensions import db, bcrypt
from app.models.user import User, Role

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Si el usuario ya está logueado, lo mandamos al panel principal
    if current_user.is_authenticated:
        return redirect(url_for('main.inicio'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Bienvenido de nuevo!', 'success')
            return redirect(url_for('main.inicio'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return render_template('auth/login.html'), 401

    # Si es método GET, mostramos la plantilla HTML
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.inicio'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'error')
            return render_template('auth/register.html')

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('El nombre de usuario ya existe', 'error')
            return render_template('auth/register.html')

        # Get or create default 'Estudiante' role
        student_role = Role.query.filter_by(name='Estudiante').first()
        if not student_role:
            student_role = Role(name='Estudiante')
            db.session.add(student_role)
            db.session.commit()

        new_user = User(username=username, role=student_role)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()

        flash('Cuenta creada con éxito. Ya puedes iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.landing'))