import os
import google.generativeai as genai
import json

class GeminiConsultant:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
        else:
            self.model = None

    def get_strategic_advice(self, results, audience_params=None):
        if not self.model:
            return "Gemini API key not configured. Please add GEMINI_API_KEY to environment."

        audience_params = audience_params or {}

        # Simplify results for prompt with safety checks
        summary = {
            "marketing_kpis": {
                k: f"{sum(v)/len(v) if v else 0:.1f}%"
                for k, v in results.get("marketing_kpis", {}).items()
            },
            "winning_probability": f"{results.get('winning_probability', 0):.1f}%",
            "moi_peaks": results.get("moi_analysis", [])
        }

        prompt = f"""
        As a world-class Performance Marketing Creative Strategist, analyze these predictive brain response results for the following target audience:
        Target Audience: {json.dumps(audience_params, indent=2)}

        Predictive Performance Summary:
        {json.dumps(summary, indent=2)}

        Task:
        1. Winning Probability Assessment: Explain why this ad has this specific winning probability for THIS audience.
        2. Neuro-Gap Analysis: Identify which marketing KPI is the bottleneck (e.g., is it failing to stop the scroll or failing to build purchase intent?).
        3. The '10x Winner' Creative Brief:
           - New Hook: Provide 2 alternative high-attention hooks.
           - Visual Script: Describe a 5-second 'Scroll-Stop' sequence.
           - CTA Optimization: How to reduce Conversion Friction at the end.
        4. Platform Optimization: Suggest how to adapt this specific creative for {audience_params.get('platform', 'the platform')} to maximize ROI.
        5. AI Prompt: Give a Midjourney or Runway Gen-2 prompt to create a more 'Attention-Grabbing' version of this creative.

        Format the response using Markdown with bold headers. Be aggressive, ROI-focused, and use performance marketing terminology (Scroll-stop, Hook, ROAS, CPA).
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"AI Consultant Error: {str(e)}"

    def chat_with_neuro_data(self, query, results):
        if not self.model:
            return "Gemini API key not configured."

        context = f"Neural Data Context: {json.dumps(results.get('marketing_kpis', {}), indent=2)}"
        full_query = f"{context}\n\nUser Question: {query}\n\nExpert Neuro-Response:"

        try:
            response = self.model.generate_content(full_query)
            return response.text
        except Exception as e:
            return f"Chat Error: {str(e)}"

    def generate_high_performance_hooks(self, product_desc, audience_params):
        if not self.model:
            return "Gemini API key not configured."

        prompt = f"""
        As a 10x Performance Marketer, generate 5 high-attention 'Scroll-Stopping' hooks for this product:
        Product: {product_desc}
        Target Audience: {json.dumps(audience_params)}

        Requirements:
        - Must be optimized for {audience_params.get('platform', 'the platform')}.
        - Focus on psychological triggers: Curiosity, Fear of Missing Out, or Direct Benefit.
        - Keep each hook under 15 words.
        - Provide a brief 'Why it works' for each.

        Format:
        1. [Hook Text] - (Reasoning)
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Hook Gen Error: {str(e)}"
