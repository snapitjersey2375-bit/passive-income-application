from .base import BaseAgent
from typing import Dict, Any
import time
import random

class TrafficAgent(BaseAgent):
    """
    Agent responsible for uploading content and managing ad spend.
    Includes Safety checks.
    """
    def __init__(self):
        super().__init__(name="TrafficAgent")
        self.blocked_keywords = ["scam", "fraud", "hacked", "illegal"]
    
    def validate_content(self, title: str, description: str) -> bool:
        """
        Checks for Brand Safety.
        """
        title = title or ""
        description = description or ""
        text = (title + " " + description).lower()
        for word in self.blocked_keywords:
            if word in text:
                self.log(f"SAFETY VIOLATION: Found blocked keyword '{word}'")
                return False
        return True

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        self.log("Checking signals for upload...")
        
        title = context.get("title", "")
        description = context.get("description", "")
        
        # 1. Safety Check
        if not self.validate_content(title, description):
             return {"upload_status": "failed", "reason": "safety_violation"}

        # 2. Simulate Network Upload via Distribution Channel
        from apps.engine.core.distribution import get_tiktok_channel
        db = context.get("db")
        user_id = context.get("user_id")
        channel = get_tiktok_channel(db=db, user_id=user_id)
        
        result = channel.upload_content({"title": title, "description": description})
        
        if result["status"] == "failed":
            return {"upload_status": "failed", "reason": result.get("error", "unknown")}

        # 3. Persist Platform Metadata
        content_id = context.get("content_id")
        if db and content_id:
            from apps.engine.db.models import Content
            content = db.query(Content).filter(Content.id == content_id).first()
            if content:
                content.platform_id = result["platform_id"]
                content.platform_url = result["url"]
                content.distribution_status = "live"
                db.commit()

        return {
            "upload_status": "success",
            "platform": "tiktok",
            "platform_id": result["platform_id"],
            "url": result["url"],
            "views_projected": random.randint(1000, 50000) # Only projected for initial return, real comes in simulation loop
        }

    def simulate_performance(self, db, content_id: str):
        """
        Simulates one "day" of performance. 
        Deducts Daily Budget -> Generates Traffic -> Records Revenue.
        """
        from apps.engine.db.models import Content, User
        from apps.engine.core.ledger_service import LedgerService
        from datetime import datetime, timedelta

        content = db.query(Content).filter(Content.id == content_id).first()
        if not content:
            return

        # 0. Check Status
        if content.campaign_status == "paused":
            self.log(f"Skipping paused campaign: {content.title}")
            return
            
        # Fetch user early for ban check
        user = db.query(User).filter(User.id == content.user_id).first()
        if not user:
            # Fallback to default user if user_id not explicitly set (legacy compat)
            user = db.query(User).first()

        if user and user.is_shadow_banned:
            self.log(f"SECURITY HOLD: Account for '{content.title}' is shadow-banned. Halting traffic.")
            return

        # 1. Burn Check (Deduct Daily Budget)
        # using the user fetched above
        daily_cost = content.daily_budget or 10.0
        
        balance = LedgerService.get_balance(db, user.id)
        
        if balance < daily_cost:
            self.log(f"BANKRUPTCY PROTECTION: Pausing campaign for '{content.title}' (Balance ${balance:.2f} < Budget ${daily_cost:.2f})")
            content.campaign_status = "paused"
            db.commit()
            return

        # Deduct Spend
        LedgerService.record_transaction(
            db,
            user.id,
            -daily_cost,
            f"Daily Ad Budget for '{content.title}'",
            "ad_spend"
        )

        self.log(f"Simulating traffic for: {content.title} (Cost: -${daily_cost:.2f})")
        
        # 2. Calculate Decay
        # Older content gets less visibility unless budget is huge
        self.log(f"Simulating traffic for: {content.title}")
        
        # 1. Fetch Integration Real Data (if applicable)
        # channel = MockTikTokChannel()
        # metrics = channel.get_metrics(content.platform_id) 
        # For now, we simulate the 'Algorithm' since the mock channel returns 0s.
        
        # 2. The Algorithm (Funnel)
        # Base Signals
        quality_score = content.confidence_score or 0.8
        viral_factor = content.viral_potential or 1.0
        
        # Funnel Math
        age_days = (datetime.now() - (content.created_at.replace(tzinfo=None) if content.created_at else datetime.now())).days
        decay_factor = 1.0 / (1.0 + (age_days * 0.1)) # View reach halves every 10 days
        
        base_reach = 500 + (content.view_count * 0.05) # Reduced Momentum (0.1 -> 0.05)
        adjusted_reach = base_reach * decay_factor
        
        new_impressions = int(adjusted_reach * viral_factor * random.uniform(0.8, 1.5))
        
        ctr = 0.05 * quality_score # 5% baseline * quality
        new_views = int(new_impressions * ctr)
        
        # 3. Update Distribution Layer
        from apps.engine.core.distribution import get_tiktok_channel
        channel = get_tiktok_channel(db, user.id)
        
        # Sync only if we have a platform ID
        if content.platform_id:
            # If the channel is stateful (Mock), report the results
            if hasattr(channel, "update_metrics"):
                channel.update_metrics(content.platform_id, new_views)
            
            # 4. Sync Database from Distribution Source (Ground Truth)
            metrics = channel.get_metrics(content.platform_id)
            if metrics:
                content.view_count = metrics.get("views", content.view_count)
                content.like_count = metrics.get("likes", content.like_count)
                content.share_count = metrics.get("shares", content.share_count)
        else:
            # Fallback for content not (yet) uploaded via this agent
            content.view_count += new_views
            content.like_count += int(new_views * 0.15)
            content.share_count += int(new_views * 0.02)

        # 5. Revenue (CPM Model)
        cpm_rate = 1.50 # $1.50 per 1,000 views
        revenue = (new_views / 1000.0) * cpm_rate
        
        # FIX: Handle Decimal vs Float (User switched to Numeric)
        from decimal import Decimal
        content.monetization_potential += Decimal(str(revenue))

        # 4. Record Earnings (If significant)
        if revenue > 0.01:
            user = db.query(User).first() # TODO: content.user_id if multi-user
            LedgerService.record_transaction(
                db,
                user.id,
                Decimal(str(revenue)),
                f"Ad Earnings ({new_views} views @ ${cpm_rate} CPM)",
                "ad_revenue"
            )
        
        db.commit()
        self.log(f"Traffic update: +{new_views} views => ${revenue:.4f}")
        db.commit()
        
        # The original code had a 'daily_cost' and 'decay_factor' in the final log,
        # but these are not calculated in the new refactored method.
        # Removing them to avoid NameError.
        # If these are needed, they should be re-introduced into the new logic.
        self.log(f"Traffic Result: {new_views} views, ${revenue:.2f} Rev")
