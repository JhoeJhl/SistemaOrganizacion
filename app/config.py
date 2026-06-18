import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'mi-clave-super-secreta')
    
    # Render PostgreSQL DATABASE_URL compatibility fix
    db_url = os.environ.get('DATABASE_URL', 'sqlite:///database.db')
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
        
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    