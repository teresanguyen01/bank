from __future__ import annotations

from decimal import Decimal
from exceptions import OverdrawError, TransactionSequenceError, TransactionLimitError, TransactionDateError
from sqlalchemy import Integer, String, ForeignKey, DateTime, Text, Column
from sqlalchemy.orm import mapped_column, relationship, backref
from sqlalchemy.orm import Mapped
from bank import Base
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime

from transactions import Transaction
import logging

class Account(Base):
    """This is an abstaact class for accounts.  Provides default functionality for adding transactions, getting balances, and assessing interest and fees.  
    Accounts should be instantiated as SavingsAccounts or CheckingAccounts
    """
    __tablename__ = "account"
    _id = mapped_column(Integer, primary_key=True)
    _bank_id = mapped_column(Integer, ForeignKey("bank._id"))
    _account_number = mapped_column(Integer)
    _account_type = mapped_column(String)
    _transactions = relationship("Transaction", backref=backref("_account"))

    __mapper_args__ = {
        'polymorphic_identity': 'account',
        'polymorphic_on': _account_type
    }

    def __init__(self, acct_num) -> None:
        self._account_number = acct_num

    def _get_acct_num(self) -> int:
        return self._account_number

    account_number = property(_get_acct_num)

    def add_transaction(self, session, amt, date, exempt=False) -> None:
        """Creates a new transaction and checks to see if it is allowed, adding it to the account if it is.

        Args:
            amt (Decimal): amount for new transaction
            date (Date): Date for the new transaction.
            exempt (bool, optional): Determines whether the transaction is exempt from account limits. Defaults to False.
        """
        t = Transaction(amt, date, exempt)
        
        # Logic is broken up into pieces and factored out into other methods.
        # This makes it easier to override specific parts of add_transaction.
        # This is called a Template Method design pattern
        if self._transactions: 
            latest_transaction = max(self._transactions, key=lambda trans: trans._date) # make sure its using datetime.date
            latest_date = latest_transaction._date.date() if isinstance(latest_transaction._date, datetime) else latest_transaction._date
            if date < latest_date: 
                raise TransactionSequenceError(error_type="balance", latest_date=latest_date)
        balance_ok = self._check_balance(t)
        if (balance_ok == False and not t.is_exempt()): 
            raise OverdrawError()
        
        limits_ok = self._check_limits(t)
        if t.is_exempt() or (balance_ok and limits_ok):
            logging.debug(f"Created transaction: {self._account_number} {amt}")
            self._transactions.append(t)
            session.add(t)
            session.commit()

    def _check_balance(self, t) -> bool:
        """Checks whether an incoming transaction would overdraw the account

        Args:
            t (Transaction): pending transaction

        Returns:
            bool: false if account is overdrawn
        """
        return t.check_balance(self.get_balance())

    def _check_limits(self, t) -> bool:
        return True

    def get_balance(self) -> Decimal:
        """Gets the balance for an account by summing its transactions

        Returns:
            Decimal: current balance
        """
        # could have a balance variable updated when transactions are added (or removed) which is faster
        # but this is more foolproof since it's always in sync with transactions
        # this could be improved by caching the sum to avoid too much
        # recalculation, while still maintaining the list as the ground truth
        return sum(self._transactions)

    def _assess_interest(self, latest_transaction, session) -> None:
        """Calculates interest for an account balance and adds it as a new transaction exempt from limits.
        """
        if self._transactions: 
            latest_transaction = max(self._transactions, key=lambda trans: trans._date)
            if any(t for t in self._transactions if t.is_exempt() and t.in_same_month(latest_transaction)):
                raise TransactionSequenceError(error_type="interest", latest_date=latest_transaction._date)
        if latest_transaction == None: 
            raise TransactionDateError()
        self.add_transaction(session, self.get_balance() * self._interest_rate, 
                        date=latest_transaction.last_day_of_month(), 
                        exempt=True)


    def _assess_fees(self, latest_transaction, session) -> None:
        pass

    def assess_interest_and_fees(self, session) -> None:
        """Used to apply interest and/or fees for this account"""
        if not self._transactions: 
            self._assess_interest(None, session)
            self._assess_fees(None, session)
            return
        latest_transaction = max(self._transactions)
        self._assess_interest(latest_transaction, session)
        self._assess_fees(latest_transaction, session)

    def __str__(self) -> str:
        """Formats the account number and balance of the account.
        For example, '#000000001,<tab>balance: $50.00'
        """
        return f"#{self._account_number:09},\tbalance: ${self.get_balance():,.2f}"

    def get_transactions(self) -> list[Transaction]:
        "Returns sorted list of transactions on this account"
        return sorted(self._transactions)


class SavingsAccount(Account):
    """Concrete Account class with daily and monthly account limits and high interest rate.
    """
    __mapper_args__ = {
        'polymorphic_identity': 'savings'
    }

    _interest_rate = Decimal("0.0033")
    _daily_limit = 2
    _monthly_limit = 5

    def __init__(self, acct_num, *args, **kwargs) -> None:
        super().__init__(acct_num, *args, **kwargs)

    def _check_limits(self, t1) -> bool:
        """determines if the incoming trasaction is within the accounts transaction limits

        Args:
            t1 (Transaction): pending transaction to be checked

        Returns:
            bool: true if within limits and false if beyond limits
        """
        # Count number of non-exempt transactions on the same day as t1

        num_today = 0
        for t2 in self._transactions:
            if not t2.is_exempt() and t2.in_same_day(t1):
                num_today += 1
        # Count number of non-exempt transactions in the same month as t1
        num_this_month = 0
        for t2 in self._transactions:
            if not t2.is_exempt() and t2.in_same_month(t1):
                num_this_month += 1
        # check counts against daily and monthly limits
        if num_today >= self._daily_limit:
            raise TransactionLimitError("day", self._daily_limit)
        elif num_this_month >= self._monthly_limit:
            raise TransactionLimitError("month", self._monthly_limit)
        return True
    

    def __str__(self) -> str:
        """Formats the type, account number, and balance of the account.
        For example, 'Savings#000000001,<tab>balance: $50.00'
        """
        return "Savings" + super().__str__()


class CheckingAccount(Account):
    """Concrete Account class with lower interest rate and low balance fees.
    """
    __mapper_args__ = {
        'polymorphic_identity': 'checking'
    }
    
    _interest_rate = Decimal("0.0008")
    _balance_threshold = 100
    _low_balance_fee = Decimal("-5.75")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._interest_rate = Decimal("0.0008")
        self._balance_threshold = 100
        self._low_balance_fee = Decimal("-5.75")

    def _assess_fees(self, latest_transaction, session) -> None:
        """Adds a low balance fee if balance is below a particular threshold. Fee amount and balance threshold are defined on the CheckingAccount.
        """
        if latest_transaction == None: 
            raise TransactionSequenceError("balance", latest_transaction)
        if self.get_balance() < self._balance_threshold:
            self.add_transaction(session, self._low_balance_fee,
                                 date=latest_transaction.last_day_of_month(), 
                                 exempt=True)

    def __str__(self) -> str:
        """Formats the type, account number, and balance of the account.
        For example, 'Checking#000000001,<tab>balance: $50.00'
        """
        return "Checking" + super().__str__()
