"""
Make.com Automation Service
Triggers Make scenarios for the Antigravity pipeline.

Key scenarios:
  4461143 - ElevenLabs to Dropbox (WINNING, confirmed working)
  4460750 - Voice reel (working)

Org: 6925356 | Team: 2011811
Dropbox connection: 7940989 (full access, scoped:false)
ElevenLabs key ID: 130752
"""

import os
import logging
import httpx
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

MAKE_API_KEY = os.getenv("MAKE_API_KEY", "")
MAKE_BASE_URL = "https://us1.make.com/api/v2"

SCENARIOS = {
    "voice_to_dropbox": 4461143,
    "voice_reel": 4460750,
}

DROPBOX_REEL_PATH = "/PINEHOMELABS/REELS/POST1"  # MUST stay all-caps


def run_scenario(scenario_name: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    scenario_id = SCENARIOS.get(scenario_name)
    if not scenario_id:
        raise ValueError(f"Unknown scenario: {scenario_name}. Available: {list(SCENARIOS.keys())}")

    url = f"{MAKE_BASE_URL}/scenarios/{scenario_id}/run"
    headers = {"Authorization": f"Token {MAKE_API_KEY}", "Content-Type": "application/json"}

    logger.info(f"[MAKE] Running scenario '{scenario_name}' (ID: {scenario_id})")
    response = httpx.post(url, headers=headers, json=data or {}, timeout=120.0)
    response.raise_for_status()
    return response.json()


def run_voice_to_dropbox(script_text: str, filename: str = "reel_voice.mp3") -> Dict[str, Any]:
    return run_scenario("voice_to_dropbox", {
        "script": script_text,
        "filename": filename,
        "dropbox_path": DROPBOX_REEL_PATH,
    })
