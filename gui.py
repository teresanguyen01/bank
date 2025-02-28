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
import tkinter as tk
from tkinter import messagebox
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
        self._window = tk.Tk()
        self._window.title("Bank Application")
        self._options_frame = tk.Frame(self._window)
        tk.Button(self._options_frame, text="Open Account", command=self._open_account).grid(row=1, column=1)
        tk.Button(self._options_frame, text="Add Transaction", command=self._add_transaction).grid(row=1, column=2)
        tk.Button(self._options_frame, text="Monthly Triggers", command=self._monthly_triggers).grid(row=1, column=3)
        tk.Button(self._options_frame, text="Quit", command=self._quit).grid(row=1, column=4)
        self._list_frame = tk.Frame(self._window)
        self._list_frame.grid(row=1, column=5, columnspan=1)
        self._options_frame.grid(row=0, column=1, columnspan=2)
        self._account_type = None
        self._session = Session()
        self._bank = self._session.get(Bank, 1)

        if self._bank is None:
            self._bank = Bank()
            self._session.add(self._bank)
            self._session.commit()
        # establishes relationship to Accounts
        self._selected_account = None
        self._window.mainloop()


    def _summary(self) -> None:
        # dependency on Account objects
        row = 0
        for x in self._bank.show_accounts():
            tk.Label(self._list_frame, text=x).grid(row=row, column=0)
            row += 1

    def _quit(self):
        self._session.close()
        sys.exit(0)

    # check here later
    def _add_transaction(self):
        def add(): 
            self._bank.add_transaction(self._session, e1.get())
            e1.destroy()
            b.destroy()
            l1.destroy()
            self._summary()

        if (self._selected_account == None):
            message = "This command requires that you first select an account."
            messagebox.showerror("Error", message)
            return
        
        def validate_amt(event, entry_widget): 
            if e1.get().isdigit(): 
                entry_widget.config(highlightbackground="green", highlightthickness=2)
            else:
                entry_widget.config(highlightbackground="red", highlightthickness=2)

        l1 = tk.Label(self._options_frame, text="Amount")
        l1.grid(row=2, column=1)
        e1 = tk.Entry(self._options_frame, command=validate_amt)
        e1.bind("<FocusOut>", lambda event, entry_widget=e1: validate_amt(event, e1))
        while amount is None: 
            try: 
                amount = Decimal(e1.get())

            except InvalidOperation as e:
                message = "Please try again with a valid dollar amount."
                amount = None
                messagebox.showerror("Error", message)

        e1.grid(row=2, column=2)
        b = tk.Button(self._options_frame, text="Submit", command=add)
        b.grid(row=2, column=3)

        amount = None
        while amount is None:
            try:
                amount = Decimal(e1.get())
            except InvalidOperation as e:
                message = "Please try again with a valid dollar amount."
                amount = None
                messagebox.showerror("Error", message)
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
        def add(): 
            if self._account_type: 
                self._bank.add_account(self._session, self._account_type)
                checking_button.destroy()
                savings_button.destroy()
                b.destroy()
                l1.destroy()
                self._summary()
                c.destroy()
                self._session.commit()

        def cancel(): 
            checking_button.destroy()
            savings_button.destroy()
            b.destroy()
            l1.destroy()
            c.destroy()

        def select_checking(): 
            self._account_type = "checking"
            checking_button.config(highlightbackground="blue")
            savings_button.config(highlightbackground="SystemButtonFace")

        def select_savings():
            self._account_type = "savings"
            savings_button.config(highlightbackground="blue")
            checking_button.config(highlightbackground="SystemButtonFace")

        l1 = tk.Label(self._options_frame, text="Account Type")
        l1.grid(row=2, column=1)
    
        checking_button = tk.Button(self._options_frame, text="Checking", command=select_checking)
        savings_button = tk.Button(self._options_frame, text="Savings", command=select_savings)
        checking_button.grid(row=2, column=2)
        savings_button.grid(row=2, column=3)
        b = tk.Button(self._options_frame, text="Submit", command=add)
        c = tk.Button(self._options_frame, text="Cancel", command=cancel) 
        b.grid(row=2, column=4)
        c.grid(row=2, column=5)

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
    BankCLI()
    #except Exception as e: 
    #    logging.error(f"{type(e).__name__}: {e}")
    #    print("Sorry! Something unexpected happened. Check the logs or contact the developer for assistance.")