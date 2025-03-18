# Library Management System

A comprehensive library management system built with Flask, SQLAlchemy, and Bootstrap. This system allows librarians to manage books, memberships, and transactions efficiently.

## Features

- User authentication with admin and regular user roles
- Book and movie management
- Membership management
- Transaction tracking (issue, return, fine collection)
- Reporting system (books, members, transactions, overdue items)
- Fine calculation and tracking

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Vipinkumar88/LMS.git
cd LMS
```

2. Create a virtual environment and activate it:
```bash
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On Unix/MacOS
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
python drop_tables.py
```

5. Add dummy data (optional):
```bash
python add_dummy_data.py
python add_fine_data.py
```

6. Run the application:
```bash
python app.py
```

7. Access the application in your browser at `http://127.0.0.1:5000/`

## Default Users

- Admin: username: `admin`, password: `admin123`
- User: username: `user`, password: `user123`

## License

MIT
