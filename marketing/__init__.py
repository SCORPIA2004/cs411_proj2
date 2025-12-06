# ./marketing/__init__.py

"""
Marketing automation blueprint initialization.
Handles customer segmentation, campaign management, and analytics.
"""

from flask import Blueprint

marketing_bp = Blueprint('marketing', __name__, url_prefix='')

from marketing import routes
