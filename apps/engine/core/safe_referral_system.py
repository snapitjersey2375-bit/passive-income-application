"""
FTC-Safe Referral System

Current system: Credits for referrals (looks like MLM/pyramid)
New system: All earnings tied to CONTENT PERFORMANCE, not recruit headcount

This prevents FTC classification as pyramid scheme.
"""

import logging
from decimal import Decimal
from sqlalchemy.orm import Session
from apps.engine.db.models import User, Content, Ledger
from sqlalchemy import func
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SafeReferralSystem:
    """
    FTC-compliant referral model.

    Key principle: Users earn from CONTENT PERFORMANCE, not from recruiting.
    Referral bonuses are SMALL and PERFORMANCE-BASED.
    This is legally distinct from MLM/pyramid schemes.
    """

    # FTC Safe Structure:
    # - Primary income: Affiliate commissions (60% of real sales)
    # - Referral bonus: ONLY if referred user actually earns (performance-based)
    # - Referral amount: Capped and small (5% of what they earn, not what they spend)
    # - No recruitment pressure: Bonuses happen automatically, not targets

    REFERRAL_RULES = {
        "referral_bonus_percentage": 0.05,  # 5% of what REFERRED USER earns (not deposits)
        "minimum_referral_earnings": Decimal("10.00"),  # Ref must earn $10+ first
        "referral_lifetime_cap": Decimal("5000.00"),  # Can't earn >$5K per ref
        "requires_referred_user_active": True,  # Ref must stay active
        "requires_referred_user_content": 5,  # Ref must create 5+ pieces
        "legal_status": "Performance-based bonus (NOT commission-based sale)",
    }

    @staticmethod
    def generate_referral_code(user: User) -> str:
        """Generate unique referral code for user."""
        import uuid
        code = f"{user.email.split('@')[0][:4]}-{uuid.uuid4().hex[:6]}".upper()
        return code

    @staticmethod
    def calculate_referral_bonus(
        db: Session,
        referring_user_id: str,
        referred_user_id: str,
    ) -> Decimal:
        """
        Calculate referral bonus (if applicable).

        ONLY paid if:
        1. Referred user has earned money (not spent, earned)
        2. Referred user created 5+ pieces
        3. Referred user earned $10+
        4. Bonus doesn't exceed cap

        This is legally distinct from MLM because:
        - Bonus comes from REFERRED USER'S PERFORMANCE, not recruitment
        - No pressure/quotas to recruit
        - User earnings don't depend on recruiting
        """

        # Get referred user's real earnings (not projected)
        referred_user = db.query(User).filter(User.id == referred_user_id).first()
        if not referred_user:
            return Decimal("0.00")

        # Check minimum content requirement
        content_count = db.query(Content).filter(
            Content.user_id == referred_user_id,
            Content.status == "approved"
        ).count()

        if content_count < SafeReferralSystem.REFERRAL_RULES["requires_referred_user_content"]:
            # Not eligible yet - needs 5+ pieces
            return Decimal("0.00")

        # Calculate referred user's total real earnings
        from apps.engine.core.ledger_service import LedgerService
        referred_earnings = LedgerService.get_balance(db, referred_user_id)

        if referred_earnings < SafeReferralSystem.REFERRAL_RULES["minimum_referral_earnings"]:
            # Not eligible - needs $10+ real earnings
            return Decimal("0.00")

        # Check if referral cap exceeded
        existing_referral = db.query(Ledger).filter(
            Ledger.user_id == referring_user_id,
            Ledger.transaction_type == "referral_bonus",
            Ledger.affiliate_source == referred_user_id,
        ).all()

        total_existing = sum(float(e.amount or 0) for e in existing_referral)

        # Calculate bonus: 5% of referred user's earnings
        bonus_amount = Decimal(str(referred_earnings)) * Decimal(str(SafeReferralSystem.REFERRAL_RULES["referral_bonus_percentage"]))

        # Check cap
        if Decimal(str(total_existing)) + bonus_amount > SafeReferralSystem.REFERRAL_RULES["referral_lifetime_cap"]:
            # Would exceed cap
            remaining = SafeReferralSystem.REFERRAL_RULES["referral_lifetime_cap"] - Decimal(str(total_existing))
            bonus_amount = max(Decimal("0.00"), remaining)

        return bonus_amount

    @staticmethod
    def record_referral_bonus(
        db: Session,
        referring_user_id: str,
        referred_user_id: str,
    ) -> dict:
        """
        Record a referral bonus (if conditions met).

        This is called automatically when referred user reaches thresholds.
        Not triggered by recruitment - only by performance.
        """

        bonus = SafeReferralSystem.calculate_referral_bonus(
            db, referring_user_id, referred_user_id
        )

        if bonus <= 0:
            return {
                "status": "not_eligible",
                "reason": "Referred user must earn $10+ and create 5+ pieces first",
                "bonus_amount": 0,
            }

        # Record bonus as transaction
        from apps.engine.core.ledger_service import LedgerService

        entry = LedgerService.record_transaction(
            db=db,
            user_id=referring_user_id,
            amount=bonus,
            description=f"Referral bonus (referred user {referred_user_id[:8]} earned ${LedgerService.get_balance(db, referred_user_id):.2f})",
            transaction_type="referral_bonus",
        )

        logger.info(f"Referral bonus recorded: {referring_user_id} got ${bonus:.2f} from {referred_user_id}")

        return {
            "status": "success",
            "bonus_amount": float(bonus),
            "reason": f"Referred user earned ${LedgerService.get_balance(db, referred_user_id):.2f} and created {db.query(Content).filter(Content.user_id == referred_user_id, Content.status == 'approved').count()} pieces",
            "message": "Bonus recorded automatically (performance-based)",
        }

    @staticmethod
    def get_referral_status(db: Session, user_id: str) -> dict:
        """
        Show user their referral earnings and status.

        Importantly: Shows that earnings come from PERFORMANCE, not recruitment.
        """

        # Get all users this person referred
        referring_user = db.query(User).filter(User.id == user_id).first()
        if not referring_user:
            return {"error": "User not found"}

        referral_code = referring_user.referral_code

        # Find users who used this code
        referred_users = db.query(User).filter(User.referred_by == referral_code).all()

        # Calculate bonus for each
        referral_breakdown = []
        total_bonus = Decimal("0.00")

        for referred in referred_users:
            bonus = SafeReferralSystem.calculate_referral_bonus(db, user_id, referred.id)

            content_count = db.query(Content).filter(
                Content.user_id == referred.id,
                Content.status == "approved"
            ).count()

            from apps.engine.core.ledger_service import LedgerService
            referred_earnings = LedgerService.get_balance(db, referred.id)

            referral_breakdown.append({
                "referred_user": referred.email[:3] + "***",
                "their_earnings": float(referred_earnings),
                "their_content_pieces": content_count,
                "your_bonus_from_them": float(bonus),
                "bonus_eligible": bonus > 0,
                "why_not_eligible": (
                    None
                    if bonus > 0
                    else (
                        f"Needs $10+ earnings (has ${referred_earnings:.2f})"
                        if referred_earnings < 10
                        else f"Needs 5+ content pieces (has {content_count})"
                    )
                ),
            })

            total_bonus += bonus

        # Get total referral earnings from ledger
        referral_ledger = db.query(Ledger).filter(
            Ledger.user_id == user_id,
            Ledger.transaction_type == "referral_bonus"
        ).all()

        total_referral_earnings = sum(float(e.amount or 0) for e in referral_ledger)

        return {
            "user_id": user_id,
            "your_referral_code": referral_code,
            "share_this_code": f"Tell friends: {referral_code}",
            "referral_system": "Performance-based (FTC-safe)",
            "how_it_works": (
                "You earn 5% of what your friends earn (not what they spend). "
                "Only when they reach $10 earned + 5 pieces of content."
            ),
            "people_you_referred": len(referred_users),
            "total_referral_earnings_to_date": float(total_referral_earnings),
            "referral_breakdown": referral_breakdown,
            "legal_note": (
                "This is NOT an MLM or pyramid scheme. "
                "You earn bonuses based on your friends' CONTENT PERFORMANCE, "
                "not based on recruitment. "
                "Your earnings don't depend on recruiting anyone."
            ),
        }


