from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Dict
import asyncio

from apps.engine.core.circuit_breaker import CircuitBreaker
from apps.engine.db.session import get_db
from apps.engine.db.models import Content, User, Ledger, AnalyticsHistory, SocialConnection
from apps.engine.core.schemas import ContentSchema
from apps.engine.core.log_store import log_store

app = FastAPI(title="NexusFlow Engine", version="0.2.2")

def get_current_user(db: Session):
    """
    Helper to get the current user. In a real app, this would use JWT tokens.
    For this prototype, it defaults to the main testing account.
    """
    user = db.query(User).filter(User.email == "dipali@nexusflow.ai").first()
    if not user:
        # Auto-create if missing (e.g. after DB reset)
        user = User(email="dipali@nexusflow.ai")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

circuit_breaker = CircuitBreaker(max_daily_spend=50.0)

@app.get("/")
def root():
    return {"status": "operational", "system": "NexusFlow Engine", "db": "SQLite"}

@app.get("/health")
def health_check():
    """Health check endpoint for deployment platforms (Railway, etc.)"""
    return {"status": "healthy", "version": "0.2.2"}

@app.get("/queue/daily", response_model=Dict[str, List[ContentSchema]])
def get_daily_queue(db: Session = Depends(get_db)):
    """
    Returns pending content from the REAL database.
    """
    contents = db.query(Content).filter(Content.status == "pending_review").limit(10).all()
    return {"queue": contents}

