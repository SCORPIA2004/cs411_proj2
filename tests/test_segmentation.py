# ./tests/test_segmentation.py

"""
Tests for customer segmentation functionality.
Tests filtering logic and segment creation.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from marketing.segmentation import filter_customers_by_segment, match_customer_rules


class TestSegmentation(unittest.TestCase):
    """Test cases for customer segmentation logic."""
    
    def setUp(self):
        """Set up test data."""
        self.customers = [
            {
                'customer_id': '1',
                'name': 'Test User 1',
                'email': 'test1@example.com',
                'age': 25,
                'location': 'Ankara',
                'total_spent': 1000.0,
                'last_purchase_date': '2024-11-15'
            },
            {
                'customer_id': '2',
                'name': 'Test User 2',
                'email': 'test2@example.com',
                'age': 35,
                'location': 'Istanbul',
                'total_spent': 2500.0,
                'last_purchase_date': '2024-11-20'
            },
            {
                'customer_id': '3',
                'name': 'Test User 3',
                'email': 'test3@example.com',
                'age': 45,
                'location': 'Izmir',
                'total_spent': 500.0,
                'last_purchase_date': '2024-10-05'
            },
        ]
    
    def test_filter_by_min_age(self):
        """Test filtering customers by minimum age."""
        rules = {'min_age': 30}
        filtered = filter_customers_by_segment(self.customers, rules)
        self.assertEqual(len(filtered), 2)
        self.assertTrue(all(c['age'] >= 30 for c in filtered))
    
    def test_filter_by_max_age(self):
        """Test filtering customers by maximum age."""
        rules = {'max_age': 40}
        filtered = filter_customers_by_segment(self.customers, rules)
        self.assertEqual(len(filtered), 2)
        self.assertTrue(all(c['age'] <= 40 for c in filtered))
    
    def test_filter_by_age_range(self):
        """Test filtering customers by age range."""
        rules = {'min_age': 30, 'max_age': 40}
        filtered = filter_customers_by_segment(self.customers, rules)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['age'], 35)
    
    def test_filter_by_location(self):
        """Test filtering customers by location."""
        rules = {'location': 'Ankara'}
        filtered = filter_customers_by_segment(self.customers, rules)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['location'], 'Ankara')
    
    def test_filter_by_location_case_insensitive(self):
        """Test location filter is case-insensitive."""
        rules = {'location': 'ankara'}
        filtered = filter_customers_by_segment(self.customers, rules)
        self.assertEqual(len(filtered), 1)
    
    def test_filter_by_min_spent(self):
        """Test filtering customers by minimum total spent."""
        rules = {'min_total_spent': 1500}
        filtered = filter_customers_by_segment(self.customers, rules)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['customer_id'], '2')
    
    def test_filter_by_multiple_rules(self):
        """Test filtering customers by multiple rules."""
        rules = {
            'min_age': 30,
            'max_age': 40,
            'min_total_spent': 2000
        }
        filtered = filter_customers_by_segment(self.customers, rules)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['customer_id'], '2')
    
    def test_no_rules(self):
        """Test filtering with no rules returns all customers."""
        rules = {}
        filtered = filter_customers_by_segment(self.customers, rules)
        self.assertEqual(len(filtered), 3)
    
    def test_no_matches(self):
        """Test filtering with rules that match no customers."""
        rules = {'min_age': 100}
        filtered = filter_customers_by_segment(self.customers, rules)
        self.assertEqual(len(filtered), 0)
    
    def test_match_customer_rules_positive(self):
        """Test match_customer_rules returns True for matching customer."""
        customer = self.customers[1]
        rules = {'min_age': 30, 'location': 'Istanbul'}
        self.assertTrue(match_customer_rules(customer, rules))
    
    def test_match_customer_rules_negative(self):
        """Test match_customer_rules returns False for non-matching customer."""
        customer = self.customers[0]
        rules = {'min_age': 30}
        self.assertFalse(match_customer_rules(customer, rules))


if __name__ == '__main__':
    unittest.main()
