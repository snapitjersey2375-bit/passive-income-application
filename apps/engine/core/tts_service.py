"""
Text-to-Speech Service - Licensed TTS Integration

Replaces unlicensed edge-tts with commercially licensed alternatives.
Supports OpenAI TTS (primary) and ElevenLabs (fallback).

Problem: edge-tts is Microsoft's undocumented API → legal shutdown risk
Solution: Use licensed commercial TTS providers with transparent cost tracking
"""

import logging
import os
from decimal import Decimal
from typing import Tuple, Optional, Dict
from sqlalchemy.orm import Session
from apps.engine.db.models import User, Ledger

logger = logging.getLogger(__name__)


class TTSProvider:
    """Abstract base for TTS providers."""

    def __init__(self):
        self.cost_per_minute = Decimal("0.00")

    def generate_speech(self, text: str, voice: str = "default") -> Tuple[bytes, float]:
        """
        Generate speech from text.

        Returns: (audio_bytes, duration_in_seconds)
        """
        raise NotImplementedError


class OpenAITTSProvider(TTSProvider):
    """OpenAI TTS Provider (primary)."""

    def __init__(self):
        super().__init__()
        self.cost_per_minute = Decimal("0.015")  # $0.015 per minute
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

    def generate_speech(
        self, text: str, voice: str = "nova", speed: float = 1.0
    ) -> Tuple[bytes, float]:
        """
        Generate speech using OpenAI TTS (TTS-1 model).

        voice: alloy, echo, fable, onyx, nova, shimmer
        speed: 0.25 to 4.0
        """
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set")

        try:
            import openai

            client = openai.OpenAI(api_key=self.api_key)

            response = client.audio.speech.create(
                model="tts-1",
                voice=voice if voice in self.voices else "nova",
                input=text,
                speed=speed,
            )

            # Get audio bytes
            audio_bytes = response.content

            # Estimate duration (rough: ~170 words per minute)
            word_count = len(text.split())
            duration_minutes = max(0.1, word_count / 170.0)  # At least 0.1 min billing

            logger.info(
                f"OpenAI TTS: {word_count} words → {duration_minutes:.2f} min → "
                f"${float(self.cost_per_minute * Decimal(str(duration_minutes))):.4f}"
            )

            return audio_bytes, duration_minutes

        except Exception as e:
            logger.error(f"OpenAI TTS failed: {e}")
            raise

    def estimate_cost(self, text: str) -> Decimal:
        """Estimate cost for text without generating."""
        word_count = len(text.split())
        duration_minutes = max(0.1, word_count / 170.0)
        return self.cost_per_minute * Decimal(str(duration_minutes))


class ElevenLabsTTSProvider(TTSProvider):
    """ElevenLabs TTS Provider (fallback)."""

    def __init__(self):
        super().__init__()
        self.cost_per_minute = Decimal("0.003")  # $0.003 per minute
        self.api_key = os.getenv("ELEVENLABS_API_KEY")

    def generate_speech(self, text: str, voice: str = "default") -> Tuple[bytes, float]:
        """Generate speech using ElevenLabs."""
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY not set")

        try:
            from elevenlabs import client as elevenlabs_client
            from elevenlabs.client import ElevenLabs

            client = ElevenLabs(api_key=self.api_key)

            # Get default voice if not specified
            if voice == "default":
                voice = "Rachel"  # ElevenLabs default

            response = client.text_to_speech.convert(
                voice_id=voice, model_id="eleven_monolingual_v1", text=text
            )

            # Get audio bytes
            audio_bytes = b"".join(response)

            # Estimate duration
            word_count = len(text.split())
            duration_minutes = max(0.1, word_count / 170.0)

            logger.info(
                f"ElevenLabs TTS: {word_count} words → {duration_minutes:.2f} min → "
                f"${float(self.cost_per_minute * Decimal(str(duration_minutes))):.4f}"
            )

            return audio_bytes, duration_minutes

        except Exception as e:
            logger.error(f"ElevenLabs TTS failed: {e}")
            raise

    def estimate_cost(self, text: str) -> Decimal:
        """Estimate cost for text without generating."""
        word_count = len(text.split())
        duration_minutes = max(0.1, word_count / 170.0)
        return self.cost_per_minute * Decimal(str(duration_minutes))


