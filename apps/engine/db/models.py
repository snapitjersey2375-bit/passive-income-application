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
    tier = Column(String, default="free") # free, pro, enterprise

    # Growth / Referrals
    referral_code = Column(String, unique=True, index=True, nullable=True) # e.g. "BOB-123"
    referred_by = Column(String, nullable=True) # Code of the referrer
    referral_count = Column(Integer, default=0)
    
    # Security / Compliance
    policy_violation_count = Column(Integer, default=0)
    is_shadow_banned = Column(Boolean, default=False)

    # YouTube OAuth
    youtube_credentials = Column(String, nullable=True)  # Encrypted JSON
    youtube_authorized = Column(Boolean, default=False)
    youtube_authorized_at = Column(DateTime(timezone=True), nullable=True)

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
    platform_id = Column(String, nullable=True)
    platform_url = Column(String, nullable=True)

    # Statistics
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    click_count = Column(Integer, default=0) # NEW: Affiliate link clicks
    conversion_count = Column(Integer, default=0) # NEW: Conversions from this content

    # NEW: Affiliate revenue tracking
    total_affiliate_revenue = Column(Numeric(10, 2), default=0.00) # Gross commission
    platform_fee_from_content = Column(Numeric(10, 2), default=0.00) # 40% platform takes
    user_earnings_from_content = Column(Numeric(10, 2), default=0.00) # 60% user gets

    # Projections
    viral_potential = Column(Float, default=0.0) # 0.0 to 1.0 (or higher)
    monetization_potential = Column(Numeric(10, 2), default=0.0) # Predicted Dollar Value

    # NEW: Affiliate links
    primary_affiliate_link = Column(String, nullable=True) # Main product link
    affiliate_network_used = Column(String, nullable=True) # Which affiliate network (amazon, shopify, cj, etc)

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
    transaction_type = Column(String) # affiliate_commission, platform_fee, user_earnings, payout, deposit

    # NEW: Profit-sharing breakdown (for affiliate_commission type)
    gross_revenue = Column(Numeric(10, 2), default=0.00) # Total commission earned
    platform_fee = Column(Numeric(10, 2), default=0.00) # 40% platform takes
    user_earnings = Column(Numeric(10, 2), default=0.00) # 60% user gets

    # NEW: Affiliate tracking
    affiliate_network = Column(String, nullable=True) # amazon, cj_affiliate, rakuten, shopify, direct
    affiliate_source = Column(String, nullable=True) # Product name or brand
    affiliate_id = Column(String, nullable=True) # Reference to the affiliate account

    # NEW: Balance snapshot for ledger display
    balance_snapshot = Column(Numeric(10, 2), nullable=True) # Balance after this transaction

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


class AffiliateNetwork(Base):
    """Track user connections to affiliate networks (Amazon, CJ, Rakuten, etc)."""
    __tablename__ = "affiliate_networks"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    network_name = Column(String, index=True) # amazon, cj_affiliate, rakuten, shopify_affiliate, direct
    account_id = Column(String) # User's account ID on that network
    api_key = Column(String, nullable=True) # Encrypted API key/token
    is_active = Column(Boolean, default=True)
    total_earnings = Column(Numeric(10, 2), default=0.00) # Total commission from this network
    platform_fee_collected = Column(Numeric(10, 2), default=0.00) # 40% platform collected
    user_earned = Column(Numeric(10, 2), default=0.00) # 60% user earned
    last_synced = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class UserEarningsDaily(Base):
    """Daily earnings snapshot for dashboard and analytics."""
    __tablename__ = "user_earnings_daily"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    date = Column(String, index=True) # YYYY-MM-DD format
    gross_revenue = Column(Numeric(10, 2), default=0.00) # Total commission that day
    platform_fee = Column(Numeric(10, 2), default=0.00) # 40% platform took
    user_earnings = Column(Numeric(10, 2), default=0.00) # 60% user got

    # Breakdown by network
    amazon_revenue = Column(Numeric(10, 2), default=0.00)
    cj_revenue = Column(Numeric(10, 2), default=0.00)
    rakuten_revenue = Column(Numeric(10, 2), default=0.00)
    shopify_revenue = Column(Numeric(10, 2), default=0.00)
    direct_revenue = Column(Numeric(10, 2), default=0.00)

    content_count = Column(Integer, default=0) # Content posted that day
    total_views = Column(Integer, default=0) # Total views that day
    total_clicks = Column(Integer, default=0) # Affiliate link clicks
    total_conversions = Column(Integer, default=0) # Actual sales

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
