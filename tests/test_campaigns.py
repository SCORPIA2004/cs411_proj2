# ./tests/test_campaigns.py

"""
Tests for campaign management functionality.
Tests campaign creation and sending logic.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import tempfile
import csv
from unittest.mock import patch, MagicMock
from app import create_app
from config import Config


class TestConfig(Config):
    """Test configuration with temporary CSV files."""
    TESTING = True
    
    def __init__(self):
        super().__init__()
        # Create temporary directory for test data
        self.temp_dir = tempfile.mkdtemp()
        self.DATA_DIR = self.temp_dir
        self.CUSTOMERS_CSV = os.path.join(self.temp_dir, 'customers.csv')
        self.SEGMENTS_CSV = os.path.join(self.temp_dir, 'segments.csv')
        self.CAMPAIGNS_CSV = os.path.join(self.temp_dir, 'campaigns.csv')
        self.EVENTS_CSV = os.path.join(self.temp_dir, 'events.csv')


class TestCampaigns(unittest.TestCase):
    """Test cases for campaign management logic."""
    
    def setUp(self):
        """Set up test app and data."""
        self.test_config = TestConfig()
        self.app = create_app(self.test_config)
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Create test CSV files
        self._create_test_customers()
        self._create_test_segments()
    
    def tearDown(self):
        """Clean up test environment."""
        self.app_context.pop()
        # Clean up temp files
        import shutil
        if os.path.exists(self.test_config.temp_dir):
            shutil.rmtree(self.test_config.temp_dir)
    
    def _create_test_customers(self):
        """Create test customers CSV."""
        with open(self.test_config.CUSTOMERS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'customer_id', 'name', 'email', 'age', 'location', 'total_spent', 'last_purchase_date'
            ])
            writer.writeheader()
            writer.writerows([
                {
                    'customer_id': '1',
                    'name': 'Test User 1',
                    'email': 'test1@example.com',
                    'age': '25',
                    'location': 'Ankara',
                    'total_spent': '1000.0',
                    'last_purchase_date': '2024-11-15'
                },
                {
                    'customer_id': '2',
                    'name': 'Test User 2',
                    'email': 'test2@example.com',
                    'age': '35',
                    'location': 'Istanbul',
                    'total_spent': '2500.0',
                    'last_purchase_date': '2024-11-20'
                },
            ])
    
    def _create_test_segments(self):
        """Create test segments CSV."""
        with open(self.test_config.SEGMENTS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['segment_id', 'segment_name', 'rules_json'])
            writer.writeheader()
            writer.writerow({
                'segment_id': '1',
                'segment_name': 'Test Segment',
                'rules_json': '{"min_age": 20}'
            })
    
    def test_create_campaign(self):
        """Test creating a new campaign."""
        from marketing.campaigns import create_campaign, get_campaign_by_id
        
        campaign_id = create_campaign(
            name='Test Campaign',
            segment_id='1',
            start_date='2024-12-01',
            subject='Test Subject',
            body='Test Body'
        )
        
        self.assertIsNotNone(campaign_id)
        
        # Verify campaign was created
        campaign = get_campaign_by_id(campaign_id)
        self.assertIsNotNone(campaign)
        self.assertEqual(campaign['name'], 'Test Campaign')
        self.assertEqual(campaign['status'], 'draft')
    
    def test_campaign_csv_structure(self):
        """Test that campaign CSV has correct structure."""
        from marketing.campaigns import create_campaign
        
        create_campaign(
            name='Test Campaign',
            segment_id='1',
            start_date='2024-12-01',
            subject='Test Subject',
            body='Test Body'
        )
        
        # Read CSV and verify structure
        with open(self.test_config.CAMPAIGNS_CSV, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 1)
            self.assertIn('campaign_id', rows[0])
            self.assertIn('name', rows[0])
            self.assertIn('segment_id', rows[0])
            self.assertIn('status', rows[0])
    
    def test_send_campaign(self):
        """Test sending a campaign creates events."""
        from marketing.campaigns import create_campaign, send_campaign, load_campaigns
        from marketing.analytics import load_events
        
        # Create campaign
        campaign_id = create_campaign(
            name='Test Campaign',
            segment_id='1',
            start_date='2024-12-01',
            subject='Test Subject',
            body='Test Body'
        )
        
        # Send campaign
        count = send_campaign(campaign_id)
        
        # Verify customers were targeted
        self.assertEqual(count, 2)
        
        # Verify events were created
        events = load_events()
        sent_events = [e for e in events if e['event_type'] == 'sent']
        self.assertEqual(len(sent_events), 2)
        
        # Verify campaign status updated
        campaigns = load_campaigns()
        campaign = next(c for c in campaigns if c['campaign_id'] == campaign_id)
        self.assertEqual(campaign['status'], 'sent')
    
    def test_send_campaign_twice(self):
        """Test that sending a campaign twice doesn't create duplicate events."""
        from marketing.campaigns import create_campaign, send_campaign
        
        campaign_id = create_campaign(
            name='Test Campaign',
            segment_id='1',
            start_date='2024-12-01',
            subject='Test Subject',
            body='Test Body'
        )
        
        # Send first time
        count1 = send_campaign(campaign_id)
        self.assertEqual(count1, 2)
        
        # Send second time (should return 0 since status is no longer 'draft')
        count2 = send_campaign(campaign_id)
        self.assertEqual(count2, 0)
    
    def test_get_campaign_customers(self):
        """Test getting customers for a campaign."""
        from marketing.campaigns import create_campaign, get_campaign_customers
        
        campaign_id = create_campaign(
            name='Test Campaign',
            segment_id='1',
            start_date='2024-12-01',
            subject='Test Subject',
            body='Test Body'
        )
        
        customers = get_campaign_customers(campaign_id)
        self.assertEqual(len(customers), 2)


if __name__ == '__main__':
    unittest.main()
