"""
Text-to-Speech Service - ElevenLabs Direct HTTP

Primary: ElevenLabs (direct HTTP, proven working)
Fallback: OpenAI TTS

Voices:
  rachel:  21m00Tcm4TlvDq8ikWAM (ready)
  husband: hirNNrNeVAwcLlSAF4cI (PineHomeLabs cloned - fix payment)
"""

import logging
import os
import httpx
from decimal import Decimal
from typing import Tuple, Optional, Dict
from sqlalchemy.orm import Session
from apps.engine.db.models import User, Ledger

logger = logging.getLogger(__name__)

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "sk_3cedde2109135c61c472d0f60eb9c5e5b375fca14a083aab")
ELEVENLABS_BASE_URL = "https://api.elevenlabs.io/v1"

VOICE_REGISTRY = {
    "rachel":  {"id": "21m00Tcm4TlvDq8ikWAM", "stability": 0.35, "similarity_boost": 0.85, "style": 0.4},
    "nova":    {"id": "21m00Tcm4TlvDq8ikWAM", "stability": 0.35, "similarity_boost": 0.85, "style": 0.4},
    "husband": {"id": "hirNNrNeVAwcLlSAF4cI", "stability": 0.40, "similarity_boost": 0.90, "style": 0.5},
}

DEFAULT_VOICE = "rachel"
DEFAULT_MODEL = "eleven_turbo_v2_5"
COST_PER_MINUTE = Decimal("0.003")


class TTSProvider:
    def __init__(self):
        self.cost_per_minute = COST_PER_MINUTE

    def generate_speech(self, text: str, voice: str = DEFAULT_VOICE) -> Tuple[bytes, float]:
        raise NotImplementedError

    def estimate_cost(self, text: str) -> Decimal:
        word_count = len(text.split())
        duration_minutes = max(0.1, word_count / 170.0)
        return self.cost_per_minute * Decimal(str(duration_minutes))


class ElevenLabsTTSProvider(TTSProvider):
    """Direct HTTP ElevenLabs - no SDK, proven working method."""

    def generate_speech(self, text: str, voice: str = DEFAULT_VOICE) -> Tuple[bytes, float]:
        profile = VOICE_REGISTRY.get(voice, VOICE_REGISTRY[DEFAULT_VOICE])
        voice_id = profile["id"]

        url = f"{ELEVENLABS_BASE_URL}/text-to-speech/{voice_id}"
        headers = {"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"}
        payload = {
            "text": text,
            "model_id": DEFAULT_MODEL,
            "voice_settings": {
                "stability": profile.get("stability", 0.35),
                "similarity_boost": profile.get("similarity_boost", 0.85),
                "style": profile.get("style", 0.4),
                "use_speaker_boost": True,
            },
        }

        logger.info(f"[TTS] ElevenLabs voice={voice} ({voice_id})")
        response = httpx.post(url, headers=headers, json=payload, timeout=60.0)
        response.raise_for_status()

        audio_bytes = response.content
        duration_minutes = max(0.1, len(text.split()) / 170.0)
        logger.info(f"[TTS] {len(audio_bytes)} bytes, {duration_minutes:.2f} min")
        return audio_bytes, duration_minutes


class OpenAITTSProvider(TTSProvider):
    """OpenAI TTS fallback."""

    def __init__(self):
        super().__init__()
        self.cost_per_minute = Decimal("0.015")
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

    def generate_speech(self, text: str, voice: str = "nova") -> Tuple[bytes, float]:
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set")
        import openai
        client = openai.OpenAI(api_key=self.api_key)
        response = client.audio.speech.create(model="tts-1", voice=voice if voice in self.voices else "nova", input=text)
        duration_minutes = max(0.1, len(text.split()) / 170.0)
        return response.content, duration_minutes


class TTSService:
    """ElevenLabs primary, OpenAI fallback."""

    PRIMARY_PROVIDER = "elevenlabs"
    FALLBACK_PROVIDER = "openai"

    @staticmethod
    def get_provider(provider_name: str = PRIMARY_PROVIDER) -> TTSProvider:
        if provider_name == "openai":
            return OpenAITTSProvider()
        return ElevenLabsTTSProvider()

    @staticmethod
    def generate_speech(
        text: str, voice: str = DEFAULT_VOICE, provider: str = PRIMARY_PROVIDER, fallback_enabled: bool = True
    ) -> Tuple[bytes, float, Dict]:
        try:
            prov = TTSService.get_provider(provider)
            audio_bytes, duration_minutes = prov.generate_speech(text, voice)
            return audio_bytes, duration_minutes, {"provider": provider, "success": True, "fallback_used": False,
                "duration_minutes": duration_minutes, "cost": float(prov.estimate_cost(text))}
        except Exception as e:
            logger.warning(f"[TTS] Primary ({provider}) failed: {e}")
            if not fallback_enabled:
                raise
            fallback_prov = TTSService.get_provider(TTSService.FALLBACK_PROVIDER)
            audio_bytes, duration_minutes = fallback_prov.generate_speech(text, voice)
            return audio_bytes, duration_minutes, {"provider": TTSService.FALLBACK_PROVIDER, "success": True,
                "fallback_used": True, "duration_minutes": duration_minutes, "cost": float(fallback_prov.estimate_cost(text))}

    @staticmethod
    def estimate_cost(text: str, provider: str = PRIMARY_PROVIDER) -> Decimal:
        return TTSService.get_provider(provider).estimate_cost(text)

    @staticmethod
    def record_tts_expense(db: Session, user_id: str, text: str, provider: str = PRIMARY_PROVIDER,
                           description: Optional[str] = None) -> Decimal:
        cost = TTSService.estimate_cost(text, provider)
        entry = Ledger(user_id=user_id, amount=-cost, transaction_type="tts_expense",
                       description=description or f"TTS ({provider}) - {len(text.split())} words",
                       affiliate_network="internal")
        db.add(entry)
        db.commit()
        return cost
