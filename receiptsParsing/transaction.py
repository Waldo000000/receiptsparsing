#!/user/bin/python
#import sys
import time, datetime
from decimal import Decimal
import re

#descriptionRe = re.compile('VISA PURCHASE   (.*)[0-9]{2}/[0-9]{2} AU AUD')

class Transaction:
  def __init__(self, inRow):

    self.source = ""
    if len(inRow) == 6:
        # loans.com.au
        (postedDateRaw, effectiveDateRaw, description, debit, credit, balance) = inRow
        amount = self.__flipSign(debit or credit)
    if len(inRow) == 5:
        # ubank old
        (blank, postedDateRaw, description, accountingStr, balance) = inRow
        effectiveDateRaw = postedDateRaw # ubank only shows one "transaction date"
        amount = self.__flipSign(accountingStr)
    if len(inRow) == 10:
        # ubank new, from "activity" view
        (dateAndTime, descriptionRaw, debit, credit, fromAccount, toAccount, paymentType, category, receiptNumber, transactionId) = inRow

        description = descriptionRaw + "; " + "; ".join(f"{name}: {value}" for name, value in [("From account", fromAccount), ("To account", toAccount), ("Payment type", paymentType), ("Category", category), ("Receipt number", receiptNumber), ("Transaction ID", transactionId)] if value)

        # set amount
        if debit:
            amount = Decimal(self.__parseCurrency(debit))
            self.source = fromAccount
        else:
            amount = Decimal(self.__parseCurrency(credit)) * -1
            self.source = toAccount

        # ubank only shows one "transaction date"
        postedDateRaw = dateAndTime
        effectiveDateRaw = dateAndTime
        
    self.postedDate = self.__formatDate(postedDateRaw)
    self.effectiveDate = self.__formatDate(effectiveDateRaw or postedDateRaw)
    self.description = description
    self.amount = amount
  
  def __parseCurrency(self, currencyStr):
    return currencyStr.replace("$", "").replace(",", "")

  def __formatDate(self, dateStr):
    formats = ["%d/%m/%Y", "%H:%M %d-%m-%y"]
    for format_str in formats:
        try:
            return datetime.datetime.strptime(dateStr, format_str)
            break
        except ValueError:
            pass
    raise ValueError('no valid date format found')

  def __flipSign(self, accountingStr):
      return Decimal(re.sub(r'[^\d.-]', '', accountingStr.strip())) * -1

  def getPurposes(self, purposesMap):
    matches = []
    self.__getPurposes(purposesMap, matches)
    return matches

  def __getPurposes(self, purposesMap, matches):
    for purpose, value in purposesMap.items():
      path = [purpose]

      if hasattr(value, 'items'):
        self.__innerGetPurposes(value, matches, path)
      else:
        for pattern in value:
          #print "-> re", re
          #print "-> re.pattern: ", re.pattern, "<"
          if re.search(pattern, self.description, re.IGNORECASE):
            #print "-> match", pattern
            matches.append(path)

  def __innerGetPurposes(self, purposesMap, matches, path):
    for purpose, value in purposesMap.items():
      #revert: path.append(purpose)
      p = path + [purpose]

      if hasattr(value, 'items'):
        self.__innerGetPurposes(value, matches, p)
      else:
        for pattern in value:
          if re.search(pattern, self.description, re.IGNORECASE):
            #print "-> match (", pattern.pattern, "); ",self.description
            #print "--> p: ",p
            matches.append(p)

  def __str__(self):
    return str.join(", ", [self.effectiveDate.strftime("%d/%m/%Y"), self.postedDate.strftime("%d/%m/%Y"), self.description, str(self.amount)])

