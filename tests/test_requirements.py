# ./tests/test_requirements.py

"""
Comprehensive tests covering all functional and quality attribute requirements
from the Marketing Automation module specification.

Requirements covered:
- 3.1 Functional Requirements (Segmentation, Campaign, Analytics, Security)
- 3.2 Quality Attribute Requirements (Scalability, Performance, Reliability, Security)
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import tempfile
import shutil
import csv
import time
from unittest.mock import patch
from app import create_app
from config import Config


class TestConfig(Config):
    """Test configuration with temporary CSV files."""
    TESTING = True
    SECRET_KEY = 'test-secret-key'
    
    def __init__(self):
        super().__init__()
        self.temp_dir = tempfile.mkdtemp()
        self.DATA_DIR = self.temp_dir
        self.CUSTOMERS_CSV = os.path.join(self.temp_dir, 'customers.csv')
        self.SEGMENTS_CSV = os.path.join(self.temp_dir, 'segments.csv')
        self.CAMPAIGNS_CSV = os.path.join(self.temp_dir, 'campaigns.csv')
        self.EVENTS_CSV = os.path.join(self.temp_dir, 'events.csv')
        self.USERS_CSV = os.path.join(self.temp_dir, 'users.csv')


# =============================================================================
# 3.1 FUNCTIONAL REQUIREMENTS TESTS
# =============================================================================

class TestCustomerSegmentation(unittest.TestCase):
    """
    FR-1: Customer Segmentation
    - Create and manage segments based on profile data (age, location, etc.)
    - Store segment definitions persistently for reuse
    """
    
    def setUp(self):
        self.test_config = TestConfig()
        self.app = create_app(self.test_config)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self._create_test_customers()
    
    def tearDown(self):
        self.app_context.pop()
        if os.path.exists(self.test_config.temp_dir):
            shutil.rmtree(self.test_config.temp_dir)
    
    def _create_test_customers(self):
        with open(self.test_config.CUSTOMERS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'customer_id', 'name', 'email', 'age', 'location', 'total_spent', 'last_purchase_date'
            ])
            writer.writeheader()
            writer.writerows([
                {'customer_id': '1', 'name': 'Alice', 'email': 'alice@test.com', 'age': '28', 'location': 'Ankara', 'total_spent': '1500', 'last_purchase_date': '2024-11-01'},
                {'customer_id': '2', 'name': 'Bob', 'email': 'bob@test.com', 'age': '35', 'location': 'Istanbul', 'total_spent': '3000', 'last_purchase_date': '2024-11-15'},
                {'customer_id': '3', 'name': 'Charlie', 'email': 'charlie@test.com', 'age': '45', 'location': 'Izmir', 'total_spent': '500', 'last_purchase_date': '2024-10-20'},
            ])
    
    def test_create_segment_by_age(self):
        """FR-1.1: Create segment based on age profile data."""
        from marketing.segmentation import create_segment, get_segment_by_id
        
        segment_id = create_segment('Young Adults', {'min_age': 25, 'max_age': 35})
        
        segment = get_segment_by_id(segment_id)
        self.assertIsNotNone(segment)
        self.assertEqual(segment['segment_name'], 'Young Adults')
        self.assertEqual(segment['rules']['min_age'], 25)
        self.assertEqual(segment['rules']['max_age'], 35)
    
    def test_create_segment_by_location(self):
        """FR-1.1: Create segment based on location profile data."""
        from marketing.segmentation import create_segment, get_segment_by_id, filter_customers_by_segment, load_customers
        
        segment_id = create_segment('Ankara Customers', {'location': 'Ankara'})
        segment = get_segment_by_id(segment_id)
        
        customers = load_customers()
        filtered = filter_customers_by_segment(customers, segment['rules'])
        
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['location'], 'Ankara')
    
    def test_create_segment_by_spending(self):
        """FR-1.1: Create segment based on spending profile data."""
        from marketing.segmentation import create_segment, filter_customers_by_segment, load_customers, get_segment_by_id
        
        segment_id = create_segment('High Spenders', {'min_total_spent': 2000})
        segment = get_segment_by_id(segment_id)
        
        customers = load_customers()
        filtered = filter_customers_by_segment(customers, segment['rules'])
        
        self.assertEqual(len(filtered), 1)
        self.assertTrue(filtered[0]['total_spent'] >= 2000)
    
    def test_segment_persistence(self):
        """FR-1.2: Segment definitions stored persistently for reuse."""
        from marketing.segmentation import create_segment, load_segments
        
        # Create segment
        create_segment('Persistent Segment', {'min_age': 30, 'location': 'Istanbul'})
        
        # Verify persisted in CSV
        self.assertTrue(os.path.exists(self.test_config.SEGMENTS_CSV))
        
        # Reload and verify
        segments = load_segments()
        self.assertEqual(len(segments), 1)
        self.assertEqual(segments[0]['segment_name'], 'Persistent Segment')
    
    def test_segment_combined_criteria(self):
        """FR-1.1: Segment with multiple profile criteria."""
        from marketing.segmentation import create_segment, filter_customers_by_segment, load_customers, get_segment_by_id
        
        segment_id = create_segment('Premium Istanbul', {
            'location': 'Istanbul',
            'min_total_spent': 2000,
            'min_age': 30
        })
        segment = get_segment_by_id(segment_id)
        
        customers = load_customers()
        filtered = filter_customers_by_segment(customers, segment['rules'])
        
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['name'], 'Bob')


class TestCampaignManagement(unittest.TestCase):
    """
    FR-2: Campaign Management
    - Create and manage marketing campaigns
    - Target specific customer segments
    - Record customer interactions (sent, opened, clicked, converted)
    """
    
    def setUp(self):
        self.test_config = TestConfig()
        self.app = create_app(self.test_config)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self._create_test_data()
    
    def tearDown(self):
        self.app_context.pop()
        if os.path.exists(self.test_config.temp_dir):
            shutil.rmtree(self.test_config.temp_dir)
    
    def _create_test_data(self):
        # Customers
        with open(self.test_config.CUSTOMERS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'customer_id', 'name', 'email', 'age', 'location', 'total_spent', 'last_purchase_date'
            ])
            writer.writeheader()
            writer.writerows([
                {'customer_id': '1', 'name': 'Alice', 'email': 'alice@test.com', 'age': '30', 'location': 'Ankara', 'total_spent': '2000', 'last_purchase_date': '2024-11-01'},
                {'customer_id': '2', 'name': 'Bob', 'email': 'bob@test.com', 'age': '35', 'location': 'Ankara', 'total_spent': '3000', 'last_purchase_date': '2024-11-15'},
            ])
        
        # Segment
        with open(self.test_config.SEGMENTS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['segment_id', 'segment_name', 'rules_json'])
            writer.writeheader()
            writer.writerow({
                'segment_id': '1',
                'segment_name': 'Ankara Adults',
                'rules_json': '{"location": "Ankara", "min_age": 25}'
            })
    
    def test_create_campaign(self):
        """FR-2.1: Create a marketing campaign."""
        from marketing.campaigns import create_campaign, get_campaign_by_id
        
        campaign_id = create_campaign(
            name='Winter Sale 2024',
            segment_id='1',
            start_date='2024-12-01',
            subject='Exclusive Winter Offers!',
            body='Check out our amazing winter deals...'
        )
        
        campaign = get_campaign_by_id(campaign_id)
        self.assertIsNotNone(campaign)
        self.assertEqual(campaign['name'], 'Winter Sale 2024')
        self.assertEqual(campaign['status'], 'draft')
    
    def test_campaign_targets_segment(self):
        """FR-2.2: Campaign targets specific customer segment."""
        from marketing.campaigns import create_campaign, get_campaign_customers
        
        campaign_id = create_campaign(
            name='Ankara Campaign',
            segment_id='1',
            start_date='2024-12-01',
            subject='Hello Ankara!',
            body='Special offers for Ankara...'
        )
        
        customers = get_campaign_customers(campaign_id)
        
        self.assertEqual(len(customers), 2)
        self.assertTrue(all(c['location'] == 'Ankara' for c in customers))
    
    def test_campaign_records_sent_events(self):
        """FR-2.3: Record 'sent' interaction events."""
        from marketing.campaigns import create_campaign, send_campaign
        from marketing.analytics import load_events
        
        campaign_id = create_campaign('Test', '1', '2024-12-01', 'Subject', 'Body')
        send_campaign(campaign_id)
        
        events = load_events()
        sent_events = [e for e in events if e['event_type'] == 'sent']
        
        self.assertEqual(len(sent_events), 2)
    
    def test_campaign_records_opened_events(self):
        """FR-2.3: Record 'opened' interaction events."""
        from marketing.campaigns import create_campaign, send_campaign, create_event
        from marketing.analytics import load_events
        
        campaign_id = create_campaign('Test', '1', '2024-12-01', 'Subject', 'Body')
        
        # Manually create opened event to test functionality (avoid randomness)
        create_event(campaign_id, '1', 'sent')
        create_event(campaign_id, '1', 'opened')
        
        events = load_events()
        opened_events = [e for e in events if e['event_type'] == 'opened']
        
        # Verify opened events can be recorded
        self.assertGreaterEqual(len(opened_events), 1)
    
    def test_campaign_records_clicked_events(self):
        """FR-2.3: Record 'clicked' interaction events."""
        from marketing.campaigns import create_campaign, create_event
        from marketing.analytics import load_events
        
        campaign_id = create_campaign('Test', '1', '2024-12-01', 'Subject', 'Body')
        
        # Manually create clicked event to test functionality
        create_event(campaign_id, '1', 'sent')
        create_event(campaign_id, '1', 'opened')
        create_event(campaign_id, '1', 'clicked')
        
        events = load_events()
        clicked_events = [e for e in events if e['event_type'] == 'clicked']
        
        # Verify clicked events can be recorded
        self.assertGreaterEqual(len(clicked_events), 1)
    
    def test_campaign_records_converted_events(self):
        """FR-2.3: Record 'converted' interaction events."""
        from marketing.campaigns import create_campaign, create_event
        from marketing.analytics import load_events
        
        campaign_id = create_campaign('Test', '1', '2024-12-01', 'Subject', 'Body')
        
        # Manually create converted event to test functionality
        create_event(campaign_id, '1', 'sent')
        create_event(campaign_id, '1', 'opened')
        create_event(campaign_id, '1', 'clicked')
        create_event(campaign_id, '1', 'converted')
        
        events = load_events()
        converted_events = [e for e in events if e['event_type'] == 'converted']
        
        # Verify converted events can be recorded
        self.assertGreaterEqual(len(converted_events), 1)
    
    def test_campaign_status_updates(self):
        """FR-2.1: Campaign status transitions (draft -> sent)."""
        from marketing.campaigns import create_campaign, send_campaign, get_campaign_by_id
        
        campaign_id = create_campaign('Test', '1', '2024-12-01', 'Subject', 'Body')
        
        # Initially draft
        campaign = get_campaign_by_id(campaign_id)
        self.assertEqual(campaign['status'], 'draft')
        
        # After sending
        send_campaign(campaign_id)
        campaign = get_campaign_by_id(campaign_id)
        self.assertEqual(campaign['status'], 'sent')


class TestMarketingAnalytics(unittest.TestCase):
    """
    FR-3: Marketing Analytics
    - Aggregate customer engagement data
    - Compute metrics (open rate, CTR, conversion rate)
    - Provide dashboard for campaign-level and system-wide analytics
    """
    
    def setUp(self):
        self.test_config = TestConfig()
        self.app = create_app(self.test_config)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self._create_test_data()
    
    def tearDown(self):
        self.app_context.pop()
        if os.path.exists(self.test_config.temp_dir):
            shutil.rmtree(self.test_config.temp_dir)
    
    def _create_test_data(self):
        # Campaign
        with open(self.test_config.CAMPAIGNS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'campaign_id', 'name', 'segment_id', 'start_date', 'status', 'subject', 'body'
            ])
            writer.writeheader()
            writer.writerows([
                {'campaign_id': '1', 'name': 'Campaign A', 'segment_id': '1', 'start_date': '2024-12-01', 'status': 'sent', 'subject': 'A', 'body': 'A'},
                {'campaign_id': '2', 'name': 'Campaign B', 'segment_id': '1', 'start_date': '2024-12-02', 'status': 'sent', 'subject': 'B', 'body': 'B'},
            ])
        
        # Events: Campaign 1 - 100 sent, 60 opened, 30 clicked, 10 converted
        events = []
        for i in range(100):
            events.append({'event_id': f'e{i}', 'campaign_id': '1', 'customer_id': str(i), 'event_type': 'sent', 'timestamp': '2024-12-01T10:00:00'})
        for i in range(60):
            events.append({'event_id': f'o{i}', 'campaign_id': '1', 'customer_id': str(i), 'event_type': 'opened', 'timestamp': '2024-12-01T11:00:00'})
        for i in range(30):
            events.append({'event_id': f'c{i}', 'campaign_id': '1', 'customer_id': str(i), 'event_type': 'clicked', 'timestamp': '2024-12-01T12:00:00'})
        for i in range(10):
            events.append({'event_id': f'v{i}', 'campaign_id': '1', 'customer_id': str(i), 'event_type': 'converted', 'timestamp': '2024-12-01T13:00:00'})
        
        with open(self.test_config.EVENTS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['event_id', 'campaign_id', 'customer_id', 'event_type', 'timestamp'])
            writer.writeheader()
            writer.writerows(events)
    
    def test_aggregate_engagement_data(self):
        """FR-3.1: Aggregate customer engagement data."""
        from marketing.analytics import get_campaign_metrics
        
        metrics = get_campaign_metrics('1')
        
        self.assertEqual(metrics['sent'], 100)
        self.assertEqual(metrics['opened'], 60)
        self.assertEqual(metrics['clicked'], 30)
        self.assertEqual(metrics['converted'], 10)
    
    def test_compute_open_rate(self):
        """FR-3.2: Compute open rate metric."""
        from marketing.analytics import get_campaign_metrics
        
        metrics = get_campaign_metrics('1')
        
        # 60/100 = 60%
        self.assertEqual(metrics['open_rate'], 60.0)
    
    def test_compute_click_through_rate(self):
        """FR-3.2: Compute click-through rate (CTR) metric."""
        from marketing.analytics import get_campaign_metrics
        
        metrics = get_campaign_metrics('1')
        
        # 30/100 = 30%
        self.assertEqual(metrics['click_rate'], 30.0)
    
    def test_compute_conversion_rate(self):
        """FR-3.2: Compute conversion rate metric."""
        from marketing.analytics import get_campaign_metrics
        
        metrics = get_campaign_metrics('1')
        
        # 10/100 = 10%
        self.assertEqual(metrics['conversion_rate'], 10.0)
    
    def test_campaign_level_analytics(self):
        """FR-3.3: Campaign-level analytics."""
        from marketing.analytics import get_all_campaign_metrics
        
        all_metrics = get_all_campaign_metrics()
        
        self.assertEqual(len(all_metrics), 2)
        campaign_a = next(m for m in all_metrics if m['campaign_name'] == 'Campaign A')
        self.assertEqual(campaign_a['sent'], 100)
    
    def test_system_wide_analytics(self):
        """FR-3.3: System-wide aggregate analytics."""
        from marketing.analytics import get_overall_metrics
        
        overall = get_overall_metrics()
        
        self.assertEqual(overall['total_sent'], 100)
        self.assertEqual(overall['total_opened'], 60)
        self.assertEqual(overall['overall_open_rate'], 60.0)


class TestSecureWebInterface(unittest.TestCase):
    """
    FR-5: Secure Web Interface
    - Authorized users can log in and access features
    - Unauthorized users prevented from accessing functionalities
    """
    
    def setUp(self):
        self.test_config = TestConfig()
        self.app = create_app(self.test_config)
        self.client = self.app.test_client()
    
    def tearDown(self):
        if os.path.exists(self.test_config.temp_dir):
            shutil.rmtree(self.test_config.temp_dir)
    
    def test_login_with_valid_credentials(self):
        """FR-5.1: Authorized users can log in."""
        response = self.client.post('/auth/login', data={
            'username': 'admin',
            'password': 'password'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard', response.data)
    
    def test_login_with_invalid_credentials(self):
        """FR-5.2: Invalid credentials rejected."""
        response = self.client.post('/auth/login', data={
            'username': 'wrong',
            'password': 'wrong'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid', response.data)
    
    def test_unauthorized_access_dashboard_redirect(self):
        """FR-5.2: Unauthorized access to dashboard redirects to login."""
        response = self.client.get('/dashboard', follow_redirects=False)
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login', response.location)
    
    def test_unauthorized_access_segments_redirect(self):
        """FR-5.2: Unauthorized access to segments redirects to login."""
        response = self.client.get('/segments', follow_redirects=False)
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login', response.location)
    
    def test_unauthorized_access_campaigns_redirect(self):
        """FR-5.2: Unauthorized access to campaigns redirects to login."""
        response = self.client.get('/campaigns', follow_redirects=False)
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login', response.location)
    
    def test_unauthorized_access_analytics_redirect(self):
        """FR-5.2: Unauthorized access to analytics redirects to login."""
        response = self.client.get('/analytics', follow_redirects=False)
        
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login', response.location)
    
    def test_logout_clears_session(self):
        """FR-5.1: Logout clears session."""
        # Login first
        self.client.post('/auth/login', data={
            'username': 'admin',
            'password': 'password'
        })
        
        # Logout
        response = self.client.get('/auth/logout', follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'logged out', response.data)
        
        # Verify can't access protected page
        response = self.client.get('/dashboard', follow_redirects=False)
        self.assertEqual(response.status_code, 302)


# =============================================================================
# 3.2 QUALITY ATTRIBUTE REQUIREMENTS TESTS
# =============================================================================

class TestScalability(unittest.TestCase):
    """
    QA-1: Scalability
    - Handle large customer datasets
    - Process high campaign volumes
    """
    
    def setUp(self):
        self.test_config = TestConfig()
        self.app = create_app(self.test_config)
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        self.app_context.pop()
        if os.path.exists(self.test_config.temp_dir):
            shutil.rmtree(self.test_config.temp_dir)
    
    def test_large_customer_dataset(self):
        """QA-1.1: System handles large customer datasets (1000+ customers)."""
        # Create 1000 customers
        with open(self.test_config.CUSTOMERS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'customer_id', 'name', 'email', 'age', 'location', 'total_spent', 'last_purchase_date'
            ])
            writer.writeheader()
            for i in range(1000):
                writer.writerow({
                    'customer_id': str(i),
                    'name': f'Customer {i}',
                    'email': f'customer{i}@test.com',
                    'age': str(20 + (i % 50)),
                    'location': ['Ankara', 'Istanbul', 'Izmir'][i % 3],
                    'total_spent': str(100 * (i % 100)),
                    'last_purchase_date': '2024-11-01'
                })
        
        from marketing.segmentation import load_customers, filter_customers_by_segment
        
        start = time.time()
        customers = load_customers()
        filtered = filter_customers_by_segment(customers, {'min_age': 40, 'location': 'Ankara'})
        elapsed = time.time() - start
        
        self.assertEqual(len(customers), 1000)
        self.assertGreater(len(filtered), 0)
        self.assertLess(elapsed, 2.0)  # Should complete within 2 seconds
    
    def test_high_event_volume(self):
        """QA-1.2: System processes high event volumes."""
        # Create 10,000 events
        with open(self.test_config.CAMPAIGNS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'campaign_id', 'name', 'segment_id', 'start_date', 'status', 'subject', 'body'
            ])
            writer.writeheader()
            writer.writerow({'campaign_id': '1', 'name': 'Big Campaign', 'segment_id': '1', 
                           'start_date': '2024-12-01', 'status': 'sent', 'subject': 'A', 'body': 'A'})
        
        with open(self.test_config.EVENTS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['event_id', 'campaign_id', 'customer_id', 'event_type', 'timestamp'])
            writer.writeheader()
            for i in range(10000):
                writer.writerow({
                    'event_id': str(i),
                    'campaign_id': '1',
                    'customer_id': str(i % 1000),
                    'event_type': ['sent', 'opened', 'clicked', 'converted'][i % 4],
                    'timestamp': '2024-12-01T10:00:00'
                })
        
        from marketing.analytics import get_campaign_metrics
        
        start = time.time()
        metrics = get_campaign_metrics('1')
        elapsed = time.time() - start
        
        self.assertEqual(metrics['sent'], 2500)  # 10000/4 events of each type
        self.assertLess(elapsed, 3.0)  # Should complete within 3 seconds


class TestPerformance(unittest.TestCase):
    """
    QA-4: Performance
    - UI actions respond within 2-3 seconds
    - Analytics dashboard loads within 3 seconds
    """
    
    def setUp(self):
        self.test_config = TestConfig()
        self.app = create_app(self.test_config)
        self.client = self.app.test_client()
        self._create_test_data()
    
    def tearDown(self):
        if os.path.exists(self.test_config.temp_dir):
            shutil.rmtree(self.test_config.temp_dir)
    
    def _create_test_data(self):
        # Campaigns
        with open(self.test_config.CAMPAIGNS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'campaign_id', 'name', 'segment_id', 'start_date', 'status', 'subject', 'body'
            ])
            writer.writeheader()
            for i in range(10):
                writer.writerow({
                    'campaign_id': str(i),
                    'name': f'Campaign {i}',
                    'segment_id': '1',
                    'start_date': '2024-12-01',
                    'status': 'sent',
                    'subject': f'Subject {i}',
                    'body': f'Body {i}'
                })
        
        # Events (20,000+)
        with open(self.test_config.EVENTS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['event_id', 'campaign_id', 'customer_id', 'event_type', 'timestamp'])
            writer.writeheader()
            for i in range(20000):
                writer.writerow({
                    'event_id': str(i),
                    'campaign_id': str(i % 10),
                    'customer_id': str(i % 1000),
                    'event_type': ['sent', 'opened', 'clicked', 'converted'][i % 4],
                    'timestamp': '2024-12-01T10:00:00'
                })
    
    def test_login_page_response_time(self):
        """QA-4.1: Login page loads within 2 seconds."""
        start = time.time()
        response = self.client.get('/auth/login')
        elapsed = time.time() - start
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(elapsed, 2.0)
    
    def test_dashboard_response_time(self):
        """QA-4.1: Dashboard loads within 2 seconds."""
        # Login
        self.client.post('/auth/login', data={'username': 'admin', 'password': 'password'})
        
        start = time.time()
        response = self.client.get('/dashboard')
        elapsed = time.time() - start
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(elapsed, 2.0)
    
    def test_analytics_dashboard_with_large_events(self):
        """QA-4.2: Analytics dashboard with 20,000+ events loads within 3 seconds."""
        # Login
        self.client.post('/auth/login', data={'username': 'admin', 'password': 'password'})
        
        start = time.time()
        response = self.client.get('/analytics')
        elapsed = time.time() - start
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(elapsed, 3.0)


class TestSecurity(unittest.TestCase):
    """
    QA-3: Security
    - All features require authentication
    - 0% unauthorized access success
    """
    
    def setUp(self):
        self.test_config = TestConfig()
        self.app = create_app(self.test_config)
        self.client = self.app.test_client()
    
    def tearDown(self):
        if os.path.exists(self.test_config.temp_dir):
            shutil.rmtree(self.test_config.temp_dir)
    
    def test_all_routes_require_authentication(self):
        """QA-3.1: All Marketing Automation features require authentication."""
        protected_routes = ['/dashboard', '/segments', '/segments/new', '/campaigns', 
                          '/campaigns/new', '/analytics']
        
        for route in protected_routes:
            response = self.client.get(route, follow_redirects=False)
            self.assertEqual(response.status_code, 302, f"Route {route} should redirect")
            self.assertIn('/auth/login', response.location, f"Route {route} should redirect to login")
    
    def test_zero_unauthorized_access_rate(self):
        """QA-3.2: 0% unauthorized access success rate."""
        # Attempt multiple unauthorized accesses
        unauthorized_attempts = 0
        successful_unauthorized = 0
        
        routes = ['/dashboard', '/segments', '/campaigns', '/analytics']
        
        for route in routes:
            unauthorized_attempts += 1
            response = self.client.get(route, follow_redirects=False)
            if response.status_code == 200:
                successful_unauthorized += 1
        
        # Calculate success rate (should be 0%)
        success_rate = (successful_unauthorized / unauthorized_attempts) * 100
        self.assertEqual(success_rate, 0.0, "Unauthorized access success rate should be 0%")
    
    def test_session_based_authentication(self):
        """QA-3.1: Session-based authentication works correctly."""
        # Access before login
        response1 = self.client.get('/dashboard', follow_redirects=False)
        self.assertEqual(response1.status_code, 302)
        
        # Login
        self.client.post('/auth/login', data={'username': 'admin', 'password': 'password'})
        
        # Access after login
        response2 = self.client.get('/dashboard')
        self.assertEqual(response2.status_code, 200)
        
        # Logout
        self.client.get('/auth/logout')
        
        # Access after logout
        response3 = self.client.get('/dashboard', follow_redirects=False)
        self.assertEqual(response3.status_code, 302)


class TestReliability(unittest.TestCase):
    """
    QA-5: Reliability
    - System operates correctly with partial failures
    - Maintains ≥95% successful operations on errors
    """
    
    def setUp(self):
        self.test_config = TestConfig()
        self.app = create_app(self.test_config)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self._create_test_data()
    
    def tearDown(self):
        self.app_context.pop()
        if os.path.exists(self.test_config.temp_dir):
            shutil.rmtree(self.test_config.temp_dir)
    
    def _create_test_data(self):
        with open(self.test_config.CUSTOMERS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'customer_id', 'name', 'email', 'age', 'location', 'total_spent', 'last_purchase_date'
            ])
            writer.writeheader()
            for i in range(100):
                writer.writerow({
                    'customer_id': str(i),
                    'name': f'Customer {i}',
                    'email': f'c{i}@test.com',
                    'age': '30',
                    'location': 'Ankara',
                    'total_spent': '1000',
                    'last_purchase_date': '2024-11-01'
                })
        
        with open(self.test_config.SEGMENTS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['segment_id', 'segment_name', 'rules_json'])
            writer.writeheader()
            writer.writerow({'segment_id': '1', 'segment_name': 'All', 'rules_json': '{}'})
    
    def test_missing_events_file_handled(self):
        """QA-5.1: System handles missing events file gracefully."""
        from marketing.analytics import load_events, get_campaign_metrics
        
        # Events file doesn't exist
        if os.path.exists(self.test_config.EVENTS_CSV):
            os.remove(self.test_config.EVENTS_CSV)
        
        # Should not crash, return empty
        events = load_events()
        metrics = get_campaign_metrics('1')
        
        self.assertEqual(events, [])
        self.assertEqual(metrics['sent'], 0)
    
    def test_missing_segments_file_handled(self):
        """QA-5.1: System handles missing segments file gracefully."""
        from marketing.segmentation import load_segments
        
        if os.path.exists(self.test_config.SEGMENTS_CSV):
            os.remove(self.test_config.SEGMENTS_CSV)
        
        segments = load_segments()
        self.assertEqual(segments, [])
    
    def test_missing_campaigns_file_handled(self):
        """QA-5.1: System handles missing campaigns file gracefully."""
        from marketing.campaigns import load_campaigns
        
        if os.path.exists(self.test_config.CAMPAIGNS_CSV):
            os.remove(self.test_config.CAMPAIGNS_CSV)
        
        campaigns = load_campaigns()
        self.assertEqual(campaigns, [])
    
    def test_campaign_send_with_segment_mismatch(self):
        """QA-5.2: Campaign with invalid segment handled gracefully."""
        from marketing.campaigns import create_campaign, get_campaign_customers
        
        # Create campaign with non-existent segment
        with open(self.test_config.CAMPAIGNS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'campaign_id', 'name', 'segment_id', 'start_date', 'status', 'subject', 'body'
            ])
            writer.writeheader()
            writer.writerow({
                'campaign_id': '999',
                'name': 'Bad Campaign',
                'segment_id': '9999',  # Non-existent
                'start_date': '2024-12-01',
                'status': 'draft',
                'subject': 'Test',
                'body': 'Test'
            })
        
        # Should not crash
        customers = get_campaign_customers('999')
        self.assertEqual(customers, [])


class TestEmailChannel(unittest.TestCase):
    """
    FR-4: Communication Channels
    - Support email outbound channel
    - Architecture allows future expansion
    """
    
    def setUp(self):
        self.test_config = TestConfig()
        self.app = create_app(self.test_config)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self._create_test_data()
    
    def tearDown(self):
        self.app_context.pop()
        if os.path.exists(self.test_config.temp_dir):
            shutil.rmtree(self.test_config.temp_dir)
    
    def _create_test_data(self):
        with open(self.test_config.CUSTOMERS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'customer_id', 'name', 'email', 'age', 'location', 'total_spent', 'last_purchase_date'
            ])
            writer.writeheader()
            writer.writerow({
                'customer_id': '1', 'name': 'Alice', 'email': 'alice@test.com',
                'age': '30', 'location': 'Ankara', 'total_spent': '1000', 'last_purchase_date': '2024-11-01'
            })
        
        with open(self.test_config.SEGMENTS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['segment_id', 'segment_name', 'rules_json'])
            writer.writeheader()
            writer.writerow({'segment_id': '1', 'segment_name': 'All', 'rules_json': '{}'})
    
    def test_campaign_has_email_subject(self):
        """FR-4.1: Campaign supports email subject field."""
        from marketing.campaigns import create_campaign, get_campaign_by_id
        
        campaign_id = create_campaign(
            name='Email Campaign',
            segment_id='1',
            start_date='2024-12-01',
            subject='Special Offer Inside!',
            body='Check out our deals'
        )
        
        campaign = get_campaign_by_id(campaign_id)
        self.assertIn('subject', campaign)
        self.assertEqual(campaign['subject'], 'Special Offer Inside!')
    
    def test_campaign_has_email_body(self):
        """FR-4.1: Campaign supports email body field."""
        from marketing.campaigns import create_campaign, get_campaign_by_id
        
        campaign_id = create_campaign(
            name='Email Campaign',
            segment_id='1',
            start_date='2024-12-01',
            subject='Offer',
            body='Dear customer, here is your exclusive offer...'
        )
        
        campaign = get_campaign_by_id(campaign_id)
        self.assertIn('body', campaign)
        self.assertEqual(campaign['body'], 'Dear customer, here is your exclusive offer...')
    
    def test_sent_event_simulates_email_delivery(self):
        """FR-4.1: Sending campaign creates 'sent' events (email delivery simulation)."""
        from marketing.campaigns import create_campaign, send_campaign
        from marketing.analytics import load_events
        
        campaign_id = create_campaign('Test', '1', '2024-12-01', 'Subject', 'Body')
        send_campaign(campaign_id)
        
        events = load_events()
        sent = [e for e in events if e['event_type'] == 'sent']
        
        # Each customer gets a 'sent' event (email delivered)
        self.assertGreater(len(sent), 0)


if __name__ == '__main__':
    unittest.main()
