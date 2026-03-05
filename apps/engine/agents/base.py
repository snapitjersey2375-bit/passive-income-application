from abc import ABC, abstractmethod
from typing import Dict, Any
from apps.engine.core.log_store import log_store

class BaseAgent(ABC):
    """
    Abstract Base Class for all NexusFlow Agents.
    Enforces a standard structure for autonomous agents.
    """
    def __init__(self, name: str):
        self.name = name
        self.status = "idle"

    @abstractmethod
    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main execution logic for the agent.
        :param context: Input data map
        :return: Result data map
        """
        pass

    def log(self, message: str):
        print(f"[{self.name.upper()}] {message}")
        log_store.add_log(self.name, message)