@app.post("/queue/{content_id}/approve")
async def approve_content(content_id: str, db: Session = Depends(get_db)):
    from apps.engine.core.ledger_service import LedgerService
    
    # 1. Fetch User
    user = get_current_user(db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2. Check Solvency
    APPROVAL_COST = 5.0 
    
    if not LedgerService.check_funds(db, user.id, APPROVAL_COST):
        raise HTTPException(
            status_code=402, 
            detail="Insufficient Funds. Please request a capital injection."
        )

    # 3. Check Circuit Breaker
    if not circuit_breaker.check_spend(db, user.id, APPROVAL_COST):
        raise HTTPException(
            status_code=503, 
            detail="Circuit Breaker Tripped: Daily spend limit reached."
        )

    # 4. Process Approval
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
        
    content.status = "approved"
    content.distribution_status = "processing"
    db.commit()

    # 5. Trigger Distribution (Upload)
    from apps.engine.agents.traffic import TrafficAgent
    agent = TrafficAgent()
    
    try:
        upload_result = await asyncio.wait_for(
            agent.run({
                "title": content.title,
                "description": content.description,
                "content_id": content.id
            }), 
            timeout=60.0
        )
    except asyncio.TimeoutError:
        content.status = "pending_review"
        content.distribution_status = "failed"
        db.commit()
        raise HTTPException(status_code=504, detail="Upload timed out (60s limit). Try again.")
    
    if upload_result.get("upload_status") == "success":
        content.distribution_status = "live"
        content.video_url = upload_result.get("url")
    else:
        content.distribution_status = "failed"
        
    # 6. Record Spend in Ledger
    LedgerService.record_transaction(
        db, 
        user.id, 
        -APPROVAL_COST, 
        f"Ad approval for Content {content_id}", 
        "ad_spend"
    )
    
    db.commit()
    
    return {
        "status": "approved", 
        "id": content_id, 
        "spend_incurred": APPROVAL_COST,
        "distribution": content.distribution_status
    }

@app.post("/queue/{content_id}/reject")
def reject_content(content_id: str, db: Session = Depends(get_db)):
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
        
    content.status = "rejected"
    db.commit()
    return {"status": "rejected", "id": content_id}

@app.post("/safety/trip")
def manual_trip():
    circuit_breaker._trip()
    return {"status": "circuit_broken", "message": "Manual override activated."}

# --- Authentication ---
from pydantic import BaseModel
class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/login")
def login(creds: LoginRequest, db: Session = Depends(get_db)):
    # Mock Auth for Skeleton Phase
    # Real app would hash passwords (bcrypt)
    from apps.engine.db.models import User
    
    user = db.query(User).filter(User.email == creds.email).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    # Mock Password Check (In dev we assume 'password' is the universal password for the mock user)
    if creds.password != "password":
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    return {"token": f"mock_token_{user.id}", "user_id": user.id}

# --- User Settings ---
class SettingsRequest(BaseModel):
    risk_tolerance: float
    is_grandma_mode: bool
    persona: str = "grandma"

@app.get("/user/settings")
def get_settings(user_id: str = "default", db: Session = Depends(get_db)):
    # Fetch current user using helper
    user = get_current_user(db)
        
    # GENESIS GRANT: Check if user has money. If no history, give seed capital.
    from apps.engine.core.ledger_service import LedgerService
    current_balance = LedgerService.get_balance(db, user.id)
    
    # If balance is 0 and no history exists (or just broke), provide seed.
    # For now, we only grant if they have absolutely 0 transactions to avoid infinite money glitch loop on refresh.
    # Actually, let's check if the ledger is empty for this user.
    from apps.engine.db.models import Ledger
    has_history = db.query(Ledger).filter(Ledger.user_id == user.id).first()
    
    if not has_history:
        print(f"[GENESIS] Granting seed capital to {user.email}")
        LedgerService.record_transaction(
            db,
            user.id,
            100.00,
            "Genesis Grant - Seed Capital",
            "deposit"
        )
        current_balance = 100.00
    
    # Referrals: Generate one if missing
    if not user.referral_code:
        import uuid
        # Simple unique code: first 8 chars of a new UUID
        user.referral_code = str(uuid.uuid4())[:8].upper()
        db.commit()
    
    return {
        "risk_tolerance": user.risk_tolerance,
        "is_grandma_mode": user.is_grandma_mode,
        "persona": user.persona,
        "wallet_balance": current_balance,
        "referral_code": user.referral_code,
        "referral_count": user.referral_count or 0
    }

@app.post("/user/settings")
def update_settings(settings: SettingsRequest, db: Session = Depends(get_db)):
    user = get_current_user(db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.risk_tolerance = settings.risk_tolerance
    user.is_grandma_mode = settings.is_grandma_mode
    user.persona = settings.persona
    
    # Sync is_grandma_mode for UI if persona is grandma
    if settings.persona == "grandma":
        user.is_grandma_mode = True
    elif settings.persona == "degen":
        user.is_grandma_mode = False
        user.risk_tolerance = 0.9 # Force high risk
    else:
        user.is_grandma_mode = False
        
    db.commit()
    
    return {"status": "updated", "settings": settings}

# --- Referral System ---
class ReferralClaim(BaseModel):
    user_id: str
    code: str

@app.post("/user/referral/claim")
def claim_referral(claim: ReferralClaim, db: Session = Depends(get_db)):
    """
    Links the specified user to a referrer.
    """
    user = db.query(User).filter(User.id == claim.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Fraud Protection 1: Account Age Limit (24 hours)
    from datetime import datetime, timedelta
    import pytz
    
    # Handle naive vs aware datetimes for SQLite
    now = datetime.now(pytz.UTC)
    user_created_at = user.created_at
    if user_created_at and user_created_at.tzinfo is None:
        user_created_at = pytz.UTC.localize(user_created_at)
        
    if user_created_at and (now - user_created_at) > timedelta(hours=24):
        raise HTTPException(status_code=400, detail="Referral codes can only be claimed within 24 hours of account creation.")

    if user.referred_by:
         raise HTTPException(status_code=400, detail="Already referred.")
         
    referrer = db.query(User).filter(User.referral_code == claim.code).first()
    if not referrer:
        raise HTTPException(status_code=404, detail="Invalid referral code.")
        
    if referrer.id == user.id:
        raise HTTPException(status_code=400, detail="Cannot refer yourself.")
        
    # Fraud Protection 2: Circular Referral Prevention
    if referrer.referred_by == user.referral_code:
        # Flag both for suspicious activity
        user.is_shadow_banned = True
        referrer.is_shadow_banned = True
        db.commit()
        raise HTTPException(status_code=400, detail="Circular referrals are not allowed. Accounts flagged.")
        
    # Link
    user.referred_by = claim.code
    
    # Update Referrer Stats
    referrer.referral_count += 1
    
    # Reward Referrer (Commission) - $10 base
    from apps.engine.core.ledger_service import LedgerService
    LedgerService.record_transaction(
        db, referrer.id, 10.00, f"Referral Bonus (User {user.email})", "commission"
    )
    
    # Milestone Bonuses
    if referrer.referral_count == 5:
        LedgerService.record_transaction(db, referrer.id, 50.00, "Referral Milestone: 5 Invites!", "commission")
    elif referrer.referral_count == 10:
        LedgerService.record_transaction(db, referrer.id, 100.00, "Referral Milestone: 10 Invites!", "commission")
    elif referrer.referral_count == 50:
        LedgerService.record_transaction(db, referrer.id, 500.00, "Legendary Curator Milestone: 50 Invites!", "commission")
    
    db.commit()
    return {"status": "success", "referrer_email": referrer.email}

@app.post("/user/capital/inject")
def request_capital(db: Session = Depends(get_db)):
    """
    Mock endpoint to inject seed capital if the user is broke.
    """
    user = get_current_user(db)
    from apps.engine.core.ledger_service import LedgerService
    
    current_balance = LedgerService.get_balance(db, user.id)
    if current_balance > 5.0:
        raise HTTPException(status_code=400, detail="You still have funds, curator! Spend them first.")
        
    LedgerService.record_transaction(
        db,
        user.id,
        50.00,
        "Emergency Capital Injection",
        "deposit"
    )
    db.commit()
    return {"status": "success", "new_balance": current_balance + 50.00}

@app.get("/user/profile")
def get_user_profile(user_id: str = "default", db: Session = Depends(get_db)):
    """
    Returns comprehensive user statistics and earnings data.
    """
    user = get_current_user(db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    from apps.engine.core.ledger_service import LedgerService
    balance = LedgerService.get_balance(db, user.id)
    
    # Calculate referral metrics
    referral_earnings = db.query(func.sum(Ledger.amount)).filter(
        Ledger.user_id == user.id,
        Ledger.transaction_type == "commission"
    ).scalar() or 0
    
    # Calculate content metrics
    content_count = db.query(Content).filter(Content.user_id == user.id).count()
    approved_count = db.query(Content).filter(Content.user_id == user.id, Content.status == "approved").count()
    
    return {
        "email": user.email,
        "referral_code": user.referral_code,
        "referral_count": user.referral_count,
        "referral_earnings": float(referral_earnings),
        "wallet_balance": float(balance),
        "stats": {
            "total_content": content_count,
            "approved_content": approved_count,
            "policy_violations": user.policy_violation_count
        }
    }

@app.get("/logs", response_model=List[Dict])
def get_agent_logs():
    """
    Returns the recent stack of agent thoughts/logs.
    """
    return log_store.get_logs()

# --- Agent Triggers ---
@app.post("/content/swarm")
async def trigger_swarm(niche: str = "general", db: Session = Depends(get_db)):
    """
    Triggers the 'ContentSwarm' agent to generate a new idea.
    """
    from apps.engine.agents.content_swarm import ContentSwarm
    agent = ContentSwarm()
    # Pass niche and user_id to run.
    user_id = None
    # Use get_current_user helper
    user = get_current_user(db)
    user_id = user.id if user else None
        
    try:
        print(f"[MAIN] Triggering swarm for niche: {niche} (User: {user_id})")
        try:
            result = await asyncio.wait_for(
                agent.run({"niche": niche, "user_id": user_id}), 
                timeout=60.0
            )
        except asyncio.TimeoutError:
            raise HTTPException(status_code=504, detail="Swarm generation timed out (60s limit). Try again.")
            
        print(f"[MAIN] Swarm result: {result}")
        
        if result.get("status") == "rejected":
             raise HTTPException(status_code=429, detail=result.get("reason", "Request rejected by agent"))
             
        return {"status": "triggered", "agent": "ContentSwarm", "result": result}
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"[MAIN_ERROR] {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# --- Analytics ---
@app.post("/analytics/simulate")
async def simulate_traffic(db: Session = Depends(get_db)):
    """
    Triggers the TrafficAgent to simulate performance for all approved content.
    """
    from apps.engine.agents.traffic import TrafficAgent
    agent = TrafficAgent()
    
    approved_content = db.query(Content).filter(Content.status == "approved").all()
    if not approved_content:
        return {"status": "skipped", "message": "No approved content to simulate."}
        
    for content in approved_content:
        agent.simulate_performance(db, content.id)
        
    # 3. Record Snapshot for History
    user = get_current_user(db)
    from apps.engine.core.ledger_service import LedgerService
    total_rev = db.query(func.sum(Content.monetization_potential)).filter(Content.user_id == user.id, Content.status == "approved").scalar() or 0
    total_views = db.query(func.sum(Content.view_count)).filter(Content.user_id == user.id, Content.status == "approved").scalar() or 0
    
    snapshot = AnalyticsHistory(
        user_id=user.id,
        total_views=int(total_views),
        total_revenue=float(total_rev)
    )
    db.add(snapshot)
    db.commit()
        
    return {"status": "success", "simulated_count": len(approved_content)}

@app.get("/analytics/stats")
def get_analytics(db: Session = Depends(get_db)):
    """
    Returns aggregated stats for Charts using real DB data and History snapshots.
    """
    user = get_current_user(db)
    
    # 1. Historical Trends from AnalyticsHistory
    history = db.query(AnalyticsHistory).filter(AnalyticsHistory.user_id == user.id).order_by(AnalyticsHistory.timestamp.asc()).all()
    
    if not history:
        # Fallback to current state if no history yet
        viral_data = [{"name": "Start", "score": 0}]
        revenue_data = [{"name": "Start", "amount": 0}]
    else:
        viral_data = [
            {"name": h.timestamp.strftime("%H:%M"), "score": h.total_views} 
            for h in history[-7:] # Show last 7 snapshots
        ]
        revenue_data = [
            {"name": h.timestamp.strftime("%H:%M"), "amount": int(h.total_revenue)} 
            for h in history[-7:]
        ]
    
    # 2. Current ROI Summary
    total_metrics = db.query(
        func.sum(Content.monetization_potential).label("total_rev"),
        func.sum(Content.view_count).label("total_views")
    ).filter(Content.user_id == user.id, Content.status == "approved").first()
    
    return {
        "viral_trends": viral_data,
        "revenue_projections": revenue_data,
        "summary": {
            "total_views": int(total_metrics.total_views or 0),
            "total_revenue": int(total_metrics.total_rev or 0),
            "approved_count": db.query(Content).filter(Content.user_id == user.id, Content.status == "approved").count()
        }
    }

@app.get("/analytics/ledger")
def get_ledger(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """
    Returns the persistent history from the Ledger table with pagination.
    """
    from apps.engine.db.models import Ledger
    entries = db.query(Ledger).order_by(Ledger.id.desc()).offset(skip).limit(limit).all()
    return {"entries": entries}

@app.put("/content/{content_id}")
def update_content(content_id: str, payload: dict, db: Session = Depends(get_db)):
    """
    Updates content title/description (Remix feature).
    """
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    if "title" in payload:
        content.title = payload["title"]
    if "description" in payload:
        content.description = payload["description"]
        
    db.commit()
    return {"status": "updated", "content": content}

@app.get("/content/search")
def search_content(q: str, db: Session = Depends(get_db)):
    """
    Simple fuzzy search for content.
    """
    results = db.query(Content).filter(
        (Content.title.contains(q)) | (Content.description.contains(q))
    ).limit(10).all()
    return {"results": results}

@app.get("/activity/recent")
def get_recent_activity():
    """
    Returns a list of recent (mocked) global activity items for social proof (FOMO).
    """
    names = ["Alice", "Bob", "CryptoCat", "Alex", "Sarah", "BigCuration", "NexusGen", "GrandmaBakes", "ViralPro"]
    actions = ["approved content", "remixed a video", "earned $50 bonus", "reached 10 referrals", "went viral in 'Tech'", "started a new swarm"]
    
    import random
    import time
    
    activities = []
    for _ in range(5):
        user = random.choice(names)
        action = random.choice(actions)
        activities.append({
            "user": user,
            "action": action,
            "time": "Just now"
        })
        
    return {"activities": activities}

@app.get("/stats/global")
def get_global_stats(db: Session = Depends(get_db)):
    """
    Returns public aggregate data for the landing page.
    """
    # 1. Total Content
    total_content = db.query(Content).count()
    
    # 2. Total Payouts (Mocked + Real)
    # Start with a base "fake" number to make it look live, then add real db values
    base_payout = 84392.00 
    real_payout = db.query(func.sum(Content.monetization_potential)).filter(Content.status == "approved").scalar() or 0
    
    # 3. Active Users (Mocked base + Real count)
    base_users = 1200
    real_users = db.query(User).count()
    
    return {
        "total_payouts": base_payout + float(real_payout),
        "total_content": 15000 + total_content,
        "active_curators": base_users + real_users
    }

@app.get("/stats/activity")
def get_live_activity(db: Session = Depends(get_db)):
    """
    Returns real recent approved mix for the ticker.
    """
    recent_approved = db.query(Content).filter(Content.status == "approved").order_by(Content.updated_at.desc()).limit(5).all()
    
    activity_feed = []
    
    # If we don't have enough real data, mix in some fake ones
    if len(recent_approved) < 5:
        return get_recent_activity() # Fallback to the mock function we already have
        
    for content in recent_approved:
        # Mask user ID
        short_uid = content.user_id[:4] if content.user_id else "Anon"
        activity_feed.append({
            "user": f"Curator-{short_uid}",
            "action": f"approved '{content.title}'",
            "time": "Just now", # In a real app calc relative time
            "value": float(content.monetization_potential)
        })
        
    return {"activities": activity_feed}

# --- Social Connections (Publisher System) ---

@app.get("/social/connections")
def get_social_connections(db: Session = Depends(get_db)):
    """
    Returns user's connected social media accounts.
    """
    user = get_current_user(db)
    connections = db.query(SocialConnection).filter(
        SocialConnection.user_id == user.id
    ).all()
    
    return {
        "connections": [
            {
                "id": conn.id,
                "platform": conn.platform,
                "account_name": conn.account_name,
                "is_active": conn.is_active,
                "created_at": conn.created_at.isoformat() if conn.created_at else None
            }
            for conn in connections
        ]
    }

@app.post("/social/connect/{platform}")
def connect_social_account(platform: str, db: Session = Depends(get_db)):
    """
    Mock OAuth flow - connects a social account.
    In production, this would redirect to platform OAuth.
    """
    user = get_current_user(db)
    
    # Check if already connected
    existing = db.query(SocialConnection).filter(
        SocialConnection.user_id == user.id,
        SocialConnection.platform == platform
    ).first()
    
    if existing:
        existing.is_active = True
        db.commit()
        return {"status": "reactivated", "platform": platform}
    
    # Create mock connection
    import uuid
    connection = SocialConnection(
        user_id=user.id,
        platform=platform,
        access_token=f"mock_token_{uuid.uuid4().hex[:16]}",
        refresh_token=f"mock_refresh_{uuid.uuid4().hex[:16]}",
        account_name=f"@{user.email.split('@')[0]}_{platform}",
        account_id=f"{platform}_{uuid.uuid4().hex[:8]}",
        is_active=True
    )
    db.add(connection)
    db.commit()
    
    return {
        "status": "connected",
        "platform": platform,
        "account_name": connection.account_name
    }

@app.delete("/social/disconnect/{platform}")
def disconnect_social_account(platform: str, db: Session = Depends(get_db)):
    """
    Disconnects (deactivates) a social account.
    """
    user = get_current_user(db)
    
    connection = db.query(SocialConnection).filter(
        SocialConnection.user_id == user.id,
        SocialConnection.platform == platform
    ).first()
    
    if not connection:
        raise HTTPException(status_code=404, detail=f"No {platform} account connected")
    
    connection.is_active = False
    db.commit()
    
    return {"status": "disconnected", "platform": platform}

@app.post("/content/{content_id}/publish")
async def publish_content(content_id: str, db: Session = Depends(get_db)):
    """
    Triggers the PublisherAgent to post content to connected platforms.
    """
    from apps.engine.agents.publisher import PublisherAgent
    
    user = get_current_user(db)
    agent = PublisherAgent()
    
    try:
        result = await asyncio.wait_for(
            agent.run({
                "content_id": content_id,
                "user_id": user.id
            }),
            timeout=60.0
        )
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Publishing timed out (60s limit). Please try again.")
    
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("reason"))
    
    if result.get("status") == "pending":
        raise HTTPException(status_code=428, detail=result.get("reason"))
    
    return result

# --- Waitlist System ---
class WaitlistSignup(BaseModel):
    email: str
    referral_code: str = None  # Optional code from referrer

@app.post("/waitlist/signup")
def waitlist_signup(signup: WaitlistSignup, db: Session = Depends(get_db)):
    """
    Adds a user to the waitlist with optional referral tracking.
    """
    from apps.engine.db.models import WaitlistEntry
    import uuid
    
    # Check if email already exists
    existing = db.query(WaitlistEntry).filter(WaitlistEntry.email == signup.email).first()
    if existing:
        return {
            "status": "already_registered",
            "position": existing.position_in_line,
            "referral_code": existing.referral_code
        }
    
    # Calculate position (simple: count + 1)
    current_count = db.query(WaitlistEntry).count()
    position = current_count + 1
    
    # Generate unique referral code for this user
    unique_code = str(uuid.uuid4())[:8].upper()
    
    # Create entry
    entry = WaitlistEntry(
        email=signup.email,
        referral_code=unique_code,
        referred_by_code=signup.referral_code,
        position_in_line=position,
        priority_score=0
    )
    db.add(entry)
    
    # If they used a referral code, boost the referrer
    if signup.referral_code:
        referrer = db.query(WaitlistEntry).filter(WaitlistEntry.referral_code == signup.referral_code).first()
        if referrer:
            referrer.priority_score += 10  # Each referral gives 10 points
            db.add(referrer)
    
    db.commit()
    
    return {
        "status": "success",
        "position": position,
        "referral_code": unique_code,
        "message": f"You're #{position} in line! Share your code to move up."
    }

@app.get("/waitlist/status/{email}")
def waitlist_status(email: str, db: Session = Depends(get_db)):
    """
    Check waitlist status for an email.
    """
    from apps.engine.db.models import WaitlistEntry
    
    entry = db.query(WaitlistEntry).filter(WaitlistEntry.email == email).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Email not found in waitlist")
    
    # Calculate effective position (original position minus priority boost)
    effective_position = max(1, entry.position_in_line - (entry.priority_score // 10))
    
    # Count how many people they've referred
    referral_count = db.query(WaitlistEntry).filter(WaitlistEntry.referred_by_code == entry.referral_code).count()
    
    return {
        "email": entry.email,
        "original_position": entry.position_in_line,
        "effective_position": effective_position,
        "referral_code": entry.referral_code,
        "referral_count": referral_count,
        "priority_score": entry.priority_score,
        "status": entry.status
    }

@app.get("/waitlist/leaderboard")
def waitlist_leaderboard(db: Session = Depends(get_db)):
    """
    Returns top referrers on the waitlist.
    """
    from apps.engine.db.models import WaitlistEntry
    
    top_referrers = db.query(WaitlistEntry).order_by(WaitlistEntry.priority_score.desc()).limit(10).all()
    
    return {
        "leaderboard": [
            {
                "email": entry.email[:3] + "***",  # Mask email
                "priority_score": entry.priority_score,
                "effective_position": max(1, entry.position_in_line - (entry.priority_score // 10))
            }
            for entry in top_referrers
        ]
    }
