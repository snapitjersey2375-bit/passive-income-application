"""
ElevenLabs Voice Service
Direct HTTP approach - no SDK dependency.

Voices:
  rachel:  21m00Tcm4TlvDq8ikWAM (premade, ready)
  husband: hirNNrNeVAwcLlSAF4cI (PineHomeLabs cloned - fix payment to use)
"""

import os
import logging
import httpx
from typing import Optional

logger = logging.getLogger(__name__)

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "sk_3cedde2109135c61c472d0f60eb9c5e5b375fca14a083aab")
ELEVENLABS_BASE_URL = "https://api.elevenlabs.io/v1"

VOICE_PROFILES = {
    "rachel": {
        "voice_id": "21m00Tcm4TlvDq8ikWAM",
        "stability": 0.35,
        "similarity_boost": 0.85,
        "style": 0.4,
        "use_speaker_boost": True,
    },
    "husband": {
        "voice_id": "hirNNrNeVAwcLlSAF4cI",
        "stability": 0.40,
        "similarity_boost": 0.90,
        "style": 0.5,
        "use_speaker_boost": True,
    },
}

DEFAULT_MODEL = "eleven_turbo_v2_5"


def generate_voiceover(text: str, voice_name: str = "rachel", output_path: Optional[str] = None) -> bytes:
    profile = VOICE_PROFILES.get(voice_name)
    if not profile:
        raise ValueError(f"Unknown voice: {voice_name}. Choose from: {list(VOICE_PROFILES.keys())}")

    voice_id = profile["voice_id"]
    url = f"{ELEVENLABS_BASE_URL}/text-to-speech/{voice_id}"
    headers = {"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"}
    payload = {
        "text": text,
        "model_id": DEFAULT_MODEL,
        "voice_settings": {
            "stability": profile["stability"],
            "similarity_boost": profile["similarity_boost"],
            "style": profile["style"],
            "use_speaker_boost": profile["use_speaker_boost"],
        },
    }

    logger.info(f"[TTS] Generating with voice={voice_name} ({voice_id})")
    response = httpx.post(url, headers=headers, json=payload, timeout=60.0)
    response.raise_for_status()

    audio_bytes = response.content
    if output_path:
        with open(output_path, "wb") as f:
            f.write(audio_bytes)
    return audio_bytes


def clone_voice(display_name: str, sample_paths: list, description: str = "") -> str:
    url = f"{ELEVENLABS_BASE_URL}/voices/add"
    headers = {"xi-api-key": ELEVENLABS_API_KEY}
    files = [("files", (os.path.basename(p), open(p, "rb"), "audio/mpeg")) for p in sample_paths]
    data = {"name": display_name, "description": description}
    response = httpx.post(url, headers=headers, data=data, files=files, timeout=120.0)
    response.raise_for_status()
    return response.json()["voice_id"]
