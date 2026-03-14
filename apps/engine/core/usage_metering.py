"""
Usage Metering & Cost Control

Prevents API cost blowout by implementing:
1. Hard per-user generation limits (by tier)
2. Real-time cost tracking
3. Automatic enforcement of caps
4. Transparent cost visibility

Problem: At 100 users × 10 videos/day = $500-2000/month in OpenAI costs
Solution: Hard limits per tier prevent unchecked spending
"""

import logging
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from apps.engine.db.models import User, Content, Ledger
from sqlalchemy import func, and_
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class UsageTier:
    """Define limits and pricing for each tier."""

    TIERS = {
        "free": {
            "name": "Free",
            "price_per_month": Decimal("0.00"),
            "limits": {
                "videos_per_day": 2,
                "videos_per_month": 40,
                "total_words_per_month": 10_000,  # ~5-10 videos
                "tts_minutes_per_month": 500,  # ~8 min videos × 5 = 40 min
                "image_generations_per_day": 2,
            },
            "features": [
                "Auto-publish to YouTube",
                "TikTok/Instagram support (manual)",
                "Affiliate commission tracking (60%)",
            ],
            "next_upgrade": "pro",
        },
        "pro": {
            "name": "Pro",
            "price_per_month": Decimal("19.99"),
            "limits": {
                "videos_per_day": 10,
                "videos_per_month": 200,
                "total_words_per_month": 100_000,
                "tts_minutes_per_month": 5_000,
                "image_generations_per_day": 20,
            },
            "features": [
                "Everything in Free",
                "Auto-publish to TikTok",
                "Auto-publish to Instagram",
                "Priority content review",
                "Advanced analytics",
                "Custom voice profiles",
            ],
            "next_upgrade": "enterprise",
        },
        "enterprise": {
            "name": "Enterprise",
            "price_per_month": Decimal("99.99"),
            "limits": {
                "videos_per_day": 100,
                "videos_per_month": None,  # Unlimited
                "total_words_per_month": None,  # Unlimited
                "tts_minutes_per_month": None,  # Unlimited
                "image_generations_per_day": None,  # Unlimited
            },
            "features": [
                "Everything in Pro",
                "Unlimited generation",
                "Dedicated success manager",
                "Custom integrations",
                "Advanced targeting",
            ],
        },
    }

    # API costs per unit
    API_COSTS = {
        "openai_gpt4_per_1k_tokens": Decimal("0.03"),  # Input tokens
        "openai_tts_per_minute": Decimal("0.015"),
        "openai_dall_e_per_image": Decimal("0.08"),
        "storage_per_gb_per_month": Decimal("0.02"),
        "bandwidth_per_gb": Decimal("0.1"),
    }


