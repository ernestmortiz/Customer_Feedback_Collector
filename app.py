'''
Ernest Ortiz
IT488 - Module 3
9/13/2025
Sprint 2 Update
'''

from flask import Flask, render_template, request, redirect, url_for
import datetime

# Create the main web app.
app = Flask(__name__)

# Sprint 2: US-04
# Define keywords and the corresponding tags.
KEYWORD_TAGS = {
    "broken": "CRITICAL",
    "error": "CRITICAL",
    "slow": "PERFORMANCE",
    "great": "POSITIVE",
    "love": "POSITIVE",
    "bad": "NEGATIVE"
}

# List will act as our simple database to store all the feedback.
feedback_list = []

# This function runs when someone visits the main homepage.
@app.route('/')
def index():
    # Shows the user the main feedback form.
    return render_template('form.html')

# This function runs when a user submits the feedback form.
@app.route('/submit', methods=['POST'])
def submit():
    # Get all the data from the form fields.
    name = request.form.get('name', 'Anonymous') # If name is empty, use 'Anonymous'.
    email = request.form.get('email')
    comment = request.form.get('comment')
    # Store the timestamp as a datetime object so we can sort it properly.
    timestamp = datetime.datetime.now()
    
    # Sprint 2: US-04
    # Scan the comment for keywords and generate tags.
    tags = []
    comment_lower = comment.lower()
    for keyword, tag in KEYWORD_TAGS.items():
        if keyword in comment_lower and tag not in tags:
            tags.append(tag)
    
    if not tags:
        tags.append("GENERAL")
    # --- End of Sprint 2 Feature ---

    # Put all the form data into a dictionary.
    feedback_entry = {
        'name': name,
        'email': email,
        'comment': comment,
        'timestamp': timestamp,
        'tags': tags # Add the list of tags
    }
    
    # Add the new feedback to our list.
    feedback_list.append(feedback_entry)
    
    # Send the user to the dashboard page to see the feedback.
    return redirect(url_for('dashboard'))

# This function runs when someone visits the '/dashboard' page.
@app.route('/dashboard')
def dashboard():
    # Sprint 2: US-03
    # Get the sort order from the URL, defaulting to 'desc'.
    sort_order = request.args.get('order', 'desc')

    # Decide if the sort should be reversed (for descending) or not.
    if sort_order == 'asc':
        reverse_sort = False
        next_order = 'desc'
    else:
        reverse_sort = True
        next_order = 'asc'

    # Sort the feedback list by timestamp using the chosen direction.
    sorted_feedback = sorted(feedback_list, key=lambda x: x['timestamp'], reverse=reverse_sort)
    # --- End of Sprint 2 Feature ---

    # Shows the dashboard page and gives it the SORTED list of feedback
    # and the next sort order for the clickable link.
    return render_template('dashboard.html', 
                           feedback_entries=sorted_feedback, 
                           next_sort_order=next_order)

# This makes the app run when the script is executed.
if __name__ == '__main__':
    app.run(debug=True)