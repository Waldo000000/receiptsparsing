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
    def write_categorized_transactions(file_path, categorized_transactions, source_label):
        """
        Write categorized transactions to CSV file.
        
        Args:
            file_path: Output file path
            categorized_transactions: List of categorized transaction dicts
            source_label: Label to add to source column
        """
        with open(file_path, 'wt', newline='') as outfile:
            writer = csv.writer(outfile, delimiter=',')
            
            for item in categorized_transactions:
                transaction = item['transaction']
                level0, level1, level2 = item['category_levels']
                
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