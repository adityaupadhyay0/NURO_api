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

        # Simplify results for prompt
        summary = {
            "marketing_kpis": {k: f"{sum(v)/len(v):.1f}%" for k, v in results["marketing_kpis"].items()},
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
        3. 3 Actionable Creative Refinements: Provide specific 'Hooks' or 'Visual Changes' to improve the bottleneck KPI.
        4. Platform Optimization: Suggest how to adapt this specific creative for {audience_params.get('platform', 'the platform')} to maximize ROI.
        5. AI Prompt: Give a Midjourney or Runway Gen-2 prompt to create a more 'Attention-Grabbing' version of this creative.

        Be aggressive, ROI-focused, and use performance marketing terminology (Scroll-stop, Hook, ROAS, CPA).
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"AI Consultant Error: {str(e)}"

    def chat_with_neuro_data(self, query, neuro_results):
        if not self.model:
            return "Gemini API key not configured."

        context = f"Neural Data Context: {json.dumps(neuro_results['metrics'], indent=2)}"
        full_query = f"{context}\n\nUser Question: {query}\n\nExpert Neuro-Response:"

        try:
            response = self.model.generate_content(full_query)
            return response.text
        except Exception as e:
            return f"Chat Error: {str(e)}"
