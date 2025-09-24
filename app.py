'''
Ernest Ortiz
IT488 - Module 5
9/26/2025
Sprint 4
'''

from flask import Flask, render_template, request, redirect, url_for, session, flash
import datetime
import sqlite3
import json # Used to store the list of tags as a string in the database

app = Flask(__name__)
app.secret_key = 'a_very_secret_key_for_this_project'
DATABASE = 'feedback.db'

# --- Database Helper Function ---
# This function helps us connect to the database easily.
def get_db():
    conn = sqlite3.connect(DATABASE)
    # This line lets us access columns by name (like a dictionary).
    conn.row_factory = sqlite3.Row 
    return conn

# --- Security Helper Function ---
def is_logged_in():
    return 'username' in session

# --- Keyword Definitions (No change) ---
KEYWORD_TAGS = {
    "broken": "CRITICAL", "error": "CRITICAL", "slow": "PERFORMANCE",
    "great": "POSITIVE", "love": "POSITIVE", "bad": "NEGATIVE"
}

# --- REMOVED THE IN-MEMORY feedback_list ---

# --- ROUTES ---

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
    if not tags:
        tags.append("GENERAL")
    
    # Convert the Python list of tags into a JSON string to store in the database.
    tags_json = json.dumps(tags)

    # --- US-08: DATABASE UPDATE ---
    # Connect to the database and insert the new record.
    db = get_db()
    db.execute('INSERT INTO feedback (name, email, comment, timestamp, tags) VALUES (?, ?, ?, ?, ?)',
               (name, email, comment, timestamp, tags_json))
    db.commit() # Save the changes
    db.close()
    # --- END OF UPDATE ---
    
    return redirect(url_for('thank_you'))

@app.route('/thank-you')
def thank_you():
    return render_template('thank-you.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # --- US-08: DATABASE UPDATE ---
        # Check credentials against the 'users' table in the database.
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ? AND password = ?', 
                          (username, password)).fetchone()
        db.close()
        # --- END OF UPDATE ---

        if user:
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.')
            return redirect(url_for('login'))
            
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
    
    # --- US-08: DATABASE UPDATE ---
    # Build the SQL query dynamically based on filters and sorting.
    db = get_db()
    query = 'SELECT * FROM feedback'
    params = []

    if filter_tag:
        # The LIKE operator helps us find the tag within the JSON string.
        query += ' WHERE tags LIKE ?'
        params.append(f'%"{filter_tag}"%') 

    # Add the sorting order to the query.
    query += f' ORDER BY timestamp {sort_order.upper()}'

    feedback_rows = db.execute(query, params).fetchall()
    db.close()

    # Convert the database rows into a list of dictionaries.
    # Also, convert the 'tags' JSON string back into a Python list.
    feedback_entries = []
    for row in feedback_rows:
        entry = dict(row) # Convert the row object to a dictionary
        entry['tags'] = json.loads(entry['tags']) # Parse the JSON string
        feedback_entries.append(entry)
    # --- END OF UPDATE ---
    
    next_order = 'asc' if sort_order == 'desc' else 'desc'

    return render_template('dashboard.html', 
                           feedback_entries=feedback_entries, 
                           next_sort_order=next_order,
                           current_filter=filter_tag)

if __name__ == '__main__':
    app.run(debug=True)