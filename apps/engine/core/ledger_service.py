import logging
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from apps.engine.db.models import Ledger, User, UserEarningsDaily
from datetime import datetime, time, date
from typing import Tuple, Dict, Optional

logger = logging.getLogger(__name__)


class LedgerService:
    # 40/60 profit-sharing model
    PLATFORM_FEE_PERCENTAGE = 0.40  # Platform keeps 40%
    USER_EARNINGS_PERCENTAGE = 0.60  # User keeps 60%

    @staticmethod
    def record_transaction(
        db: Session,
        user_id: str,
        amount,
        description: str,
        transaction_type: str,
    ) -> "Ledger":
        """
        Records a transaction.
        Acquires a row-level lock on the User to prevent concurrent modification.
        """
        user = db.query(User).filter(User.id == user_id).with_for_update().first()
        if not user:
            raise ValueError(f"User {user_id} not found")

        # Shadow-ban: silently suppress income for flagged accounts
        if user.is_shadow_banned and float(amount) > 0:
            logger.warning("[LEDGER] Silencing income for shadow-banned user %s", user_id)
            return Ledger(
                user_id=user_id,
                amount=amount,
                description=f"(SILENCED) {description}",
                transaction_type=transaction_type,
            )

        # Calculate balance snapshot AFTER this transaction
        current_balance = db.query(func.sum(Ledger.amount)).filter(
            Ledger.user_id == user_id
        ).scalar() or 0.0
        balance_snapshot = float(current_balance) + float(amount)

        entry = Ledger(
            user_id=user_id,
            amount=amount,
            description=description,
            transaction_type=transaction_type,
            balance_snapshot=Decimal(str(balance_snapshot)),
        )
        db.add(entry)
        db.commit()
        return entry

    @staticmethod
    def record_affiliate_commission(
        db: Session,
        user_id: str,
        gross_revenue: float,
        affiliate_network: str,
        affiliate_source: str,
        affiliate_id: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Tuple["Ledger", Dict[str, float]]:
        """
        Records an affiliate commission with automatic 40/60 profit-sharing split.

        Args:
            gross_revenue: Total commission earned (before platform fee)
            affiliate_network: 'amazon', 'cj_affiliate', 'rakuten', 'shopify_affiliate', 'direct'
            affiliate_source: Product name or brand
            affiliate_id: Reference to affiliate account
            description: Optional custom description

        Returns:
            (ledger_entry, breakdown_dict)
            breakdown_dict = {
                'gross_revenue': 100.00,
                'platform_fee': 40.00,
                'user_earnings': 60.00,
            }
        """
        user = db.query(User).filter(User.id == user_id).with_for_update().first()
        if not user:
            raise ValueError(f"User {user_id} not found")

        gross_revenue = float(gross_revenue)
        platform_fee = gross_revenue * LedgerService.PLATFORM_FEE_PERCENTAGE
        user_earnings = gross_revenue * LedgerService.USER_EARNINGS_PERCENTAGE

        # Shadow-ban check: silently suppress income for flagged accounts
        if user.is_shadow_banned:
            logger.warning(
                "[LEDGER] Silencing commission for shadow-banned user %s", user_id
            )
            actual_user_earnings = 0.0
        else:
            actual_user_earnings = user_earnings

        description = description or f"Commission from {affiliate_source} ({affiliate_network})"

        # Calculate balance snapshot
        current_balance = db.query(func.sum(Ledger.amount)).filter(
            Ledger.user_id == user_id
        ).scalar() or 0.0
        balance_snapshot = float(current_balance) + actual_user_earnings

        entry = Ledger(
            user_id=user_id,
            amount=Decimal(str(actual_user_earnings)),
            description=description,
            transaction_type="affiliate_commission",
            gross_revenue=Decimal(str(gross_revenue)),
            platform_fee=Decimal(str(platform_fee)),
            user_earnings=Decimal(str(actual_user_earnings)),
            affiliate_network=affiliate_network,
            affiliate_source=affiliate_source,
            affiliate_id=affiliate_id,
            balance_snapshot=Decimal(str(balance_snapshot)),
        )
        db.add(entry)
        db.commit()

        return entry, {
            "gross_revenue": gross_revenue,
            "platform_fee": platform_fee,
            "user_earnings": actual_user_earnings,
        }

    @staticmethod
    def get_earnings_breakdown(
        db: Session,
        user_id: str,
        days: int = 30,
    ) -> Dict[str, any]:
        """
        Returns earnings breakdown for the last N days.

        Returns:
            {
                'period_days': 30,
                'total_gross_revenue': 3000.00,
                'total_platform_fee': 1200.00,
                'total_user_earnings': 1800.00,
                'by_network': {
                    'amazon': {'gross': 1500, 'platform_fee': 600, 'user_earnings': 900},
                    'cj_affiliate': {...},
                },
                'daily_breakdown': [...]
            }
        """
        start_date = datetime.now().date() - __import__("datetime").timedelta(days=days)

        # Get all affiliate commissions in period
        commissions = db.query(Ledger).filter(
            and_(
                Ledger.user_id == user_id,
                Ledger.transaction_type == "affiliate_commission",
                func.date(Ledger.created_at) >= start_date,
            )
        ).all()

        total_gross = sum(float(c.gross_revenue or 0) for c in commissions)
        total_platform = sum(float(c.platform_fee or 0) for c in commissions)
        total_user = sum(float(c.user_earnings or 0) for c in commissions)

        # Breakdown by network
        by_network = {}
        for commission in commissions:
            network = commission.affiliate_network or "unknown"
            if network not in by_network:
                by_network[network] = {
                    "gross_revenue": 0.0,
                    "platform_fee": 0.0,
                    "user_earnings": 0.0,
                    "count": 0,
                }
            by_network[network]["gross_revenue"] += float(commission.gross_revenue or 0)
            by_network[network]["platform_fee"] += float(commission.platform_fee or 0)
            by_network[network]["user_earnings"] += float(commission.user_earnings or 0)
            by_network[network]["count"] += 1

        return {
            "period_days": days,
            "total_gross_revenue": total_gross,
            "total_platform_fee": total_platform,
            "total_user_earnings": total_user,
            "platform_fee_percentage": LedgerService.PLATFORM_FEE_PERCENTAGE * 100,
            "by_network": by_network,
            "commission_count": len(commissions),
        }

    @staticmethod
    def deduct_if_solvent(
        db: Session,
        user_id: str,
        amount: float,
        description: str,
        transaction_type: str,
    ) -> Tuple[bool, float]:
        """
        Atomically checks balance and records a debit in a single locked transaction.
        This eliminates the check-then-act race condition.

        Returns:
            (success, new_balance)
        """
        user = db.query(User).filter(User.id == user_id).with_for_update().first()
        if not user:
            return False, 0.0

        balance = db.query(func.sum(Ledger.amount)).filter(
            Ledger.user_id == user_id
        ).scalar()
        balance = float(balance or 0.0)

        if balance < amount:
            logger.warning(
                "[LEDGER] Insufficient funds for %s: balance=%.2f required=%.2f",
                user_id, balance, amount,
            )
            return False, balance

        balance_snapshot = balance - amount

        entry = Ledger(
            user_id=user_id,
            amount=Decimal(str(-amount)),
            description=description,
            transaction_type=transaction_type,
            balance_snapshot=Decimal(str(balance_snapshot)),
        )
        db.add(entry)
        db.commit()
        return True, balance_snapshot

    @staticmethod
    def get_daily_spend(db: Session, user_id: str) -> float:
        """Returns total spend (positive number) for the current calendar day."""
        today = datetime.now().date()
        start_of_day = datetime.combine(today, time.min)

        spend = db.query(func.sum(Ledger.amount)).filter(
            Ledger.user_id == user_id,
            Ledger.amount < 0,
            Ledger.created_at >= start_of_day,
        ).scalar()
        return abs(float(spend or 0.0))

    @staticmethod
    def get_balance(db: Session, user_id: str) -> float:
        """Returns current balance by summing all ledger entries."""
        balance = db.query(func.sum(Ledger.amount)).filter(
            Ledger.user_id == user_id
        ).scalar()
        return float(balance or 0.0)

    @staticmethod
    def check_funds(db: Session, user_id: str, required_amount: float) -> bool:
        """Quick non-locking solvency check (use deduct_if_solvent for atomic ops)."""
        return LedgerService.get_balance(db, user_id) >= required_amount
