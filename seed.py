from app import create_app
from app.extensions import db
from app.models.user import User, Role

app = create_app()

with app.app_context():
    # Create roles if they don't exist
    admin_role = Role.query.filter_by(name='Admin').first()
    if not admin_role:
        admin_role = Role(name='Admin')
        db.session.add(admin_role)
        db.session.commit()
        print("Role 'Admin' created.")
    else:
        print("Role 'Admin' already exists.")

    # Create a test user
    test_user = User.query.filter_by(username='admin').first()
    if not test_user:
        test_user = User(username='admin', role=admin_role)
        test_user.set_password('admin123')
        db.session.add(test_user)
        db.session.commit()
        print("User 'admin' created with password 'admin123'.")
    else:
        print("User 'admin' already exists.")
