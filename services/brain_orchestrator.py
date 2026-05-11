from agents.specialized_agents import NeuroAnalyst, CreativeStrategist, MediaBuyer, CROOptimizer
import json

class CampaignBrain:
    """The 'Campaign Brain' Orchestrator: Hides internal multi-agent complexity."""

    def __init__(self):
        self.analyst = NeuroAnalyst()
        self.strategist = CreativeStrategist()
        self.buyer = MediaBuyer()
        self.cro = CROOptimizer()

    def _orchestrate_plan(self, goal):
        """Uses Gemini to decide which agents to invoke and in what order."""
        orchestrator_prompt = f"""
        You are the NeuroMark Pro Orchestrator.
        Your task is to analyze a marketing goal and determine which of these specialized agents are needed:
        1. Neuro-Analyst: For neural data, psychological signals, and bottlenecks.
        2. Creative Strategist: For angles, hooks, and scripts.
        3. Media Buyer: For funnel optimization and auction competitiveness.
        4. CRO Optimizer: For landing page friction.

        Return a JSON list of agents to invoke in order.
        Example Output: ["Neuro-Analyst", "Creative Strategist"]
        Goal: {goal}
        """
        # We reuse the strategist's model for orchestration to avoid adding more dependencies
        try:
            response = self.strategist.model.generate_content(orchestrator_prompt).text
            # Simple cleanup in case of markdown blocks
            clean_res = response.replace("```json", "").replace("```", "").strip()
            plan = json.loads(clean_res)
            return plan if isinstance(plan, list) else ["Creative Strategist", "Media Buyer"]
        except Exception:
            return ["Creative Strategist", "Media Buyer"] # Robust fallback

    async def process_goal(self, goal, campaign_id=None):
        """Conversational entry point for the AaaS brain with dynamic agent selection."""
        # 1. Dynamic Agent Selection based on LLM orchestration
        plan = self._orchestrate_plan(goal)
        involved_agents = []

        # 2. Sequential Reasoning and Collaboration
        context = f"User Goal: {goal}"
        agent_outputs = {}

        for agent_role in plan:
            if agent_role == "Neuro-Analyst":
                involved_agents.append(self.analyst.role)
                res = self.analyst.analyze({"goal": goal}, context=context)
                agent_outputs["neuro"] = res
                context += f"\nNeuro Analysis: {res}"

            elif agent_role == "Creative Strategist":
                involved_agents.append(self.strategist.role)
                strategy_input = agent_outputs.get("neuro", {"goal": goal})
                res = self.strategist.develop_strategy(strategy_input, {"platform": "Omnichannel"}, context=context)
                agent_outputs["strategy"] = res
                context += f"\nCreative Strategy: {res}"

            elif agent_role == "Media Buyer":
                involved_agents.append(self.buyer.role)
                res = self.buyer.optimize_funnel(agent_outputs.get("strategy", goal), "Market Average", context=context)
                agent_outputs["media"] = res
                context += f"\nMedia Buying Plan: {res}"

            elif agent_role == "CRO Optimizer":
                involved_agents.append(self.cro.role)
                res = self.cro.optimize_cro("Current Landing Page", agent_outputs.get("neuro", "General Friction"), context=context)
                agent_outputs["cro"] = res
                context += f"\nCRO Report: {res}"

        # 3. Construct Unified Response
        response_parts = [f"I've coordinated with the **{', '.join(involved_agents)}**."]

        if "neuro" in agent_outputs:
            response_parts.append(f"### 🕵️ Neuro-Analysis\n{agent_outputs['neuro']}")
        if "strategy" in agent_outputs:
            response_parts.append(f"### 🎨 Creative Strategy\n{agent_outputs['strategy']}")
        if "media" in agent_outputs:
            response_parts.append(f"### 💰 Media Buying Plan\n{agent_outputs['media']}")
        if "cro" in agent_outputs:
            response_parts.append(f"### 🚀 CRO Report\n{agent_outputs['cro']}")

        return {
            "response": "\n\n".join(response_parts),
            "involved_agents": involved_agents,
            "agent_outputs": agent_outputs
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
