from sqlalchemy.orm import Session
from sqlalchemy import func
from apps.engine.db.models import Ledger
from datetime import datetime, time

class LedgerService:
    @staticmethod
    def record_transaction(db: Session, user_id: str, amount: float, description: str, transaction_type: str):
        """
        Records a transaction.
        CRITICAL: Locks the User row to ensure sequential processing of financial transactions.
        """
        # 1. Lock the User row to prevent concurrent modifications
        from apps.engine.db.models import User
        user = db.query(User).filter(User.id == user_id).with_for_update().first()
        
        if not user:
            raise ValueError(f"User {user_id} not found")

        entry = Ledger(
            user_id=user_id,
            amount=amount,
            description=description,
            transaction_type=transaction_type
        )
        db.add(entry)
        db.commit()
        return entry

    @staticmethod
    def get_daily_spend(db: Session, user_id: str) -> float:
        """
        Calculates total negative spend for the current day.
        """
        today = datetime.now().date()
        start_of_day = datetime.combine(today, time.min)
        
        spend = db.query(func.sum(Ledger.amount)).filter(
            Ledger.user_id == user_id,
            Ledger.amount < 0,
            Ledger.created_at >= start_of_day
        ).scalar()
        
        return abs(float(spend or 0.0))


    @staticmethod
    def get_balance(db: Session, user_id: str) -> float:
        """
        Returns the current user balance by summing all transactions.
        """
        balance = db.query(func.sum(Ledger.amount)).filter(Ledger.user_id == user_id).scalar()
        return float(balance or 0.0)

    @staticmethod
    def check_funds(db: Session, user_id: str, required_amount: float) -> bool:
        """
        Returns True if user has enough positive balance to cover the cost.
        """
        balance = LedgerService.get_balance(db, user_id)
        return balance >= required_amount
