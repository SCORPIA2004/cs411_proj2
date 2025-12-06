# ./marketing/analytics.py

"""
Marketing analytics logic.
Computes campaign performance metrics based on events.
"""

import csv
import os
from flask import current_app
from marketing.campaigns import load_campaigns


def load_events():
    """
    Load all events from CSV file.
    
    Returns:
        list: List of event dictionaries
    """
    events = []
    csv_path = current_app.config['EVENTS_CSV']
    
    if not os.path.exists(csv_path):
        return events
    
    try:
        with open(csv_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                events.append(row)
    except Exception as e:
        print(f"Error loading events: {e}")
    
    return events


def get_campaign_metrics(campaign_id):
    """
    Calculate metrics for a specific campaign.
    
    Args:
        campaign_id: The campaign ID
    
    Returns:
        dict: Metrics dictionary with counts and rates
    """
    events = load_events()
    
    # Filter events for this campaign
    campaign_events = [e for e in events if e['campaign_id'] == str(campaign_id)]
    
    # Count each event type
    sent_count = len([e for e in campaign_events if e['event_type'] == 'sent'])
    opened_count = len([e for e in campaign_events if e['event_type'] == 'opened'])
    clicked_count = len([e for e in campaign_events if e['event_type'] == 'clicked'])
    converted_count = len([e for e in campaign_events if e['event_type'] == 'converted'])
    
    # Calculate rates (avoid division by zero)
    open_rate = (opened_count / sent_count * 100) if sent_count > 0 else 0
    click_rate = (clicked_count / sent_count * 100) if sent_count > 0 else 0
    conversion_rate = (converted_count / sent_count * 100) if sent_count > 0 else 0
    
    return {
        'campaign_id': campaign_id,
        'sent': sent_count,
        'opened': opened_count,
        'clicked': clicked_count,
        'converted': converted_count,
        'open_rate': round(open_rate, 2),
        'click_rate': round(click_rate, 2),
        'conversion_rate': round(conversion_rate, 2)
    }


def get_all_campaign_metrics():
    """
    Calculate metrics for all campaigns.
    
    Returns:
        list: List of metrics dictionaries, one per campaign
    """
    campaigns = load_campaigns()
    metrics_list = []
    
    for campaign in campaigns:
        metrics = get_campaign_metrics(campaign['campaign_id'])
        metrics['campaign_name'] = campaign['name']
        metrics['status'] = campaign['status']
        metrics_list.append(metrics)
    
    return metrics_list


def get_overall_metrics():
    """
    Calculate overall metrics across all campaigns.
    
    Returns:
        dict: Aggregate metrics across all campaigns
    """
    events = load_events()
    
    sent_count = len([e for e in events if e['event_type'] == 'sent'])
    opened_count = len([e for e in events if e['event_type'] == 'opened'])
    clicked_count = len([e for e in events if e['event_type'] == 'clicked'])
    converted_count = len([e for e in events if e['event_type'] == 'converted'])
    
    open_rate = (opened_count / sent_count * 100) if sent_count > 0 else 0
    click_rate = (clicked_count / sent_count * 100) if sent_count > 0 else 0
    conversion_rate = (converted_count / sent_count * 100) if sent_count > 0 else 0
    
    return {
        'total_sent': sent_count,
        'total_opened': opened_count,
        'total_clicked': clicked_count,
        'total_converted': converted_count,
        'overall_open_rate': round(open_rate, 2),
        'overall_click_rate': round(click_rate, 2),
        'overall_conversion_rate': round(conversion_rate, 2)
    }
