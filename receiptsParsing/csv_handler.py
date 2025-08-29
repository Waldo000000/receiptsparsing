"""
CSV file handling - pure I/O operations without business logic.
"""
import csv


class CsvHandler:
    """Handles reading and writing CSV files."""
    
    @staticmethod
    def read_csv_files(file_paths):
        """
        Read multiple CSV files and return all rows.
        
        Args:
            file_paths: List of file paths to read
            
        Returns:
            list: All CSV rows combined from all files
        """
        all_rows = []
        
        for file_path in file_paths:
            with open(file_path, 'rt') as csvfile:
                reader = csv.reader(csvfile, delimiter=',')
                for row in reader:
                    all_rows.append(row)
        
        return all_rows
    
    @staticmethod
    def write_transactions(file_path, transaction_items, source_label):
        """
        Write transaction items to CSV file.
        
        Args:
            file_path: Output file path
            transaction_items: List of transaction result dicts from processor
            source_label: Label to add to source column
        """
        with open(file_path, 'wt', newline='') as outfile:
            writer = csv.writer(outfile, delimiter=',')
            
            for item in transaction_items:
                transaction = item['transaction']
                categorization = item['categorization']
                
                # Format category levels - use TODO for unmatched, otherwise format the category path
                level0, level1, level2 = CsvHandler._format_category_levels(
                    ["TODO"] if categorization['status'] == 'no_match' else categorization['selected_category']
                )
                
                effective_date_str = transaction.effectiveDate.strftime("%Y-%m-%d")
                posted_date_str = transaction.postedDate.strftime("%Y-%m-%d")
                
                source_info = f"{transaction.source} ({source_label})" if transaction.source else source_label
                
                writer.writerow([
                    effective_date_str,
                    posted_date_str,
                    transaction.amount,
                    level0,
                    level1,
                    level2,
                    transaction.description,
                    "",  # Notes column (empty for now)
                    source_info
                ])
    
    @staticmethod
    def _format_category_levels(category_path):
        """
        Convert category path to standardized 3-level format for CSV output.
        
        Args:
            category_path: List representing category hierarchy
            
        Returns:
            tuple: (level0, level1, level2) with empty strings for missing levels
        """
        level0 = category_path[0] if len(category_path) > 0 else ""
        level1 = category_path[1] if len(category_path) > 1 else ""
        level2 = category_path[2] if len(category_path) > 2 else ""
        
        return (level0, level1, level2)