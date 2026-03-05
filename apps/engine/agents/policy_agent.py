from .base import BaseAgent
from typing import Dict, Any
from apps.engine.core.llm import LLMClient
import json

class PolicyAgent(BaseAgent):
    """
    Agent responsible for checking content compliance against platform policies.
    """
    def __init__(self):
        super().__init__(name="PolicyAgent")
        self.llm = LLMClient()

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs the compliance check on a given video concept.
        :param context: Must contain 'title' and 'description'
        """
        title = context.get("title", "")
        description = context.get("description", "")
        
        self.log(f"Reviewing content: {title}")
        
        if self.llm.mode == "mock":
            return self._mock_check(title, description)
            
        return await self._real_check(title, description)

    async def _real_check(self, title: str, description: str) -> Dict[str, Any]:
        try:
            from openai import OpenAI
            from apps.engine.core.prompts import POLICY_CHECK_SYSTEM_PROMPT
            
            client = OpenAI(api_key=self.llm.api_key)
            
            user_prompt = f"Review the following video concept for policy compliance:\n\nTitle: {title}\nDescription: {description}"
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": POLICY_CHECK_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0 # High precision
            )
            
            content_str = response.choices[0].message.content
            # Clean possible markdown
            content_str = content_str.replace("```json", "").replace("```", "").strip()
            
            data = json.loads(content_str)
            return {
                "is_compliant": bool(data.get("is_compliant", True)),
                "reason": data.get("reason", "Approved")
            }
            
        except Exception as e:
            self.log(f"Policy check error: {e}. Falling back to approval.")
            return {"is_compliant": True, "reason": "Approved (Check Failed)"}

    def _mock_check(self, title: str, description: str) -> Dict[str, Any]:
        # Simple keywords for mock mode
        forbidden = ["casino", "betting", "gambling", "crypto scam", "hack", "illegal", "medical advice", "cure"]
        text = (title + " " + description).lower()
        
        for word in forbidden:
            if word in text:
                return {
                    "is_compliant": False,
                    "reason": f"Violates policy: Found forbidden keyword '{word}'"
                }
                
        return {"is_compliant": True, "reason": "Approved"}