class TTSService:
    """Main TTS service with provider selection and fallback."""

    PRIMARY_PROVIDER = "openai"
    FALLBACK_PROVIDER = "elevenlabs"

    @staticmethod
    def get_provider(provider_name: str = PRIMARY_PROVIDER) -> TTSProvider:
        """Get TTS provider instance."""
        if provider_name == "elevenlabs":
            return ElevenLabsTTSProvider()
        else:  # Default to OpenAI
            return OpenAITTSProvider()

    @staticmethod
    def generate_speech(
        text: str,
        voice: str = "nova",
        provider: str = PRIMARY_PROVIDER,
        fallback_enabled: bool = True,
    ) -> Tuple[bytes, float, Dict]:
        """
        Generate speech with fallback support.

        Args:
            text: Text to convert to speech
            voice: Voice name (provider-specific)
            provider: Primary provider name
            fallback_enabled: Try fallback if primary fails

        Returns:
            (audio_bytes, duration_minutes, metadata)
        """

        try:
            # Try primary provider
            prov = TTSService.get_provider(provider)
            audio_bytes, duration_minutes = prov.generate_speech(text, voice)

            return audio_bytes, duration_minutes, {
                "provider": provider,
                "success": True,
                "fallback_used": False,
                "duration_minutes": duration_minutes,
                "cost": float(prov.estimate_cost(text)),
            }

        except Exception as e:
            logger.warning(f"Primary provider ({provider}) failed: {e}")

            if not fallback_enabled:
                raise

            # Try fallback provider
            try:
                logger.info(f"Attempting fallback to {TTSService.FALLBACK_PROVIDER}")
                fallback_prov = TTSService.get_provider(TTSService.FALLBACK_PROVIDER)
                audio_bytes, duration_minutes = fallback_prov.generate_speech(text, voice)

                return audio_bytes, duration_minutes, {
                    "provider": TTSService.FALLBACK_PROVIDER,
                    "success": True,
                    "fallback_used": True,
                    "duration_minutes": duration_minutes,
                    "cost": float(fallback_prov.estimate_cost(text)),
                }

            except Exception as fallback_error:
                logger.error(f"Both TTS providers failed: {fallback_error}")
                raise Exception(
                    f"TTS generation failed (primary: {e}, fallback: {fallback_error})"
                )

    @staticmethod
    def estimate_cost(text: str, provider: str = PRIMARY_PROVIDER) -> Decimal:
        """Estimate TTS cost without generating."""
        prov = TTSService.get_provider(provider)
        return prov.estimate_cost(text)

    @staticmethod
    def record_tts_expense(
        db: Session,
        user_id: str,
        text: str,
        provider: str = PRIMARY_PROVIDER,
        description: Optional[str] = None,
    ) -> Decimal:
        """
        Record TTS cost and deduct from user balance.

        Returns: cost deducted
        """
        cost = TTSService.estimate_cost(text, provider)

        # Record as ledger transaction
        entry = Ledger(
            user_id=user_id,
            amount=-cost,  # Negative = expense
            transaction_type="tts_expense",
            description=description
            or f"TTS generation ({provider}) - {len(text.split())} words",
            affiliate_network="internal",
        )

        db.add(entry)
        db.commit()

        logger.info(f"TTS expense recorded: user={user_id}, cost=${cost:.4f}, provider={provider}")

        return cost


class TTSServiceAPI:
    """API endpoints for TTS service."""

    @staticmethod
    def register_endpoints(app):
        """Register TTS endpoints."""

        @app.post("/tts/generate")
        def generate_speech(
            text: str,
            voice: str = "nova",
            current_user: User = None,
            db: Session = None,
        ):
            """Generate speech from text."""
            try:
                audio_bytes, duration, metadata = TTSService.generate_speech(text, voice)

                # Record cost
                cost = TTSService.record_tts_expense(
                    db, current_user.id, text, description=f"Generated {len(text.split())} word clip"
                )

                return {
                    "success": True,
                    "duration_minutes": duration,
                    "cost_deducted": float(cost),
                    "provider_used": metadata["provider"],
                    "fallback_used": metadata["fallback_used"],
                    "message": f"✅ Speech generated using {metadata['provider']} TTS. Cost: ${cost:.4f}",
                }

            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "message": "❌ TTS generation failed. Please try again.",
                }

        @app.get("/tts/estimate")
        def estimate_tts_cost(text: str, provider: str = "openai"):
            """Estimate TTS cost without generating."""
            try:
                cost = TTSService.estimate_cost(text, provider)
                word_count = len(text.split())

                return {
                    "provider": provider,
                    "word_count": word_count,
                    "estimated_duration_minutes": float(cost / TTSService.get_provider(provider).cost_per_minute),
                    "estimated_cost": float(cost),
                    "message": f"${cost:.4f} for {word_count} words",
                }

            except Exception as e:
                return {
                    "error": str(e),
                    "message": "Failed to estimate cost",
                }

        @app.get("/tts/providers")
        def get_tts_providers():
            """List available TTS providers."""
            return {
                "primary": {
                    "name": "OpenAI TTS",
                    "cost_per_minute": "0.015",
                    "quality": "high",
                    "speed": "fast",
                    "voices": OpenAITTSProvider().voices,
                },
                "fallback": {
                    "name": "ElevenLabs",
                    "cost_per_minute": "0.003",
                    "quality": "high",
                    "speed": "medium",
                    "description": "Used if OpenAI fails",
                },
            }
