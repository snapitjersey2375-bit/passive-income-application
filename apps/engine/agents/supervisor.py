from .base import BaseAgent
from typing import Dict, Any

class Supervisor(BaseAgent):
    """
    Agent representing the Human-in-the-Loop decision maker.
    """
    def __init__(self):
        super().__init__(name="Supervisor")
    
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        content_id = context.get("content_id")
        decision = context.get("decision", "pending")
        
        self.log(f"Reviewing content {content_id}. Decision: {decision}")
        
        if decision == "approved":
            return {"status": "ready_for_upload"}
        elif decision == "rejected":
            return {"status": "archived"}
            
        return {"status": "pending_approval"}
