from typing import List, Dict
import uuid
import random

def generate_mock_queue() -> List[Dict]:
    """
    Generates mock video content for the Supervisor Dashboard.
    """
    topics = ["AI Tools", "Crypto News", "Life Hacks", "Coding Tips", "Fitness 101"]
    queue = []
    
    for _ in range(5):
        viral_potential = round(random.uniform(5.0, 9.5), 1)
        monetization = random.randint(500, 5000)
        views = random.randint(10000, 150000)
        
        queue.append({
            "id": str(uuid.uuid4()),
            "title": f"Viral {random.choice(topics)} Video",
            "confidence_score": round(random.uniform(0.7, 0.99), 2),
            "status": "pending_review",
            "thumbnail_url": "https://via.placeholder.com/150",
            "viral_potential": viral_potential,
            "monetization_potential": monetization,
            "view_count": views,
            "like_count": int(views * random.uniform(0.05, 0.15)),  # 5-15% like rate
            "comment_count": int(views * random.uniform(0.01, 0.03)),  # 1-3% comment rate
            "share_count": int(views * random.uniform(0.005, 0.02))  # 0.5-2% share rate
        })
        
    return queue
