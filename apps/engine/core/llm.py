import random
import os

class LLMClient:
    """
    Unified Client for LLM generation.
    Falls back to 'MockLLM' if no API Key is found.
    """
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        self.mode = "real" if self.api_key else "mock"
        
        if self.mode == "mock":
            print("[LLM] No API Key found. Running in MOCK mode.")

    def generate_idea(self, niche: str = "general", context_data: str = "", risk_tolerance: float = 0.5, persona: str = "grandma"):
        """
        Generates a video idea with Title, Description, and Virality Score.
        """
        if self.mode == "mock":
            return self._mock_generate(niche, risk_tolerance, persona)
        
        return self._real_generate(niche, context_data, risk_tolerance, persona)

    def _real_generate(self, niche: str, context_data: str = "", risk_tolerance: float = 0.5, persona: str = "grandma"):
        try:
            from openai import OpenAI
            import json
            from apps.engine.core.prompts import VIRAL_CONTENT_SYSTEM_PROMPT
            
            client = OpenAI(api_key=self.api_key)
            
            persona_map = {
                "grandma": "a sweet, encouraging, and slightly confused grandmother who loves knitting and baking.",
                "degen": "a high-energy, crypto-native degen who uses slang like 'LFG', 'HODL', and 'to the moon'.",
                "corporate": "a refined, professional, and efficiency-obsessed corporate executive focused on ROI and KPIs."
            }
            
            persona_inst = persona_map.get(persona, persona_map["grandma"])
            user_prompt = f"Generate a viral video idea for the niche: {niche}.\n\nYOUR PERSONA: You are {persona_inst}\n\nCURRENT RISK TOLERANCE: {risk_tolerance}\n\nContext/News:\n{context_data}"
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": VIRAL_CONTENT_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8
            )
            
            # Parse JSON
            content_str = response.choices[0].message.content
            content_str = content_str.replace("```json", "").replace("```", "").strip()
            
            data = json.loads(content_str)
            
            return {
                "title": data.get("title", "Untitled Idea"),
                "description": data.get("description", "No description provided."),
                "confidence_score": float(data.get("confidence_score", 0.5)),
                "virality_score": float(data.get("confidence_score", 0.5)),
                "script_outline": data.get("script_outline", "")
            }
            
        except Exception as e:
            print(f"[LLM] Error in generation: {e}. Falling back to mock.")
            return self._mock_generate(niche, risk_tolerance, persona) 


    def synthesize_research(self, niche: str, search_results: str) -> str:
        """
        Synthesizes raw search results into a 'Deep Dive' report.
        """
        if self.mode == "mock":
            return f"**Deep Dive: {niche}**\n\n(Mock Analysis)\nBased on recent trends, {niche} is seeing a surge in interest due to [Mock Event]. Key drivers include Factor A and Factor B.\n\n**Strategy:** Focus on sub-niche X for maximum ROI."
            
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            
            prompt = f"Analyze the following search results for the niche '{niche}' and write a comprehensive 'Deep Dive' research report. Highlight key trends, opportunities, and audience sentiment.\n\nSearch Results:\n{search_results}"
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a world-class market researcher. Output in Markdown."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"[LLM] Error in research synthesis: {e}")
            return f"Error synthesizing research for {niche}."

    def _mock_generate(self, niche: str, risk_tolerance: float = 0.5, persona: str = "grandma"):
        templates = [
            ("The Secret to {}", "Uncover the hidden truth about {} that experts verify."),
            ("Stop Doing {}!", "Why you are wasting time with {} and what to do instead."),
            ("Top 5 {} Tools", "The best tools for {} that will 10x your productivity."),
            ("How I made $10k with {}", "A breakdown of the strategy used for {} profit."),
            ("The Future of {}", "Predictions for {} in 2026 based on new data.")
        ]
        
        subjects = [
            "AI Automation", "Crypto Trading", "Passive Income", "Python Coding", 
            "Biohacking", "SaaS Development", "Dropshipping"
        ]
        
        template, desc_template = random.choice(templates)
        subject = random.choice(subjects)
        
        title = template.format(subject)
        
        # Persona logic
        if persona == "grandma":
            title = f"Deary, have you seen this? {title}"
            if "!" in title: title = title.replace("!", " 🧶")
        elif persona == "degen":
            title = f"🚀 LFG: {title.upper()} !!!"
        elif persona == "corporate":
            title = f"Strategic Analysis: {title} (Q1 Update)"

        description = desc_template.format(subject)
        score = random.uniform(0.75, 0.99)
        
        return {
            "title": title,
            "description": description,
            "confidence_score": score,
            "virality_score": score,
            "script_outline": f"Hook: {title}. Persona Style: {persona}. Body: 3 key points about {subject}. CTA: Follow for more."
        }
