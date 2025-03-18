from app import app, db
from models import Membership, Book, BookTransaction
from datetime import datetime, timedelta
import random

# Create application context
with app.app_context():
    print("Adding additional fine-related data to the database...")
    
    # Get all memberships and available books
    memberships = Membership.query.all()
    available_books = Book.query.filter_by(status="available").all()
    
    if not available_books:
        print("No available books found! Please run add_dummy_data.py first.")
        exit(1)
    
    if not memberships:
        print("No memberships found! Please run add_dummy_data.py first.")
        exit(1)
    
    # 1. Create more overdue returned books with higher fine amounts
    # Take some available books and create transactions with high fines
    high_fine_books = random.sample(available_books, min(4, len(available_books)))
    
    for book in high_fine_books:
        # Randomly select a membership
        membership = random.choice(memberships)
        
        # Calculate dates
        issue_date = datetime.now() - timedelta(days=random.randint(60, 90))  # Issued a long time ago
        expected_return_date = issue_date + timedelta(days=15)
        # Returned very late (30-45 days late)
        actual_return_date = expected_return_date + timedelta(days=random.randint(30, 45))
        
        # Calculate fine (₹10 per day)
        days_late = (actual_return_date - expected_return_date).days
        fine_amount = days_late * 10.0
        
        # Randomly decide if fine was paid
        fine_paid = random.choice([True, False])
        
        # Create transaction
        transaction = BookTransaction(
            book_id=book.id,
            membership_id=membership.id,
            issue_date=issue_date,
            return_date=expected_return_date,
            actual_return_date=actual_return_date,
            fine_amount=fine_amount,
            fine_paid=fine_paid,
            status="returned",
            remarks=f"Returned very late with high fine of ₹{fine_amount}"
        )
        
        # If fine is not paid, update membership pending amount
        if not fine_paid:
            member = Membership.query.get(membership.id)
            member.pending_amount += fine_amount
        
        db.session.add(transaction)
    
    db.session.commit()
    print(f"Added {len(high_fine_books)} transactions with high fines")
    
    # 2. Create currently issued books that are already overdue
    # Find more available books
    remaining_books = Book.query.filter_by(status="available").all()
    
    if remaining_books:
        # Take some books and mark them as issued but overdue
        currently_overdue_books = random.sample(remaining_books, min(3, len(remaining_books)))
        
        for book in currently_overdue_books:
            # Randomly select a membership
            membership = random.choice(memberships)
            
            # Calculate dates
            issue_date = datetime.now() - timedelta(days=random.randint(20, 30))  # Issued recently
            # Return date has already passed by 5-15 days
            expected_return_date = issue_date + timedelta(days=15)
            
            # Create transaction
            transaction = BookTransaction(
                book_id=book.id,
                membership_id=membership.id,
                issue_date=issue_date,
                return_date=expected_return_date,
                status="issued",
                remarks="Currently overdue"
            )
            
            # Update book status
            book.status = "issued"
            
            db.session.add(transaction)
        
        db.session.commit()
        print(f"Added {len(currently_overdue_books)} currently overdue books")
    
    # 3. Update some memberships with large pending amounts directly
    # Randomly select 3 memberships to have large pending amounts
    members_with_pending = random.sample(memberships, min(3, len(memberships)))
    
    for member in members_with_pending:
        # Add a random large amount (500-2000 rupees)
        additional_amount = random.randint(500, 2000)
        member.pending_amount += additional_amount
    
    db.session.commit()
    print(f"Updated {len(members_with_pending)} memberships with large pending amounts")
    
    # Display some statistics about the fines
    total_fine_amount = db.session.query(db.func.sum(BookTransaction.fine_amount)).scalar() or 0
    paid_fine_amount = db.session.query(db.func.sum(BookTransaction.fine_amount)) \
                          .filter(BookTransaction.fine_paid == True).scalar() or 0
    unpaid_fine_amount = total_fine_amount - paid_fine_amount
    
    overdue_transactions = BookTransaction.query.filter(
        BookTransaction.status == 'issued',
        BookTransaction.return_date < datetime.now()
    ).count()
    
    total_pending_amount = db.session.query(db.func.sum(Membership.pending_amount)).scalar() or 0
    
    print("\nFine Statistics:")
    print(f"Total fine amount: ₹{total_fine_amount:.2f}")
    print(f"Paid fine amount: ₹{paid_fine_amount:.2f}")
    print(f"Unpaid fine amount: ₹{unpaid_fine_amount:.2f}")
    print(f"Number of currently overdue books: {overdue_transactions}")
    print(f"Total pending amount across all memberships: ₹{total_pending_amount:.2f}")
    
    print("\nAdditional fine data added successfully!") 