# ./marketing/segmentation.py

"""
Customer segmentation logic.
Handles loading customers, creating segments, and filtering customers by segment rules.
"""

import csv
import json
import os
from datetime import datetime
from flask import current_app


def load_customers():
    """
    Load all customers from CSV file.
    
    Returns:
        list: List of customer dictionaries
    """
    customers = []
    csv_path = current_app.config['CUSTOMERS_CSV']
    
    if not os.path.exists(csv_path):
        return customers
    
    try:
        with open(csv_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert numeric fields
                row['age'] = int(row['age']) if row.get('age') else 0
                row['total_spent'] = float(row['total_spent']) if row.get('total_spent') else 0.0
                customers.append(row)
    except Exception as e:
        print(f"Error loading customers: {e}")
    
    return customers


def load_segments():
    """
    Load all segments from CSV file.
    
    Returns:
        list: List of segment dictionaries with parsed rules
    """
    segments = []
    csv_path = current_app.config['SEGMENTS_CSV']
    
    if not os.path.exists(csv_path):
        return segments
    
    try:
        with open(csv_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Parse JSON rules
                try:
                    row['rules'] = json.loads(row['rules_json'])
                except:
                    row['rules'] = {}
                segments.append(row)
    except Exception as e:
        print(f"Error loading segments: {e}")
    
    return segments


def get_segment_by_id(segment_id):
    """
    Get a specific segment by ID.
    
    Args:
        segment_id: The segment ID to find
    
    Returns:
        dict or None: Segment dictionary if found, None otherwise
    """
    segments = load_segments()
    for segment in segments:
        if segment['segment_id'] == str(segment_id):
            return segment
    return None


def filter_customers_by_segment(customers, rules):
    """
    Filter customers based on segment rules.
    
    Args:
        customers: List of customer dictionaries
        rules: Dictionary of filtering rules
    
    Returns:
        list: Filtered list of customers matching the rules
    """
    filtered = []
    
    for customer in customers:
        # Check each rule
        if not match_customer_rules(customer, rules):
            continue
        filtered.append(customer)
    
    return filtered


def match_customer_rules(customer, rules):
    """
    Check if a customer matches all segment rules.
    
    Args:
        customer: Customer dictionary
        rules: Dictionary of filtering rules
    
    Returns:
        bool: True if customer matches all rules, False otherwise
    """
    # Check min_age
    if 'min_age' in rules and rules['min_age']:
        if customer['age'] < int(rules['min_age']):
            return False
    
    # Check max_age
    if 'max_age' in rules and rules['max_age']:
        if customer['age'] > int(rules['max_age']):
            return False
    
    # Check location (case-insensitive partial match)
    if 'location' in rules and rules['location']:
        if rules['location'].lower() not in customer.get('location', '').lower():
            return False
    
    # Check min_total_spent
    if 'min_total_spent' in rules and rules['min_total_spent']:
        if customer['total_spent'] < float(rules['min_total_spent']):
            return False
    
    return True


def create_segment(segment_name, rules):
    """
    Create a new customer segment.
    
    Args:
        segment_name: Name of the segment
        rules: Dictionary of filtering rules
    
    Returns:
        str: The new segment ID
    """
    csv_path = current_app.config['SEGMENTS_CSV']
    
    # Generate new segment ID
    segments = load_segments()
    new_id = str(len(segments) + 1)
    
    # Prepare row
    row = {
        'segment_id': new_id,
        'segment_name': segment_name,
        'rules_json': json.dumps(rules)
    }
    
    # Write to CSV
    file_exists = os.path.exists(csv_path)
    
    with open(csv_path, 'a', newline='', encoding='utf-8') as f:
        fieldnames = ['segment_id', 'segment_name', 'rules_json']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        # Write header if file is new
        if not file_exists:
            writer.writeheader()
        
        writer.writerow(row)
    
    return new_id


def count_customers_in_segment(segment):
    """
    Count how many customers match a segment's rules.
    
    Args:
        segment: Segment dictionary with rules
    
    Returns:
        int: Number of matching customers
    """
    customers = load_customers()
    filtered = filter_customers_by_segment(customers, segment['rules'])
    return len(filtered)
