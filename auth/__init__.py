# ./auth/__init__.py

"""
Authentication blueprint initialization.
Handles user login and logout functionality.
"""

from flask import Blueprint

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

from auth import routes
