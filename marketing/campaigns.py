# ./marketing/campaigns.py

"""
Campaign management logic.
Handles creating campaigns, sending campaigns, and simulating marketing events.
"""

import csv
import json
import os
import random
from datetime import datetime
from flask import current_app
from marketing.segmentation import load_customers, get_segment_by_id, filter_customers_by_segment


def load_campaigns():
    """
    Load all campaigns from CSV file.
    
    Returns:
        list: List of campaign dictionaries
    """
    campaigns = []
    csv_path = current_app.config['CAMPAIGNS_CSV']
    
    if not os.path.exists(csv_path):
        return campaigns
    
    try:
        with open(csv_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                campaigns.append(row)
    except Exception as e:
        print(f"Error loading campaigns: {e}")
    
    return campaigns


def get_campaign_by_id(campaign_id):
    """
    Get a specific campaign by ID.
    
    Args:
        campaign_id: The campaign ID to find
    
    Returns:
        dict or None: Campaign dictionary if found, None otherwise
    """
    campaigns = load_campaigns()
    for campaign in campaigns:
        if campaign['campaign_id'] == str(campaign_id):
            return campaign
    return None


def create_campaign(name, segment_id, start_date, subject, body):
    """
    Create a new marketing campaign.
    
    Args:
        name: Campaign name
        segment_id: Target segment ID
        start_date: Campaign start date
        subject: Email subject
        body: Email body
    
    Returns:
        str: The new campaign ID
    """
    csv_path = current_app.config['CAMPAIGNS_CSV']
    
    # Generate new campaign ID
    campaigns = load_campaigns()
    new_id = str(len(campaigns) + 1)
    
    # Prepare row
    row = {
        'campaign_id': new_id,
        'name': name,
        'segment_id': segment_id,
        'start_date': start_date,
        'status': 'draft',
        'subject': subject,
        'body': body
    }
    
    # Write to CSV
    file_exists = os.path.exists(csv_path)
    
    with open(csv_path, 'a', newline='', encoding='utf-8') as f:
        fieldnames = ['campaign_id', 'name', 'segment_id', 'start_date', 'status', 'subject', 'body']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        # Write header if file is new
        if not file_exists:
            writer.writeheader()
        
        writer.writerow(row)
    
    return new_id


def get_campaign_customers(campaign_id):
    """
    Get list of customers targeted by a campaign.
    
    Args:
        campaign_id: The campaign ID
    
    Returns:
        list: List of customer dictionaries
    """
    campaign = get_campaign_by_id(campaign_id)
    if not campaign:
        return []
    
    segment = get_segment_by_id(campaign['segment_id'])
    if not segment:
        return []
    
    customers = load_customers()
    return filter_customers_by_segment(customers, segment['rules'])


def send_campaign(campaign_id):
    """
    Send a campaign to all customers in its target segment.
    Creates "sent" events and simulates additional engagement events.
    
    Args:
        campaign_id: The campaign ID to send
    
    Returns:
        int: Number of customers the campaign was sent to
    """
    # Get campaign and target customers
    campaign = get_campaign_by_id(campaign_id)
    if not campaign or campaign['status'] != 'draft':
        return 0
    
    customers = get_campaign_customers(campaign_id)
    
    # Generate events for each customer
    for customer in customers:
        # Always create a "sent" event
        create_event(campaign_id, customer['customer_id'], 'sent')
        
        # Simulate opened event (70% chance)
        if random.random() < 0.7:
            create_event(campaign_id, customer['customer_id'], 'opened')
            
            # Simulate clicked event (40% of those who opened)
            if random.random() < 0.4:
                create_event(campaign_id, customer['customer_id'], 'clicked')
                
                # Simulate conversion event (30% of those who clicked)
                if random.random() < 0.3:
                    create_event(campaign_id, customer['customer_id'], 'converted')
    
    # Update campaign status to "sent"
    update_campaign_status(campaign_id, 'sent')
    
    return len(customers)


def create_event(campaign_id, customer_id, event_type):
    """
    Create a marketing event.
    
    Args:
        campaign_id: The campaign ID
        customer_id: The customer ID
        event_type: Type of event (sent, opened, clicked, converted)
    """
    csv_path = current_app.config['EVENTS_CSV']
    
    # Generate event ID
    event_id = generate_event_id()
    
    # Prepare row
    row = {
        'event_id': event_id,
        'campaign_id': campaign_id,
        'customer_id': customer_id,
        'event_type': event_type,
        'timestamp': datetime.now().isoformat()
    }
    
    # Write to CSV
    file_exists = os.path.exists(csv_path)
    
    with open(csv_path, 'a', newline='', encoding='utf-8') as f:
        fieldnames = ['event_id', 'campaign_id', 'customer_id', 'event_type', 'timestamp']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        # Write header if file is new
        if not file_exists:
            writer.writeheader()
        
        writer.writerow(row)


def generate_event_id():
    """
    Generate a unique event ID.
    
    Returns:
        str: New event ID
    """
    csv_path = current_app.config['EVENTS_CSV']
    
    if not os.path.exists(csv_path):
        return '1'
    
    try:
        with open(csv_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if rows:
                return str(len(rows) + 1)
    except:
        pass
    
    return '1'


def update_campaign_status(campaign_id, new_status):
    """
    Update the status of a campaign.
    
    Args:
        campaign_id: The campaign ID
        new_status: New status value
    """
    csv_path = current_app.config['CAMPAIGNS_CSV']
    
    if not os.path.exists(csv_path):
        return
    
    # Read all campaigns
    campaigns = []
    with open(csv_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['campaign_id'] == str(campaign_id):
                row['status'] = new_status
            campaigns.append(row)
    
    # Write back all campaigns
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['campaign_id', 'name', 'segment_id', 'start_date', 'status', 'subject', 'body']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(campaigns)
