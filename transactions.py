from sqlalchemy import ForeignKey, Column, Integer, Numeric, DateTime, Boolean
from sqlalchemy.orm import relationship, backref
from datetime import date, timedelta
from decimal import Decimal
from bank import Base

class Transaction(Base):
    __tablename__ = "transaction"
    _id = Column(Integer, primary_key=True)
    _amt = Column(Numeric)
    _date = Column(DateTime)
    _exempt = Column(Boolean)
    _account_id = Column(Integer, ForeignKey("account._id"))
    
    def __init__(self, amt, date, exempt=False):
        """
        Args:
            amt (Decimal): Decimal object representing dollar amount of the transaction.
            date (Date): Date object representing the date the transaction was created.
            exempt (bool, optional): Determines whether the transaction is exempt from account limits. Defaults to False.
        """ 
        self._amt = amt
        self._date = date
        self._exempt = exempt

    def __str__(self) -> str:
        """Formats the date and amount of this transaction
        For example, 2022-9-15, $50.00'
        """
        return f"{self._date.date()}, ${self._amt:,.2f}"

    def is_exempt(self) -> bool:
        "Check if the transaction is exempt from account limits"
        return self._exempt

    def in_same_day(self, other) -> bool:
        "Takes in a transaction object and checks whether this transaction shares the same date"
        return self._date.date() == other._date

    def in_same_month(self, other) -> bool:
        "Takes in a transaction object and checks whether this transaction shares the same month and year"
        return self._date.month == other._date.month and self._date.year == other._date.year

    def __radd__(self, other) -> Decimal:
        "Adds Transactions by their amounts"

        # allows us to use sum() with transactions
        return other + self._amt

    def check_balance(self, balance) -> bool:
        "Takes in an amount and checks whether this transaction would withdraw more than that amount"
        return self._amt >= 0 or balance >= abs(self._amt)

    def __lt__(self, value) -> bool:
        "Compares Transactions by date"

        # Note that I did not include the ComparableMixin here.
        # It is not needed since only less than is used currently.
        # More importantly, it makes sense to do this comparison by date, 
        # but if we base all the others off of this, including __eq__, 
        # then we could run into a bug down the road where all transactions 
        # on the same date are treated as equal. This probably isn't what 
        # you would want to happen, so it's better to manually write another 
        # __eq__ method as needed that can also check the amount, or some other 
        # identifier to make transactions unique.
        return self._date < value._date

    def last_day_of_month(self) -> date:
        "Returns a date corresponding to the last day in the same month as this transaction"

        # Creates a date on the first of the next month (being careful about
        # wrapping around to January)
        first_of_next_month = date(self._date.year + self._date.month // 12,
                                   self._date.month % 12 + 1, 1)
        # Then subtracts one day
        return first_of_next_month - timedelta(days=1)
