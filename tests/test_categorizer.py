"""
Unit tests for TransactionCategorizer - testing transaction-to-category mapping.
"""
import unittest
from datetime import datetime
from receiptsParsing.categorizer import TransactionCategorizer
from receiptsParsing.transaction import Transaction


class TestTransactionCategorizer(unittest.TestCase):
    
    def setUp(self):
        """Set up test categorizer with sample purposes map."""
        self.purposes_map = {
            'Bills': {
                'Health': [
                    'PHARMACY',
                    'MEDICAL CENTRE'
                ],
                'Telecom': {
                    'Mobile': [
                        'VAYA',
                        'TPG INTERNET'
                    ]
                }
            },
            'Groceries': [
                'WOOLWORTHS',
                'COLES'
            ],
            'Transport': {
                'Public': [
                    'TRANSLINK'
                ]
            }
        }
        self.categorizer = TransactionCategorizer(self.purposes_map)
    
    def test_single_match_categorization(self):
        """Test transaction with single category match."""
        # Create a transaction with PHARMACY in description
        transaction = self._create_transaction('PHARMACY GUILD HEALTH')
        
        result = self.categorizer.categorize_transaction(transaction)
        
        self.assertEqual(result['status'], 'matched')
        self.assertEqual(len(result['categories']), 1)
        self.assertEqual(result['selected_category'], ['Bills', 'Health'])
    
    def test_no_match_categorization(self):
        """Test transaction with no category matches."""
        transaction = self._create_transaction('UNKNOWN MERCHANT XYZ')
        
        result = self.categorizer.categorize_transaction(transaction)
        
        self.assertEqual(result['status'], 'no_match')
        self.assertEqual(len(result['categories']), 0)
        self.assertIsNone(result['selected_category'])
    
    def test_multiple_matches_categorization(self):
        """Test transaction matching multiple categories."""
        # Add overlapping patterns to create multiple matches
        overlap_map = {
            'Category1': ['TEST MERCHANT'],
            'Category2': ['MERCHANT']
        }
        categorizer = TransactionCategorizer(overlap_map)
        transaction = self._create_transaction('TEST MERCHANT STORE')
        
        result = categorizer.categorize_transaction(transaction)
        
        self.assertEqual(result['status'], 'multiple_matches')
        self.assertEqual(len(result['categories']), 2)
        # Should default to first match
        self.assertEqual(result['selected_category'], ['Category1'])
    
    def test_nested_category_matching(self):
        """Test matching transactions to nested categories."""
        transaction = self._create_transaction('VAYA MOBILE PAYMENT')
        
        result = self.categorizer.categorize_transaction(transaction)
        
        self.assertEqual(result['status'], 'matched')
        self.assertEqual(result['selected_category'], ['Bills', 'Telecom', 'Mobile'])
    
    def test_case_insensitive_matching(self):
        """Test that pattern matching is case insensitive."""
        transaction = self._create_transaction('woolworths supermarket')
        
        result = self.categorizer.categorize_transaction(transaction)
        
        self.assertEqual(result['status'], 'matched')
        self.assertEqual(result['selected_category'], ['Groceries'])
    
    
    def _create_transaction(self, description, amount=-10.50):
        """Helper to create test transaction."""
        # Using UBank new format (10 fields) for testing
        test_row = [
            "12:34 01-01-25",  # dateAndTime
            description,        # description
            "10.50" if amount > 0 else "",  # debit
            "10.50" if amount < 0 else "",  # credit
            "Test Account",     # fromAccount
            "",                # toAccount
            "Visa",            # paymentType
            "Shopping",        # category
            "123456",          # receiptNumber
            "789012345"        # transactionId
        ]
        return Transaction(test_row)


if __name__ == '__main__':
    unittest.main()