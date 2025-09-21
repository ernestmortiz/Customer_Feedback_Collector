'''
Ernest Ortiz
IT488 - Module 4
9/23/2025
Sprint 3 Update - Security & Confirmation
'''

from flask import Flask, render_template, request, redirect, url_for, session, flash
import datetime

# Create the main web app.
app = Flask(__name__)
# A secret key is required by Flask to securely manage user sessions.
# This should be a long, random string in a real application.
app.secret_key = 'a_very_secret_key_for_this_project'

# --- US-06: Simple User Store ---
# In a real application, this would be a database with hashed passwords.
# For this project, a simple dictionary is sufficient for authentication.
VALID_USERS = {
    "admin": "password123",
    "support": "supportpass"
}

# This list acts as our simple database.
feedback_list = []

# Keywords for automatic tagging.
KEYWORD_TAGS = {
    "broken": "CRITICAL", "error": "CRITICAL", "slow": "PERFORMANCE",
    "great": "POSITIVE", "love": "POSITIVE", "bad": "NEGATIVE"
}

# --- Helper function to check if a user is logged in ---
def is_logged_in():
    # Checks if 'username' is stored in the session cookie.
    return 'username' in session

### --- Main Application Routes --- ###

@app.route('/')
def index():
    # Shows the main feedback form to the customer.
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    # Get all the data from the form fields.
    name = request.form.get('name', 'Anonymous')
    email = request.form.get('email')
    comment = request.form.get('comment')
    timestamp = datetime.datetime.now()
    
    # Scan the comment for keywords to generate tags.
    tags = []
    comment_lower = comment.lower()
    for keyword, tag in KEYWORD_TAGS.items():
        if keyword in comment_lower and tag not in tags:
            tags.append(tag)
    if not tags:
        tags.append("GENERAL")

    # Store the feedback entry as a dictionary.
    feedback_entry = {
        'name': name, 'email': email, 'comment': comment,
        'timestamp': timestamp, 'tags': tags
    }
    
    feedback_list.append(feedback_entry)
    
    # --- US-07: Redirect to a confirmation page ---
    # Instead of showing the dashboard, we redirect to a simple thank-you page.
    return redirect(url_for('thank_you'))

### --- US-07: New Route for Confirmation Page --- ###
@app.route('/thank-you')
def thank_you():
    # This page confirms to the customer that their feedback was received.
    # It also provides a link to submit another response.
    return render_template('thank-you.html')

### --- US-06: New Routes and Logic for Secure Access --- ###

@app.route('/login', methods=['GET', 'POST'])
def login():
    # This route handles both displaying the login form (GET) and processing it (POST).
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if the username exists and the password is correct.
        if username in VALID_USERS and VALID_USERS[username] == password:
            session['username'] = username # Store the username in the session.
            return redirect(url_for('dashboard')) # Redirect to the dashboard on success.
        else:
            # If login fails, 'flash' an error message to the login page.
            flash('Invalid username or password.')
            return redirect(url_for('login'))
            
    # For a GET request, just show the login page.
    return render_template('login.html')

@app.route('/logout')
def logout():
    # US-06: The logout link on the dashboard points here.
    session.pop('username', None) # Remove the username from the session.
    return redirect(url_for('login')) # Redirect the user to the login page.

@app.route('/dashboard')
def dashboard():
    # --- US-06: Protect this route ---
    # Before displaying the dashboard, check if the user is logged in.
    if not is_logged_in():
        # If not, redirect them to the login page.
        return redirect(url_for('login'))
    
    # --- Existing Dashboard Logic (Sorting/Filtering) ---
    sort_order = request.args.get('order', 'desc')
    filter_tag = request.args.get('tag')
    
    display_list = feedback_list
    if filter_tag:
        display_list = [entry for entry in feedback_list if filter_tag in entry['tags']]
    
    reverse_sort = sort_order == 'desc'
    sorted_feedback = sorted(display_list, key=lambda x: x['timestamp'], reverse=reverse_sort)
    
    next_order = 'asc' if sort_order == 'desc' else 'desc'

    return render_template('dashboard.html', 
                           feedback_entries=sorted_feedback, 
                           next_sort_order=next_order,
                           current_filter=filter_tag)

# This makes the app run when the script is executed.
if __name__ == '__main__':
    app.run(debug=True)