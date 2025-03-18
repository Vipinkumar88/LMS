from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta
from models import db, User, Book, Membership, BookTransaction

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Create all tables
@app.before_first_request
def create_tables():
    db.create_all()

# Home route
@app.route('/')
def home():
    if 'user_id' in session:
        # Redirect based on user role
        if session.get('role') == 'admin':
            return redirect(url_for('admin_home'))
        else:
            return redirect(url_for('user_home'))
    return render_template('home.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            
            # Redirect admin users to admin_home, others to user_home
            if session['role'] == 'admin':
                return redirect(url_for('admin_home'))
            else:
                return redirect(url_for('user_home'))
        else:
            error = 'Invalid credentials. Please enter correct username and password.'
    
    return render_template('login.html', error=error)

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    return render_template('logout_success.html')

# Book Search route
@app.route('/search_book', methods=['GET', 'POST'])
def search_book():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    books = []
    if request.method == 'POST':
        search_query = request.form.get('search_query', '')
        search_by = request.form.get('search_by', 'title')
        
        if search_query:
            if search_by == 'title':
                books = Book.query.filter(Book.title.like(f'%{search_query}%')).all()
            elif search_by == 'author':
                books = Book.query.filter(Book.author.like(f'%{search_query}%')).all()
            elif search_by == 'serial':
                books = Book.query.filter(Book.serial_number.like(f'%{search_query}%')).all()
    
    return render_template('search_book.html', books=books)

# Book Issue route
@app.route('/issue_book/<int:book_id>', methods=['GET', 'POST'])
def issue_book(book_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    book = Book.query.get_or_404(book_id)
    
    if book.status != 'available':
        flash('This book is not available for issue')
        return redirect(url_for('search_book'))
    
    if request.method == 'POST':
        membership_number = request.form.get('membership_number')
        issue_date_str = request.form.get('issue_date')
        return_date_str = request.form.get('return_date')
        remarks = request.form.get('remarks')
        
        if not membership_number:
            flash('Membership number is required')
            return render_template('issue_book.html', book=book, now=datetime.now())
        
        membership = Membership.query.filter_by(membership_number=membership_number).first()
        if not membership:
            flash('Invalid membership number')
            return render_template('issue_book.html', book=book, now=datetime.now())
        
        # Validate issue date
        issue_date = datetime.strptime(issue_date_str, '%Y-%m-%d')
        if issue_date.date() < datetime.now().date():
            flash('Issue date cannot be in the past')
            return render_template('issue_book.html', book=book, now=datetime.now())
        
        # Validate return date
        return_date = datetime.strptime(return_date_str, '%Y-%m-%d')
        max_return_date = issue_date + timedelta(days=15)
        if return_date > max_return_date:
            flash('Return date cannot be more than 15 days from issue date')
            return render_template('issue_book.html', book=book, now=datetime.now())
        
        transaction = BookTransaction(
            book_id=book.id,
            membership_id=membership.id,
            issue_date=issue_date,
            return_date=return_date,
            remarks=remarks
        )
        
        book.status = 'issued'
        
        db.session.add(transaction)
        db.session.commit()
        
        flash('Book issued successfully')
        return redirect(url_for('search_book'))
    
    return render_template('issue_book.html', book=book, now=datetime.now())

# Return Book route
@app.route('/return_book', methods=['GET', 'POST'])
def return_book():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        book_title = request.form.get('book_title')
        serial_number = request.form.get('serial_number')
        
        if not book_title or not serial_number:
            flash('Book title and serial number are required')
            return render_template('return_book.html')
        
        book = Book.query.filter_by(title=book_title, serial_number=serial_number).first()
        if not book:
            flash('Book not found')
            return render_template('return_book.html')
        
        transaction = BookTransaction.query.filter_by(
            book_id=book.id, 
            status='issued'
        ).order_by(BookTransaction.issue_date.desc()).first()
        
        if not transaction:
            flash('No issue record found for this book')
            return render_template('return_book.html')
        
        return redirect(url_for('confirm_return', transaction_id=transaction.id))
    
    return render_template('return_book.html')

# Confirm Return route
@app.route('/confirm_return/<int:transaction_id>', methods=['GET', 'POST'])
def confirm_return(transaction_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    transaction = BookTransaction.query.get_or_404(transaction_id)
    book = transaction.book
    
    if request.method == 'POST':
        actual_return_date_str = request.form.get('actual_return_date')
        actual_return_date = datetime.strptime(actual_return_date_str, '%Y-%m-%d')
        
        # Calculate fine if any
        fine_amount = 0
        if actual_return_date.date() > transaction.return_date.date():
            days_late = (actual_return_date.date() - transaction.return_date.date()).days
            fine_amount = days_late * 10  # Assume Rs. 10 per day
        
        transaction.actual_return_date = actual_return_date
        transaction.fine_amount = fine_amount
        transaction.status = 'returned'
        book.status = 'available'
        
        db.session.commit()
        
        if fine_amount > 0:
            return redirect(url_for('pay_fine', transaction_id=transaction.id))
        else:
            flash('Book returned successfully')
            return redirect(url_for('transaction_completed'))
    
    return render_template('confirm_return.html', transaction=transaction, book=book)

# Pay Fine route
@app.route('/pay_fine/<int:transaction_id>', methods=['GET', 'POST'])
def pay_fine(transaction_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    transaction = BookTransaction.query.get_or_404(transaction_id)
    
    if request.method == 'POST':
        fine_paid = request.form.get('fine_paid') == 'yes'
        remarks = request.form.get('remarks')
        
        if transaction.fine_amount > 0 and not fine_paid:
            flash('Please pay the fine to complete the return process')
            return render_template('pay_fine.html', transaction=transaction)
        
        transaction.fine_paid = fine_paid
        transaction.remarks = remarks
        
        db.session.commit()
        
        flash('Book return process completed successfully')
        return redirect(url_for('transaction_completed'))
    
    return render_template('pay_fine.html', transaction=transaction)

# Maintenance routes (Admin only)
@app.route('/maintenance')
def maintenance():
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please login first')
        return redirect(url_for('login'))
    
    # Check if user has admin role
    if 'role' in session and session['role'] == 'admin':
        # Add debug info to flash message
        flash(f'Welcome, {session.get("username")}! You are on the maintenance page.', 'success')
        return render_template('maintenance.html')
    else:
        # Flash message in English
        flash('Only admin users can view the maintenance page')
        return redirect(url_for('user_home' if 'role' in session and session['role'] == 'user' else 'login'))

# Add Membership route
@app.route('/add_membership', methods=['GET', 'POST'])
def add_membership():
    if 'role' not in session or session['role'] != 'admin':
        flash('Only admins can add memberships')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        contact_name = request.form.get('contact_name')
        contact_address = request.form.get('contact_address')
        aadhar_card_number = request.form.get('aadhar_card_number')
        membership_type = request.form.get('membership_type', '6 months')
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        
        if not first_name or not last_name or not contact_name or not contact_address:
            flash('Please fill all required fields')
            return render_template('add_membership.html')
        
        # Generate membership number
        import random
        membership_number = f'MEM{random.randint(10000, 99999)}'
        
        # Full name from first and last name
        name = f"{first_name} {last_name}"
        
        # Process dates
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        except ValueError:
            flash('Date format is invalid')
            return render_template('add_membership.html')
        
        # Validate end date is after start date
        if end_date <= start_date:
            flash('End date must be after start date')
            return render_template('add_membership.html')
        
        # Create empty values for missing fields that were in the old form
        phone = ""
        email = ""
        
        membership = Membership(
            membership_number=membership_number,
            name=name,
            address=contact_address,
            phone=phone,
            email=email,
            aadhar_card_number=aadhar_card_number,
            membership_type=membership_type,
            start_date=start_date,
            end_date=end_date
        )
        
        db.session.add(membership)
        db.session.commit()
        
        flash(f'Membership added successfully. Membership Number: {membership_number}')
        return redirect(url_for('maintenance'))
    
    return render_template('add_membership.html')

# Update Membership route
@app.route('/update_membership', methods=['GET', 'POST'])
def update_membership():
    if 'role' not in session or session['role'] != 'admin':
        flash('Only admins can update memberships')
        return redirect(url_for('login'))
    
    membership = None
    
    if request.method == 'POST':
        membership_number = request.form.get('membership_number')
        
        if 'search' in request.form:
            if not membership_number:
                flash('Membership number is required')
                return render_template('update_membership.html')
            
            membership = Membership.query.filter_by(membership_number=membership_number).first()
            if not membership:
                flash('Membership not found')
                return render_template('update_membership.html')
            
            return render_template('update_membership.html', membership=membership)
        
        elif 'update' in request.form:
            membership = Membership.query.filter_by(membership_number=membership_number).first()
            if not membership:
                flash('Membership not found')
                return render_template('update_membership.html')
            
            action = request.form.get('action')
            extension_type = request.form.get('extension_type', '6 months')
            pending_amount_str = request.form.get('pending_amount', '0')
            
            # Update pending amount
            try:
                pending_amount = float(pending_amount_str)
                membership.pending_amount = pending_amount
            except ValueError:
                flash('Pending amount must be a valid number')
                return render_template('update_membership.html', membership=membership)
            
            # Remove membership if the cancel action is selected
            if action == 'cancel':
                membership.status = 'cancelled'
                db.session.commit()
                flash('Membership cancelled successfully')
                return redirect(url_for('maintenance'))
            
            # Otherwise extend membership based on extension_type
            if extension_type == '6 months':
                membership.end_date = membership.end_date + timedelta(days=180)
            elif extension_type == '1 year':
                membership.end_date = membership.end_date + timedelta(days=365)
            else:  # 2 years
                membership.end_date = membership.end_date + timedelta(days=730)
            
            membership.status = 'active'
            db.session.commit()
            flash('Membership extended successfully')
            return redirect(url_for('maintenance'))
    
    return render_template('update_membership.html', membership=membership)

# Add Book route
@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if 'role' not in session or session['role'] != 'admin':
        flash('Only admins can add books/movies')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        type = request.form.get('type', 'book')
        title = request.form.get('title')
        author = request.form.get('author', '-')
        publisher = request.form.get('publisher', '-')
        year = request.form.get('year', datetime.now().year)
        cost = request.form.get('cost', 0)
        procurement_date_str = request.form.get('procurement_date')
        quantity = int(request.form.get('quantity', 1))
        
        if not title or not procurement_date_str:
            flash('Please fill all required fields')
            return render_template('add_book.html', current_year=datetime.now().year)
        
        # Process procurement_date
        try:
            procurement_date = datetime.strptime(procurement_date_str, '%Y-%m-%d')
        except ValueError:
            flash('Procurement date must be a valid date')
            return render_template('add_book.html', current_year=datetime.now().year)
        
        # Process cost
        cost_float = 0
        if cost and cost.strip() and cost != '0':
            try:
                cost_float = float(cost)
            except ValueError:
                flash('Cost must be a valid number')
                return render_template('add_book.html', current_year=datetime.now().year)
        
        # Add multiple copies based on quantity
        added_serials = []
        for _ in range(quantity):
            # Generate serial number for each copy
            import random
            serial_number = f'BK{random.randint(10000, 99999)}'
            
            book = Book(
                serial_number=serial_number,
                type=type,
                title=title,
                author=author,
                publisher=publisher,
                year=year,
                status='available',
                cost=cost_float,
                procurement_date=procurement_date
            )
            
            db.session.add(book)
            added_serials.append(serial_number)
        
        db.session.commit()
        
        if quantity == 1:
            flash(f'Book/Movie added successfully. Serial Number: {added_serials[0]}')
        else:
            flash(f'{quantity} copies added successfully. Serial Numbers: {", ".join(added_serials)}')
        
        return redirect(url_for('maintenance'))
    
    return render_template('add_book.html', current_year=datetime.now().year)

# Update Book route
@app.route('/update_book', methods=['GET', 'POST'])
def update_book():
    if 'role' not in session or session['role'] != 'admin':
        flash('Only admins can update books/movies')
        return redirect(url_for('login'))
    
    book = None
    
    if request.method == 'POST':
        serial_number = request.form.get('serial_number')
        
        if 'search' in request.form:
            if not serial_number:
                flash('Serial number is required')
                return render_template('update_book.html')
            
            book = Book.query.filter_by(serial_number=serial_number).first()
            if not book:
                flash('Book/Movie not found')
                return render_template('update_book.html')
            
            return render_template('update_book.html', book=book)
        
        elif 'update' in request.form:
            book = Book.query.filter_by(serial_number=serial_number).first()
            if not book:
                flash('Book/Movie not found')
                return render_template('update_book.html')
            
            # Get form fields
            type = request.form.get('type')
            title = request.form.get('title')
            status = request.form.get('status')
            procurement_date_str = request.form.get('procurement_date')
            
            # Get hidden fields
            author = request.form.get('author')
            publisher = request.form.get('publisher')
            year = request.form.get('year')
            cost = request.form.get('cost')
            
            if not title:
                flash('Book/Movie name is required')
                return render_template('update_book.html', book=book)
            
            # Process procurement_date
            procurement_date = None
            if procurement_date_str and procurement_date_str.strip():
                try:
                    procurement_date = datetime.strptime(procurement_date_str, '%Y-%m-%d')
                except ValueError:
                    flash('Date must be a valid date')
                    return render_template('update_book.html', book=book)
            
            # Update book fields
            book.type = type
            book.title = title
            book.status = status
            
            # Update optional fields if they exist
            if procurement_date:
                book.procurement_date = procurement_date
            if author:
                book.author = author
            if publisher:
                book.publisher = publisher
            if year:
                book.year = int(year)
            if cost:
                try:
                    book.cost = float(cost)
                except ValueError:
                    # Default to 0 if cost can't be converted
                    book.cost = 0
            
            db.session.commit()
            flash('Book/Movie updated successfully')
            return redirect(url_for('maintenance'))
    
    return render_template('update_book.html', book=book)

# User Management route
@app.route('/user_management', methods=['GET', 'POST'])
def user_management():
    if 'role' not in session or session['role'] != 'admin':
        flash('Only admins can manage users')
        return redirect(url_for('login'))
    
    user = None
    
    # Get action from URL parameter in GET request
    if request.method == 'GET':
        action = request.args.get('action', 'new')
    else:
        action = request.form.get('action', 'new')
    
    if request.method == 'POST':
        if action == 'new':
            # Generate random username if not provided
            import random
            import string
            username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
            
            # Default password same as username
            password = username
            name = request.form.get('name')
            
            # Check if admin checkbox is checked
            role = 'admin' if request.form.get('role') == 'admin' else 'user'
            
            # Check if status checkbox is checked
            status = 'active' if request.form.get('status') == 'active' else 'inactive'
            
            if not name:
                flash('Name field is required')
                return render_template('user_management.html', action=action)
            
            user = User(
                username=username,
                password=password,
                name=name,
                role=role,
                status=status
            )
            
            db.session.add(user)
            db.session.commit()
            
            flash(f'User added successfully. Username: {username}, Password: {password}')
            return redirect(url_for('maintenance'))
        
        elif action == 'existing':
            # Here we would need to show a search form first
            # Since the new template uses radio buttons, we need to handle this differently
            # We could redirect to a search page or implement a modal search
            
            # For now, we'll just flash a message
            flash('Existing user update feature is under development')
            return render_template('user_management.html', action=action)
    
    return render_template('user_management.html', user=user, action=action)

# Reports routes
@app.route('/reports')
def reports():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('reports.html')

# Book Report
@app.route('/book_report')
def book_report():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    books = Book.query.all()
    return render_template('book_report.html', books=books)

# Membership Report
@app.route('/membership_report')
def membership_report():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    memberships = Membership.query.all()
    return render_template('membership_report.html', memberships=memberships)

# Transaction Report
@app.route('/transaction_report')
def transaction_report():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    status_filter = request.args.get('status')
    overdue_filter = request.args.get('overdue')
    
    if status_filter:
        transactions = BookTransaction.query.filter_by(status=status_filter).all()
    elif overdue_filter == 'true':
        # Get all active transactions that are overdue
        transactions = BookTransaction.query.filter(
            BookTransaction.status == 'issued',
            BookTransaction.return_date < datetime.now().date()
        ).all()
    else:
        transactions = BookTransaction.query.all()
    
    return render_template('transaction_report.html', transactions=transactions, 
                          status_filter=status_filter, overdue_filter=overdue_filter)

# Signup route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        name = request.form['name']
        
        if password != confirm_password:
            error = 'Passwords do not match'
            return render_template('signup.html', error=error)
        
        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            error = 'This username is already in use'
            return render_template('signup.html', error=error)
        
        # Create new user
        user = User(
            username=username,
            password=password,
            name=name,
            role='user',  # Default role is user
            status='active'  # Default status is active
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('Your account has been successfully created. Please login.')
        return redirect(url_for('login'))
    
    return render_template('signup.html', error=error)

# User Home Page
@app.route('/user_home')
def user_home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Only allow non-admin users
    if session.get('role') == 'admin':
        return redirect(url_for('admin_home'))
    
    return render_template('user_home.html')

# Book Categories
@app.route('/categories')
def categories():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Redirect all logged-in users to their respective home pages
    if session.get('role') == 'admin':
        return redirect(url_for('admin_home'))
    else:
        return redirect(url_for('user_home'))
    
    # This code is now unreachable, keeping it for reference
    # Get unique book types (categories)
    book_types = db.session.query(Book.type).distinct().all()
    book_types = [t[0] for t in book_types]
    
    # If no book types exist yet, add default ones
    if not book_types:
        book_types = ['book', 'movie']
    
    return render_template('categories.html', book_types=book_types)

# Books by Category
@app.route('/category/<category>')
def category(category):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    books = Book.query.filter_by(type=category).all()
    return render_template('category_books.html', books=books, category=category)

# Admin Home Page
@app.route('/admin_home')
def admin_home():
    if 'role' not in session or session['role'] != 'admin':
        flash('Only admin users can view this page')
        return redirect(url_for('login'))
    
    return render_template('admin_home.html')

# Transaction Routes Section
@app.route('/transactions')
def transactions():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('transactions.html')

# Book Availability route
@app.route('/book_availability', methods=['GET', 'POST'])
def book_availability():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get all unique book titles and authors for datalist
    all_books = Book.query.all()
    all_authors = db.session.query(Book.author).distinct().all()
    all_authors = [author[0] for author in all_authors]
    
    books = []
    searched = False
    
    if request.method == 'POST':
        searched = True
        book_title = request.form.get('book_title', '')
        book_author = request.form.get('book_author', '')
        
        # Build query
        query = Book.query
        
        if book_title:
            query = query.filter(Book.title.like(f'%{book_title}%'))
        
        if book_author:
            query = query.filter(Book.author.like(f'%{book_author}%'))
        
        books = query.all()
    
    return render_template('book_availability.html', 
                           books=books, 
                           all_books=all_books, 
                           all_authors=all_authors,
                           searched=searched)

# Book Issue Page route
@app.route('/book_issue', methods=['GET', 'POST'])
def book_issue():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get all unique book titles for datalist
    all_books = Book.query.all()
    
    error = None
    book = None
    book_found = False
    membership_number = ""
    issue_date = ""
    return_date = ""
    remarks = ""
    
    now = datetime.now()
    
    if request.method == 'POST':
        book_title = request.form.get('book_title', '')
        book_author = request.form.get('book_author', '')
        membership_number = request.form.get('membership_number', '')
        issue_date = request.form.get('issue_date', '')
        return_date = request.form.get('return_date', '')
        remarks = request.form.get('remarks', '')
        
        # Validate required fields
        if not book_title:
            error = "Book name is required"
        elif not membership_number:
            error = "Membership number is required"
        elif not issue_date:
            error = "Issue date is required"
        elif not return_date:
            error = "Return date is required"
        else:
            # Search for the book
            query = Book.query.filter(Book.title.like(f'%{book_title}%'))
            
            if book_author:
                query = query.filter(Book.author.like(f'%{book_author}%'))
            
            book = query.first()
            
            if not book:
                error = "Book not found. Please try different search criteria."
            else:
                book_found = True
                
                # Validate membership
                membership = Membership.query.filter_by(membership_number=membership_number).first()
                if not membership:
                    error = "Invalid membership number"
                    book_found = False
    
    return render_template('book_issue.html', 
                          all_books=all_books,
                          error=error,
                          book=book,
                          book_found=book_found,
                          membership_number=membership_number,
                          issue_date=issue_date,
                          return_date=return_date,
                          remarks=remarks,
                          now=now,
                          timedelta=timedelta)

# Direct Book Issue route
@app.route('/direct_issue/<int:book_id>', methods=['POST'])
def direct_issue(book_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    book = Book.query.get_or_404(book_id)
    
    if book.status != 'available':
        flash('This book is not available for issue')
        return redirect(url_for('book_issue'))
    
    membership_number = request.form.get('membership_number')
    issue_date_str = request.form.get('issue_date')
    return_date_str = request.form.get('return_date')
    remarks = request.form.get('remarks')
    
    if not membership_number:
        flash('Membership number is required')
        return redirect(url_for('book_issue'))
    
    membership = Membership.query.filter_by(membership_number=membership_number).first()
    if not membership:
        flash('Invalid membership number')
        return redirect(url_for('book_issue'))
    
    # Validate issue date
    issue_date = datetime.strptime(issue_date_str, '%Y-%m-%d')
    if issue_date.date() < datetime.now().date():
        flash('Issue date cannot be in the past')
        return redirect(url_for('book_issue'))
    
    # Validate return date
    return_date = datetime.strptime(return_date_str, '%Y-%m-%d')
    max_return_date = issue_date + timedelta(days=15)
    if return_date > max_return_date:
        flash('Return date cannot be more than 15 days from issue date')
        return redirect(url_for('book_issue'))
    
    transaction = BookTransaction(
        book_id=book.id,
        membership_id=membership.id,
        issue_date=issue_date,
        return_date=return_date,
        remarks=remarks
    )
    
    book.status = 'issued'
    
    db.session.add(transaction)
    db.session.commit()
    
    flash('Book issued successfully')
    return redirect(url_for('transaction_completed'))

# Search For Fine route
@app.route('/search_for_fine', methods=['POST'])
def search_for_fine():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    book_title = request.form.get('book_title')
    serial_number = request.form.get('serial_number')
    
    if not book_title or not serial_number:
        flash('Book title and serial number are required')
        return redirect(url_for('transactions'))
    
    book = Book.query.filter_by(title=book_title, serial_number=serial_number).first()
    if not book:
        flash('Book not found')
        return redirect(url_for('transactions'))
    
    # Find the latest returned transaction with fine for this book
    transaction = BookTransaction.query.filter_by(
        book_id=book.id, 
        status='returned',
        fine_paid=False
    ).filter(BookTransaction.fine_amount > 0).order_by(BookTransaction.actual_return_date.desc()).first()
    
    if not transaction:
        flash('There is no payable fine for this book')
        return redirect(url_for('transactions'))
    
    return redirect(url_for('pay_fine', transaction_id=transaction.id))

# Search For Cancel route
@app.route('/search_for_cancel', methods=['POST'])
def search_for_cancel():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    book_title = request.form.get('book_title')
    serial_number = request.form.get('serial_number')
    
    if not book_title or not serial_number:
        flash('Book title and serial number are required')
        return redirect(url_for('transactions'))
    
    book = Book.query.filter_by(title=book_title, serial_number=serial_number).first()
    if not book:
        flash('Book not found')
        return redirect(url_for('transactions'))
    
    # Find the active transaction for this book
    transaction = BookTransaction.query.filter_by(
        book_id=book.id, 
        status='issued'
    ).order_by(BookTransaction.issue_date.desc()).first()
    
    if not transaction:
        flash('There is no active transaction for this book')
        return redirect(url_for('transactions'))
    
    return redirect(url_for('cancel_transaction', transaction_id=transaction.id))

# Movie Report (Movies Master List)
@app.route('/movie_report')
def movie_report():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get all books of type 'movie'
    movies = Book.query.filter_by(type='movie').all()
    return render_template('movie_report.html', books=movies)

# Issue Requests Report
@app.route('/issue_requests_report')
def issue_requests_report():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # In a real application, you would have a separate model for issue requests
    # For this implementation, we'll simulate it with dummy data
    
    # Get all memberships for the demo
    memberships = Membership.query.all()
    books = Book.query.all()
    
    # Create dummy issue requests
    issue_requests = []
    
    if memberships and books:
        # Add a few sample requests
        import random
        from datetime import timedelta
        
        # Ensure we have at least some data to show
        num_requests = min(5, len(memberships), len(books))
        
        for i in range(num_requests):
            membership = memberships[i % len(memberships)]
            book = books[i % len(books)]
            
            # Random requested date in the past 30 days
            requested_date = datetime.now() - timedelta(days=random.randint(1, 30))
            
            # Some requests fulfilled, some pending
            fulfilled_date = None
            if random.choice([True, False]):
                fulfilled_date = requested_date + timedelta(days=random.randint(1, 7))
            
            issue_requests.append({
                'membership_number': membership.membership_number,
                'book_title': book.title,
                'requested_date': requested_date,
                'fulfilled_date': fulfilled_date
            })
    
    return render_template('issue_requests_report.html', issue_requests=issue_requests)

# Overdue Returns Report
@app.route('/overdue_returns')
def overdue_returns():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get all active transactions that are overdue
    overdue_transactions = BookTransaction.query.filter(
        BookTransaction.status == 'issued',
        BookTransaction.return_date < datetime.now().date()
    ).all()
    
    return render_template('overdue_returns.html', transactions=overdue_transactions, now=datetime.now())

# Cancel Transaction route
@app.route('/cancel_transaction/<int:transaction_id>')
def cancel_transaction(transaction_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    transaction = BookTransaction.query.get_or_404(transaction_id)
    book = transaction.book
    
    # Only allow cancellation of transactions that are in 'issued' status
    if transaction.status == 'issued':
        # Update transaction status
        transaction.status = 'cancelled'
        
        # Update book status back to available
        book.status = 'available'
        
        db.session.commit()
        
        flash('Transaction cancelled successfully')
    else:
        flash('Only issued transactions can be cancelled')
    
    return redirect(url_for('transaction_completed'))

# Generic cancel page (no transaction ID)
@app.route('/cancel')
def cancel():
    return render_template('cancel_transaction.html')

# Transaction Completed route
@app.route('/transaction_completed')
def transaction_completed():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('transaction_completed.html')

if __name__ == '__main__':
    app.run(debug=True) 