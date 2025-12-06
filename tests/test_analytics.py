# ./tests/test_analytics.py

"""
Tests for marketing analytics functionality.
Tests metric calculation logic.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import tempfile
import csv
from app import create_app
from config import Config


class TestConfig(Config):
    """Test configuration with temporary CSV files."""
    TESTING = True
    
    def __init__(self):
        super().__init__()
        self.temp_dir = tempfile.mkdtemp()
        self.DATA_DIR = self.temp_dir
        self.EVENTS_CSV = os.path.join(self.temp_dir, 'events.csv')
        self.CAMPAIGNS_CSV = os.path.join(self.temp_dir, 'campaigns.csv')


class TestAnalytics(unittest.TestCase):
    """Test cases for analytics and metrics calculation."""
    
    def setUp(self):
        """Set up test app and data."""
        self.test_config = TestConfig()
        self.app = create_app(self.test_config)
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Create test data
        self._create_test_campaigns()
        self._create_test_events()
    
    def tearDown(self):
        """Clean up test environment."""
        self.app_context.pop()
        import shutil
        if os.path.exists(self.test_config.temp_dir):
            shutil.rmtree(self.test_config.temp_dir)
    
    def _create_test_campaigns(self):
        """Create test campaigns CSV."""
        with open(self.test_config.CAMPAIGNS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'campaign_id', 'name', 'segment_id', 'start_date', 'status', 'subject', 'body'
            ])
            writer.writeheader()
            writer.writerow({
                'campaign_id': '1',
                'name': 'Test Campaign 1',
                'segment_id': '1',
                'start_date': '2024-12-01',
                'status': 'sent',
                'subject': 'Test',
                'body': 'Test'
            })
    
    def _create_test_events(self):
        """Create test events CSV with known metrics."""
        events = [
            # Campaign 1: 10 sent, 7 opened, 4 clicked, 2 converted
            # Expected rates: 70% open, 40% CTR, 20% conversion
            {'event_id': '1', 'campaign_id': '1', 'customer_id': '1', 'event_type': 'sent', 'timestamp': '2024-12-01T10:00:00'},
            {'event_id': '2', 'campaign_id': '1', 'customer_id': '2', 'event_type': 'sent', 'timestamp': '2024-12-01T10:00:00'},
            {'event_id': '3', 'campaign_id': '1', 'customer_id': '3', 'event_type': 'sent', 'timestamp': '2024-12-01T10:00:00'},
            {'event_id': '4', 'campaign_id': '1', 'customer_id': '4', 'event_type': 'sent', 'timestamp': '2024-12-01T10:00:00'},
            {'event_id': '5', 'campaign_id': '1', 'customer_id': '5', 'event_type': 'sent', 'timestamp': '2024-12-01T10:00:00'},
            {'event_id': '6', 'campaign_id': '1', 'customer_id': '6', 'event_type': 'sent', 'timestamp': '2024-12-01T10:00:00'},
            {'event_id': '7', 'campaign_id': '1', 'customer_id': '7', 'event_type': 'sent', 'timestamp': '2024-12-01T10:00:00'},
            {'event_id': '8', 'campaign_id': '1', 'customer_id': '8', 'event_type': 'sent', 'timestamp': '2024-12-01T10:00:00'},
            {'event_id': '9', 'campaign_id': '1', 'customer_id': '9', 'event_type': 'sent', 'timestamp': '2024-12-01T10:00:00'},
            {'event_id': '10', 'campaign_id': '1', 'customer_id': '10', 'event_type': 'sent', 'timestamp': '2024-12-01T10:00:00'},
            
            {'event_id': '11', 'campaign_id': '1', 'customer_id': '1', 'event_type': 'opened', 'timestamp': '2024-12-01T11:00:00'},
            {'event_id': '12', 'campaign_id': '1', 'customer_id': '2', 'event_type': 'opened', 'timestamp': '2024-12-01T11:00:00'},
            {'event_id': '13', 'campaign_id': '1', 'customer_id': '3', 'event_type': 'opened', 'timestamp': '2024-12-01T11:00:00'},
            {'event_id': '14', 'campaign_id': '1', 'customer_id': '4', 'event_type': 'opened', 'timestamp': '2024-12-01T11:00:00'},
            {'event_id': '15', 'campaign_id': '1', 'customer_id': '5', 'event_type': 'opened', 'timestamp': '2024-12-01T11:00:00'},
            {'event_id': '16', 'campaign_id': '1', 'customer_id': '6', 'event_type': 'opened', 'timestamp': '2024-12-01T11:00:00'},
            {'event_id': '17', 'campaign_id': '1', 'customer_id': '7', 'event_type': 'opened', 'timestamp': '2024-12-01T11:00:00'},
            
            {'event_id': '18', 'campaign_id': '1', 'customer_id': '1', 'event_type': 'clicked', 'timestamp': '2024-12-01T12:00:00'},
            {'event_id': '19', 'campaign_id': '1', 'customer_id': '2', 'event_type': 'clicked', 'timestamp': '2024-12-01T12:00:00'},
            {'event_id': '20', 'campaign_id': '1', 'customer_id': '3', 'event_type': 'clicked', 'timestamp': '2024-12-01T12:00:00'},
            {'event_id': '21', 'campaign_id': '1', 'customer_id': '4', 'event_type': 'clicked', 'timestamp': '2024-12-01T12:00:00'},
            
            {'event_id': '22', 'campaign_id': '1', 'customer_id': '1', 'event_type': 'converted', 'timestamp': '2024-12-01T13:00:00'},
            {'event_id': '23', 'campaign_id': '1', 'customer_id': '2', 'event_type': 'converted', 'timestamp': '2024-12-01T13:00:00'},
        ]
        
        with open(self.test_config.EVENTS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['event_id', 'campaign_id', 'customer_id', 'event_type', 'timestamp'])
            writer.writeheader()
            writer.writerows(events)
    
    def test_get_campaign_metrics(self):
        """Test calculating metrics for a specific campaign."""
        from marketing.analytics import get_campaign_metrics
        
        metrics = get_campaign_metrics('1')
        
        self.assertEqual(metrics['sent'], 10)
        self.assertEqual(metrics['opened'], 7)
        self.assertEqual(metrics['clicked'], 4)
        self.assertEqual(metrics['converted'], 2)
    
    def test_open_rate_calculation(self):
        """Test open rate is calculated correctly."""
        from marketing.analytics import get_campaign_metrics
        
        metrics = get_campaign_metrics('1')
        
        # 7 opened / 10 sent = 70%
        self.assertEqual(metrics['open_rate'], 70.0)
    
    def test_click_rate_calculation(self):
        """Test click-through rate is calculated correctly."""
        from marketing.analytics import get_campaign_metrics
        
        metrics = get_campaign_metrics('1')
        
        # 4 clicked / 10 sent = 40%
        self.assertEqual(metrics['click_rate'], 40.0)
    
    def test_conversion_rate_calculation(self):
        """Test conversion rate is calculated correctly."""
        from marketing.analytics import get_campaign_metrics
        
        metrics = get_campaign_metrics('1')
        
        # 2 converted / 10 sent = 20%
        self.assertEqual(metrics['conversion_rate'], 20.0)
    
    def test_no_events_campaign(self):
        """Test metrics for campaign with no events."""
        from marketing.analytics import get_campaign_metrics
        
        metrics = get_campaign_metrics('999')
        
        self.assertEqual(metrics['sent'], 0)
        self.assertEqual(metrics['opened'], 0)
        self.assertEqual(metrics['clicked'], 0)
        self.assertEqual(metrics['converted'], 0)
        self.assertEqual(metrics['open_rate'], 0)
        self.assertEqual(metrics['click_rate'], 0)
        self.assertEqual(metrics['conversion_rate'], 0)
    
    def test_get_all_campaign_metrics(self):
        """Test getting metrics for all campaigns."""
        from marketing.analytics import get_all_campaign_metrics
        
        all_metrics = get_all_campaign_metrics()
        
        self.assertEqual(len(all_metrics), 1)
        self.assertEqual(all_metrics[0]['campaign_name'], 'Test Campaign 1')
        self.assertEqual(all_metrics[0]['sent'], 10)
    
    def test_overall_metrics(self):
        """Test overall metrics across all campaigns."""
        from marketing.analytics import get_overall_metrics
        
        overall = get_overall_metrics()
        
        self.assertEqual(overall['total_sent'], 10)
        self.assertEqual(overall['total_opened'], 7)
        self.assertEqual(overall['total_clicked'], 4)
        self.assertEqual(overall['total_converted'], 2)
        self.assertEqual(overall['overall_open_rate'], 70.0)
        self.assertEqual(overall['overall_click_rate'], 40.0)
        self.assertEqual(overall['overall_conversion_rate'], 20.0)


if __name__ == '__main__':
    unittest.main()
