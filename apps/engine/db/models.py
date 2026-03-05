from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .session import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    
    # Settings
    risk_tolerance = Column(Float, default=0.5)
    persona = Column(String, default="grandma") # grandma, degen, corporate
    is_grandma_mode = Column(Boolean, default=True) # Keep for UI compatibility
    
    # Growth / Referrals
    referral_code = Column(String, unique=True, index=True, nullable=True) # e.g. "BOB-123"
    referred_by = Column(String, nullable=True) # Code of the referrer
    referral_count = Column(Integer, default=0)
    
    # Security / Compliance
    policy_violation_count = Column(Integer, default=0)
    is_shadow_banned = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    ledger_entries = relationship("Ledger", back_populates="user")


class Content(Base):
    __tablename__ = "content"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id")) # Multi-tenancy support
    niche = Column(String, index=True, default="general") # Saturation tracking
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    thumbnail_url = Column(String)
    video_url = Column(String, nullable=True)
    
    # Metadata
    confidence_score = Column(Float, default=0.0)
    platform = Column(String, default="tiktok")
    
    # Statistics
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    
    # Projections
    viral_potential = Column(Float, default=0.0) # 0.0 to 1.0 (or higher)
    monetization_potential = Column(Numeric(10, 2), default=0.0) # Predicted Dollar Value
    
    # Compliance
    policy_status = Column(Boolean, default=True)
    policy_reason = Column(String, default="Approved")
    
    # Campaign Settings (Economy 2.0)
    daily_budget = Column(Numeric(10, 2), default=10.00) # Daily spend limit
    campaign_status = Column(String, default="paused") # active, paused
    distribution_status = Column(String, default="pending") # pending, processing, live, failed
    last_simulation_run = Column(DateTime(timezone=True), nullable=True)

    # Status: pending_review, approved, rejected, uploaded
    status = Column(String, default="pending_review")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Ledger(Base):
    __tablename__ = "ledger"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    amount = Column(Numeric(10, 2)) # Positive for income, negative for spend
    description = Column(String)
    transaction_type = Column(String) # deposit, ad_spend, ad_revenue, commission
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="ledger_entries")

class AnalyticsHistory(Base):
    __tablename__ = "analytics_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    total_views = Column(Integer, default=0)
    total_revenue = Column(Numeric(10, 2), default=0.00)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


class SocialConnection(Base):
    """
    Tracks user's connected social media accounts for auto-publishing.
    """
    __tablename__ = "social_connections"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    platform = Column(String, index=True)  # tiktok, youtube, instagram
    access_token = Column(String, nullable=True)  # Encrypted in production
    refresh_token = Column(String, nullable=True)
    account_name = Column(String, nullable=True)  # Display name (e.g., @username)
    account_id = Column(String, nullable=True)  # Platform-specific user ID
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class WaitlistEntry(Base):
    __tablename__ = "waitlist"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    referral_code = Column(String, unique=True, index=True)  # Their unique code
    referred_by_code = Column(String, nullable=True)  # Code they used to signup
    position_in_line = Column(Integer, default=0)
    priority_score = Column(Integer, default=0)  # Bumped by referrals
    status = Column(String, default="waiting")  # waiting, invited, converted
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
