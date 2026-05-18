import google.generativeai as genai
import os
import json
import re
from core.config import GEMINI_API_KEY

class BaseAgent:
    def __init__(self, role, goal, backstory):
        self.api_key = GEMINI_API_KEY
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
        else:
            self.model = None

        self.role = role
        self.goal = goal
        self.backstory = backstory

    def _sanitize(self, text):
        """Basic prompt sanitization to prevent common injection patterns (case-insensitive)."""
        if not text or not isinstance(text, str):
            return text
        # Remove potential instruction overrides and suspicious patterns
        forbidden_phrases = ["ignore previous instructions", "system prompt", "as a service", "disregard"]
        sanitized = text
        for phrase in forbidden_phrases:
            # Case-insensitive replacement using regex
            sanitized = re.sub(re.escape(phrase), "[REDACTED]", sanitized, flags=re.IGNORECASE)
        return sanitized

    def _generate(self, prompt, context=None):
        if not self.model: return "Gemini API key not configured."

        # Sanitize inputs
        s_prompt = self._sanitize(prompt)
        s_context = self._sanitize(context)

        context_str = f"\n\nCollaboration Context:\n{s_context}" if s_context else ""
        full_prompt = f"Role: {self.role}\nGoal: {self.goal}\nBackstory: {self.backstory}{context_str}\n\nTask: {s_prompt}"
        try:
            return self.model.generate_content(full_prompt).text
        except Exception as e:
            return f"Agent Error: {str(e)}"

class NeuroAnalyst(BaseAgent):
    def __init__(self):
        super().__init__(
            role="Neuro-Analyst Scientist",
            goal="Extract deep psychological signals and attention gaps from neural prediction data.",
            backstory="You are an expert in cognitive neuroscience with a focus on consumer behavior."
        )

    def analyze(self, neuro_results, context=None):
        prompt = f"Analyze these neural metrics and identify the top 3 engagement bottlenecks: {json.dumps(neuro_results, indent=2)}"
        return self._generate(prompt, context=context)

class CreativeStrategist(BaseAgent):
    def __init__(self):
        super().__init__(
            role="10x Creative Director",
            goal="Turn neural bottlenecks into winning creative angles, hooks, and scripts.",
            backstory="You have scaled dozens of D2C brands to 8-figures using data-driven creative."
        )

    def develop_strategy(self, analysis, audience_params, context=None):
        prompt = f"Based on this neuro-analysis: {analysis}, develop a creative strategy for this audience: {json.dumps(audience_params)}"
        return self._generate(prompt, context=context)

class MediaBuyer(BaseAgent):
    def __init__(self):
        super().__init__(
            role="Media Buying Algorithmic Expert",
            goal="Optimize campaign structure and auction competitiveness based on performance metrics.",
            backstory="You understand the Meta and TikTok auction algorithms better than anyone."
        )

    def optimize_funnel(self, strategy, cpm_data, context=None):
        prompt = f"Optimize the media buying funnel for this strategy: {strategy}. Consider this CPM context: {cpm_data}"
        return self._generate(prompt, context=context)

class CROOptimizer(BaseAgent):
    def __init__(self):
        super().__init__(
            role="Conversion Rate Scientist",
            goal="Eliminate friction points on landing pages to maximize ROAS.",
            backstory="You have optimized thousands of checkout flows for maximum efficiency."
        )

    def optimize_cro(self, landing_page_data, neuro_gaps, context=None):
        prompt = f"Optimize this landing page: {landing_page_data} by addressing these neuro-gaps: {neuro_gaps}"
        return self._generate(prompt, context=context)

class AudienceAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            role="Synthetic Audience Architect",
            goal="Derive precise neurological ROI multipliers from complex persona descriptions.",
            backstory="You are a pioneer in synthetic psychographics and cross-sectional consumer profiling."
        )
        self._persona_cache = {}

    def derive_multipliers(self, persona_description, context=None):
        if not persona_description:
            return {}

        if persona_description in self._persona_cache:
            return self._persona_cache[persona_description]
        prompt = f"""
        Analyze this persona: "{persona_description}".

        Return a JSON object containing neurological multipliers (0.5 to 1.5) for the following marketing ROIs based on their psychographics, biases, and behavioral patterns:
        - Attention
        - Emotion
        - Reward
        - Memory
        - CognitiveLoad
        - VisualEngagement

        Example Output:
        {{
            "Attention": 1.2,
            "Emotion": 0.9,
            "Reward": 1.1,
            "Memory": 1.0,
            "CognitiveLoad": 1.3,
            "VisualEngagement": 1.0
        }}
        """
        response = self._generate(prompt, context=context)
        try:
            # Cleanup potential markdown and extract JSON
            clean_res = re.search(r'\{.*\}', response, re.DOTALL).group()
            multipliers = json.loads(clean_res)
            self._persona_cache[persona_description] = multipliers
            return multipliers
        except Exception as e:
            # Deterministic fallback
            return {
                "Attention": 1.0, "Emotion": 1.0, "Reward": 1.0,
                "Memory": 1.0, "CognitiveLoad": 1.0, "VisualEngagement": 1.0
            }
