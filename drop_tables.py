from app import app, db
from models import User
import os

# Create application context
with app.app_context():
    # Drop all tables
    db.drop_all()
    print("All tables dropped")
    
    # Create all tables
    db.create_all()
    print("All tables recreated")
    
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
    
    # Create adm user
    adm = User(
        username='adm',
        password='adm',
        name='Administrator',
        role='admin',
        status='active'
    )
    db.session.add(adm)
    
    db.session.commit()
    print('Default users created successfully') 