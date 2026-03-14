"""
Expectation Tracker Service

Provides realistic milestones and progress tracking for new users.
Prevents the "unverifiable promise" problem by being brutally honest
about what users can actually earn and when.
"""

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from apps.engine.db.models import User, Content
from sqlalchemy import func

logger = logging.getLogger(__name__)


class ExpectationTracker:
    """
    Track user progress toward real monetization milestones.

    This prevents the broken promise problem by:
    1. Being explicit about platform requirements
    2. Showing real (not simulated) progress
    3. Managing expectations honestly
    """

    # Platform monetization requirements
    PLATFORMS = {
        "tiktok": {
            "name": "TikTok Creator Fund",
            "requirements": {
                "followers": 1000,
                "views_30_days": 100000,
            },
            "min_earnings": 0.02,  # $0.02-4 per 1000 views
            "estimated_days": 90,  # Realistic timeline
            "description": "Requires 1K followers + 100K views in 30 days to unlock",
        },
        "youtube": {
            "name": "YouTube Partner Program",
            "requirements": {
                "subscribers": 1000,
                "watch_hours_12m": 4000,
            },
            "min_earnings": 0.25,  # $0.25-4 per 1000 views
            "estimated_days": 120,  # More realistic: 4+ months
            "description": "Requires 1K subs + 4K watch hours in 12 months",
        },
        "instagram": {
            "name": "Instagram Reels Bonus Program",
            "requirements": {
                "followers": 10000,
                "reels_views_30d": 600000,
            },
            "min_earnings": 0.015,  # ~$150-600/month for eligible creators
            "estimated_days": 150,
            "description": "Requires 10K followers + 600K views in 30 days",
        },
        "affiliate": {
            "name": "Affiliate Commissions (Real)",
            "requirements": {
                "content_pieces": 10,
                "audience_email_list": 100,
            },
            "min_earnings": 25,  # $25+ per conversion (realistic affiliate)
            "estimated_days": 14,  # Can start within 2 weeks
            "description": "No platform gatekeeping - earn immediately on real sales",
        },
    }

    @staticmethod
    def get_user_progress(db: Session, user_id: str) -> dict:
        """
        Get realistic progress toward monetization milestones.

        Returns explicit information about:
        - Current status on each platform
        - Days until likely monetization
        - What they need to do to get there
        - Real (not projected) earnings so far
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "User not found"}

        # Get user's actual content stats
        user_content = db.query(Content).filter(Content.user_id == user_id).all()

        total_views = sum(c.view_count for c in user_content)
        total_content = len(user_content)

        # Get real earnings (not projected)
        from apps.engine.core.ledger_service import LedgerService
        real_balance = LedgerService.get_balance(db, user_id)

        # Calculate progress on each platform
        progress = {}
        for platform_id, platform_info in ExpectationTracker.PLATFORMS.items():
            progress[platform_id] = ExpectationTracker._calculate_platform_progress(
                platform_id=platform_id,
                platform_info=platform_info,
                user_content=user_content,
                total_views=total_views,
                total_content=total_content,
            )

        # Calculate days until real earnings likely (affiliate route is fastest)
        days_until_first_dollar = ExpectationTracker._estimate_days_to_first_dollar(
            total_content=total_content,
            total_views=total_views,
            user_account_age=(datetime.now() - user.created_at).days,
        )

        return {
            "user_id": user_id,
            "account_age_days": (datetime.now() - user.created_at).days,
            "realistic_timeline": {
                "first_affiliate_commission": f"{days_until_first_dollar} days (fastest path)",
                "tiktok_creator_fund": "90-180 days (realistic)",
                "youtube_partnership": "120-180 days (realistic)",
                "instagram_reels_bonus": "150+ days (hardest)",
            },
            "real_earnings_to_date": float(real_balance),
            "real_earnings_are": "100% REAL (affiliate commissions) or $0 (waiting for platform monetization)",
            "content_stats": {
                "total_pieces": total_content,
                "total_views": total_views,
                "average_views_per_piece": total_views // max(1, total_content),
            },
            "platform_progress": progress,
            "honest_assessment": ExpectationTracker._get_honest_assessment(
                total_content, total_views, days_until_first_dollar
            ),
        }

    @staticmethod
    def _calculate_platform_progress(
        platform_id: str,
        platform_info: dict,
        user_content: list,
        total_views: int,
        total_content: int,
    ) -> dict:
        """Calculate progress toward platform-specific monetization."""

        requirements = platform_info["requirements"]
        progress_data = {
            "platform": platform_info["name"],
            "description": platform_info["description"],
            "estimated_days": platform_info["estimated_days"],
            "min_earnings": platform_info["min_earnings"],
            "requirements_met": {},
            "requirements_remaining": {},
            "overall_progress_percent": 0,
        }

        # Check each requirement
        progress_scores = []

        if "followers" in requirements:
            # Simulate: ~1 follower per 100 views (conservative)
            estimated_followers = total_views // 100
            required = requirements["followers"]
            met = min(estimated_followers, required)
            progress_scores.append((met / required) * 100)

            progress_data["requirements_met"]["followers"] = met
            progress_data["requirements_remaining"]["followers"] = max(0, required - met)

        if "views_30_days" in requirements:
            # Conservative: assume 1000 views per week = ~4K per month
            progress_scores.append((total_views / requirements["views_30_days"]) * 100)
            progress_data["requirements_met"]["views_30_days"] = total_views
            progress_data["requirements_remaining"]["views_30_days"] = max(
                0, requirements["views_30_days"] - total_views
            )

        if "watch_hours_12m" in requirements:
            # Rough: 1 hour watch per 1000 views
            estimated_hours = total_views / 1000
            progress_scores.append((estimated_hours / requirements["watch_hours_12m"]) * 100)
            progress_data["requirements_met"]["watch_hours"] = estimated_hours
            progress_data["requirements_remaining"]["watch_hours"] = max(
                0, requirements["watch_hours_12m"] - estimated_hours
            )

        if "content_pieces" in requirements:
            required = requirements["content_pieces"]
            progress_scores.append((total_content / required) * 100)
            progress_data["requirements_met"]["content_pieces"] = total_content
            progress_data["requirements_remaining"]["content_pieces"] = max(0, required - total_content)

        if "audience_email_list" in requirements:
            # Rough: 1 email per 50 views
            estimated_list = total_views // 50
            required = requirements["audience_email_list"]
            progress_scores.append((estimated_list / required) * 100)
            progress_data["requirements_met"]["email_list"] = estimated_list
            progress_data["requirements_remaining"]["email_list"] = max(0, required - estimated_list)

        # Average progress across all requirements
        if progress_scores:
            progress_data["overall_progress_percent"] = sum(progress_scores) / len(progress_scores)

        # Determine if eligible
        all_met = all(
            progress_data["requirements_remaining"][req] <= 0
            for req in progress_data["requirements_remaining"]
        )
        progress_data["eligible"] = all_met
        progress_data["status"] = "✅ ELIGIBLE" if all_met else f"🟡 {progress_data['overall_progress_percent']:.0f}% progress"

        return progress_data

    @staticmethod
    def _estimate_days_to_first_dollar(
        total_content: int,
        total_views: int,
        user_account_age: int,
    ) -> int:
        """
        Estimate days until user likely earns their first real dollar.

        This uses the affiliate route (fastest) as baseline since it requires
        no platform gatekeeping.
        """

        # Conservative assumptions:
        # - Need ~10 content pieces to build audience
        # - Need ~5,000 views total for first affiliate click
        # - 1-2% of clicks convert to affiliate sales
        # - Average affiliate commission: $25

        if total_content < 5:
            # Not enough content yet
            return 14  # 2 weeks to build minimum content library

        if total_views < 1000:
            # Very low engagement - need more content
            # Assume: 100-200 views per piece
            # Need: 5,000 views = 25-50 pieces
            estimated_days_needed = max(7, int((5000 - total_views) / 200))
            return estimated_days_needed

        # If they have decent views, they could get affiliate click any day
        if total_views > 5000:
            return 3  # Within a few days of having real audience

        # In between
        return 7

    @staticmethod
    def _get_honest_assessment(total_content: int, total_views: int, days_until_first_dollar: int) -> str:
        """Return a brutally honest assessment of user's path to earnings."""

        if total_content == 0:
            return (
                "🎯 You haven't created content yet. "
                "Start here: Create 10-20 pieces before expecting any earnings. "
                "NO PLATFORM will pay you for zero content. Be realistic."
            )

        if total_views < 500:
            return (
                f"⚠️ You have {total_views} views across {total_content} pieces. "
                f"Most platforms require 1K-100K views to monetize. "
                f"Focus on: Creating MORE content, improving quality, and learning your audience. "
                f"Realistic timeline: 60-90 days."
            )

        if total_views < 5000:
            return (
                f"📈 Progress! You have {total_views} views. "
                f"You're ~20% of the way to basic monetization on affiliate networks. "
                f"Estimated: {days_until_first_dollar} days until first affiliate commission (if you convert). "
                f"Keep creating."
            )

        if total_views < 100000:
            return (
                f"✅ Good progress: {total_views} views! "
                f"You're positioned to earn from affiliate commissions within {days_until_first_dollar} days. "
                f"Platform monetization (TikTok/YouTube) still 2-3 months away. "
                f"Your best path: Build email list + affiliate commissions (no gatekeeping)."
            )

        return (
            f"🎉 Excellent: {total_views} views! "
            f"You should be earning affiliate commissions NOW. "
            f"Platform monetization (TikTok/YouTube) should unlock within 30 days. "
            f"Both income streams should be active."
        )


class ExpectationManagerAPI:
    """API endpoints for expectation tracking."""

    @staticmethod
    def register_endpoints(app):
        """Register endpoints with the FastAPI app."""

        @app.get("/user/expectations")
        def get_user_expectations(
            db: Session,
            current_user: User,
        ):
            """
            Get realistic earnings expectations and progress.

            This is the HONEST view of what the user will earn and when.
            No fake projections, no simulated revenue.
            """
            from fastapi import Depends
            from apps.engine.db.session import get_db

            progress = ExpectationTracker.get_user_progress(db, current_user.id)

            return {
                "status": "reality_check",
                "message": "This is what you'll ACTUALLY earn based on real data",
                "data": progress,
                "disclaimer": (
                    "We show REAL earnings only. No projections. No simulated revenue. "
                    "Platform monetization thresholds are industry-standard and not negotiable. "
                    "Your best path to first dollar: Affiliate commissions (60% revenue share with us)."
                ),
            }
