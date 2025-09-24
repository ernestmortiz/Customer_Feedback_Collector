'''
Ernest Ortiz
IT488 - Module 5
9/26/2025
Sprint 4
'''

import sqlite3

# Connects to the database file. It will be created if it doesn't exist.
conn = sqlite3.connect('feedback.db')
cursor = conn.cursor()

# Creates the feedback table
# This schema matches the data we collect from the form.
# TEXT is for strings, DATETIME for timestamps.
# The 'tags' column will store the list of tags as a JSON string.
cursor.execute('''
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    comment TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    tags TEXT
);
''')

# Creates the users table
# This will store our user credentials for the login feature.
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);
''')

# Adds default users so we can log in
# 'INSERT OR IGNORE' prevents an error if the users already exist.
try:
    cursor.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", ('admin', 'password123'))
    cursor.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", ('support', 'supportpass'))
    print("Default users created or already exist.")
except sqlite3.IntegrityError:
    print("Users already exist.")

# Save (commit) the changes and close the connection.
conn.commit()
conn.close()

print("Database 'feedback.db' initialized successfully.")