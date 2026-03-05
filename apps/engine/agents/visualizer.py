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
        Translates a title/niche into a high-quality image URL.
        """
        title = context.get("title", "")
        niche = context.get("niche", "general")
        
        self.log(f"Generating visual preview for: {title}")
        
        # In a real system, we'd use DALL-E 3 or Midjourney.
        # For this prototype, we use high-quality dynamic Unsplash Source images
        # filtered by the niche keywords.
        
        search_term = niche
        if "crypto" in title.lower(): search_term = "cryptocurrency"
        if "money" in title.lower(): search_term = "cash"
        if "code" in title.lower() or "python" in title.lower(): search_term = "programming"
        if "fitness" in title.lower() or "gym" in title.lower(): search_term = "workout"
        
        encoded_term = urllib.parse.quote(search_term)
        
        # Using Source Unsplash with random seed to prevent duplicate images in a single session
        thumbnail_url = f"https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&q=80&w=800&keyword={encoded_term}"
        
        # Alternatively, use dynamic source (less stable but more variety)
        # Note: source.unsplash is being deprecated, using a high-quality static proxy fallback
        variety_id = hash(title) % 1000
        thumbnail_url = f"https://source.unsplash.com/featured/800x600?{encoded_term}&sig={variety_id}"
        
        # Fallback to high-quality placeholder if unsplash source fails
        # thumbnail_url = f"https://loremflickr.com/800/600/{encoded_term}?lock={variety_id}"

        self.log(f"Visual acquired: {thumbnail_url}")
        
        return {"thumbnail_url": thumbnail_url}
