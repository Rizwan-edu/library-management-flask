from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

# --- DATABASE CONNECTION HANDLER ---
def get_db_connection():
    conn = sqlite3.connect('library.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- DATABASE SETUP ---
def init_db():
    with get_db_connection() as conn:
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
    seed_data()

# --- 150+ BOOKS SEED DATA ---
def seed_data():
    with get_db_connection() as conn:
        if conn.execute('SELECT count(*) FROM books').fetchone()[0] == 0:
            books = [
                # --- TECHNOLOGY & CODING ---
                ('Python Crash Course', 'Eric Matthes', 'Technology'),
                ('Clean Code', 'Robert Martin', 'Technology'),
                ('The Pragmatic Programmer', 'Andrew Hunt', 'Technology'),
                ('Introduction to Algorithms', 'Thomas H. Cormen', 'Technology'),
                ('Design Patterns', 'Erich Gamma', 'Technology'),
                ('You Don\'t Know JS', 'Kyle Simpson', 'Technology'),
                ('Cracking the Coding Interview', 'Gayle Laakmann McDowell', 'Technology'),
                ('Code Complete', 'Steve McConnell', 'Technology'),
                ('Head First Java', 'Kathy Sierra', 'Technology'),
                ('The Mythical Man-Month', 'Fred Brooks', 'Technology'),
                ('Refactoring', 'Martin Fowler', 'Technology'),
                ('Artificial Intelligence: A Modern Approach', 'Stuart Russell', 'Technology'),
                ('Deep Learning', 'Ian Goodfellow', 'Technology'),
                ('Automate the Boring Stuff with Python', 'Al Sweigart', 'Technology'),
                ('Fluent Python', 'Luciano Ramalho', 'Technology'),
                ('The Linux Command Line', 'William Shotts', 'Technology'),
                ('Pro Git', 'Scott Chacon', 'Technology'),
                ('Effective Java', 'Joshua Bloch', 'Technology'),
                ('Rust Programming Language', 'Steve Klabnik', 'Technology'),
                ('Grokking Algorithms', 'Aditya Bhargava', 'Technology'),

                # --- FICTION & CLASSICS ---
                ('The Great Gatsby', 'F. Scott Fitzgerald', 'Fiction'),
                ('1984', 'George Orwell', 'Fiction'),
                ('To Kill a Mockingbird', 'Harper Lee', 'Fiction'),
                ('Pride and Prejudice', 'Jane Austen', 'Romance'),
                ('The Catcher in the Rye', 'J.D. Salinger', 'Fiction'),
                ('The Alchemist', 'Paulo Coelho', 'Fiction'),
                ('The Kite Runner', 'Khaled Hosseini', 'Fiction'),
                ('Life of Pi', 'Yann Martel', 'Fiction'),
                ('The Book Thief', 'Markus Zusak', 'Fiction'),
                ('The Grapes of Wrath', 'John Steinbeck', 'Classic'),
                ('Brave New World', 'Aldous Huxley', 'Fiction'),
                ('Animal Farm', 'George Orwell', 'Classic'),
                ('Lord of the Flies', 'William Golding', 'Classic'),
                ('Jane Eyre', 'Charlotte Bronte', 'Romance'),
                ('Wuthering Heights', 'Emily Bronte', 'Romance'),
                ('Little Women', 'Louisa May Alcott', 'Classic'),
                ('Moby Dick', 'Herman Melville', 'Adventure'),
                ('War and Peace', 'Leo Tolstoy', 'Classic'),
                ('Crime and Punishment', 'Fyodor Dostoevsky', 'Classic'),
                ('The Brothers Karamazov', 'Fyodor Dostoevsky', 'Classic'),
                ('Anna Karenina', 'Leo Tolstoy', 'Classic'),
                ('Don Quixote', 'Miguel de Cervantes', 'Classic'),
                ('Ulysses', 'James Joyce', 'Classic'),
                ('One Hundred Years of Solitude', 'Gabriel Garcia Marquez', 'Fiction'),
                ('The Great Expectations', 'Charles Dickens', 'Classic'),
                ('Frankenstein', 'Mary Shelley', 'Classic'),
                ('Dracula', 'Bram Stoker', 'Classic'),
                ('The Picture of Dorian Gray', 'Oscar Wilde', 'Classic'),
                ('Les Misérables', 'Victor Hugo', 'Classic'),
                
                # --- FANTASY & SCI-FI ---
                ('Harry Potter and the Sorcerer\'s Stone', 'J.K. Rowling', 'Fantasy'),
                ('Harry Potter and the Chamber of Secrets', 'J.K. Rowling', 'Fantasy'),
                ('Harry Potter and the Prisoner of Azkaban', 'J.K. Rowling', 'Fantasy'),
                ('The Hobbit', 'J.R.R. Tolkien', 'Fantasy'),
                ('The Fellowship of the Ring', 'J.R.R. Tolkien', 'Fantasy'),
                ('The Two Towers', 'J.R.R. Tolkien', 'Fantasy'),
                ('The Return of the King', 'J.R.R. Tolkien', 'Fantasy'),
                ('Dune', 'Frank Herbert', 'Sci-Fi'),
                ('Ender\'s Game', 'Orson Scott Card', 'Sci-Fi'),
                ('The Hitchhiker\'s Guide to the Galaxy', 'Douglas Adams', 'Sci-Fi'),
                ('Fahrenheit 451', 'Ray Bradbury', 'Sci-Fi'),
                ('The Hunger Games', 'Suzanne Collins', 'Sci-Fi'),
                ('Catching Fire', 'Suzanne Collins', 'Sci-Fi'),
                ('Mockingjay', 'Suzanne Collins', 'Sci-Fi'),
                ('A Game of Thrones', 'George R.R. Martin', 'Fantasy'),
                ('A Clash of Kings', 'George R.R. Martin', 'Fantasy'),
                ('The Name of the Wind', 'Patrick Rothfuss', 'Fantasy'),
                ('Ready Player One', 'Ernest Cline', 'Sci-Fi'),
                ('The Martian', 'Andy Weir', 'Sci-Fi'),
                ('Foundation', 'Isaac Asimov', 'Sci-Fi'),
                ('Neuromancer', 'William Gibson', 'Sci-Fi'),

                # --- MYSTERY & THRILLER ---
                ('The Da Vinci Code', 'Dan Brown', 'Thriller'),
                ('Angels & Demons', 'Dan Brown', 'Thriller'),
                ('Gone Girl', 'Gillian Flynn', 'Mystery'),
                ('The Girl with the Dragon Tattoo', 'Stieg Larsson', 'Mystery'),
                ('Sherlock Holmes: Complete', 'Arthur Conan Doyle', 'Mystery'),
                ('And Then There Were None', 'Agatha Christie', 'Mystery'),
                ('Murder on the Orient Express', 'Agatha Christie', 'Mystery'),
                ('The Silent Patient', 'Alex Michaelides', 'Thriller'),
                ('The Woman in the Window', 'A.J. Finn', 'Thriller'),
                ('Big Little Lies', 'Liane Moriarty', 'Mystery'),

                # --- BUSINESS & ECONOMICS ---
                ('Rich Dad Poor Dad', 'Robert Kiyosaki', 'Business'),
                ('Think and Grow Rich', 'Napoleon Hill', 'Business'),
                ('Zero to One', 'Peter Thiel', 'Business'),
                ('The Lean Startup', 'Eric Ries', 'Business'),
                ('Good to Great', 'Jim Collins', 'Business'),
                ('Freakonomics', 'Steven Levitt', 'Economics'),
                ('Thinking, Fast and Slow', 'Daniel Kahneman', 'Psychology'),
                ('The Intelligent Investor', 'Benjamin Graham', 'Business'),
                ('Principles', 'Ray Dalio', 'Business'),
                ('Shoe Dog', 'Phil Knight', 'Biography'),

                # --- HISTORY & SCIENCE ---
                ('Sapiens: A Brief History of Humankind', 'Yuval Noah Harari', 'History'),
                ('Homo Deus', 'Yuval Noah Harari', 'History'),
                ('A Brief History of Time', 'Stephen Hawking', 'Science'),
                ('Cosmos', 'Carl Sagan', 'Science'),
                ('The Selfish Gene', 'Richard Dawkins', 'Science'),
                ('Guns, Germs, and Steel', 'Jared Diamond', 'History'),
                ('The Silk Roads', 'Peter Frankopan', 'History'),
                ('1491', 'Charles C. Mann', 'History'),
                ('Astrophysics for People in a Hurry', 'Neil deGrasse Tyson', 'Science'),
                ('Silent Spring', 'Rachel Carson', 'Science'),

                # --- BIOGRAPHY & SELF-HELP ---
                ('Steve Jobs', 'Walter Isaacson', 'Biography'),
                ('Elon Musk', 'Ashlee Vance', 'Biography'),
                ('Becoming', 'Michelle Obama', 'Biography'),
                ('The Diary of a Young Girl', 'Anne Frank', 'Biography'),
                ('Long Walk to Freedom', 'Nelson Mandela', 'Biography'),
                ('Wings of Fire', 'A.P.J. Abdul Kalam', 'Biography'),
                ('Atomic Habits', 'James Clear', 'Self-Help'),
                ('The Power of Habit', 'Charles Duhigg', 'Self-Help'),
                ('How to Win Friends and Influence People', 'Dale Carnegie', 'Self-Help'),
                ('Deep Work', 'Cal Newport', 'Self-Help'),
                ('Start with Why', 'Simon Sinek', 'Self-Help'),
                ('The 7 Habits of Highly Effective People', 'Stephen Covey', 'Self-Help'),
                ('Can\'t Hurt Me', 'David Goggins', 'Self-Help'),
                ('Educated', 'Tara Westover', 'Biography'),
                ('The Subtle Art of Not Giving a F*ck', 'Mark Manson', 'Self-Help'),
                
                # --- COOKING & ART ---
                ('Salt, Fat, Acid, Heat', 'Samin Nosrat', 'Cooking'),
                ('The Joy of Cooking', 'Irma S. Rombauer', 'Cooking'),
                ('Kitchen Confidential', 'Anthony Bourdain', 'Cooking'),
                ('The Story of Art', 'E.H. Gombrich', 'Art'),
                ('Ways of Seeing', 'John Berger', 'Art')
            ]
            conn.executemany('INSERT INTO books (title, author, category) VALUES (?, ?, ?)', books)
            conn.commit()
            print("LibraCore Database seeded with 150+ Books.")

# --- ROUTES ---

@app.route('/')
def index():
    with get_db_connection() as conn:
        # 1. Fetch Basic Stats
        total = conn.execute('SELECT count(*) FROM books').fetchone()[0]
        issued = conn.execute('SELECT count(*) FROM books WHERE status="Issued"').fetchone()[0]
        available = total - issued # Calculated field
        
        # 2. Overdue Logic
        issued_list = conn.execute('SELECT * FROM books WHERE status="Issued"').fetchall()
        today = datetime.now().date()
        overdue = 0
        fine = 0
        
        for book in issued_list:
            if book['due_date']:
                due = datetime.strptime(book['due_date'], '%Y-%m-%d').date()
                if due < today:
                    overdue += 1
                    days = (today - due).days
                    fine += (days * 10)

        # 3. Chart Data Analytics (Group by Category)
        cat_data = conn.execute('SELECT category, COUNT(*) as count FROM books GROUP BY category').fetchall()
        chart_labels = [row['category'] for row in cat_data]
        chart_values = [row['count'] for row in cat_data]

    # Language Dictionary
    lang = request.args.get('lang', 'en')
    text = {
        'en': { 'title': 'LibraCore Dashboard', 'slogan': '"The Central Hub of Knowledge"', 'total': 'Total Volumes', 'borrowed': 'Currently Borrowed', 'overdue': 'Overdue Books', 'fines': 'Total Fines', 'btn': '📚 Enter Vault & Manage Inventory' },
        'es': { 'title': 'Tablero LibraCore', 'slogan': '"El Centro del Conocimiento"', 'total': 'Volúmenes Totales', 'borrowed': 'Actualmente Prestados', 'overdue': 'Libros Vencidos', 'fines': 'Multas Totales', 'btn': '📚 Entrar y Gestionar Inventario' }
    }
    
    return render_template('index.html', 
                           total=total, issued=issued, available=available, overdue=overdue, fine=fine, 
                           t=text[lang], lang=lang,
                           chart_labels=chart_labels, chart_values=chart_values)

@app.route('/inventory')
def inventory():
    # 1. Get Filters from URL
    search_query = request.args.get('q', '')
    sort_by = request.args.get('sort', 'title')
    category_filter = request.args.get('category', '')
    status_filter = request.args.get('status', '')

    with get_db_connection() as conn:
        # 2. Build Dynamic SQL
        sql_query = 'SELECT * FROM books WHERE 1=1'
        params = []

        if search_query:
            sql_query += ' AND (title LIKE ? OR author LIKE ?)'
            params.extend(['%' + search_query + '%', '%' + search_query + '%'])

        if category_filter:
            sql_query += ' AND category = ?'
            params.append(category_filter)
        
        if status_filter:
            sql_query += ' AND status = ?'
            params.append(status_filter)

        # 3. Sorting Whitelist
        valid_sorts = {'title': 'title', 'author': 'author', 'category': 'category', 'status': 'status'}
        sort_column = valid_sorts.get(sort_by, 'title')
        sql_query += f' ORDER BY {sort_column}'

        books = conn.execute(sql_query, params).fetchall()

        # 4. Get Categories for Dropdown
        categories_data = conn.execute('SELECT DISTINCT category FROM books ORDER BY category').fetchall()
        categories = [row['category'] for row in categories_data]

    return render_template('inventory.html', books=books, categories=categories, 
                           current_sort=sort_by, current_cat=category_filter, current_stat=status_filter, current_q=search_query)

@app.route('/add_book', methods=('GET', 'POST'))
def add_book():
    if request.method == 'POST':
        with get_db_connection() as conn:
            conn.execute('INSERT INTO books (title, author, category) VALUES (?, ?, ?)', 
                         (request.form['title'], request.form['author'], request.form['category']))
            conn.commit()
        return redirect(url_for('inventory'))
    return render_template('add_book.html')

@app.route('/edit/<int:book_id>', methods=('GET', 'POST'))
def edit_book(book_id):
    with get_db_connection() as conn:
        book = conn.execute('SELECT * FROM books WHERE id = ?', (book_id,)).fetchone()
        if request.method == 'POST':
            conn.execute('UPDATE books SET title = ?, author = ?, category = ? WHERE id = ?', 
                         (request.form['title'], request.form['author'], request.form['category'], book_id))
            conn.commit()
            return redirect(url_for('inventory'))
    return render_template('edit_book.html', book=book)

@app.route('/delete/<int:book_id>')
def delete_book(book_id):
    with get_db_connection() as conn:
        conn.execute('DELETE FROM books WHERE id = ?', (book_id,))
        conn.commit()
    return redirect(url_for('inventory'))

@app.route('/issue/<int:book_id>', methods=('GET', 'POST'))
def issue_book(book_id):
    if request.method == 'POST':
        borrower = request.form['borrower']
        days = int(request.form['days'])
        issue_date = datetime.now()
        due_date = issue_date + timedelta(days=days)
        with get_db_connection() as conn:
            conn.execute('UPDATE books SET status="Issued", borrower_name=?, issue_date=?, due_date=? WHERE id=?',
                         (borrower, issue_date.strftime('%Y-%m-%d'), due_date.strftime('%Y-%m-%d'), book_id))
            conn.commit()
        return redirect(url_for('inventory'))
    return render_template('issue_modal.html', book_id=book_id)

@app.route('/issued_books')
def issued_books():
    book_list = []
    today = datetime.now().date()
    with get_db_connection() as conn:
        books = conn.execute('SELECT * FROM books WHERE status="Issued"').fetchall()
        for book in books:
            if book['due_date']:
                due_date = datetime.strptime(book['due_date'], '%Y-%m-%d').date()
                days_overdue = (today - due_date).days
                fine = max(0, days_overdue * 10)
                book_list.append({
                    'id': book['id'],
                    'title': book['title'],
                    'borrower': book['borrower_name'],
                    'issue_date': book['issue_date'], 
                    'due_date': book['due_date'],
                    'fine': fine
                })
    return render_template('issued_books.html', books=book_list)

@app.route('/return/<int:book_id>')
def return_book(book_id):
    with get_db_connection() as conn:
        conn.execute('UPDATE books SET status="Available", borrower_name=NULL, issue_date=NULL, due_date=NULL WHERE id=?', (book_id,))
        conn.commit()
    return redirect(url_for('issued_books'))

# Initialize DB
init_db()

if __name__ == '__main__':
    # SECURITY FIX: Debug mode disabled for production simulation
    app.run(debug=False)