# ./marketing/routes.py

"""
Marketing module routes.
Handles dashboard, segmentation, campaigns, and analytics views.
"""

from flask import render_template, redirect, url_for, request, flash
from marketing import marketing_bp
from auth.forms import login_required
from marketing.segmentation import (
    load_customers, load_segments, get_segment_by_id,
    filter_customers_by_segment, create_segment, count_customers_in_segment
)
from marketing.campaigns import (
    load_campaigns, get_campaign_by_id, create_campaign,
    get_campaign_customers, send_campaign
)
from marketing.analytics import get_campaign_metrics, get_all_campaign_metrics, get_overall_metrics


@marketing_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Main dashboard view after login.
    """
    # Get summary stats
    customers = load_customers()
    segments = load_segments()
    campaigns = load_campaigns()
    
    stats = {
        'total_customers': len(customers),
        'total_segments': len(segments),
        'total_campaigns': len(campaigns),
        'active_campaigns': len([c for c in campaigns if c['status'] == 'sent'])
    }
    
    return render_template('dashboard.html', stats=stats)


# ============================================================================
# SEGMENTATION ROUTES
# ============================================================================

@marketing_bp.route('/segments')
@login_required
def segments():
    """
    List all customer segments.
    """
    segments = load_segments()
    
    # Add customer count to each segment
    for segment in segments:
        segment['customer_count'] = count_customers_in_segment(segment)
    
    return render_template('segments.html', segments=segments)


@marketing_bp.route('/segments/new', methods=['GET', 'POST'])
@login_required
def new_segment():
    """
    Create a new customer segment.
    GET: Display form
    POST: Save segment
    """
    if request.method == 'POST':
        segment_name = request.form.get('segment_name', '').strip()
        
        if not segment_name:
            flash('Segment name is required', 'error')
            return render_template('segment_form.html')
        
        # Build rules dictionary
        rules = {}
        
        min_age = request.form.get('min_age', '').strip()
        if min_age:
            rules['min_age'] = int(min_age)
        
        max_age = request.form.get('max_age', '').strip()
        if max_age:
            rules['max_age'] = int(max_age)
        
        location = request.form.get('location', '').strip()
        if location:
            rules['location'] = location
        
        min_total_spent = request.form.get('min_total_spent', '').strip()
        if min_total_spent:
            rules['min_total_spent'] = float(min_total_spent)
        
        # Create segment
        segment_id = create_segment(segment_name, rules)
        flash(f'Segment "{segment_name}" created successfully!', 'success')
        return redirect(url_for('marketing.segments'))
    
    return render_template('segment_form.html')


@marketing_bp.route('/segments/<segment_id>')
@login_required
def segment_detail(segment_id):
    """
    Show details of a specific segment and its matching customers.
    """
    segment = get_segment_by_id(segment_id)
    
    if not segment:
        flash('Segment not found', 'error')
        return redirect(url_for('marketing.segments'))
    
    # Get matching customers
    all_customers = load_customers()
    customers = filter_customers_by_segment(all_customers, segment['rules'])
    
    return render_template('segment_detail.html', segment=segment, customers=customers)


# ============================================================================
# CAMPAIGN ROUTES
# ============================================================================

@marketing_bp.route('/campaigns')
@login_required
def campaigns():
    """
    List all marketing campaigns.
    """
    campaigns = load_campaigns()
    segments = load_segments()
    
    # Create segment lookup for display
    segment_lookup = {s['segment_id']: s['segment_name'] for s in segments}
    
    # Add segment name to each campaign
    for campaign in campaigns:
        campaign['segment_name'] = segment_lookup.get(campaign['segment_id'], 'Unknown')
    
    return render_template('campaigns.html', campaigns=campaigns)


@marketing_bp.route('/campaigns/new', methods=['GET', 'POST'])
@login_required
def new_campaign():
    """
    Create a new marketing campaign.
    GET: Display form
    POST: Save campaign
    """
    segments = load_segments()
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        segment_id = request.form.get('segment_id', '').strip()
        start_date = request.form.get('start_date', '').strip()
        subject = request.form.get('subject', '').strip()
        body = request.form.get('body', '').strip()
        
        # Validate
        if not all([name, segment_id, start_date, subject, body]):
            flash('All fields are required', 'error')
            return render_template('campaign_form.html', segments=segments)
        
        # Create campaign
        campaign_id = create_campaign(name, segment_id, start_date, subject, body)
        flash(f'Campaign "{name}" created successfully!', 'success')
        return redirect(url_for('marketing.campaigns'))
    
    return render_template('campaign_form.html', segments=segments)


@marketing_bp.route('/campaigns/<campaign_id>')
@login_required
def campaign_detail(campaign_id):
    """
    Show details of a specific campaign.
    """
    campaign = get_campaign_by_id(campaign_id)
    
    if not campaign:
        flash('Campaign not found', 'error')
        return redirect(url_for('marketing.campaigns'))
    
    # Get segment and customers
    segment = get_segment_by_id(campaign['segment_id'])
    customers = get_campaign_customers(campaign_id)
    
    # Get metrics if campaign has been sent
    metrics = None
    if campaign['status'] == 'sent':
        metrics = get_campaign_metrics(campaign_id)
    
    return render_template('campaign_detail.html', 
                         campaign=campaign, 
                         segment=segment,
                         customers=customers,
                         metrics=metrics)


@marketing_bp.route('/campaigns/<campaign_id>/send', methods=['POST'])
@login_required
def send_campaign_route(campaign_id):
    """
    Send a campaign to its target segment.
    """
    campaign = get_campaign_by_id(campaign_id)
    
    if not campaign:
        flash('Campaign not found', 'error')
        return redirect(url_for('marketing.campaigns'))
    
    if campaign['status'] != 'draft':
        flash('Campaign has already been sent', 'warning')
        return redirect(url_for('marketing.campaign_detail', campaign_id=campaign_id))
    
    # Send campaign
    count = send_campaign(campaign_id)
    flash(f'Campaign sent to {count} customers!', 'success')
    
    return redirect(url_for('marketing.campaign_detail', campaign_id=campaign_id))


# ============================================================================
# ANALYTICS ROUTES
# ============================================================================

@marketing_bp.route('/analytics')
@login_required
def analytics():
    """
    Show marketing analytics for all campaigns.
    """
    # Get metrics for all campaigns
    campaign_metrics = get_all_campaign_metrics()
    
    # Get overall metrics
    overall = get_overall_metrics()
    
    return render_template('analytics.html', 
                         campaign_metrics=campaign_metrics,
                         overall=overall)


@marketing_bp.route('/analytics/<campaign_id>')
@login_required
def campaign_analytics(campaign_id):
    """
    Show detailed analytics for a specific campaign.
    """
    campaign = get_campaign_by_id(campaign_id)
    
    if not campaign:
        flash('Campaign not found', 'error')
        return redirect(url_for('marketing.analytics'))
    
    metrics = get_campaign_metrics(campaign_id)
    
    return render_template('campaign_analytics.html', 
                         campaign=campaign,
                         metrics=metrics)
