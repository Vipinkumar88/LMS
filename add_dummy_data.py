from app import app, db
from models import Membership, Book, BookTransaction
from datetime import datetime, timedelta
import random

# Create application context
with app.app_context():
    print("Adding dummy data to the database...")
    
    # Create dummy Memberships (at least 10)
    membership_types = ['6 months', '1 year', '2 years']
    membership_data = [
        {"membership_number": "M001", "name": "John Smith", "address": "123 Main St, Mumbai", "phone": "9876543210", "email": "john@example.com", "aadhar_card_number": "1234-5678-9012", "membership_type": "1 year"},
        {"membership_number": "M002", "name": "Priya Sharma", "address": "456 Park Ave, Delhi", "phone": "8765432109", "email": "priya@example.com", "aadhar_card_number": "2345-6789-0123", "membership_type": "6 months"},
        {"membership_number": "M003", "name": "Rahul Kumar", "address": "789 River Rd, Bangalore", "phone": "7654321098", "email": "rahul@example.com", "aadhar_card_number": "3456-7890-1234", "membership_type": "2 years"},
        {"membership_number": "M004", "name": "Amit Patel", "address": "234 Lake View, Ahmedabad", "phone": "6543210987", "email": "amit@example.com", "aadhar_card_number": "4567-8901-2345", "membership_type": "1 year"},
        {"membership_number": "M005", "name": "Sneha Gupta", "address": "567 Hill Rd, Pune", "phone": "5432109876", "email": "sneha@example.com", "aadhar_card_number": "5678-9012-3456", "membership_type": "6 months"},
        {"membership_number": "M006", "name": "Raj Malhotra", "address": "890 Ocean Blvd, Chennai", "phone": "4321098765", "email": "raj@example.com", "aadhar_card_number": "6789-0123-4567", "membership_type": "2 years"},
        {"membership_number": "M007", "name": "Ananya Singh", "address": "123 Valley St, Hyderabad", "phone": "3210987654", "email": "ananya@example.com", "aadhar_card_number": "7890-1234-5678", "membership_type": "1 year"},
        {"membership_number": "M008", "name": "Vikram Joshi", "address": "456 Mountain Ave, Kolkata", "phone": "2109876543", "email": "vikram@example.com", "aadhar_card_number": "8901-2345-6789", "membership_type": "6 months"},
        {"membership_number": "M009", "name": "Neha Khanna", "address": "789 Desert Rd, Jaipur", "phone": "1098765432", "email": "neha@example.com", "aadhar_card_number": "9012-3456-7890", "membership_type": "2 years"},
        {"membership_number": "M010", "name": "Ravi Verma", "address": "234 Forest Dr, Lucknow", "phone": "0987654321", "email": "ravi@example.com", "aadhar_card_number": "0123-4567-8901", "membership_type": "1 year"},
        {"membership_number": "M011", "name": "Meera Reddy", "address": "567 Garden Ln, Chandigarh", "phone": "9876543219", "email": "meera@example.com", "aadhar_card_number": "1234-5678-9013", "membership_type": "6 months"},
        {"membership_number": "M012", "name": "Karan Mehta", "address": "890 Sunset Blvd, Surat", "phone": "8765432198", "email": "karan@example.com", "aadhar_card_number": "2345-6789-0124", "membership_type": "2 years"},
    ]
    
    # First, commit memberships
    memberships = []
    for data in membership_data:
        if data["membership_type"] == "6 months":
            end_date = datetime.now() + timedelta(days=180)
        elif data["membership_type"] == "1 year":
            end_date = datetime.now() + timedelta(days=365)
        else:  # 2 years
            end_date = datetime.now() + timedelta(days=730)
        
        membership = Membership(
            membership_number=data["membership_number"],
            name=data["name"],
            address=data["address"],
            phone=data["phone"],
            email=data["email"],
            aadhar_card_number=data["aadhar_card_number"],
            membership_type=data["membership_type"],
            start_date=datetime.now(),
            end_date=end_date,
            status="active",
            pending_amount=0.0
        )
        db.session.add(membership)
    
    # Commit memberships first
    db.session.commit()
    print(f"Added {len(membership_data)} memberships successfully!")
    
    # Reload memberships for later use in transactions
    memberships = Membership.query.all()
    
    # Create dummy Books (at least 10)
    # First, science books
    science_books = [
        {"serial_number": "SC(B)000001", "type": "book", "title": "A Brief History of Time", "author": "Stephen Hawking", "publisher": "Bantam Books", "year": 1988, "cost": 450.00},
        {"serial_number": "SC(B)000002", "type": "book", "title": "Cosmos", "author": "Carl Sagan", "publisher": "Random House", "year": 1980, "cost": 380.00},
        {"serial_number": "SC(B)000003", "type": "book", "title": "The Selfish Gene", "author": "Richard Dawkins", "publisher": "Oxford University Press", "year": 1976, "cost": 420.00},
        {"serial_number": "SC(B)000004", "type": "book", "title": "Sapiens: A Brief History of Humankind", "author": "Yuval Noah Harari", "publisher": "Harper", "year": 2014, "cost": 550.00},
    ]
    
    # Economics books
    economics_books = [
        {"serial_number": "EC(B)000001", "type": "book", "title": "Freakonomics", "author": "Steven D. Levitt & Stephen J. Dubner", "publisher": "William Morrow", "year": 2005, "cost": 400.00},
        {"serial_number": "EC(B)000002", "type": "book", "title": "Capital in the Twenty-First Century", "author": "Thomas Piketty", "publisher": "Harvard University Press", "year": 2013, "cost": 600.00},
        {"serial_number": "EC(B)000003", "type": "book", "title": "The Wealth of Nations", "author": "Adam Smith", "publisher": "W. Strahan and T. Cadell", "year": 1776, "cost": 350.00},
    ]
    
    # Fiction books
    fiction_books = [
        {"serial_number": "FC(B)000001", "type": "book", "title": "To Kill a Mockingbird", "author": "Harper Lee", "publisher": "J.B. Lippincott & Co.", "year": 1960, "cost": 320.00},
        {"serial_number": "FC(B)000002", "type": "book", "title": "1984", "author": "George Orwell", "publisher": "Secker & Warburg", "year": 1949, "cost": 280.00},
        {"serial_number": "FC(B)000003", "type": "book", "title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "publisher": "Charles Scribner's Sons", "year": 1925, "cost": 300.00},
        {"serial_number": "FC(B)000004", "type": "book", "title": "Harry Potter and the Philosopher's Stone", "author": "J.K. Rowling", "publisher": "Bloomsbury", "year": 1997, "cost": 420.00},
    ]
    
    # Movies
    movies = [
        {"serial_number": "SC(M)000001", "type": "movie", "title": "Interstellar", "author": "Christopher Nolan", "publisher": "Paramount Pictures", "year": 2014, "cost": 250.00},
        {"serial_number": "SC(M)000002", "type": "movie", "title": "The Martian", "author": "Ridley Scott", "publisher": "20th Century Fox", "year": 2015, "cost": 280.00},
        {"serial_number": "FC(M)000001", "type": "movie", "title": "The Shawshank Redemption", "author": "Frank Darabont", "publisher": "Castle Rock Entertainment", "year": 1994, "cost": 200.00},
        {"serial_number": "FC(M)000002", "type": "movie", "title": "The Godfather", "author": "Francis Ford Coppola", "publisher": "Paramount Pictures", "year": 1972, "cost": 180.00},
        {"serial_number": "CH(M)000001", "type": "movie", "title": "Toy Story", "author": "John Lasseter", "publisher": "Pixar", "year": 1995, "cost": 220.00},
        {"serial_number": "CH(M)000002", "type": "movie", "title": "Finding Nemo", "author": "Andrew Stanton", "publisher": "Pixar", "year": 2003, "cost": 240.00},
    ]
    
    # Combine all books and movies
    all_books = science_books + economics_books + fiction_books + movies
    
    # Add books and commit
    for book_data in all_books:
        book = Book(
            serial_number=book_data["serial_number"],
            type=book_data["type"],
            title=book_data["title"],
            author=book_data["author"],
            publisher=book_data["publisher"],
            year=book_data["year"],
            status="available",
            cost=book_data["cost"],
            procurement_date=datetime.now() - timedelta(days=random.randint(30, 365))
        )
        db.session.add(book)
    
    # Commit books
    db.session.commit()
    print(f"Added {len(all_books)} books/movies successfully!")
    
    # Reload books for transactions
    books = Book.query.all()
    
    # Create some random book transactions (some books issued, some returned)
    # First, let's issue a few books
    issued_books = random.sample(books, 5)
    for book in issued_books:
        # Randomly select a membership
        membership = random.choice(memberships)
        
        # Calculate dates
        issue_date = datetime.now() - timedelta(days=random.randint(1, 10))
        expected_return_date = issue_date + timedelta(days=15)
        
        # Create transaction
        transaction = BookTransaction(
            book_id=book.id,
            membership_id=membership.id,
            issue_date=issue_date,
            return_date=expected_return_date,
            status="issued",
            remarks="Regular issue"
        )
        
        # Update book status
        book.status = "issued"
        
        db.session.add(transaction)
    
    # Commit issued books
    db.session.commit()
    print(f"Added 5 issued book transactions successfully!")
    
    # Now, let's create some returned book transactions
    available_books = Book.query.filter_by(status="available").all()
    returned_books = random.sample(available_books, min(3, len(available_books)))
    
    for book in returned_books:
        # Randomly select a membership
        membership = random.choice(memberships)
        
        # Calculate dates
        issue_date = datetime.now() - timedelta(days=random.randint(20, 30))
        expected_return_date = issue_date + timedelta(days=15)
        actual_return_date = expected_return_date - timedelta(days=random.randint(1, 5))  # Returned early
        
        # Create transaction
        transaction = BookTransaction(
            book_id=book.id,
            membership_id=membership.id,
            issue_date=issue_date,
            return_date=expected_return_date,
            actual_return_date=actual_return_date,
            status="returned",
            remarks="Returned early"
        )
        
        db.session.add(transaction)
    
    # Commit returned books
    db.session.commit()
    print(f"Added {len(returned_books)} returned book transactions successfully!")
    
    # Finally, let's create some overdue books with fines
    available_books = Book.query.filter_by(status="available").all()
    overdue_books = random.sample(available_books, min(2, len(available_books)))
    
    for book in overdue_books:
        # Randomly select a membership
        membership = random.choice(memberships)
        
        # Calculate dates
        issue_date = datetime.now() - timedelta(days=random.randint(20, 30))
        expected_return_date = issue_date + timedelta(days=15)
        actual_return_date = expected_return_date + timedelta(days=random.randint(5, 10))  # Returned late
        
        # Calculate fine (₹10 per day)
        days_late = (actual_return_date - expected_return_date).days
        fine_amount = days_late * 10.0
        
        # Create transaction
        transaction = BookTransaction(
            book_id=book.id,
            membership_id=membership.id,
            issue_date=issue_date,
            return_date=expected_return_date,
            actual_return_date=actual_return_date,
            fine_amount=fine_amount,
            fine_paid=random.choice([True, False]),
            status="returned",
            remarks="Returned late with fine"
        )
        
        db.session.add(transaction)
    
    # Commit overdue books
    db.session.commit()
    print(f"Added {len(overdue_books)} overdue book transactions with fines successfully!")
    
    print("Dummy data added successfully!")
    print(f"Added: {len(membership_data)} memberships, {len(all_books)} books/movies, and {5 + len(returned_books) + len(overdue_books)} transactions") 