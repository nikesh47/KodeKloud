from flask import Flask, render_template, request, redirect, url_for, flash, session, g
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Database configuration
DATABASE = 'task_manager.db'

def get_db():
    """Get database connection"""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_db(exception):
    """Close database connection"""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize database with tables"""
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL DEFAULT 'Not started',
                assigned_user_id INTEGER NOT NULL,
                created_by_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (assigned_user_id) REFERENCES users (id),
                FOREIGN KEY (created_by_id) REFERENCES users (id)
            )
        ''')
        
        db.commit()
        
        # Create default admin user if it doesn't exist
        cursor.execute('SELECT id FROM users WHERE username = ?', ('admin',))
        if not cursor.fetchone():
            admin_password = generate_password_hash('admin123')
            cursor.execute('''
                INSERT INTO users (username, email, password_hash)
                VALUES (?, ?, ?)
            ''', ('admin', 'admin@example.com', admin_password))
            db.commit()

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Main page - redirect to dashboard if logged in, otherwise to login"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        cursor = db.cursor()
        user = cursor.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')
        
        db = get_db()
        cursor = db.cursor()
        
        # Check if username or email already exists
        existing_user = cursor.execute(
            'SELECT id FROM users WHERE username = ? OR email = ?', 
            (username, email)
        ).fetchone()
        
        if existing_user:
            flash('Username or email already exists.', 'error')
            return render_template('register.html')
        
        # Create new user
        password_hash = generate_password_hash(password)
        cursor.execute('''
            INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)
        ''', (username, email, password_hash))
        db.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard with task list and filters"""
    db = get_db()
    cursor = db.cursor()
    
    # Get filter parameters
    status_filter = request.args.get('status', '')
    assignee_filter = request.args.get('assignee', '')
    
    # Build query with filters
    query = '''
        SELECT t.*, u1.username as assigned_username, u2.username as created_by_username
        FROM tasks t
        JOIN users u1 ON t.assigned_user_id = u1.id
        JOIN users u2 ON t.created_by_id = u2.id
        WHERE 1=1
    '''
    params = []
    
    if status_filter:
        query += ' AND t.status = ?'
        params.append(status_filter)
    
    if assignee_filter:
        query += ' AND t.assigned_user_id = ?'
        params.append(assignee_filter)
    
    query += ' ORDER BY t.created_at DESC'
    
    tasks = cursor.execute(query, params).fetchall()
    
    # Get all users for assignee filter
    users = cursor.execute('SELECT id, username FROM users ORDER BY username').fetchall()
    
    # Get task counts by status
    status_counts = cursor.execute('''
        SELECT status, COUNT(*) as count
        FROM tasks
        GROUP BY status
    ''').fetchall()
    
    return render_template('dashboard.html', 
                         tasks=tasks, 
                         users=users, 
                         status_counts=status_counts,
                         status_filter=status_filter,
                         assignee_filter=assignee_filter)

@app.route('/tasks/new', methods=['GET', 'POST'])
@login_required
def new_task():
    """Create new task"""
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        status = request.form['status']
        assigned_user_id = request.form['assigned_user_id']
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO tasks (title, description, status, assigned_user_id, created_by_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, description, status, assigned_user_id, session['user_id']))
        db.commit()
        
        flash('Task created successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    # Get all users for assignee dropdown
    db = get_db()
    users = db.execute('SELECT id, username FROM users ORDER BY username').fetchall()
    
    status_options = ['Not started', 'In progress', 'Complete', 'Blocked', 'Closed']
    return render_template('task_form.html', 
                         task=None, 
                         users=users, 
                         status_options=status_options,
                         action='Create')

@app.route('/tasks/<int:task_id>')
@login_required
def view_task(task_id):
    """View single task"""
    db = get_db()
    cursor = db.cursor()
    task = cursor.execute('''
        SELECT t.*, u1.username as assigned_username, u2.username as created_by_username
        FROM tasks t
        JOIN users u1 ON t.assigned_user_id = u1.id
        JOIN users u2 ON t.created_by_id = u2.id
        WHERE t.id = ?
    ''', (task_id,)).fetchone()
    
    if not task:
        flash('Task not found.', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('task_detail.html', task=task)

@app.route('/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    """Edit existing task"""
    db = get_db()
    cursor = db.cursor()
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        status = request.form['status']
        assigned_user_id = request.form['assigned_user_id']
        
        cursor.execute('''
            UPDATE tasks 
            SET title = ?, description = ?, status = ?, assigned_user_id = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (title, description, status, assigned_user_id, task_id))
        db.commit()
        
        flash('Task updated successfully!', 'success')
        return redirect(url_for('view_task', task_id=task_id))
    
    # Get task details
    task = cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()
    if not task:
        flash('Task not found.', 'error')
        return redirect(url_for('dashboard'))
    
    # Get all users for assignee dropdown
    users = cursor.execute('SELECT id, username FROM users ORDER BY username').fetchall()
    
    status_options = ['Not started', 'In progress', 'Complete', 'Blocked', 'Closed']
    return render_template('task_form.html', 
                         task=task, 
                         users=users, 
                         status_options=status_options,
                         action='Update')

@app.route('/tasks/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    """Delete task"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    db.commit()
    
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
