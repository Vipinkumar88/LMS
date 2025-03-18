from app import app, db
from models import User

def create_normal_user():
    with app.app_context():
        # Check if user already exists
        user = User.query.filter_by(username='user').first()
        
        if user:
            print("Normal user 'user' already exists.")
            return
        
        # Create new user
        normal_user = User(
            username='user',
            password='user',
            name='Normal User',
            role='user',
            status='active'
        )
        
        db.session.add(normal_user)
        db.session.commit()
        print("Normal user 'user' created successfully, password: 'user'")

if __name__ == '__main__':
    create_normal_user() 