"""
Content Variation Engine - Anti-Detection System

Prevents AI-generated content from being detected and suppressed by platforms
by creating unique, user-specific content variations.

Problem: All users generate with same templates → platforms detect pattern → shadowban
Solution: Each user gets unique personality, sentence patterns, and editing style

Implementation:
- Deterministic: Same user always gets same style (consistency)
- Diverse: Different users get different styles (pattern breaking)
- Hashable: Based on user ID, not random (reproducible)
"""

import logging
import hashlib
from typing import Dict, Optional
from apps.engine.db.models import User

logger = logging.getLogger(__name__)


class ContentVariationEngine:
    """
    Generate user-specific content variations to prevent detection.

    Each user gets a deterministic but unique:
    1. Personality profile (how they speak)
    2. Sentence patterns (structure variation)
    3. Editing style (pacing and rhythm)
    """

    # Personality profiles
    PERSONALITIES = {
        "mentor": {
            "voice": "I teach and guide",
            "tone": "authoritative but warm",
            "phrases": [
                "Here's what I learned:",
                "Let me show you:",
                "The key insight is:",
                "Trust me on this:",
            ],
        },
        "friend": {
            "voice": "I'm relatable and casual",
            "tone": "conversational and genuine",
            "phrases": [
                "So check this out:",
                "No cap, this is wild:",
                "Real talk though:",
                "You gotta see this:",
            ],
        },
        "storyteller": {
            "voice": "I paint pictures",
            "tone": "narrative and immersive",
            "phrases": [
                "Picture this:",
                "Here's the thing:",
                "Let me paint you a picture:",
                "So what happened was:",
            ],
        },
        "analyst": {
            "voice": "I break down data",
            "tone": "precise and logical",
            "phrases": [
                "The data shows:",
                "Breaking this down:",
                "Looking at the numbers:",
                "Here's the analysis:",
            ],
        },
        "entertainer": {
            "voice": "I make it fun",
            "tone": "energetic and playful",
            "phrases": [
                "This is insane:",
                "Wait for it:",
                "Mind = blown:",
                "You won't believe:",
            ],
        },
    }

    # Sentence pattern variations
    SENTENCE_PATTERNS = {
        "short_punchy": {
            "name": "Short and punchy",
            "description": "Quick sentences. Short words. Fast pace.",
            "avg_length": 8,
            "example": "This works. Trust me. Try it.",
        },
        "flowing": {
            "name": "Flowing narrative",
            "description": "Connected sentences with complex structures.",
            "avg_length": 22,
            "example": "When you understand how this works, you'll realize the power behind it.",
        },
        "mixed": {
            "name": "Mixed rhythm",
            "description": "Alternates between short and long sentences for impact.",
            "avg_length": 15,
            "example": "Quick hit. Then a longer explanation that gives context and meaning.",
        },
        "question_driven": {
            "name": "Question-driven",
            "description": "Uses questions to engage and guide.",
            "avg_length": 14,
            "example": "Ever wonder why this works? Because it taps into human psychology.",
        },
    }

    # Editing/pacing styles
    EDITING_STYLES = {
        "fast": {
            "name": "Fast paced",
            "description": "Quick cuts, high energy, constant movement",
            "cut_frequency": "every 2-3 seconds",
            "music_tempo": "120-140 BPM",
        },
        "medium": {
            "name": "Medium paced",
            "description": "Balanced cuts with moments of calm",
            "cut_frequency": "every 4-5 seconds",
            "music_tempo": "100-120 BPM",
        },
        "slow": {
            "name": "Slow and deliberate",
            "description": "Long holds, cinematic, let moments breathe",
            "cut_frequency": "every 6-8 seconds",
            "music_tempo": "80-100 BPM",
        },
    }

    @staticmethod
    def _hash_user_id(user_id: str) -> int:
        """Deterministic hash of user ID for selecting styles."""
        return int(hashlib.md5(user_id.encode()).hexdigest(), 16)

    @staticmethod
    def get_user_style(user: User) -> Dict:
        """
        Get deterministic but unique content style for user.

        Same user always gets same style (consistency).
        Different users get different styles (prevents detection).
        """
        hash_val = ContentVariationEngine._hash_user_id(user.id)

        # Pick personality
        personality_idx = hash_val % len(ContentVariationEngine.PERSONALITIES)
        personality_name = list(ContentVariationEngine.PERSONALITIES.keys())[personality_idx]
        personality = ContentVariationEngine.PERSONALITIES[personality_name]

        # Pick sentence pattern
        pattern_idx = (hash_val // 100) % len(ContentVariationEngine.SENTENCE_PATTERNS)
        pattern_name = list(ContentVariationEngine.SENTENCE_PATTERNS.keys())[pattern_idx]
        pattern = ContentVariationEngine.SENTENCE_PATTERNS[pattern_name]

        # Pick editing style
        style_idx = (hash_val // 10000) % len(ContentVariationEngine.EDITING_STYLES)
        style_name = list(ContentVariationEngine.EDITING_STYLES.keys())[style_idx]
        editing_style = ContentVariationEngine.EDITING_STYLES[style_name]

        return {
            "user_id": user.id,
            "personality": {
                "name": personality_name,
                "voice": personality["voice"],
                "tone": personality["tone"],
                "sample_phrases": personality["phrases"][:2],  # Show 2 examples
            },
            "sentence_pattern": {
                "name": pattern_name,
                "description": pattern["description"],
                "avg_word_length": pattern["avg_length"],
            },
            "editing_style": {
                "name": style_name,
                "description": editing_style["description"],
                "cut_frequency": editing_style["cut_frequency"],
                "music_tempo": editing_style["music_tempo"],
            },
            "instruction": "Inject these variations into your LLM prompt for content generation",
        }

    @staticmethod
    def get_prompt_variant(user: User) -> str:
        """
        Generate LLM prompt injection that creates user-specific variations.

        Prepend this to your content generation prompt to ensure unique voice.
        """
        style = ContentVariationEngine.get_user_style(user)
        personality = style["personality"]
        pattern = style["sentence_pattern"]
        editing_style = style["editing_style"]

        prompt_injection = f"""
STYLE GUIDE FOR THIS CONTENT:

PERSONALITY: {personality['name'].upper()}
- Voice: {personality['voice']}
- Tone: {personality['tone']}
- Use phrases like: {', '.join(personality['sample_phrases'])}

SENTENCE STRUCTURE: {pattern['name'].upper()}
- Description: {pattern['description']}
- Target average: {pattern['avg_word_length']} words per sentence

PACING & EDITING: {editing_style['name'].upper()}
- Description: {editing_style['description']}
- Edit frequency: {editing_style['cut_frequency']}
- Music tempo: {editing_style['music_tempo']}

CRITICAL: Apply these variations consistently throughout. This is how THIS creator speaks.
Do not use generic templates. Sound like a real person with a unique voice.
"""
        return prompt_injection.strip()

    @staticmethod
    def get_variation_report(user: User) -> Dict:
        """Get a user-friendly report of their unique content style."""
        style = ContentVariationEngine.get_user_style(user)

        return {
            "headline": f"Your Unique Voice: {style['personality']['name'].title()}",
            "summary": (
                f"You naturally speak as a {style['personality']['name']}, "
                f"with {style['sentence_pattern']['name'].lower()} sentences, "
                f"and {style['editing_style']['name'].lower()} pacing. "
                f"This unique combination helps your content stand out."
            ),
            "personality": style["personality"],
            "sentence_pattern": style["sentence_pattern"],
            "editing_style": style["editing_style"],
            "benefit": (
                "Platform algorithms respect unique voices. This variation "
                "prevents your content from being detected as AI-generated template content."
            ),
            "consistency": (
                "Your style is deterministic - you'll always sound like yourself across all content. "
                "This builds audience familiarity and trust."
            ),
        }


class ContentVariationAPI:
    """API endpoints for content variation system."""

    @staticmethod
    def register_endpoints(app):
        """Register content variation endpoints."""

        @app.get("/user/content-style")
        def get_my_content_style(current_user: User):
            """Show user their unique content style."""
            return ContentVariationEngine.get_variation_report(current_user)

        @app.get("/content/style-guide")
        def get_style_guide(current_user: User):
            """Get detailed style guide for LLM prompt injection."""
            return {
                "style": ContentVariationEngine.get_user_style(current_user),
                "prompt_injection": ContentVariationEngine.get_prompt_variant(current_user),
                "instruction": (
                    "When generating content, prepend the prompt_injection above "
                    "to your LLM request. This ensures consistent, unique voice."
                ),
            }
