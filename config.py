# ./config.py

"""
Configuration settings for the Marketing Automation Flask application.
Defines paths to CSV files, secret keys, and other app settings.
"""

import os


class Config:
    """
    Configuration class for Flask application.
    """
    # Secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Base directory
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Data directory for CSV files
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    
    # CSV file paths
    CUSTOMERS_CSV = os.path.join(DATA_DIR, 'customers.csv')
    SEGMENTS_CSV = os.path.join(DATA_DIR, 'segments.csv')
    CAMPAIGNS_CSV = os.path.join(DATA_DIR, 'campaigns.csv')
    EVENTS_CSV = os.path.join(DATA_DIR, 'events.csv')
    USERS_CSV = os.path.join(DATA_DIR, 'users.csv')
    
    # Hard-coded credentials for simple login (for demo purposes)
    DEFAULT_USERNAME = 'admin'
    DEFAULT_PASSWORD = 'password'
