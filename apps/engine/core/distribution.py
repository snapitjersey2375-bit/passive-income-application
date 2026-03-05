from abc import ABC, abstractmethod
from typing import Dict, Any
import time
import random

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
