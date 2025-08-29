# Receipt/Transaction Parsing System

A Python-based bank transaction parsing and categorization system that automatically processes CSV exports from various banks and categorizes transactions for financial analysis.

## Overview

This tool reads CSV files from bank exports (primarily UBank format), applies intelligent pattern matching to categorize transactions into meaningful categories, and outputs structured CSV files ready for financial analysis or import into other systems.

## Features

- **Multi-format CSV support**: Handles UBank (old/new formats) and loans.com.au CSV exports
- **Automatic categorization**: Uses regex pattern matching against a hierarchical category system
- **Date range filtering**: Process all transactions or filter by specific months/years  
- **Backup system**: Automatically backs up previous outputs before processing
- **Transaction validation**: Handles journal credits and transaction merging
- **Uncategorized detection**: Lists transactions that couldn't be automatically categorized

## Quick Start

1. Place your bank CSV export in the `in/` directory (e.g., `in/in.ubank.csv`)
2. Run the automated processing script:
   ```bash
   ./parse_csv.all.sh
   ```
3. Find your categorized transactions in `out/out.csv`

## Usage

### Basic Processing
```bash
# Process all transactions from input CSV
python parse_csv.py --readAll --outFileName out/output.csv --source BankName input.csv

# Process specific month/year
python parse_csv.py --year 2025 --month 8 --outFileName out/output.csv input.csv
```

### Automated Processing
```bash
# Process UBank CSV from in/ to out/ with automatic backup
./parse_csv.all.sh
```

## File Structure

```
├── in/                     # Input CSV files
│   └── in.ubank.csv       # Your bank export goes here
├── out/                   # Processed output files
│   ├── out.csv           # Combined categorized transactions
│   └── out.ubank.csv     # Bank-specific output
├── bkp/                   # Timestamped backups
├── receiptsParsing/       # Core Python module
│   └── transaction.py     # Transaction parsing logic
├── parse_csv.py          # Main processing script
├── parse_csv.sh          # Processing wrapper
└── parse_csv.all.sh      # Automated processing script
```

## Supported CSV Formats

- **UBank new format** (10 fields): Date/time, Description, Debit, Credit, From account, To account, Payment type, Category, Receipt number, Transaction ID
- **UBank old format** (5 fields): Blank, Posted date, Description, Accounting string, Balance  
- **loans.com.au format** (6 fields): Posted date, Effective date, Description, Debit, Credit, Balance

## Output Format

The processed CSV contains these columns:
- Effective Date (YYYY-MM-DD)
- Posted Date (YYYY-MM-DD)  
- Amount (positive for credits, negative for debits)
- Category Level 1 (e.g., "Bills", "Groceries", "Transport")
- Category Level 2 (e.g., "Electricity", "Health", "Telecom")
- Category Level 3 (e.g., "Netflix", "Pharmacy", "Uber")
- Description (original transaction description)
- Notes (empty field for manual notes)
- Source (bank/account identifier)

## Category System

The system includes pre-configured categories for:
- **Revenue**: Salary, transfers, interest
- **Bills**: House, electricity, health, telecom, childcare
- **Groceries**: Supermarkets, organic stores
- **Discretionary**: Eating out, entertainment
- **Transport**: Public transport, rideshare, parking, tolls
- **Assets**: Home improvement, investments

## Customization

To add new transaction patterns:
1. Edit the `purposesMap` dictionary in `parse_csv.py`
2. Add regex patterns that match your transaction descriptions
3. Organize patterns into the hierarchical category structure

## Requirements

- Python 3.x
- Standard library modules (csv, datetime, decimal, re, argparse)

## License

This is a personal financial tool. Use and modify as needed for your own transaction processing.