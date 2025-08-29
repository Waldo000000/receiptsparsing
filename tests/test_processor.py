"""
Integration tests for TransactionProcessor - testing end-to-end processing logic.
"""
import unittest
from datetime import datetime
from receiptsParsing.processor import TransactionProcessor
from receiptsParsing.transaction import Transaction


class TestTransactionProcessor(unittest.TestCase):
    
    def setUp(self):
        """Set up test processor with sample purposes map."""
        self.purposes_map = {
            'Bills': {
                'Health': ['PHARMACY']
            },
            'Groceries': ['WOOLWORTHS']
        }
        self.processor = TransactionProcessor(self.purposes_map)
    
    def test_transaction_separation_into_distinct_lists(self):
        """Test that transactions are separated into distinct lists."""
        # Create transactions with different outcomes
        matched_row = [
            "12:34 01-01-25", "PHARMACY GUILD", "", "10.50", 
            "Test Account", "", "Visa", "Health", "123", "789"
        ]
        unmatched_row = [
            "12:34 01-01-25", "UNKNOWN MERCHANT", "", "15.25", 
            "Test Account", "", "Visa", "Shopping", "124", "790"
        ]
        
        transactions = [Transaction(matched_row), Transaction(unmatched_row)]
        
        result = self.processor.process_transactions(transactions)
        
        # Should have 1 matched, 1 unmatched, 0 multiple matches
        self.assertEqual(len(result['categorized']), 1)
        self.assertEqual(len(result['unmatched']), 1)
        self.assertEqual(len(result['multiple_matches']), 0)
        
        # Verify the matched transaction
        matched_item = result['categorized'][0]
        self.assertEqual(matched_item['categorization']['status'], 'matched')
        self.assertIn("PHARMACY GUILD", matched_item['transaction'].description)
        
        # Verify the unmatched transaction
        unmatched_item = result['unmatched'][0]
        self.assertEqual(unmatched_item['categorization']['status'], 'no_match')
        self.assertIn("UNKNOWN MERCHANT", unmatched_item['transaction'].description)
    
    def test_multiple_matches_behavior(self):
        """Test that multiple matches go to separate list."""
        # Create overlapping patterns
        overlap_map = {
            'Category1': ['TEST'],
            'Category2': ['MERCHANT']
        }
        processor = TransactionProcessor(overlap_map)
        
        test_row = [
            "12:34 01-01-25", "TEST MERCHANT STORE", "", "10.50",
            "Test Account", "", "Visa", "Shopping", "123", "789"
        ]
        transactions = [Transaction(test_row)]
        
        result = processor.process_transactions(transactions)
        
        # Should be in multiple_matches only, not categorized
        self.assertEqual(len(result['categorized']), 0)
        self.assertEqual(len(result['multiple_matches']), 1)
        self.assertEqual(len(result['unmatched']), 0)
        
        # Should have first match selected by default
        item = result['multiple_matches'][0]
        self.assertEqual(item['categorization']['status'], 'multiple_matches')
        self.assertEqual(item['categorization']['selected_category'], ['Category1'])
    
    def test_journal_credit_processing(self):
        """Test that journal credits are properly handled."""
        # Create journal credit followed by debit transaction (negative amount)
        journal_row = [
            "12:34 01-01-25", "JOURNAL CREDIT TEST", "", "0.00",
            "Test Account", "", "Internal", "Transfer", "123", "789"
        ]
        debit_row = [
            "12:34 01-01-25", "PHARMACY PURCHASE", "", "25.50",
            "Test Account", "", "Visa", "Health", "124", "790"
        ]
        
        csv_rows = [journal_row, debit_row]
        parse_result = self.processor.parse_csv_rows(csv_rows)
        
        # Should have 1 transaction (journal credit gets merged with debit)
        self.assertEqual(len(parse_result['transactions']), 1)
        transaction = parse_result['transactions'][0]
        
        # Transaction description should include journal credit prefix
        self.assertIn("JOURNAL CREDIT TEST", transaction.description)
        self.assertIn("PHARMACY PURCHASE", transaction.description)
    
    def test_date_filtering(self):
        """Test that date filtering works correctly."""
        # Create transaction with specific date
        test_row = [
            "12:34 15-06-25", "PHARMACY TEST", "", "10.50",
            "Test Account", "", "Visa", "Health", "123", "789"
        ]
        transactions = [Transaction(test_row)]
        
        # Filter to exclude this transaction
        date_filter = {
            'start': datetime(2025, 1, 1),
            'end': datetime(2025, 5, 31)  # Transaction is in June, should be filtered out
        }
        
        result = self.processor.process_transactions(transactions, date_filter)
        
        # Should be filtered out
        self.assertEqual(len(result['categorized']), 0)
        self.assertEqual(result['filtered_out'], 1)
    
    def test_error_handling_in_csv_parsing(self):
        """Test that CSV parsing handles errors gracefully."""
        # Invalid rows
        invalid_rows = [
            ["too", "few", "fields"],  # Wrong number of fields
            None  # This will cause an exception in Transaction()
        ]
        
        # Add a valid row
        valid_row = [
            "12:34 01-01-25", "PHARMACY TEST", "", "10.50",
            "Test Account", "", "Visa", "Health", "123", "789"
        ]
        
        # Mix valid and invalid
        csv_rows = [invalid_rows[0], valid_row]
        
        try:
            parse_result = self.processor.parse_csv_rows(csv_rows)
            
            # Should have 1 valid transaction and 1 error
            self.assertEqual(len(parse_result['transactions']), 1)
            self.assertEqual(len(parse_result['errors']), 1)
            self.assertIn("Unexpected number of fields", parse_result['errors'][0])
        except Exception as e:
            self.fail(f"CSV parsing should handle errors gracefully, but got: {e}")


if __name__ == '__main__':
    unittest.main()