#!/usr/bin/python
import sys
import csv
import argparse
import calendar
import re
import os
from datetime import datetime, date
from receiptsParsing.transaction import Transaction

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

expectedNumFields = 6
transactions = []
journalCredit = re.compile('^JOURNAL CREDIT')
journalCredits = []
for inFile in args.inFiles:
    #print 'Reading from: ' + inFile
    with open(inFile, 'rt') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for inRow in reader:
            if not len(inRow) in (5, 6, 10):
                print("Unexpected number of fields: " + str.join(", ", inRow))
                continue

            try:
                trans = Transaction(inRow)
            except Exception as e:
                print("Failed to parse row: " + str.join(", ", inRow) + str(e))
                continue

            if journalCredit.search(trans.description):
                if trans.amount != 0:
                    print("Warning: ignoring non-zero journal credit: ", trans)
                else:
                    journalCredits.append(trans)
            else:
                if len(journalCredits):
                    if trans.amount < 0:
                        while (len(journalCredits)):
                            trans.description = journalCredits.pop().description + "; " + trans.description
                    else:
                        while (len(journalCredits)):
                            print("Warning: ignoring non-prefix journal credit: ", journalCredits.pop())
                transactions.append(trans)

transactions = sorted(transactions, key=lambda transaction: transaction.effectiveDate)

noMatchTransactions = []
startOfMonth = datetime(args.year, args.month, 1)
endOfMonth = datetime(args.year, args.month, calendar.monthrange(args.year, args.month)[1])
with open(args.outFileName, 'wt', newline='') as outFile:
    writer = csv.writer(outFile, delimiter=',')
    for transaction in transactions:
        
        if (args.readAll or transaction.postedDate >= startOfMonth and transaction.postedDate <= endOfMonth):
            purposeLists = transaction.getPurposes(purposesMap)

            if len(purposeLists) == 1:
                purposeList = purposeLists[0]
            else:
                # TODO: prompt, with autocomplete
                if len(purposeLists) > 1:
                    print("Multiple matches for: " + transaction.description + " (" + str(transaction.amount) + ")")
                    purposeList = purposeLists[0]
                else:
                    noMatchTransactions.append(transaction)
                    purposeList = ["TODO", "", ""]

            purpose0 = purposeList[0] if len(purposeList) > 0 else ""
            purpose1 = purposeList[1] if len(purposeList) > 1 else ""
            purpose2 = purposeList[2] if len(purposeList) > 2 else ""

            #dateString = "dummy"
            #dateString = transaction.postedDate.strftime("%d/%m/%y")
            #effectiveDateString = transaction.effectiveDate.strftime("%d/%m/%Y")
            #postedDateString = transaction.postedDate.strftime("%d/%m/%Y")
            effectiveDateString = transaction.effectiveDate.strftime("%Y-%m-%d")
            postedDateString = transaction.postedDate.strftime("%Y-%m-%d")
            writer.writerow([effectiveDateString, postedDateString, transaction.amount, purpose0, purpose1, purpose2, transaction.description, "", f"{transaction.source} ({args.source})" if transaction.source else args.source])

sortedNoMatchTransactions = sorted(noMatchTransactions, key=lambda transaction: transaction.description)
for noMatchTransaction in sortedNoMatchTransactions:
    print("No match: " + noMatchTransaction.description + " (" + str(noMatchTransaction.amount) + ")")


