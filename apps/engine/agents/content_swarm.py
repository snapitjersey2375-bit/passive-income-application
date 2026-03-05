from .base import BaseAgent
from typing import Dict, Any
from apps.engine.core.llm import LLMClient
from apps.engine.db.session import engine
from apps.engine.db.models import Content, User
from .researcher import ResearchAgent
from .policy_agent import PolicyAgent
from .visualizer import VisualizerAgent
from .video_gen import VideoGenAgent
from sqlalchemy.orm import Session

class ContentSwarm(BaseAgent):
    """
    Agent responsible for finding and remixing video content.
    """
    def __init__(self):
        super().__init__(name="ContentSwarm")
        self.llm = LLMClient()
        self.researcher = ResearchAgent()
        self.policy_agent = PolicyAgent()
        self.visualizer = VisualizerAgent()
        self.video_gen = VideoGenAgent()
    
    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        self.log("Scouting for viral content...")
        
        niche = context.get("niche", "general")
        
        # 1. Research Step
        research_result = await self.researcher.run({"niche": niche})
        research_context = research_result.get("summary", "")
        self.log(f"Research gathered: {len(research_context)} chars")

        # 1.5 Fetch User & Saturation Check (Niche Partitioning)
        user_id = context.get("user_id")
        with Session(engine) as session:
            # Saturation Check: Max 50 users per niche
            from sqlalchemy import func
            active_users_in_niche = session.query(func.count(Content.user_id.distinct()))\
                .filter(Content.niche == niche)\
                .scalar()
            
            if active_users_in_niche and active_users_in_niche >= 50:
                self.log(f"⚠️ NICHE SATURATED: {niche} has {active_users_in_niche} users. Max 50.")
                return {
                    "status": "rejected",
                    "reason": "Niche Saturated (Max 50 Users)",
                    "suggestion": "Try 'Sub-Niche' or 'Blue Ocean' strategy."
                }

            user = session.query(User).filter(User.id == user_id).first() if user_id else session.query(User).first()
            if user and user.is_shadow_banned:
                self.log(f"Wait... User {user.id} is SHADOW BANNED. simulating busy signal.")
                return {
                    "status": "error", 
                    "reason": "System requires manual verification. Please contact support."
                }
                
            risk_tolerance = user.risk_tolerance if user else 0.5
            persona = user.persona if user and hasattr(user, 'persona') else "grandma"
            current_user_id = user.id if user else None

        # 2. Generate Idea
        idea = self.llm.generate_idea(niche=niche, context_data=research_context, risk_tolerance=risk_tolerance, persona=persona)
        
        # 3. Policy Check (Compliance filter)
        policy_result = await self.policy_agent.run({
            "title": idea["title"],
            "description": idea["description"]
        })
        
        # 4. Visualization Step
        viz_result = await self.visualizer.run({
            "title": idea["title"],
            "niche": niche
        })

        # 5. Video Generation Step (HTML5)
        video_result = await self.video_gen.run({
            "title": idea["title"],
            "description": idea["description"],
            "image_url": viz_result["thumbnail_url"]
        })
        
        # Persist to DB & Enforce Policy
        with Session(engine) as session:
            # Re-fetch user to update policy stats if needed
            if current_user_id:
                user = session.query(User).filter(User.id == current_user_id).first()
            
            final_status = "pending_review"
            
            if not policy_result["is_compliant"]:
                self.log(f"❌ POLICY VIOLATION: {idea['title']}")
                final_status = "rejected"
                
                if user:
                    user.policy_violation_count += 1
                    if user.policy_violation_count >= 3:
                        user.is_shadow_banned = True
                        self.log(f"🚨 USER SHADOW BANNED: {user.email} (Violations: {user.policy_violation_count})")
                    session.add(user) # Mark as modified
            
            content = Content(
                title=idea["title"],
                description=idea["description"],
                confidence_score=idea["confidence_score"],
                status=final_status,
                thumbnail_url=viz_result["thumbnail_url"],
                video_url=video_result["video_url"], # HTML5 Video URL
                platform="tiktok",
                # Niche Partitioning Fields
                niche=niche,
                user_id=current_user_id,
                # New compliance fields
                policy_status=policy_result["is_compliant"],
                policy_reason=policy_result["reason"]
            )
            session.add(content)
            session.commit()
            content_id = content.id
            
        self.log(f"Generated content: {idea['title']} (Status: {final_status})")
        
        return {
            "content_id": content_id,
            "title": idea["title"],
            "status": final_status, 
            "reason": policy_result["reason"],
            "video_url": video_result["video_url"]
        }
