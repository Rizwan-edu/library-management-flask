from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('library.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- DATABASE SETUP ---
def init_db():
    conn = get_db_connection()
    # Create table with ALL columns needed for the project
    conn.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            category TEXT,
            status TEXT DEFAULT 'Available',
            borrower_name TEXT DEFAULT NULL,
            issue_date DATE DEFAULT NULL,
            due_date DATE DEFAULT NULL
        )
    ''')
    conn.commit()
    conn.close()
    seed_data()

def seed_data():
    conn = get_db_connection()
    if conn.execute('SELECT count(*) FROM books').fetchone()[0] == 0:
        # Seeding Initial Data
        books = [
            ('Python Crash Course', 'Eric Matthes', 'Technology'),
            ('Clean Code', 'Robert Martin', 'Technology'),
            ('The Great Gatsby', 'F. Scott Fitzgerald', 'Fiction'),
            ('1984', 'George Orwell', 'Fiction'),
            ('A Brief History of Time', 'Stephen Hawking', 'Science'),
            ('Sapiens', 'Yuval Noah Harari', 'History')
        ]
        conn.executemany('INSERT INTO books (title, author, category) VALUES (?, ?, ?)', books)
        conn.commit()
        print("Database seeded with initial books.")
    conn.close()

# --- ROUTES ---

@app.route('/')
def index():
    # DASHBOARD: Shows Statistics
    conn = get_db_connection()
    
    total_books = conn.execute('SELECT count(*) FROM books').fetchone()[0]
    issued_books = conn.execute('SELECT count(*) FROM books WHERE status="Issued"').fetchone()[0]
    
    # Calculate Overdue & Fines
    today = datetime.now().date()
    overdue_count = 0
    total_fine = 0
    issued_list = conn.execute('SELECT * FROM books WHERE status="Issued"').fetchall()
    
    for book in issued_list:
        if book['due_date']:
            due = datetime.strptime(book['due_date'], '%Y-%m-%d').date()
            if due < today:
                overdue_count += 1
                days_late = (today - due).days
                total_fine += (days_late * 10) # 10 currency units fine per day

    conn.close()
    
    return render_template('index.html', 
                           total=total_books, 
                           issued=issued_books, 
                           overdue=overdue_count,
                           fine=total_fine)

@app.route('/inventory')
def inventory():
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM books').fetchall()
    conn.close()
    return render_template('inventory.html', books=books)

@app.route('/add_book', methods=('GET', 'POST'))
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        category = request.form['category']
        conn = get_db_connection()
        conn.execute('INSERT INTO books (title, author, category) VALUES (?, ?, ?)', (title, author, category))
        conn.commit()
        conn.close()
        return redirect(url_for('inventory'))
    return render_template('add_book.html')

# --- NEW: EDIT & DELETE ROUTES ---

@app.route('/edit/<int:book_id>', methods=('GET', 'POST'))
def edit_book(book_id):
    conn = get_db_connection()
    book = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        category = request.form['category']
        
        conn.execute('UPDATE books SET title = ?, author = ?, category = ? WHERE id = ?',
                     (title, author, category, book_id))
        conn.commit()
        conn.close()
        return redirect(url_for('inventory'))

    conn.close()
    return render_template('edit_book.html', book=book)

@app.route('/delete/<int:book_id>')
def delete_book(book_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM books WHERE id = ?', (book_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('inventory'))

# --- ISSUE & RETURN ROUTES ---

@app.route('/issue/<int:book_id>', methods=('GET', 'POST'))
def issue_book(book_id):
    if request.method == 'POST':
        borrower = request.form['borrower']
        days = int(request.form['days'])
        
        issue_date = datetime.now()
        due_date = issue_date + timedelta(days=days)
        
        conn = get_db_connection()
        conn.execute('UPDATE books SET status="Issued", borrower_name=?, issue_date=?, due_date=? WHERE id=?',
                     (borrower, issue_date.strftime('%Y-%m-%d'), due_date.strftime('%Y-%m-%d'), book_id))
        conn.commit()
        conn.close()
        return redirect(url_for('inventory'))
        
    return render_template('issue_modal.html', book_id=book_id)

@app.route('/issued_books')
def issued_books():
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM books WHERE status="Issued"').fetchall()
    conn.close()
    
    book_list = []
    today = datetime.now().date()
    
    for book in books:
        if book['due_date']:
            due_date = datetime.strptime(book['due_date'], '%Y-%m-%d').date()
            days_overdue = (today - due_date).days
            fine = max(0, days_overdue * 10)
            
            book_list.append({
                'id': book['id'],
                'title': book['title'],
                'borrower': book['borrower_name'],
                'due_date': book['due_date'],
                'fine': fine
            })
        
    return render_template('issued_books.html', books=book_list)

@app.route('/return/<int:book_id>')
def return_book(book_id):
    conn = get_db_connection()
    conn.execute('UPDATE books SET status="Available", borrower_name=NULL, issue_date=NULL, due_date=NULL WHERE id=?', (book_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('issued_books'))

# --- APP STARTUP ---
init_db()

if __name__ == '__main__':
    app.run(debug=True)