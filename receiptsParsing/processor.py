"""
Transaction processing logic - orchestrates parsing and categorization without I/O.
"""
import re
from datetime import datetime
from .transaction import Transaction
from .categorizer import TransactionCategorizer


class TransactionProcessor:
    """Handles the business logic of processing transactions."""
    
    def __init__(self, purposes_map):
        """Initialize with configuration."""
        self.categorizer = TransactionCategorizer(purposes_map)
        self.journal_credit_pattern = re.compile('^JOURNAL CREDIT')
    
    def parse_csv_rows(self, csv_rows):
        """
        Parse CSV rows into Transaction objects.
        
        Args:
            csv_rows: List of CSV row lists
            
        Returns:
            dict: {
                'transactions': list of Transaction objects,
                'errors': list of error messages,
                'journal_credits': list of journal credit transactions
            }
        """
        transactions = []
        errors = []
        journal_credits = []
        
        for row in csv_rows:
            if not len(row) in (5, 6, 10):
                errors.append(f"Unexpected number of fields: {', '.join(row)}")
                continue
            
            try:
                trans = Transaction(row)
            except Exception as e:
                errors.append(f"Failed to parse row: {', '.join(row)} - {str(e)}")
                continue
            
            if self.journal_credit_pattern.search(trans.description):
                if trans.amount != 0:
                    errors.append(f"Warning: ignoring non-zero journal credit: {trans}")
                else:
                    journal_credits.append(trans)
            else:
                # Apply any pending journal credits to this transaction
                if journal_credits:
                    if trans.amount < 0:
                        while journal_credits:
                            trans.description = journal_credits.pop().description + "; " + trans.description
                    else:
                        while journal_credits:
                            errors.append(f"Warning: ignoring non-prefix journal credit: {journal_credits.pop()}")
                
                transactions.append(trans)
        
        return {
            'transactions': transactions,
            'errors': errors,
            'journal_credits': journal_credits
        }
    
    def process_transactions(self, transactions, date_filter=None):
        """
        Process transactions through categorization and filtering.
        
        Args:
            transactions: List of Transaction objects
            date_filter: Optional dict with 'start' and 'end' datetime objects
            
        Returns:
            dict: {
                'categorized': list of dicts with transaction + categorization info,
                'unmatched': list of transactions that couldn't be categorized,
                'multiple_matches': list of transactions with multiple category matches,
                'filtered_out': count of transactions filtered by date
            }
        """
        # Sort transactions by effective date
        sorted_transactions = sorted(transactions, key=lambda t: t.effectiveDate)
        
        categorized = []
        unmatched = []
        multiple_matches = []
        filtered_out = 0
        
        for transaction in sorted_transactions:
            # Apply date filter if specified
            if date_filter and not self._passes_date_filter(transaction, date_filter):
                filtered_out += 1
                continue
            
            # Categorize the transaction
            categorization = self.categorizer.categorize_transaction(transaction)
            
            # Create result object
            result = {
                'transaction': transaction,
                'categorization': categorization,
                'category_levels': self.categorizer.get_category_levels(categorization['selected_category'])
            }
            
            # Sort into appropriate buckets
            if categorization['status'] == 'matched':
                categorized.append(result)
            elif categorization['status'] == 'no_match':
                unmatched.append(result)
            elif categorization['status'] == 'multiple_matches':
                multiple_matches.append(result)
                categorized.append(result)  # Still include in output with first match
        
        return {
            'categorized': categorized,
            'unmatched': unmatched,
            'multiple_matches': multiple_matches,
            'filtered_out': filtered_out
        }
    
    def _passes_date_filter(self, transaction, date_filter):
        """Check if transaction passes date filter."""
        if 'start' in date_filter and transaction.postedDate < date_filter['start']:
            return False
        if 'end' in date_filter and transaction.postedDate > date_filter['end']:
            return False
        return True