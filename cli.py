import os
import sys
import pickle

from decimal import Decimal, setcontext, BasicContext
from datetime import datetime

from bank import Bank

# context with ROUND_HALF_UP
setcontext(BasicContext)

class BankCLI:
    """Driver class for a command-line REPL interface to the Bank application"""

    def __init__(self) -> None:
        self._load()

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

    def _summary(self) -> None:
        # dependency on Account objects
        for x in self._bank.show_accounts():
            print(x)

    def _load(self) -> None:
        if os.path.exists("bank.pickle"):
            with open("bank.pickle", "rb") as f:
                self._bank = pickle.load(f)
        else:
            self._bank = Bank()

    def _save(self) -> None:
        with open("bank.pickle", "wb") as f:
            pickle.dump(self._bank, f)

    def _quit(self):
        self._save()
        sys.exit(0)

    def _add_transaction(self):
        amount = input("Amount?\n>")
        amount = Decimal(amount) # convert to Decimal
        date = input("Date? (YYYY-MM-DD)\n>")
        date = datetime.strptime(date, "%Y-%m-%d").date() # convert to date

        self._selected_account.add_transaction(amount, date)

    def _open_account(self):
        acct_type = input("Type of account? (checking/savings)\n>")
        self._bank.add_account(acct_type)

    def _select(self):
        num = int(input("Enter account number\n>"))
        self._selected_account = self._bank.get_account(num)

    def _monthly_triggers(self):
        self._selected_account.assess_interest_and_fees()

    def _list_transactions(self):
        for t in self._selected_account.get_transactions():
            print(t)


if __name__ == "__main__":
    BankCLI().run()