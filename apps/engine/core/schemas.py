from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ContentBase(BaseModel):
    title: str
    description: Optional[str] = None
    thumbnail_url: str
    video_url: Optional[str] = None
    confidence_score: float = 0.0
    platform: str = "tiktok"
    
    # Stats
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    share_count: int = 0
    viral_potential: float = 0.0
    monetization_potential: float = 0.0
    status: str = "pending_review"
    
    # Compliance
    policy_status: bool = True
    policy_reason: str = "Approved"

class ContentCreate(ContentBase):
    pass

class ContentSchema(ContentBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
