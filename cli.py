import os
import sys
import pickle
from exceptions import OverdrawError, TransactionSequenceError, TransactionLimitError, TransactionDateError
import logging
import calendar
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from decimal import Decimal, setcontext, BasicContext, InvalidOperation
from datetime import datetime

from bank import Bank, Base

logging.basicConfig(
    filename='bank.log',
    format='%(asctime)s|%(levelname)s|%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.DEBUG
)
# context with ROUND_HALF_UP
setcontext(BasicContext)

class BankCLI:
    """Driver class for a command-line REPL interface to the Bank application"""
    def __init__(self) -> None:
        self._session = Session()
        self._bank = self._session.get(Bank, 1)
        if self._bank is None:
            self._bank = Bank()
            self._session.add(self._bank)
            self._session.commit()
        # establishes relationship to Accounts
        self._selected_account = None

        self._choices = {
            "1": self._open_account,
            "2": self._summary,
            "3": self._select,
            "4": self._add_transaction,
            "5": self._list_transactions,
            "6": self._monthly_triggers,
            "7": self._quit,
        }

    def _display_menu(self):
        print(f"""--------------------------------
Currently selected account: {self._selected_account}
Enter command
1: open account
2: summary
3: select account
4: add transaction
5: list transactions
6: interest and fees
7: quit""")

    def run(self):
        """Display the menu and respond to choices."""
        while True:
            self._display_menu()
            choice = input(">")
            action = self._choices.get(choice)
            # expecting a digit 1-9
            if action:
                action()
            else: 
                print("{0} is not a valid choice".format(choice))

    def _summary(self) -> None:
        # dependency on Account objects
        for x in self._bank.show_accounts():
            print(x)

    def _quit(self):
        self._session.close()
        sys.exit(0)

    # check here later
    def _add_transaction(self):
        if (self._selected_account == None): 
            message = "This command requires that you first select an account."
            print(message)
            return
        amount = None
        while amount is None:
            try:
                amount = input("Amount?\n>")
                amount = Decimal(amount)
            except InvalidOperation as e:
                message = "Please try again with a valid dollar amount."
                amount = None
                print(message)
        date = None
        while not date: 
            try: 
                date = datetime.strptime(input("Date? (YYYY-MM-DD)\n>"), "%Y-%m-%d").date()
            except ValueError as e:
                print("Please try again with a valid date in the format YYYY-MM-DD.")
        try: 
            self._selected_account.add_transaction(self._session, amount, date)
            self._session.commit()
        except OverdrawError as e: 
            print("This transaction could not be completed due to an insufficient account balance.")
        except TransactionSequenceError as e: 
            if e.error_type == "balance": 
                print(f"New transactions must be from {e.latest_date} onward.")
            elif e.error_type == "interest":
                print(f"This transaction could not be completed because the account already has a transaction in {e.latest_date}.")
        except TransactionLimitError as e: 
            print(f"This transaction could not be completed because this account already has {e.limit} transactions in this {e.limit_type}.")


    def _open_account(self):
        acct_type = input("Type of account? (checking/savings)\n>")
        self._bank.add_account(self._session, acct_type)
        self._session.commit()

    def _select(self):
        num = int(input("Enter account number\n>"))
        self._selected_account = self._bank.get_account(num)

    def _monthly_triggers(self):
        try: 
            self._selected_account.assess_interest_and_fees(self._session)
            logging.debug("Triggered interest and fees")
        except TransactionSequenceError as e: 
            print(f"Cannot apply interest and fees again in the month of {calendar.month_name[e.latest_date.month]}.")
        except TransactionDateError as e: 
            print("No transactions have been made on this account yet.")
        except AttributeError as e: 
            print("This command requires that you first select an account.")
        self._session.commit()

    def _list_transactions(self):
        try: 
            for t in self._selected_account.get_transactions():
                print(t)
        except AttributeError as e: 
            print("This command requires that you first select an account.")


if __name__ == "__main__":
    # Run the CLI - if an exception occurs, log it and print a message to the user
    #try: 
    engine = create_engine('sqlite:///bank.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine)
    BankCLI().run()
    #except Exception as e: 
    #    logging.error(f"{type(e).__name__}: {e}")
    #    print("Sorry! Something unexpected happened. Check the logs or contact the developer for assistance.")