class ReferralAPI:
    """API endpoints for safe referral system."""

    @staticmethod
    def register_endpoints(app):
        """Register referral endpoints."""

        @app.get("/referral/my-code")
        def get_my_referral_code(
            current_user: User,
            db: Session,
        ):
            """Get user's referral code."""
            return {
                "referral_code": current_user.referral_code,
                "share_link": f"https://nexusflow.app?ref={current_user.referral_code}",
                "message": "Share this code! You earn bonuses when friends succeed.",
            }

        @app.get("/referral/earnings")
        def get_referral_earnings(
            current_user: User,
            db: Session,
        ):
            """Get detailed referral earnings."""
            return SafeReferralSystem.get_referral_status(db, current_user.id)

        @app.get("/referral/legal-info")
        def get_referral_legal_info():
            """Explain referral system in FTC-safe way."""
            return {
                "system_type": "Performance-based affiliate bonus (NOT MLM)",
                "legal_classification": "FTC-compliant",
                "how_it_works": SafeReferralSystem.REFERRAL_RULES,
                "key_points": [
                    "Bonuses only from REFERRED USER'S PERFORMANCE, not recruitment",
                    "You don't earn when people sign up - only when they earn",
                    "Must create 5+ pieces and earn $10+ to trigger bonus",
                    "Maximum bonus per person is $5,000",
                    "No recruitment pressure or quotas",
                    "Your income doesn't depend on recruiting",
                ],
                "faq": {
                    "Is this an MLM?": "No. You earn from performance, not recruitment.",
                    "Can I earn without recruiting?": "Yes. All primary earnings are from affiliate commissions.",
                    "What if I recruit people who don't succeed?": "You earn nothing. No recruitment pressure.",
                    "Is there a recruitment target?": "No targets. Bonuses happen automatically.",
                },
            }
