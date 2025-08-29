"""
Unit tests for CsvHandler - testing CSV formatting and TODO logic.
"""
import unittest
import tempfile
import csv
import os
from receiptsParsing.csv_handler import CsvHandler


class TestCsvHandler(unittest.TestCase):
    
    def test_format_category_levels_with_full_path(self):
        """Test category level formatting with 3-level path."""
        category_path = ['Bills', 'Telecom', 'Mobile']
        
        levels = CsvHandler._format_category_levels(category_path)
        
        self.assertEqual(levels, ('Bills', 'Telecom', 'Mobile'))
    
    def test_format_category_levels_with_partial_path(self):
        """Test category level formatting with partial path."""
        category_path = ['Groceries']
        
        levels = CsvHandler._format_category_levels(category_path)
        
        self.assertEqual(levels, ('Groceries', '', ''))
    
    def test_format_category_levels_with_todo(self):
        """Test category level formatting with TODO path."""
        category_path = ['TODO']
        
        levels = CsvHandler._format_category_levels(category_path)
        
        self.assertEqual(levels, ('TODO', '', ''))

    def test_write_transactions_with_mixed_types(self):
        """Test writing transactions with different categorization outcomes."""
        # Create mock transaction items
        from datetime import datetime
        from decimal import Decimal
        
        # Mock transaction object
        class MockTransaction:
            def __init__(self, desc, amount):
                self.description = desc
                self.amount = Decimal(str(amount))
                self.effectiveDate = datetime(2025, 1, 15)
                self.postedDate = datetime(2025, 1, 15)
                self.source = "Test Account"
        
        # Create test data
        matched_item = {
            'transaction': MockTransaction("PHARMACY PURCHASE", -25.50),
            'categorization': {
                'status': 'matched',
                'selected_category': ['Bills', 'Health']
            }
        }
        
        unmatched_item = {
            'transaction': MockTransaction("UNKNOWN MERCHANT", -15.00),
            'categorization': {
                'status': 'no_match',
                'selected_category': None
            }
        }
        
        multiple_item = {
            'transaction': MockTransaction("TEST MERCHANT", -10.00),
            'categorization': {
                'status': 'multiple_matches',
                'selected_category': ['Category1']
            }
        }
        
        transaction_items = [matched_item, unmatched_item, multiple_item]
        
        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as temp_file:
            temp_path = temp_file.name
        
        try:
            CsvHandler.write_transactions(temp_path, transaction_items, "TestBank")
            
            # Read back and verify
            with open(temp_path, 'r') as file:
                reader = csv.reader(file)
                rows = list(reader)
            
            self.assertEqual(len(rows), 3)
            
            # Check matched transaction
            self.assertEqual(rows[0][3:6], ['Bills', 'Health', ''])  # Categories
            self.assertIn('PHARMACY PURCHASE', rows[0][6])  # Description
            
            # Check unmatched transaction (should have TODO)
            self.assertEqual(rows[1][3:6], ['TODO', '', ''])  # Categories
            self.assertIn('UNKNOWN MERCHANT', rows[1][6])  # Description
            
            # Check multiple matches (should use first match)
            self.assertEqual(rows[2][3:6], ['Category1', '', ''])  # Categories
            self.assertIn('TEST MERCHANT', rows[2][6])  # Description
            
        finally:
            os.unlink(temp_path)


if __name__ == '__main__':
    unittest.main()