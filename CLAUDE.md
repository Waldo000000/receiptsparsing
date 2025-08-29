# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based receipt/bank transaction parsing and categorization system. It reads CSV files from bank exports (primarily UBank format), applies pattern matching to categorize transactions into meaningful categories, and outputs structured CSV files for financial analysis.

## Architecture

- **parse_csv.py**: Main entry point for processing CSV files with configurable date ranges and output files
- **receiptsParsing/transaction.py**: Core Transaction class that handles parsing different CSV formats and pattern matching
- **purposes_config.py**: Personal configuration file containing transaction categorization patterns (gitignored)
- **Shell scripts**: Automation wrappers for common processing workflows

The system uses a hierarchical category mapping loaded from `purposes_config.py` that matches transaction descriptions against regex patterns to automatically categorize expenses into areas like Bills, Groceries, Transport, etc.

## Key Commands

### Processing Bank CSV Files
```bash
# Process all transactions from input CSV
python parse_csv.py --readAll --outFileName out/output.csv --source BankName input.csv

# Process specific month/year
python parse_csv.py --year 2025 --month 8 --outFileName out/output.csv input.csv

# Use the automated script (processes UBank CSV from in/ to out/)
./parse_csv.all.sh
```

### File Structure
- `in/`: Input CSV files (e.g., in.ubank.csv)
- `out/`: Processed output CSV files
- `bkp/`: Timestamped backups of previous outputs
- `receiptsParsing/`: Core Python module

## CSV Format Support

The system handles multiple CSV formats:
- **UBank new format** (10 fields): Date/time, Description, Debit, Credit, From account, To account, Payment type, Category, Receipt number, Transaction ID
- **UBank old format** (5 fields): Blank, Posted date, Description, Accounting string, Balance
- **loans.com.au format** (6 fields): Posted date, Effective date, Description, Debit, Credit, Balance

## Configuration Setup

Before first use, you must create your personal configuration file:

```bash
# Copy the example configuration
cp purposes_config.example.py purposes_config.py

# Edit with your personal transaction patterns
# This file is gitignored and will not be committed to version control
```

The configuration file contains hierarchical mappings of transaction patterns to categories. Customize the patterns to match your bank transaction descriptions.

## Output Format

Generated CSV contains: Effective Date, Posted Date, Amount, Category Level 1, Category Level 2, Category Level 3, Description, Notes, Source

Transactions without category matches are marked with "TODO" and listed at the end of processing for manual review.