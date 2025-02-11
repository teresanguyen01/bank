from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime

class Account:
    """Parent class Account that includes methods that pertain to an Account such as adding transactions and all transactions"""

    def __init__(self, size, type): 
        self._balance = 0
        self._transactions = []
        self.number = size # set this to public because I use this for the search method in Bank class
        self._type = type[0].upper() + type[1:].lower()
    
    def add_transaction(self, amt, date): 
        """first checks if the withdrawal is greater than the balance and if so, break
        else, format the value to use round half up, append to transactions, and apply the transaction to the balance
        """
        if (float(amt) < 0) and (abs(float(amt)) > self._balance):
            return
        formatted_amt = Decimal(float(amt)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        self._transactions.append(f"{date}, ${(formatted_amt):,.2f}")
        self._balance = self._balance + float(amt)
    
    def all_transactions(self):
        """sort based on date and if the date is the same, leave it as it is"""
        self._transactions.sort(key=lambda transaction: datetime.strptime(transaction.split(', ')[0], "%Y-%m-%d"))
        return self._transactions

    def __str__(self): 
        """if we need to print out the transaction, it would be formatted this way"""
        formatted_balance = Decimal(self._balance).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return f"{self._type}#{self.number:09d},\tbalance: ${formatted_balance:,.2f}"
    