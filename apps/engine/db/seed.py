from sqlalchemy.orm import Session
from apps.engine.db.session import SessionLocal, engine, Base
from apps.engine.db.models import Content, User
from apps.engine.db.mock_data import generate_mock_queue
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """Create tables if they don't exist"""
    Base.metadata.create_all(bind=engine)
    logger.info("Tables created (if they didn't exist).")

def seed_users(db: Session):
    """Seed the database with a default mock user"""
    existing_user = db.query(User).filter(User.email == "dipali@nexusflow.ai").first()
    if existing_user:
        logger.info("Mock user already exists. Skipping.")
        return

    logger.info("Seeding mock user...")
    user = User(
        email="dipali@nexusflow.ai",
        hashed_password="password",
        is_grandma_mode=False,
        risk_tolerance=0.8
    )
    db.add(user)
    db.commit()
    
    # Economy 2.0: Seed Funding
    from apps.engine.core.ledger_service import LedgerService
    LedgerService.record_transaction(
        db,
        user.id,
        1000.0,
        "Seed Round Funding",
        "funding"
    )
    
    logger.info("User seed complete! Added $1000 funding.")

def seed_data(db: Session):
    """Seed the database with mock content"""
    # Seed user first
    seed_users(db)
    
    # Check if data exists
    existing_count = db.query(Content).count()
    if existing_count > 0:
        logger.info(f"Database already has {existing_count} items. Skipping seed.")
        return

    # Fetch user for ownership
    user = db.query(User).filter(User.email == "dipali@nexusflow.ai").first()
    
    logger.info("Seeding database with mock data...")
    mock_items = generate_mock_queue()
    
    for item in mock_items:
        content = Content(
            id=item["id"],
            title=item["title"],
            confidence_score=item["confidence_score"],
            status=item["status"],
            thumbnail_url=item["thumbnail_url"],
            platform="tiktok", # Default
            daily_budget=15.0,
            campaign_status="active",
            user_id=user.id if user else None,
            niche="general",
            description=f"Auto-generated mock content for {item['title']}",
            # Add projections from mock data
            viral_potential=item.get("viral_potential", 0.0),
            monetization_potential=item.get("monetization_potential", 0.0),
            # Add stats from mock data
            view_count=item.get("view_count", 0),
            like_count=item.get("like_count", 0),
            comment_count=item.get("comment_count", 0),
            share_count=item.get("share_count", 0)
        )
        db.add(content)
    
    db.commit()
    logger.info("Seeding complete!")

if __name__ == "__main__":
    init_db()
    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()
