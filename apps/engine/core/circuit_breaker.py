from sqlalchemy.orm import Session
from .ledger_service import LedgerService

class CircuitBreaker:
    """
    Safety module using persistent database records to prevent run-away Ad Spend.
    """
    def __init__(self, max_daily_spend: float = 100.0):
        self.max_spend = max_daily_spend
        self.is_open = False 

    def check_spend(self, db: Session, user_id: str, amount: float) -> bool:
        """
        Returns True if spend is allowed based on the database ledger.
        """
        if self.is_open:
            return False
        
        # 1. Check Solvency (Economy 2.0)
        current_balance = LedgerService.get_balance(db, user_id)
        if current_balance < amount:
            print(f"[CIRCUIT] Insufficient funds (${current_balance:.2f} < ${amount:.2f})")
            return False

        # 2. Query Ledger for daily spend
        daily_spend = LedgerService.get_daily_spend(db, user_id)
        
        if daily_spend > self.max_spend:
            # CRITICAL: We are already over budget! The previous check failed or race condition occurred.
            self._trigger_panic(daily_spend)
            return False

        if daily_spend + amount > self.max_spend:
            print(f"[CIRCUIT] Daily limit reached (${daily_spend:.2f} + ${amount:.2f} > ${self.max_spend})")
            self._trip()
            return False
            
        return True

    def _trip(self):
        self.is_open = True
        print("!!! CIRCUIT TRIPPED !!! MAX SPEND EXCEEDED.")

    def _trigger_panic(self, current_spend: float):
        self.is_open = True
        print(f"🚨 BOOTSTRAPPER PANIC METHOD 🚨: DETECTED SPEND ${current_spend:.2f} > LIMIT ${self.max_spend}")
        print("Creating emergency stop signal... (Simulated)")
        # In real implementation: automated email to user + kill switch on payment gateway

