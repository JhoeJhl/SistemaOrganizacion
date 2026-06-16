from app.extensions import db
from app.extensions import bcrypt
from flask_login import UserMixin

class Role(db.Model):
    __tablename__="roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable = False)
    users = db.relationship('User', backref = 'role', lazy = True)

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable = False)
    password = db.Column(db.String(255), nullable = False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable = False)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
    