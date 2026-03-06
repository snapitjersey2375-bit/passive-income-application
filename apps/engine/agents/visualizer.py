from .base import BaseAgent
from typing import Dict, Any
import urllib.parse

class VisualizerAgent(BaseAgent):
    """
    Agent responsible for generating/fetching visual previews for content ideas.
    """
    def __init__(self):
        super().__init__(name="VisualizerAgent")

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translates a title/niche into one or more high-quality image URLs.
        """
        title = context.get("title", "")
        niche = context.get("niche", "tech")
        count = context.get("count", 1)
        
        self.log(f"Generating {count} visual previews for: {title}")
        
        # High-quality Unsplash IDs curated for a "Premium Tech/Business" aesthetic
        image_pool = [
            "1611162617213-7d7a39e9b1d7", # Abstract Apps
            "1550751827-4bd374c3f58b", # High-tech Matrix
            "1451187580459-43490279c0fa", # Earth/Data
            "1581091226825-a6a2a5aee158", # Robotics/Lab
            "1518770660439-4636190af475", # Circuits
            "1460925895917-afdab827c52f", # Dashboard/Charts
            "1551288049-bbbda595c7a8", # Data visualization
            "1558494949-ef010c7191ae", # Server room
        ]
        
        import random
        selected_ids = random.sample(image_pool, min(count, len(image_pool)))
        
        urls = [
            f"https://images.unsplash.com/photo-{img_id}?q=80&w=1200&auto=format&fit=crop"
            for img_id in selected_ids
        ]

        if count == 1:
            return {"thumbnail_url": urls[0]}
        
        return {"urls": urls}
