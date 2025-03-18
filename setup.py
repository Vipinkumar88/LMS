from app import app, db
from models import User
from datetime import datetime

# Create a context
with app.app_context():
    # Create all tables
    db.create_all()
    
    # Check if admin user already exists
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        # Create admin user
        admin = User(
            username='admin',
            password='admin123',
            name='Admin User',
            role='admin',
            status='active'
        )
        db.session.add(admin)
        
        # Create regular user
        user = User(
            username='user',
            password='user123',
            name='Regular User',
            role='user',
            status='active'
        )
        db.session.add(user)
        
        db.session.commit()
        print('Default users created successfully')
    else:
        print('Default users already exist') 