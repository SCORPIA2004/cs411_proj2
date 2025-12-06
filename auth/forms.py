# ./auth/forms.py

"""
Authentication helper functions and decorators.
Provides login_required decorator for protecting routes.
"""

from functools import wraps
from flask import session, redirect, url_for, request


def login_required(f):
    """
    Decorator to require login for a route.
    Redirects to login page if user is not authenticated.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # Store the page user was trying to access
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function
