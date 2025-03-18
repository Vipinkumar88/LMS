import os
from app import app, db
from models import User

# Create a context
with app.app_context():
    # Remove the database file if it exists
    if os.path.exists('instance/library.db'):
        os.remove('instance/library.db')
        print("Database file deleted")
    
    # Create all tables
    db.create_all()
    print("Database tables created")
    
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