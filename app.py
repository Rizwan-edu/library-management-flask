from flask import Flask, render_template, request, redirect, url_for
import os
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

# --- DATABASE CONNECTION ---
def get_db_connection():
    conn = sqlite3.connect('library.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- INITIALIZE DATABASE ---
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            category TEXT,
            status TEXT DEFAULT 'Available',
            borrower TEXT DEFAULT NULL,
            due_date TEXT DEFAULT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- ROUTES ---

@app.route('/')
def index():
    conn = get_db_connection()
    # Dashboard Stats
    total = conn.execute('SELECT COUNT(*) FROM books').fetchone()[0]
    borrowed = conn.execute("SELECT COUNT(*) FROM books WHERE status='Issued'").fetchone()[0]
    # Check for Overdue Books
    overdue = 0
    today = datetime.now().date()
    all_borrowed = conn.execute("SELECT * FROM books WHERE status='Issued'").fetchall()
    
    for book in all_borrowed:
        if book['due_date']:
            due = datetime.strptime(book['due_date'], '%Y-%m-%d').date()
            if today > due:
                overdue += 1
                
    conn.close()
    return render_template('index.html', total=total, borrowed=borrowed, overdue=overdue)

@app.route('/books')
def view_books():
    conn = get_db_connection()
    books = conn.execute("SELECT * FROM books").fetchall()
    conn.close()
    
    # Calculate Fines for Display
    books_with_fines = []
    today = datetime.now().date()
    
    for book in books:
        fine = 0
        is_overdue = False
        if book['status'] == 'Issued' and book['due_date']:
            due = datetime.strptime(book['due_date'], '%Y-%m-%d').date()
            if today > due:
                days_late = (today - due).days
                fine = days_late * 10  # $10 fine per day
                is_overdue = True
        
        # Convert row to dict to append fine data
        book_dict = dict(book)
        book_dict['fine'] = fine
        book_dict['is_overdue'] = is_overdue
        books_with_fines.append(book_dict)

    return render_template('books.html', books=books_with_fines)

@app.route('/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        category = request.form['category']
        
        conn = get_db_connection()
        conn.execute("INSERT INTO books (title, author, category) VALUES (?, ?, ?)", 
                     (title, author, category))
        conn.commit()
        conn.close()
        return redirect(url_for('view_books'))
    return render_template('add_book.html')

@app.route('/issue/<int:id>', methods=['POST'])
def issue_book(id):
    student_name = request.form['student_name']
    # Set Due Date to 7 days from now
    due_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    
    conn = get_db_connection()
    conn.execute("UPDATE books SET status='Issued', borrower=?, due_date=? WHERE id=?", 
                 (student_name, due_date, id))
    conn.commit()
    conn.close()
    return redirect(url_for('view_books'))

@app.route('/return/<int:id>')
def return_book(id):
    conn = get_db_connection()
    conn.execute("UPDATE books SET status='Available', borrower=NULL, due_date=NULL WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('view_books'))

@app.route('/delete/<int:id>')
def delete_book(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM books WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('view_books'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)