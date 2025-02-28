import calendar

class OverdrawError(Exception):
    """Raised when a transaction exceeds the account balance."""
    def __init__(self):
        super().__init__()
    
class TransactionSequenceError(Exception):
    """Raised when a transaction occurs out of sequence."""
    def __init__(self, error_type, latest_date): # error type is either "balance" or "interest"
        self.latest_date = latest_date
        self.error_type = error_type
        super().__init__()

class TransactionLimitError(Exception):
    """Raised when a transaction exceeds the allowed limit."""
    def __init__(self, limit_type, limit):
        super().__init__()
        self.limit_type = limit_type
        self.limit = limit

class TransactionDateError(Exception):
    """Raised when interest is applied to an account with no transactions"""
    def __init__(self):
        super().__init__()

