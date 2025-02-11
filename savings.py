from account import Account
from datetime import datetime
from calendar import monthrange 

class Savings(Account):
    """Child class Savings that inherits methods from Account"""

    def add_transaction(self, amt, date):
        """Inherits from Account but includes its own changes -- for instance if the is a 3rd transaction that happens on the same day, we ignore it.
         If there is a 6th or more transaction for the same month/year, we ignore it. """
        date = datetime.strptime(date, "%Y-%m-%d")
        count_same_day = 0
        count_same_month = 0

        for transaction in self._transactions:
            transaction_parts = transaction.split(', ')
            transaction_date = datetime.strptime(transaction_parts[0], "%Y-%m-%d")

            if transaction_date.date() == date.date():
                count_same_day += 1

            if transaction_date.year == date.year and transaction_date.month == date.month:
               count_same_month += 1

            if count_same_day == 2: 
                return

            if count_same_month == 5: 
                return 

        return super().add_transaction(amt, date.strftime("%Y-%m-%d"))

    def interest_amounts(self):
        """Applies the 0.0033% interest for savings accounts"""
        # note: I first thought of adding this method to account and having the method be inherited and changed in the child classes, 
        # but both of the interest methods were doing very different things
        # so I decided to make them separate   
        latest_transaction_date = None

        for transaction in self._transactions:
            transaction_parts = transaction.split(', ')
            transaction_date = datetime.strptime(transaction_parts[0], "%Y-%m-%d")

            if not latest_transaction_date or transaction_date > latest_transaction_date:
                latest_transaction_date = transaction_date

        year = latest_transaction_date.year
        month = latest_transaction_date.month
        last_day_of_month = monthrange(year, month)[1]
        interest_date = datetime(year, month, last_day_of_month)

        interest = 0.0033 * self._balance

        self._balance += interest
        
        return super().add_transaction(interest, interest_date.strftime("%Y-%m-%d"))


