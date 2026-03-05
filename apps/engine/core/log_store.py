import time
from collections import deque
from typing import List, Dict, Any

class AgentLogStore:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentLogStore, cls).__new__(cls)
            # Store last 50 logs
            cls._instance.logs = deque(maxlen=50)
        return cls._instance

    def add_log(self, agent_name: str, message: str):
        log_entry = {
            "id": int(time.time() * 1000),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "agent": agent_name,
            "message": message
        }
        self.logs.appendleft(log_entry)

    def get_logs(self) -> List[Dict[str, Any]]:
        return list(self.logs)

# Global singleton
log_store = AgentLogStore()
