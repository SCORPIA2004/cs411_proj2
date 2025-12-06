# ./app.py

"""
Flask application entry point for Marketing Automation CRM module.
This file creates the Flask app, registers blueprints, and runs the application.
"""

import os
from flask import Flask, redirect, url_for
from config import Config


def create_app(config_class=Config):
    """
    Application factory function.
    Creates and configures the Flask application.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Ensure data directory exists
    os.makedirs(app.config['DATA_DIR'], exist_ok=True)
    
    # Register blueprints
    from auth import auth_bp
    from marketing import marketing_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(marketing_bp)
    
    # Root route redirects to dashboard
    @app.route('/')
    def index():
        return redirect(url_for('marketing.dashboard'))
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
