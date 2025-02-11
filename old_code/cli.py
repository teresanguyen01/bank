import os
import sys
import pickle
from typing import NoReturn


from bank import Bank

class Cli:
    """Display a bank and respond to choices when run."""

    def __init__(self) -> None: 
        """Initializes the bank.
        If there is a local save file named bank.pickle, it loads it.
        Otherwise, it creates a new bank."""
        self._load()
    
    def _display_menu(self) -> None: 
        print(
            """Enter command
1: open account
2: summary
3: select account
4: add transaction
5: list transactions
6: interest and fees
7: quit"""
                    )
        
    def run(self) -> NoReturn:
        """Runs when "CLI" is started"""        
        while True: 
            print("--------------------------------")
            print(f"Currently selected account: {self._bank.selected_print()}")
            self._display_menu()
            choice = input(">")
            if choice == "1": 
                self._open_account()
            elif choice == "2": 
                self._summary()
            elif choice == "3": 
                self._select_account()
            elif choice == "4":
                self._add_transaction()
            elif choice == "5":
                self._list_transactions()
            elif choice == "6": 
                self._interest_and_fees()
            elif choice == "7": 
                self._save()
                self._quit()
        
    def _open_account(self) -> None: 
        choice = input("Type of account? (checking/savings)\n>")
        self._bank.new_account(choice)
    
    def _summary(self, accounts=None) -> None: 
        if accounts is None: 
            accounts = self._bank.all_accounts()
        for account in accounts:
            print(account)
    
    def _select_account(self) -> None: 
         number = input("Enter account number\n>")
         self._bank.search(number) # will need to add here

    def _add_transaction(self) -> None: 
         amount = input("Amount?\n>")
         date = input("Date? (YYYY-MM-DD)\n>")
         self._bank.new_transaction(amount, date)
    
    def _list_transactions(self) -> None: 
        transactions = self._bank.all_t_list()
        for transaction in transactions: 
            print(transaction)
        
    def _interest_and_fees(self) -> None: 
         self._bank.do_interest()

    def _save(self) -> None: 
        self._bank.deselect()
        with open("bank.pickle", "wb") as f: 
            pickle.dump(self._bank, f)

    def _load(self) -> None: 
        if os.path.exists("bank.pickle"): 
            with open("bank.pickle", "rb") as f: 
                self._bank = pickle.load(f)
        else: 
            self._bank = Bank()

    def _quit(self) -> NoReturn: 
        sys.exit(0)

if __name__ == "__main__":
    Cli().run()
