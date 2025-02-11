from checking import Checking
from savings import Savings
from decimal import Decimal, ROUND_HALF_UP

class Bank(): 
    """Bank class models what a bank would do based on the menu choices"""
    
    def __init__(self): 
        self._accounts = []
        self._currently_selected = None
        self._size = 0
    
    def new_account(self, type): 
        """appends a new account (either checking or savings) to the list of accounts"""
        self._size += 1
        if type == "savings": 
            s = Savings(self._size, type)
            self._accounts.append(s)
        elif type == "checking": 
            c = Checking(self._size, type)
            self._accounts.append(c)   

    def all_accounts(self): 
        """returns all accounts in the bank"""
        return self._accounts

    def search(self, number): 
        """search for the account using the number and initalize the currently selected account"""
        for account in self._accounts: 
            if int(number) == account.number: 
                self._currently_selected = account
    
    def selected_print(self): 
        """this is so that way we can print the selected account in each run without accessing the private variable (_currently_selected) outside our class"""
        if self._currently_selected == None: 
            return None
        formatted_balance = Decimal(self._currently_selected._balance).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return f"{self._currently_selected._type}#{self._currently_selected.number:09d},\tbalance: ${formatted_balance:,.2f}"
    
    # Note: for functions new_transaction, all_t_list_, do_interest, we make calls to the Account class (Checking or Savings inherits the Account class)
    # this is because if we were actually modeling a bank, we wouldn't want the CLI to access the account, but rather the bank is the one to have the information and change it in Account!
    def new_transaction(self, amount, date):
        """makes a call to the function from Account to add a transaction to the object (Checking or Savings)"""
        self._currently_selected.add_transaction(amount, date)
    
    def all_t_list(self): 
        """makes a call to the function from Account to show all the transactions from the object (Checking or Savings)"""
        return self._currently_selected.all_transactions()
    
    def do_interest(self): 
        """makes a call to the function from either Checking or Savings to show all the transactions from the object (Checking or Savings)"""
        self._currently_selected.interest_amounts()
    
    def deselect(self): 
        """deselect to reset for the pickle file"""
        self._currently_selected = None

    


