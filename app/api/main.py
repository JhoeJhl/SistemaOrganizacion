from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def landing():
    if current_user.is_authenticated:
        return redirect(url_for('main.inicio'))
    return render_template('main/landing.html')

@main_bp.route('/dashboard')
@login_required
def inicio():
    return render_template('main/index.html')