class UsageMeter:
    """Track and enforce usage limits."""

    @staticmethod
    def get_user_tier(user: User) -> str:
        """Get user's current tier (from subscription model)."""
        # For now, default to free
        # Will integrate with payment system later
        return user.tier if hasattr(user, "tier") else "free"

    @staticmethod
    def get_user_limits(user: User) -> Dict:
        """Get usage limits for user's tier."""
        tier = UsageMeter.get_user_tier(user)
        return UsageTier.TIERS.get(tier, UsageTier.TIERS["free"])["limits"]

    @staticmethod
    def get_current_month_usage(db: Session, user_id: str) -> Dict:
        """Get user's usage this month."""

        # Start of current month
        now = datetime.now()
        month_start = datetime(now.year, now.month, 1)

        # Count videos created this month
        videos_this_month = db.query(Content).filter(
            and_(
                Content.user_id == user_id,
                Content.created_at >= month_start,
            )
        ).count()

        # Count words generated (estimated from content)
        content = db.query(Content).filter(
            and_(
                Content.user_id == user_id,
                Content.created_at >= month_start,
            )
        ).all()

        total_words = sum(
            len((c.title or "").split()) + len((c.description or "").split())
            for c in content
        )

        # Count videos this month by day
        videos_today = db.query(Content).filter(
            and_(
                Content.user_id == user_id,
                func.date(Content.created_at) == datetime.now().date(),
            )
        ).count()

        # Get TTS costs from ledger
        tts_expenses = db.query(Ledger).filter(
            and_(
                Ledger.user_id == user_id,
                Ledger.transaction_type == "tts_expense",
                Ledger.created_at >= month_start,
            )
        ).all()

        total_tts_cost = sum(abs(float(e.amount or 0)) for e in tts_expenses)
        # Convert cost back to minutes (rough estimate)
        tts_minutes = int(total_tts_cost / float(UsageTier.API_COSTS["openai_tts_per_minute"]))

        return {
            "period": f"{month_start.strftime('%B %Y')}",
            "videos_created_this_month": videos_this_month,
            "videos_created_today": videos_today,
            "words_generated_this_month": total_words,
            "tts_minutes_used": tts_minutes,
            "estimated_api_cost_this_month": total_tts_cost,
            "usage_date": datetime.now().isoformat(),
        }

    @staticmethod
    def check_limits(
        db: Session,
        user_id: str,
        action: str,
        estimated_cost: Decimal = Decimal("0.00"),
    ) -> Dict:
        """
        Check if user can perform action without exceeding limits.

        Args:
            action: 'create_video', 'generate_tts', 'generate_image'
            estimated_cost: Estimated cost of this action

        Returns:
            {
                "allowed": True/False,
                "reason": "explanation",
                "current_usage": {...},
                "limits": {...},
            }
        """

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"allowed": False, "reason": "User not found"}

        tier_name = UsageMeter.get_user_tier(user)
        tier_config = UsageTier.TIERS.get(tier_name, UsageTier.TIERS["free"])
        limits = tier_config["limits"]

        current_usage = UsageMeter.get_current_month_usage(db, user_id)

        # Check specific limits
        if action == "create_video":
            # Check daily limit
            if limits["videos_per_day"] is not None:
                if current_usage["videos_created_today"] >= limits["videos_per_day"]:
                    return {
                        "allowed": False,
                        "reason": f"Daily limit reached ({limits['videos_per_day']} videos). "
                        f"Upgrade to Pro for more.",
                        "current_usage": current_usage,
                        "limits": limits,
                        "suggested_action": f"Upgrade to {tier_config['next_upgrade']} tier",
                    }

            # Check monthly limit
            if limits["videos_per_month"] is not None:
                if current_usage["videos_created_this_month"] >= limits["videos_per_month"]:
                    return {
                        "allowed": False,
                        "reason": f"Monthly limit reached ({limits['videos_per_month']} videos). "
                        f"Upgrade for unlimited generation.",
                        "current_usage": current_usage,
                        "limits": limits,
                    }

        elif action == "generate_tts":
            if limits["tts_minutes_per_month"] is not None:
                if current_usage["tts_minutes_used"] >= limits["tts_minutes_per_month"]:
                    return {
                        "allowed": False,
                        "reason": f"TTS monthly limit reached ({limits['tts_minutes_per_month']} minutes). "
                        f"Upgrade for more.",
                        "current_usage": current_usage,
                        "limits": limits,
                    }

        elif action == "generate_image":
            # Check daily limit
            if limits["image_generations_per_day"] is not None:
                # Count images today (simplified - would track in real system)
                if current_usage["videos_created_today"] >= limits["image_generations_per_day"]:
                    return {
                        "allowed": False,
                        "reason": f"Daily image limit reached ({limits['image_generations_per_day']}). "
                        f"Upgrade for more.",
                        "current_usage": current_usage,
                        "limits": limits,
                    }

        # Passed all checks
        return {
            "allowed": True,
            "reason": "Within limits",
            "current_usage": current_usage,
            "limits": limits,
            "cost_for_this_action": float(estimated_cost),
            "message": f"Proceeding. You'll have {limits.get('videos_per_month', 'unlimited') - current_usage['videos_created_this_month']} videos left this month.",
        }

    @staticmethod
    def enforce_limit(
        db: Session,
        user_id: str,
        action: str,
    ) -> bool:
        """
        Enforce usage limit.

        Returns True if action is allowed, False if blocked.
        """

        result = UsageMeter.check_limits(db, user_id, action)
        return result["allowed"]


class UsageMeteringAPI:
    """API endpoints for usage tracking."""

    @staticmethod
    def register_endpoints(app):
        """Register usage metering endpoints."""

        @app.get("/usage/current")
        def get_current_usage(
            current_user: User,
            db: Session,
        ):
            """Get user's current month usage."""
            usage = UsageMeter.get_current_month_usage(db, current_user.id)
            tier_name = UsageMeter.get_user_tier(current_user)
            tier_config = UsageTier.TIERS[tier_name]
            limits = tier_config["limits"]

            # Calculate percentage used
            usage_percent = {}
            if limits["videos_per_month"]:
                usage_percent["videos"] = (
                    usage["videos_created_this_month"] / limits["videos_per_month"] * 100
                )
            if limits["tts_minutes_per_month"]:
                usage_percent["tts"] = (
                    usage["tts_minutes_used"] / limits["tts_minutes_per_month"] * 100
                )

            return {
                "current_tier": tier_name,
                "usage": usage,
                "limits": limits,
                "usage_percent": usage_percent,
                "warnings": (
                    [
                        f"⚠️ You're {usage_percent.get('videos', 0):.0f}% of video limit. "
                        f"Upgrade to Pro for more."
                    ]
                    if usage_percent.get("videos", 0) > 80
                    else []
                ),
                "upgrade_url": f"/billing/upgrade?from={tier_name}",
            }

        @app.get("/usage/check")
        def check_usage_allowed(
            action: str,  # 'create_video', 'generate_tts', etc.
            current_user: User = None,
            db: Session = None,
        ):
            """Check if user can perform an action."""
            result = UsageMeter.check_limits(db, current_user.id, action)
            return result

        @app.get("/tiers")
        def get_all_tiers():
            """Get tier information."""
            return {
                "tiers": {
                    name: {
                        "name": config["name"],
                        "price": str(config["price_per_month"]),
                        "limits": config["limits"],
                        "features": config["features"],
                    }
                    for name, config in UsageTier.TIERS.items()
                },
                "api_costs": {
                    k: str(v) for k, v in UsageTier.API_COSTS.items()
                },
                "message": "Choose a tier that matches your growth plans",
            }
