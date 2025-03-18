from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db, Book, Membership
import sqlite3

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

def add_new_columns():
    """Add new columns to the Book and Membership models."""
    with app.app_context():
        conn = sqlite3.connect('library.db')
        cursor = conn.cursor()
        
        # First, handle Book model updates
        cursor.execute("PRAGMA table_info(book)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        # Add cost column if it doesn't exist
        if 'cost' not in column_names:
            print("Adding 'cost' column to book table...")
            cursor.execute("ALTER TABLE book ADD COLUMN cost FLOAT")
        else:
            print("'cost' column already exists in book table.")
        
        # Add procurement_date column if it doesn't exist
        if 'procurement_date' not in column_names:
            print("Adding 'procurement_date' column to book table...")
            cursor.execute("ALTER TABLE book ADD COLUMN procurement_date TIMESTAMP")
        else:
            print("'procurement_date' column already exists in book table.")
        
        # Now, handle Membership model updates
        cursor.execute("PRAGMA table_info(membership)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        # Add aadhar_card_number column if it doesn't exist
        if 'aadhar_card_number' not in column_names:
            print("Adding 'aadhar_card_number' column to membership table...")
            cursor.execute("ALTER TABLE membership ADD COLUMN aadhar_card_number TEXT")
        else:
            print("'aadhar_card_number' column already exists in membership table.")
        
        # Add pending_amount column if it doesn't exist
        if 'pending_amount' not in column_names:
            print("Adding 'pending_amount' column to membership table...")
            cursor.execute("ALTER TABLE membership ADD COLUMN pending_amount FLOAT DEFAULT 0.0")
        else:
            print("'pending_amount' column already exists in membership table.")
        
        conn.commit()
        conn.close()
        print("Migration completed successfully!")

if __name__ == '__main__':
    add_new_columns() 