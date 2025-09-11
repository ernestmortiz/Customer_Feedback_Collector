'''
Ernest Ortiz
IT488 - Module 2
9/9/2025
'''

from flask import Flask, render_template, request, redirect, url_for
import datetime

# Create the main web app.
app = Flask(__name__)

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
    # Get the current time and format it as a string.
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Put all the form data into a dictionary.
    feedback_entry = {
        'name': name,
        'email': email,
        'comment': comment,
        'timestamp': timestamp
    }
    
    # Add the new feedback to the top of our list.
    feedback_list.insert(0, feedback_entry)
    
    # Send the user to the dashboard page to see the feedback.
    return redirect(url_for('dashboard'))

# This function runs when someone visits the '/dashboard' page.
@app.route('/dashboard')
def dashboard():
    # Shows the dashboard page and gives it the full list of feedback
    # so it can be displayed in a table.
    return render_template('dashboard.html', feedback_entries=feedback_list)

# This makes the app run when the script is executed.
if __name__ == '__main__':
    app.run(debug=True)