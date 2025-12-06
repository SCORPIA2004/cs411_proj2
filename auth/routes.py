# ./auth/routes.py

"""
Authentication routes for login and logout.
Implements simple session-based authentication.
"""

from flask import render_template, redirect, url_for, request, session, flash, current_app
from auth import auth_bp
import csv
import os


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login.
    GET: Display login form
    POST: Validate credentials and create session
    """
    # If already logged in, redirect to dashboard
    if 'user_id' in session:
        return redirect(url_for('marketing.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Check credentials
        if authenticate_user(username, password):
            # Store user in session
            session['user_id'] = username
            session['username'] = username
            flash('Login successful!', 'success')
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            return redirect(next_page or url_for('marketing.dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """
    Handle user logout.
    Clear session and redirect to login page.
    """
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


def authenticate_user(username, password):
    """
    Authenticate user credentials.
    Checks against default credentials or users CSV file.
    
    Args:
        username: The username to check
        password: The password to check
    
    Returns:
        bool: True if credentials are valid, False otherwise
    """
    # Check against default credentials
    if (username == current_app.config['DEFAULT_USERNAME'] and 
        password == current_app.config['DEFAULT_PASSWORD']):
        return True
    
    # Optionally check against users CSV if it exists
    users_csv = current_app.config['USERS_CSV']
    if os.path.exists(users_csv):
        try:
            with open(users_csv, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['username'] == username and row['password'] == password:
                        return True
        except Exception as e:
            print(f"Error reading users CSV: {e}")
    
    return False
