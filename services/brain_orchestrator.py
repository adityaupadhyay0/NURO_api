from agents.specialized_agents import NeuroAnalyst, CreativeStrategist, MediaBuyer, CROOptimizer
import json

class CampaignBrain:
    """The 'Campaign Brain' Orchestrator: Hides internal multi-agent complexity."""

    def __init__(self):
        self.analyst = NeuroAnalyst()
        self.strategist = CreativeStrategist()
        self.buyer = MediaBuyer()
        self.cro = CROOptimizer()

    async def process_goal(self, goal, campaign_id=None):
        """Conversational entry point for the AaaS brain."""
        # 1. Decompose goal and determine involved agents
        involved_agents = ["Creative Strategist", "Media Buyer"]
        if "competitor" in goal.lower() or "spy" in goal.lower():
            involved_agents.append("Neuro-Analyst")

        # 2. Coordinate multi-agent response
        context = f"Goal: {goal}"
        strategy_text = self.strategist.develop_strategy({"goal": goal}, {"platform": "Omnichannel"})
        funnel_text = self.buyer.optimize_funnel(strategy_text, "Variable")

        response = (
            f"I've coordinated with the **{' and '.join(involved_agents)}**. "
            f"For your goal: '{goal}', I recommend focusing on the following creative strategy:\n\n"
            f"{strategy_text[:500]}...\n\n"
            f"Our Media Buyer suggests:\n{funnel_text[:300]}..."
        )

        return {
            "response": response,
            "strategy": strategy_text,
            "involved_agents": involved_agents
        }

    def run_campaign_optimization(self, neuro_results, audience_params, media_type="video", file_path=None):
        # 1. Neuro-Analysis
        analysis = self.analyst.analyze(neuro_results)

        # 2. Strategy Development
        strategy = self.strategist.develop_strategy(analysis, audience_params)

        # 3. Media Buying & Funnel Optimization
        funnel_plan = self.buyer.optimize_funnel(strategy, neuro_results.get("predicted_cpm", "Unknown"))

        # 4. Optional CRO Optimization
        cro_report = None
        if media_type == "url":
            cro_report = self.cro.optimize_cro(file_path, analysis)

        return {
            "neuro_intelligence": analysis,
            "creative_strategy": strategy,
            "media_buying_plan": funnel_plan,
            "cro_optimization": cro_report,
            "summary": f"Campaign strategy generated for {audience_params.get('platform')} targeting {audience_params.get('age')} group."
        }
