'''
Ernest Ortiz
IT488 - Module 5
9/26/2025
Sprint 4
'''

from flask import Flask, render_template, request, redirect, url_for, session, flash
import datetime
import sqlite3
import json

app = Flask(__name__)
app.secret_key = 'a_very_secret_key_for_this_project'
DATABASE = 'feedback.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def is_logged_in():
    return 'username' in session

KEYWORD_TAGS = {
    "broken": "CRITICAL", "error": "CRITICAL",
    "slow": "PERFORMANCE", "great": "POSITIVE", "love": "POSITIVE"
}

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name', 'Anonymous')
    email = request.form.get('email')
    comment = request.form.get('comment')
    timestamp = datetime.datetime.now()

    tags = []
    comment_lower = comment.lower()
    for keyword, tag in KEYWORD_TAGS.items():
        if keyword in comment_lower and tag not in tags:
            tags.append(tag)
    if not tags: tags.append("GENERAL")
    
    tags_json = json.dumps(tags)

    db = get_db()
    db.execute('INSERT INTO feedback (name, email, comment, timestamp, tags) VALUES (?, ?, ?, ?, ?)',
               (name, email, comment, timestamp, tags_json))
    db.commit()
    db.close()
    
    return redirect(url_for('thank_you'))

@app.route('/thank-you')
def thank_you():
    return render_template('thank-you.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        db.close()

        if user:
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if not is_logged_in():
        return redirect(url_for('login'))

    sort_order = request.args.get('order', 'desc')
    filter_tag = request.args.get('tag')
    
    db = get_db()
    query = 'SELECT * FROM feedback'
    params = []

    if filter_tag:
        query += ' WHERE tags LIKE ?'
        params.append(f'%"{filter_tag}"%')

    query += f' ORDER BY timestamp {sort_order.upper()}'

    feedback_rows = db.execute(query, params).fetchall()
    db.close()

    feedback_entries = []
    for row in feedback_rows:
        entry = dict(row)
        entry['tags'] = json.loads(entry['tags'])
        # FIX FOR ISSUE #2: Convert timestamp string from DB back to datetime object
        if isinstance(entry['timestamp'], str):
             entry['timestamp'] = datetime.datetime.fromisoformat(entry['timestamp'])
        feedback_entries.append(entry)

    next_order = 'asc' if sort_order == 'desc' else 'desc'

    return render_template('dashboard.html', 
                           feedback_entries=feedback_entries, 
                           next_sort_order=next_order,
                           current_filter=filter_tag)

# --- USER MANAGEMENT ROUTES ---

@app.route('/users')
def manage_users():
    # FIX FOR ISSUE #1: Correct and explicit security check
    if not is_logged_in() or session.get('username') != 'admin':
        flash('You must be an admin to manage users.', 'error')
        return redirect(url_for('dashboard'))
    
    db = get_db()
    users = db.execute('SELECT id, username FROM users').fetchall()
    db.close()
    return render_template('users.html', users=users)

@app.route('/users/add', methods=['POST'])
def add_user():
    if not is_logged_in() or session.get('username') != 'admin':
        return redirect(url_for('login'))

    username = request.form.get('username')
    password = request.form.get('password')

    if username and password:
        db = get_db()
        try:
            db.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            db.commit()
        except sqlite3.IntegrityError:
            flash('Username already exists.', 'error')
        finally:
            db.close()

    return redirect(url_for('manage_users'))

@app.route('/users/delete/<int:user_id>')
def delete_user(user_id):
    if not is_logged_in() or session.get('username') != 'admin':
        return redirect(url_for('login'))
    
    db = get_db()
    user_to_delete = db.execute('SELECT username FROM users WHERE id = ?', (user_id,)).fetchone()
    if user_to_delete and user_to_delete['username'] != 'admin':
        db.execute('DELETE FROM users WHERE id = ?', (user_id,))
        db.commit()
    db.close()

    return redirect(url_for('manage_users'))

# --- FIX FOR ISSUE #3: ADD THE MISSING DELETE_FEEDBACK FUNCTION ---
@app.route('/delete/<int:feedback_id>')
def delete_feedback(feedback_id):
    if not is_logged_in():
        return redirect(url_for('login'))

    db = get_db()
    db.execute('DELETE FROM feedback WHERE id = ?', (feedback_id,))
    db.commit()
    db.close()

    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)