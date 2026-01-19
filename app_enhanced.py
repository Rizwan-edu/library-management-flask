from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import sqlite3
from datetime import datetime, timedelta
import os
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import json

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

def get_db_connection():
    try:
        conn = sqlite3.connect('library.db')
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        raise

# Authentication decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Admin access required.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Enhanced database setup
def init_db():
    try:
        conn = get_db_connection()
        
        # Enhanced books table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                category TEXT,
                isbn TEXT UNIQUE,
                language TEXT DEFAULT 'English',
                publication_year INTEGER,
                rating REAL DEFAULT 0.0,
                total_copies INTEGER DEFAULT 1,
                available_copies INTEGER DEFAULT 1,
                status TEXT DEFAULT 'Available',
                borrower_name TEXT DEFAULT NULL,
                issue_date DATE DEFAULT NULL,
                due_date DATE DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Users table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                phone TEXT,
                role TEXT DEFAULT 'member',
                membership_date DATE DEFAULT CURRENT_DATE,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        
        # Reservations table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER,
                user_id INTEGER,
                reservation_date DATE DEFAULT CURRENT_DATE,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (book_id) REFERENCES books (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Reviews table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER,
                user_id INTEGER,
                rating INTEGER CHECK(rating >= 1 AND rating <= 5),
                review_text TEXT,
                review_date DATE DEFAULT CURRENT_DATE,
                FOREIGN KEY (book_id) REFERENCES books (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Transaction history
        conn.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER,
                user_id INTEGER,
                action TEXT,
                transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (book_id) REFERENCES books (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        seed_data()
    except Exception as e:
        print(f"Database initialization error: {e}")
        raise

def seed_data():
    try:
        conn = get_db_connection()
        if conn.execute('SELECT count(*) FROM books').fetchone()[0] == 0:
            # International collection with enhanced data
            books = [
                # English Literature
                ('The Great Gatsby', 'F. Scott Fitzgerald', 'Fiction', '9780743273565', 'English', 1925, 4.2),
                ('1984', 'George Orwell', 'Fiction', '9780451524935', 'English', 1949, 4.5),
                ('Pride and Prejudice', 'Jane Austen', 'Classic', '9780141439518', 'English', 1813, 4.3),
                ('To Kill a Mockingbird', 'Harper Lee', 'Classic', '9780061120084', 'English', 1960, 4.4),
                
                # Technology & Programming
                ('Python Crash Course', 'Eric Matthes', 'Technology', '9781593279288', 'English', 2019, 4.6),
                ('Clean Code', 'Robert Martin', 'Technology', '9780132350884', 'English', 2008, 4.4),
                ('JavaScript: The Good Parts', 'Douglas Crockford', 'Technology', '9780596517748', 'English', 2008, 4.2),
                ('Design Patterns', 'Gang of Four', 'Technology', '9780201633612', 'English', 1994, 4.3),
                
                # International Literature
                ('Cien años de soledad', 'Gabriel García Márquez', 'Fiction', '9788437604947', 'Spanish', 1967, 4.5),
                ('El Quijote', 'Miguel de Cervantes', 'Classic', '9788424116378', 'Spanish', 1605, 4.2),
                ('Les Misérables', 'Victor Hugo', 'Classic', '9782070409228', 'French', 1862, 4.4),
                ('Der Prozess', 'Franz Kafka', 'Fiction', '9783596294329', 'German', 1925, 4.1),
                ('Crime and Punishment', 'Fyodor Dostoevsky', 'Classic', '9780486454115', 'Russian', 1866, 4.3),
                ('Maus', 'Art Spiegelman', 'Graphic Novel', '9780394747231', 'English', 1991, 4.6),
                
                # Science & Philosophy
                ('Sapiens', 'Yuval Noah Harari', 'History', '9780062316097', 'English', 2014, 4.4),
                ('A Brief History of Time', 'Stephen Hawking', 'Science', '9780553380163', 'English', 1988, 4.2),
                ('Thinking, Fast and Slow', 'Daniel Kahneman', 'Psychology', '9780374533557', 'English', 2011, 4.3),
                ('The Art of War', 'Sun Tzu', 'Philosophy', '9781590302255', 'Chinese', -500, 4.1),
                
                # Fantasy & Sci-Fi
                ('The Hobbit', 'J.R.R. Tolkien', 'Fantasy', '9780547928227', 'English', 1937, 4.5),
                ('Dune', 'Frank Herbert', 'Sci-Fi', '9780441172719', 'English', 1965, 4.3),
                ('Harry Potter and the Philosopher\'s Stone', 'J.K. Rowling', 'Fantasy', '9780747532699', 'English', 1997, 4.6),
                ('The Hitchhiker\'s Guide to the Galaxy', 'Douglas Adams', 'Sci-Fi', '9780345391803', 'English', 1979, 4.4),
                
                # Contemporary Fiction
                ('The Kite Runner', 'Khaled Hosseini', 'Fiction', '9781594631931', 'English', 2003, 4.3),
                ('Life of Pi', 'Yann Martel', 'Fiction', '9780156027328', 'English', 2001, 4.0),
                ('The Alchemist', 'Paulo Coelho', 'Fiction', '9780062315007', 'Portuguese', 1988, 4.2),
                ('Norwegian Wood', 'Haruki Murakami', 'Fiction', '9780375704024', 'Japanese', 1987, 4.1),
                
                # Biography & Self-Help
                ('Steve Jobs', 'Walter Isaacson', 'Biography', '9781451648539', 'English', 2011, 4.4),
                ('Atomic Habits', 'James Clear', 'Self-Help', '9780735211292', 'English', 2018, 4.5),
                ('Educated', 'Tara Westover', 'Biography', '9780399590504', 'English', 2018, 4.4)
            ]
            conn.executemany('INSERT INTO books (title, author, category, isbn, language, publication_year, rating) VALUES (?, ?, ?, ?, ?, ?, ?)', books)
            conn.commit()
            print("LibraCore Database seeded with international collection.")
            
        # Create admin user
        admin_exists = conn.execute('SELECT count(*) FROM users WHERE username = ?', ('admin',)).fetchone()[0]
        if admin_exists == 0:
            admin_hash = generate_password_hash('admin123')
            conn.execute('INSERT INTO users (username, email, password_hash, full_name, role) VALUES (?, ?, ?, ?, ?)',
                        ('admin', 'admin@library.com', admin_hash, 'System Administrator', 'admin'))
            conn.commit()
            print("Admin user created: admin/admin123")
            
        conn.close()
    except Exception as e:
        print(f"Seeding error: {e}")
        raise

# --- ROUTES ---

@app.route('/')
def index():
    try:
        conn = get_db_connection()
        
        # Get comprehensive statistics
        stats = conn.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'Issued' THEN 1 ELSE 0 END) as issued,
                COUNT(DISTINCT language) as languages,
                COUNT(DISTINCT category) as categories
            FROM books
        ''').fetchone()
        
        # Calculate overdue and fines
        today = datetime.now().date()
        overdue_books = conn.execute('''
            SELECT COUNT(*) as overdue, 
                   SUM((julianday('now') - julianday(due_date)) * 10) as total_fines
            FROM books 
            WHERE status = 'Issued' AND due_date < date('now')
        ''').fetchone()
        
        # Recent activities
        recent_books = conn.execute('''
            SELECT title, author, category, rating 
            FROM books 
            ORDER BY created_at DESC 
            LIMIT 5
        ''').fetchall()
        
        # Popular categories
        categories = conn.execute('''
            SELECT category, COUNT(*) as count 
            FROM books 
            GROUP BY category 
            ORDER BY count DESC 
            LIMIT 6
        ''').fetchall()
        
        conn.close()
        
        # Enhanced multilingual support
        lang = request.args.get('lang', 'en')
        translations = {
            'en': {
                'title': 'LibraCore International',
                'slogan': '"Global Knowledge Hub"',
                'total': 'Total Books',
                'issued': 'Books Issued',
                'overdue': 'Overdue',
                'fines': 'Total Fines',
                'languages': 'Languages',
                'categories': 'Categories',
                'recent': 'Recent Additions',
                'popular': 'Popular Categories',
                'btn_inventory': '📚 Browse Collection',
                'btn_analytics': '📊 Analytics',
                'btn_users': '👥 Users'
            },
            'es': {
                'title': 'LibraCore Internacional',
                'slogan': '"Centro Global del Conocimiento"',
                'total': 'Total de Libros',
                'issued': 'Libros Prestados',
                'overdue': 'Vencidos',
                'fines': 'Multas Totales',
                'languages': 'Idiomas',
                'categories': 'Categorías',
                'recent': 'Adiciones Recientes',
                'popular': 'Categorías Populares',
                'btn_inventory': '📚 Explorar Colección',
                'btn_analytics': '📊 Analíticas',
                'btn_users': '👥 Usuarios'
            },
            'fr': {
                'title': 'LibraCore International',
                'slogan': '"Hub Mondial du Savoir"',
                'total': 'Total des Livres',
                'issued': 'Livres Empruntés',
                'overdue': 'En Retard',
                'fines': 'Amendes Totales',
                'languages': 'Langues',
                'categories': 'Catégories',
                'recent': 'Ajouts Récents',
                'popular': 'Catégories Populaires',
                'btn_inventory': '📚 Parcourir Collection',
                'btn_analytics': '📊 Analytiques',
                'btn_users': '👥 Utilisateurs'
            }
        }
        
        return render_template('index.html', 
                             stats=stats,
                             overdue=overdue_books['overdue'] or 0,
                             fines=overdue_books['total_fines'] or 0,
                             recent_books=recent_books,
                             categories=categories,
                             t=translations.get(lang, translations['en']),
                             lang=lang,
                             user_logged_in='user_id' in session)
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return render_template('error.html')

@app.route('/inventory')
def inventory():
    try:
        conn = get_db_connection()
        
        # Advanced filtering
        search = request.args.get('q', '')
        category = request.args.get('category', '')
        language = request.args.get('language', '')
        sort_by = request.args.get('sort', 'title')
        
        query = 'SELECT * FROM books WHERE 1=1'
        params = []
        
        if search:
            query += ' AND (title LIKE ? OR author LIKE ? OR isbn LIKE ?)'
            params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])
        
        if category:
            query += ' AND category = ?'
            params.append(category)
            
        if language:
            query += ' AND language = ?'
            params.append(language)
        
        # Sorting
        valid_sorts = ['title', 'author', 'category', 'rating', 'publication_year']
        if sort_by in valid_sorts:
            query += f' ORDER BY {sort_by}'
        
        books = conn.execute(query, params).fetchall()
        
        # Get filter options
        categories = conn.execute('SELECT DISTINCT category FROM books ORDER BY category').fetchall()
        languages = conn.execute('SELECT DISTINCT language FROM books ORDER BY language').fetchall()
        
        conn.close()
        
        return render_template('inventory.html', 
                             books=books, 
                             categories=categories,
                             languages=languages,
                             current_search=search,
                             current_category=category,
                             current_language=language,
                             current_sort=sort_by)
    except Exception as e:
        flash(f'Error loading inventory: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Username and password are required.', 'error')
            return render_template('login.html')
        
        try:
            conn = get_db_connection()
            user = conn.execute('SELECT * FROM users WHERE username = ? AND is_active = 1', (username,)).fetchone()
            conn.close()
            
            if user and check_password_hash(user['password_hash'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
                session['full_name'] = user['full_name']
                flash(f'Welcome back, {user["full_name"]}!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password.', 'error')
        except Exception as e:
            flash(f'Login error: {str(e)}', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        
        if not all([username, email, password, full_name]):
            flash('All fields except phone are required.', 'error')
            return render_template('register.html')
        
        try:
            conn = get_db_connection()
            
            # Check if user exists
            existing = conn.execute('SELECT id FROM users WHERE username = ? OR email = ?', (username, email)).fetchone()
            if existing:
                flash('Username or email already exists.', 'error')
                conn.close()
                return render_template('register.html')
            
            password_hash = generate_password_hash(password)
            conn.execute('''
                INSERT INTO users (username, email, password_hash, full_name, phone) 
                VALUES (?, ?, ?, ?, ?)
            ''', (username, email, password_hash, full_name, phone))
            conn.commit()
            conn.close()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Registration error: {str(e)}', 'error')
    
    return render_template('register.html')

@app.route('/analytics')
@admin_required
def analytics():
    try:
        conn = get_db_connection()
        
        # Comprehensive analytics
        analytics_data = {
            'books_by_category': conn.execute('''
                SELECT category, COUNT(*) as count FROM books GROUP BY category ORDER BY count DESC
            ''').fetchall(),
            'books_by_language': conn.execute('''
                SELECT language, COUNT(*) as count FROM books GROUP BY language ORDER BY count DESC
            ''').fetchall(),
            'monthly_transactions': conn.execute('''
                SELECT strftime('%Y-%m', transaction_date) as month, 
                       COUNT(*) as count,
                       action
                FROM transactions 
                WHERE transaction_date >= date('now', '-12 months')
                GROUP BY month, action 
                ORDER BY month DESC
            ''').fetchall(),
            'top_rated_books': conn.execute('''
                SELECT title, author, rating FROM books 
                WHERE rating > 0 
                ORDER BY rating DESC 
                LIMIT 10
            ''').fetchall(),
            'overdue_stats': conn.execute('''
                SELECT COUNT(*) as count, 
                       AVG(julianday('now') - julianday(due_date)) as avg_days_overdue
                FROM books 
                WHERE status = 'Issued' AND due_date < date('now')
            ''').fetchone()
        }
        
        conn.close()
        return render_template('analytics.html', data=analytics_data)
    except Exception as e:
        flash(f'Error loading analytics: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/search')
def api_search():
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify([])
    
    try:
        conn = get_db_connection()
        results = conn.execute('''
            SELECT id, title, author, category, rating 
            FROM books 
            WHERE title LIKE ? OR author LIKE ? 
            LIMIT 10
        ''', (f'%{query}%', f'%{query}%')).fetchall()
        conn.close()
        
        return jsonify([dict(row) for row in results])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Initialize database
init_db()

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))