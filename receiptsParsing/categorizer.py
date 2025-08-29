"""
Transaction categorization logic - pure functions with no I/O or side effects.
"""

class TransactionCategorizer:
    """Handles categorization of transactions based on purpose mapping."""
    
    def __init__(self, purposes_map):
        """Initialize with a purposes mapping configuration."""
        self.purposes_map = purposes_map
    
    def categorize_transaction(self, transaction):
        """
        Categorize a single transaction.
        
        Args:
            transaction: Transaction object to categorize
            
        Returns:
            dict: {
                'status': 'matched' | 'no_match' | 'multiple_matches',
                'categories': list of category paths (e.g. [['Bills', 'Health'], ['Bills', 'Pharmacy']]),
                'selected_category': chosen category path or None
            }
        """
        purpose_lists = transaction.getPurposes(self.purposes_map)
        
        if len(purpose_lists) == 0:
            return {
                'status': 'no_match',
                'categories': [],
                'selected_category': None
            }
        elif len(purpose_lists) == 1:
            return {
                'status': 'matched',
                'categories': purpose_lists,
                'selected_category': purpose_lists[0]
            }
        else:
            return {
                'status': 'multiple_matches',
                'categories': purpose_lists,
                'selected_category': purpose_lists[0]  # Default to first match
            }
    
    def get_category_levels(self, category_path):
        """
        Convert category path to standardized 3-level format.
        
        Args:
            category_path: List representing category hierarchy
            
        Returns:
            tuple: (level0, level1, level2) with empty strings for missing levels
        """
        if category_path is None:
            return ("TODO", "", "")
        
        level0 = category_path[0] if len(category_path) > 0 else ""
        level1 = category_path[1] if len(category_path) > 1 else ""
        level2 = category_path[2] if len(category_path) > 2 else ""
        
        return (level0, level1, level2)