from .base import BaseAgent
from duckduckgo_search import AsyncDDGS
import asyncio
from typing import Dict, Any

class ResearchAgent(BaseAgent):
    """
    Agent responsible for gathering real-time data from the web.
    """
    def __init__(self):
        super().__init__(name="ResearchAgent")

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the search_trends logic via the standard Agent interface.
        """
        niche = context.get("niche", "general")
        summary = await self.search_trends(niche)
        return {"summary": summary}

    async def search_trends(self, niche: str) -> str:
        """
        Searches for the latest news and trends in a specific niche.
        Returns a summarized string context.
        """
        self.log(f"Scouting the web for: {niche}")
        
        query = f"latest trends and news in {niche} {2024}"
        
        try:
            async with AsyncDDGS() as ddgs:
                results = await ddgs.text(query, max_results=5)
                
            if not results:
                return "No recent news found."
                
            context = "Recent News:\n"
            for i, res in enumerate(results):
                context += f"{i+1}. {res['title']}: {res['body']}\n"
                
            # Synthesize with LLM
            from apps.engine.core.llm import LLMClient
            llm = LLMClient()
            deep_dive = llm.synthesize_research(niche, context)
            
            return deep_dive
            
        except Exception as e:
            import traceback
            with open("apps/engine/research_error.log", "w") as f:
                f.write(traceback.format_exc())
            print(f"[RESEARCH_ERROR] Full Traceback: {e}")
            self.log(f"Search failed: {e}")
            return "Search unavailable (Mock Mode)."
