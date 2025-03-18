from app import app, db
from models import User

def create_admin_user():
    with app.app_context():
        # Check if admin user already exists
        admin = User.query.filter_by(username='adm').first()
        
        if admin:
            print("Admin user 'adm' already exists.")
            return
        
        # Create new admin user
        admin_user = User(
            username='adm',
            password='adm',
            name='Administrator',
            role='admin',
            status='active'
        )
        
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user 'adm' created successfully, password: 'adm'")

if __name__ == '__main__':
    create_admin_user() 