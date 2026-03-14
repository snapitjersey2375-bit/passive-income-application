import logging
import traceback
from .base import BaseAgent
from duckduckgo_search import AsyncDDGS
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ResearchAgent(BaseAgent):
    """Agent responsible for gathering real-time data from the web."""

    def __init__(self):
        super().__init__(name="ResearchAgent")

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        niche = context.get("niche", "general")
        summary = await self.search_trends(niche)
        return {"summary": summary}

    async def search_trends(self, niche: str) -> str:
        """
        Searches for the latest news and trends in a specific niche.
        Returns a synthesized research summary string.
        """
        self.log(f"Scouting the web for: {niche}")

        query = f"latest trends and news in {niche} {datetime.now().year}"

        try:
            async with AsyncDDGS() as ddgs:
                results = await ddgs.text(query, max_results=5)

            if not results:
                return "No recent news found."

            raw = "Recent News:\n"
            for i, res in enumerate(results):
                raw += f"{i+1}. {res['title']}: {res['body']}\n"

            from apps.engine.core.llm import LLMClient
            llm = LLMClient()
            return llm.synthesize_research(niche, raw)

        except Exception as e:
            logger.exception("[RESEARCH] Search failed for niche '%s': %s", niche, e)
            self.log(f"Search failed: {e}")
            return "Search unavailable (Mock Mode)."
