from .base import BaseAgent
from typing import Dict, Any
from apps.engine.db.session import engine
from apps.engine.db.models import Content, User, SocialConnection, Ledger
from sqlalchemy.orm import Session
from decimal import Decimal
import random


class PublisherAgent(BaseAgent):
    """
    Agent responsible for publishing approved content to connected social platforms.
    Simulates the upload process and updates distribution status.
    """
    
    def __init__(self):
        super().__init__(name="Publisher")
    
    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        content_id = context.get("content_id")
        user_id = context.get("user_id")
        
        if not content_id:
            return {"status": "error", "reason": "No content_id provided"}
        
        with Session(engine) as session:
            # Fetch content
            content = session.query(Content).filter(Content.id == content_id).first()
            if not content:
                return {"status": "error", "reason": "Content not found"}
            
            if content.status != "approved":
                self.log(f"⚠️ Content {content_id} is not approved (status: {content.status})")
                return {"status": "error", "reason": f"Content must be approved first (current: {content.status})"}
            
            # --- NEW WORKFLOW: Asset Download ---
            # Bypass actual API connections for now. Return a direct download URL.
            
            # Update content status
            content.distribution_status = "live"
            content.status = "uploaded"
            
            # No platform fee in download mode to save complexity
            session.commit()
            
            self.log(f"🚀 Asset prepared for manual download: '{content.title}'")
            
            return {
                "status": "success",
                "published_to": ["manual_download"],
                "content_id": content_id,
                "distribution_status": "live",
                "download_url": content.video_url, # Pass back the generated asset link
                "message": "Video is ready for manual upload to TikTok/YouTube."
            }
    
    async def _publish_to_platform(self, content: Content, connection: SocialConnection) -> Dict[str, Any]:
        """
        Simulates publishing to a social platform.
        In production, this would call the actual platform APIs.
        """
        self.log(f"📤 Uploading to {connection.platform}...")
        
        # Simulate API call latency and potential failures
        # In production: use httpx to call TikTok/YouTube APIs
        
        # 95% success rate simulation
        if random.random() < 0.95:
            # Simulate successful upload
            fake_post_id = f"{connection.platform}_{content.id[:8]}"
            self.log(f"🎬 {connection.platform.upper()} Post ID: {fake_post_id}")
            return {
                "success": True,
                "platform": connection.platform,
                "post_id": fake_post_id,
                "url": f"https://{connection.platform}.com/@{connection.account_name}/{fake_post_id}"
            }
        else:
            return {
                "success": False,
                "platform": connection.platform,
                "error": "Rate limit exceeded. Retry in 60s."
            }
