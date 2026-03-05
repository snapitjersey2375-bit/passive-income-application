from abc import ABC, abstractmethod
from typing import Dict, Any
import time
import random
import os

class DistributionChannel(ABC):
    @abstractmethod
    def upload_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Uploads content to the external platform.
        Returns: 
            {"status": "live" | "pending" | "failed", "platform_id": str, "url": str}
        """
        pass

    @abstractmethod
    def get_metrics(self, platform_id: str) -> Dict[str, float]:
        """
        Fetches real-time metrics (views, likes) from the platform.
        """
        pass

class MockTikTokChannel(DistributionChannel):
    """
    Simulates a high-fidelity TikTok API integration.
    """
    def upload_content(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        # Simulate network latency
        # time.sleep(0.5) 
        
        # 95% Success Rate
        if random.random() < 0.05:
            return {"status": "failed", "error": "API Timeout"}
            
        post_id = f"tt_{int(time.time())}_{random.randint(1000,9999)}"
        return {
            "status": "live", # In reality this would be 'processing' first
            "platform_id": post_id,
            "url": f"https://www.tiktok.com/@antigravity/video/{post_id}"
        }

    def get_metrics(self, platform_id: str) -> Dict[str, float]:
        # Simulate organic growth curve based on "Quality Score" (hidden variable)
        # For now, we return a base set.
        return {
            "views": 0,
            "likes": 0,
            "shares": 0
        }

def get_tiktok_channel(db=None, user_id=None) -> DistributionChannel:
    """
    Factory function to return the appropriate TikTok channel.
    Retrieves tokens from DB if user_id is provided.
    """
    from apps.engine.core.channels.tiktok import RealTikTokChannel
    from apps.engine.db.models import SocialConnection
    from apps.engine.core.security import decrypt_token
    
    token = os.getenv("TIKTOK_ACCESS_TOKEN")
    biz_id = os.getenv("TIKTOK_BUSINESS_ID")

    if db and user_id:
        conn = db.query(SocialConnection).filter(
            SocialConnection.user_id == user_id,
            SocialConnection.platform == "tiktok",
            SocialConnection.is_active == True
        ).first()
        if conn and conn.access_token:
            token = decrypt_token(conn.access_token)
            biz_id = conn.account_id # Assuming account_id stores business_id

    if token:
        return RealTikTokChannel(access_token=token, business_id=biz_id)
    return MockTikTokChannel()

def get_shopify_channel(db=None, user_id=None) -> DistributionChannel:
    """
    Factory function to return the appropriate Shopify channel.
    """
    from apps.engine.core.channels.shopify import RealShopifyChannel
    from apps.engine.db.models import SocialConnection
    from apps.engine.core.security import decrypt_token

    token = os.getenv("SHOPIFY_ACCESS_TOKEN")
    shop_url = os.getenv("SHOPIFY_SHOP_URL")

    if db and user_id:
        conn = db.query(SocialConnection).filter(
            SocialConnection.user_id == user_id,
            SocialConnection.platform == "shopify",
            SocialConnection.is_active == True
        ).first()
        if conn and conn.access_token:
            token = decrypt_token(conn.access_token)
            shop_url = conn.account_name # For Shopify, we might store the domain in account_name

    if token:
        return RealShopifyChannel(shop_url=shop_url, access_token=token)
    return MockTikTokChannel() # Use mock for now as fallback
