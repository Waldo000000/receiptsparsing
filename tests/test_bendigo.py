"""
Tests for Bendigo credit card CSV format support (3-field format).
"""
import unittest
import os
from datetime import datetime
from decimal import Decimal
from receiptsParsing.transaction import Transaction
from receiptsParsing.processor import TransactionProcessor
from receiptsParsing.csv_handler import CsvHandler


FIXTURE_PATH = os.path.join(os.path.dirname(__file__), 'fixtures', 'bendigo_credit_card.csv')


class TestBendigoTransaction(unittest.TestCase):
    """Tests for 3-field Bendigo credit card format parsing."""

    def test_domestic_purchase_parsing(self):
        """Test parsing a domestic retail purchase."""
        row = ["25/02/2026", "-7.47", "RETAIL PURCHASE ACME GROCERY STORE, SPRINGFIELD C 2102 AUD000000000747"]
        t = Transaction(row)

        self.assertEqual(t.postedDate, datetime(2026, 2, 25))
        self.assertEqual(t.effectiveDate, datetime(2026, 2, 25))
        self.assertEqual(t.description, "RETAIL PURCHASE ACME GROCERY STORE, SPRINGFIELD C 2102 AUD000000000747")
        self.assertEqual(t.amount, Decimal("7.47"))
        self.assertEqual(t.source, "")

    def test_expense_sign_convention(self):
        """Bendigo negative amounts (expenses) become positive in system convention."""
        row = ["22/02/2026", "-59.94", "RETAIL PURCHASE-INTERNATIONAL EUROPA CAR RENTAL, GENEVA 2002 CHF000000003254"]
        t = Transaction(row)

        self.assertEqual(t.amount, Decimal("59.94"))

    def test_payment_sign_convention(self):
        """Bendigo positive amounts (payments/credits) become negative in system convention."""
        row = ["19/02/2026", "314.00", "PAYMENT - BPAY BPAY CR:0198765432 19022026 0198765432"]
        t = Transaction(row)

        self.assertEqual(t.amount, Decimal("-314.00"))

    def test_large_credit_sign_convention(self):
        """Large positive amount (salary deposit) becomes negative."""
        row = ["05/02/2026", "1500.00", "PAYMENT - DIRECT CREDIT SALARY DEPOSIT REF:87654321"]
        t = Transaction(row)

        self.assertEqual(t.amount, Decimal("-1500.00"))

    def test_date_format(self):
        """Bendigo DD/MM/YYYY dates parse correctly."""
        row = ["05/02/2026", "-10.00", "TEST"]
        t = Transaction(row)

        self.assertEqual(t.postedDate, datetime(2026, 2, 5))
        self.assertEqual(t.effectiveDate, datetime(2026, 2, 5))


class TestBendigoIntegration(unittest.TestCase):
    """Integration tests for Bendigo format through the full pipeline."""

    def setUp(self):
        self.purposes_map = {
            'Groceries': ['ACME GROCERY'],
            'Transport': ['CAR RENTAL']
        }
        self.processor = TransactionProcessor(self.purposes_map)

    def test_fixture_file_end_to_end(self):
        """Test that the fixture file parses through the full pipeline without errors."""
        csv_rows = CsvHandler.read_csv_files([FIXTURE_PATH])
        parse_result = self.processor.parse_csv_rows(csv_rows)

        self.assertEqual(len(parse_result['errors']), 0)
        self.assertEqual(len(parse_result['transactions']), 6)

        # Verify first transaction (domestic purchase, sign-flipped)
        self.assertEqual(parse_result['transactions'][0].amount, Decimal("7.47"))
        # Verify third transaction (BPAY payment, sign-flipped)
        self.assertEqual(parse_result['transactions'][2].amount, Decimal("-314.00"))

    def test_categorization_integration(self):
        """Test that Bendigo transactions categorize correctly."""
        row = ["25/02/2026", "-7.47", "RETAIL PURCHASE ACME GROCERY STORE, SPRINGFIELD"]
        t = Transaction(row)

        result = self.processor.process_transactions([t])

        self.assertEqual(len(result['categorized']), 1)
        self.assertEqual(result['categorized'][0]['categorization']['selected_category'], ['Groceries'])

    def test_processor_accepts_3_field_rows(self):
        """Test that the processor accepts 3-field rows."""
        rows = [["25/02/2026", "-7.47", "TEST PURCHASE"]]
        parse_result = self.processor.parse_csv_rows(rows)

        self.assertEqual(len(parse_result['errors']), 0)
        self.assertEqual(len(parse_result['transactions']), 1)

    def test_processor_still_rejects_invalid_field_counts(self):
        """Regression test: field counts 2, 4, 7 are still rejected."""
        rows = [
            ["field1", "field2"],
            ["field1", "field2", "field3", "field4"],
            ["f1", "f2", "f3", "f4", "f5", "f6", "f7"],
        ]
        parse_result = self.processor.parse_csv_rows(rows)

        self.assertEqual(len(parse_result['transactions']), 0)
        self.assertEqual(len(parse_result['errors']), 3)


if __name__ == '__main__':
    unittest.main()
