from accounts import Account
from datetime import datetime
from calendar import monthrange 

class Checking(Account):
    """Child class Checking that inherits methods from Account"""

    def interest_amounts(self):
        """Applies the 0.08% interest for checking accounts and if the balance is less than 100, add a transaction fee"""
        # note: I first thought of adding this method to account and having the method be inherited and changed in the child classes, 
        # but both of the interest methods were doing very different things
        # so I decided to make them separate
        latest_transaction_date = None

        # go through all the transactions and see the latest month
        for transaction in self._transactions:
            transaction_parts = transaction.split(', ')
            transaction_date = datetime.strptime(transaction_parts[0], "%Y-%m-%d")

            if not latest_transaction_date or transaction_date > latest_transaction_date:
                latest_transaction_date = transaction_date

        year = latest_transaction_date.year
        month = latest_transaction_date.month
        last_day_of_month = monthrange(year, month)[1]
        interest_date = datetime(year, month, last_day_of_month)

        interest = 0.0008 * self._balance

        super().add_transaction(interest, interest_date.strftime("%Y-%m-%d"))
        
        # if balance is less than 100, add the penalty (only for Checking accounts)
        if self._balance < 100: 
            return super().add_transaction(-5.75, interest_date.strftime("%Y-%m-%d"))
        return 
