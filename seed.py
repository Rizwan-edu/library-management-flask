import sqlite3
from datetime import datetime, timedelta

def seed_database():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    
    # 1. Wipe old data to start fresh
    cursor.execute("DROP TABLE IF EXISTS books")
    
    # 2. Re-create the table
    cursor.execute('''
        CREATE TABLE books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            category TEXT,
            status TEXT DEFAULT 'Available',
            borrower TEXT DEFAULT NULL,
            due_date TEXT DEFAULT NULL
        )
    ''')

    # 3. Create Fake Dates
    today = datetime.now().strftime('%Y-%m-%d')
    next_week = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    last_week = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d') # Overdue!

    # 4. Add Dummy Books
    books = [
        # (Title, Author, Category, Status, Borrower, DueDate)
        ("The Great Gatsby", "F. Scott Fitzgerald", "Fiction", "Available", None, None),
        ("Clean Code", "Robert C. Martin", "Technology", "Available", None, None),
        ("Introduction to Algorithms", "Thomas Cormen", "Technology", "Issued", "John Doe", next_week),
        ("To Kill a Mockingbird", "Harper Lee", "Fiction", "Available", None, None),
        ("Harry Potter", "J.K. Rowling", "Fiction", "Issued", "Alice Smith", last_week), # OVERDUE!
        ("Rich Dad Poor Dad", "Robert Kiyosaki", "Finance", "Available", None, None),
        ("Python Crash Course", "Eric Matthes", "Technology", "Issued", "Bob Jones", next_week),
        ("Sapiens", "Yuval Noah Harari", "History", "Available", None, None),
        ("Atomic Habits", "James Clear", "Self-Help", "Available", None, None),
        ("The Alchemist", "Paulo Coelho", "Fiction", "Issued", "Sarah Connor", next_week)
    ]

    cursor.executemany("INSERT INTO books (title, author, category, status, borrower, due_date) VALUES (?, ?, ?, ?, ?, ?)", books)
    
    conn.commit()
    conn.close()
    print("Database populated with 10 books! (Includes Borrowers and Fines)")

if __name__ == "__main__":
    seed_database()