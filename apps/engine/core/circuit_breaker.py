import logging
from sqlalchemy.orm import Session
from .ledger_service import LedgerService

logger = logging.getLogger(__name__)

class CircuitBreaker:
    """
    Safety module using persistent database records to prevent run-away Ad Spend.
    State is derived entirely from the DB ledger so server restarts do not reset it.
    """
    def __init__(self, max_daily_spend: float = 100.0):
        self.max_spend = max_daily_spend

    def is_tripped(self, db: Session, user_id: str) -> bool:
        """Returns True if the user has already hit or exceeded the daily spend limit."""
        daily_spend = LedgerService.get_daily_spend(db, user_id)
        return daily_spend >= self.max_spend

    def check_spend(self, db: Session, user_id: str, amount: float) -> bool:
        """
        Returns True if spend is allowed based on the database ledger.
        All state is read from the DB — survives restarts and redeployments.
        """
        # 1. Check Solvency
        current_balance = LedgerService.get_balance(db, user_id)
        if current_balance < amount:
            logger.warning("[CIRCUIT] Insufficient funds ($%.2f < $%.2f)", current_balance, amount)
            return False

        # 2. Check daily spend against persistent ledger
        daily_spend = LedgerService.get_daily_spend(db, user_id)

        if daily_spend >= self.max_spend:
            logger.warning("[CIRCUIT] Daily limit already reached ($%.2f >= $%.2f)", daily_spend, self.max_spend)
            return False

        if daily_spend + amount > self.max_spend:
            logger.warning("[CIRCUIT] Daily limit would be exceeded ($%.2f + $%.2f > $%.2f)", daily_spend, amount, self.max_spend)
            return False

        return True

    def _trip(self):
        """Kept for the manual /safety/trip endpoint — no-op since state is DB-driven."""
        logger.warning("!!! CIRCUIT TRIPPED manually via API !!!")

