from sqlalchemy.orm import Session
from .models import Content, User
from .session import engine
import random

def populate_mock_data():
    session = Session(bind=engine)
    
    # Create Default User
    if not session.query(User).filter_by(email="supervisor@nexusflow.ai").first():
        user = User(email="supervisor@nexusflow.ai", risk_tolerance=0.7)
        session.add(user)
    
    # Create Content
    topics = ["Crypto", "AI", "Fitness", "Tech", "Money"]
    
    if session.query(Content).count() < 5:
        for i in range(5):
            content = Content(
                title=f"Viral {random.choice(topics)} Video {i+1}",
                confidence_score=round(random.uniform(0.7, 0.99), 2),
                description="Auto-generated content for review",
                thumbnail_url="https://via.placeholder.com/150",
                status="pending_review",
                
                # Mock Stats
                view_count=random.randint(1000, 1000000),
                like_count=random.randint(100, 50000),
                comment_count=random.randint(10, 5000),
                share_count=random.randint(5, 1000),
                viral_potential=round(random.uniform(0.5, 10.0), 1),
                monetization_potential=round(random.uniform(10.0, 5000.0), 2)
            )
            session.add(content)
    
    session.commit()
    print("Mock data populated.")
    session.close()

if __name__ == "__main__":
    populate_mock_data()
