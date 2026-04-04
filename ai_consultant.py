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

    def get_strategic_advice(self, neuro_results):
        if not self.model:
            return "Gemini API key not configured. Please add GEMINI_API_KEY to environment."

        # Simplify results for prompt
        summary = {
            "metrics": {k: f"{sum(v)/len(v):.1f}%" for k, v in neuro_results["metrics"].items()},
            "moi_peaks": neuro_results.get("moi_analysis", [])
        }

        prompt = f"""
        As a world-class Neuromarketing Creative Director, analyze these brain response results from a TRIBE v2 foundation model:

        Neural Metrics Summary:
        {json.dumps(summary, indent=2)}

        Task:
        1. Interpret what these brain signals mean for consumer behavior.
        2. Identify specific 'Moments of Impact' that worked or failed.
        3. Provide 3 actionable creative recommendations to improve 'Purchase Intent' (Reward ROI) and 'Attention'.
        4. Suggest a specific generative AI prompt for an image/video tool that would fix the weakest segment.

        Be concise, professional, and data-driven.
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
