#!/usr/bin/python
import sys
import argparse
import calendar
from datetime import datetime
from receiptsParsing.processor import TransactionProcessor
from receiptsParsing.csv_handler import CsvHandler


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--year', type=int, dest='year', default=2016)
    parser.add_argument('--readAll', action='store_true')
    parser.add_argument('--month', type=int, metavar='month', default=1)
    parser.add_argument('inFiles', metavar='inFile', nargs='+')
    parser.add_argument('--outFileName', dest='outFileName', default="tmp.out.txt")
    parser.add_argument('--source', dest='source')
    args = parser.parse_args()

    # Load purposes configuration from external file
    try:
        from purposes_config import purposesMap
    except ImportError:
        print("Error: purposes_config.py not found. Please create it from purposes_config.example.py")
        sys.exit(1)

    # Initialize processor
    processor = TransactionProcessor(purposesMap)
    
    # Read CSV files
    try:
        csv_rows = CsvHandler.read_csv_files(args.inFiles)
    except Exception as e:
        print(f"Error reading CSV files: {e}")
        sys.exit(1)
    
    # Parse transactions
    parse_result = processor.parse_csv_rows(csv_rows)
    
    # Print any parsing errors
    for error in parse_result['errors']:
        print(error)
    
    # Set up date filter if not reading all
    date_filter = None
    if not args.readAll:
        start_of_month = datetime(args.year, args.month, 1)
        end_of_month = datetime(args.year, args.month, calendar.monthrange(args.year, args.month)[1])
        date_filter = {'start': start_of_month, 'end': end_of_month}
    
    # Process transactions
    process_result = processor.process_transactions(parse_result['transactions'], date_filter)
    
    # Combine all transactions for CSV output:
    # - Categorized transactions (as-is)
    # - Multiple matches (use first match, show warning)
    # - Unmatched transactions (will get TODO category in CSV handler)
    all_for_csv = []
    all_for_csv.extend(process_result['categorized'])
    all_for_csv.extend(process_result['multiple_matches']) 
    all_for_csv.extend(process_result['unmatched'])
    
    # Write output file
    try:
        CsvHandler.write_transactions(
            args.outFileName, 
            all_for_csv, 
            args.source
        )
    except Exception as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)
    
    # Print multiple matches warnings
    for item in process_result['multiple_matches']:
        transaction = item['transaction']
        print(f"Multiple matches for: {transaction.description} ({transaction.amount})")
    
    # Print unmatched transactions
    sorted_unmatched = sorted(process_result['unmatched'], 
                             key=lambda item: item['transaction'].description)
    for item in sorted_unmatched:
        transaction = item['transaction']
        print(f"No match: {transaction.description} ({transaction.amount})")


if __name__ == "__main__":
    main()


