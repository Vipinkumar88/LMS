from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin' or 'user'
    status = db.Column(db.String(20), nullable=False, default='active')  # 'active' or 'inactive'
    
class Membership(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    membership_number = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    aadhar_card_number = db.Column(db.String(20), nullable=True)
    membership_type = db.Column(db.String(20), nullable=False)  # '6 months', '1 year', '2 years'
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    end_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='active')  # 'active', 'expired', 'cancelled'
    pending_amount = db.Column(db.Float, default=0.0)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    serial_number = db.Column(db.String(50), unique=True, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'book' or 'movie'
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    publisher = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='available')  # 'available', 'issued'
    cost = db.Column(db.Float, nullable=True)
    procurement_date = db.Column(db.DateTime, nullable=True)

class BookTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    membership_id = db.Column(db.Integer, db.ForeignKey('membership.id'), nullable=False)
    issue_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    return_date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now() + timedelta(days=15))
    actual_return_date = db.Column(db.DateTime)
    remarks = db.Column(db.String(200))
    fine_amount = db.Column(db.Float, default=0.0)
    fine_paid = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), nullable=False, default='issued')  # 'issued', 'returned', 'cancelled'
    
    book = db.relationship('Book', backref='transactions')
    membership = db.relationship('Membership', backref='transactions') 