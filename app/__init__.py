from flask import Flask, request
from app.extensions import db, bcrypt, migrate, login_manager
from app.models.user import User
from app.config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicialización de extensiones
    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'error'

    # Configuración de Flask-Login para cargar al usuario en memoria
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # 1. Importación del blueprint (Para cada módulo)
    from app.api.auth import auth_bp
    from app.api.main import main_bp
    from app.api.study import study_bp

    # 2. Registrar el blueprint (Para cada módulo)
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(main_bp, url_prefix='/')
    app.register_blueprint(study_bp, url_prefix='/study')

    @app.context_processor
    def inject_base():
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return {'base_template': 'spa_base.html'}
        return {'base_template': 'base.html'}

    return app
