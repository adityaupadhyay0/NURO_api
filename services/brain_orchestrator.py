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
        """Conversational entry point for the AaaS brain with dynamic agent selection."""
        # 1. Dynamic Agent Selection based on keywords and context
        involved_agents = []

        # Mapping keywords to agents
        agent_map = {
            "strategy": self.strategist,
            "hook": self.strategist,
            "script": self.strategist,
            "ad": self.strategist,
            "funnel": self.buyer,
            "cpm": self.buyer,
            "auction": self.buyer,
            "competitor": self.analyst,
            "spy": self.analyst,
            "neuro": self.analyst,
            "bottleneck": self.analyst,
            "landing": self.cro,
            "page": self.cro,
            "conversion": self.cro,
            "cro": self.cro
        }

        selected_agents = []
        for keyword, agent in agent_map.items():
            if keyword in goal.lower():
                if agent.role not in involved_agents:
                    involved_agents.append(agent.role)
                    selected_agents.append(agent)

        # Default fallback if no keywords match
        if not selected_agents:
            involved_agents = [self.strategist.role, self.buyer.role]
            selected_agents = [self.strategist, self.buyer]

        # 2. Sequential Reasoning and Collaboration
        context = f"User Goal: {goal}"
        agent_outputs = {}

        # Collaborative Flow
        # Analyst first if present
        if self.analyst in selected_agents:
            agent_outputs["neuro"] = self.analyst.analyze({"goal": goal})
            context += f"\nNeuro Analysis: {agent_outputs['neuro']}"

        # Strategist next
        if self.strategist in selected_agents:
            strategy_input = agent_outputs.get("neuro", {"goal": goal})
            agent_outputs["strategy"] = self.strategist.develop_strategy(strategy_input, {"platform": "Omnichannel"})
            context += f"\nCreative Strategy: {agent_outputs['strategy']}"

        # Media Buyer and CRO last
        if self.buyer in selected_agents:
            agent_outputs["media"] = self.buyer.optimize_funnel(agent_outputs.get("strategy", goal), "Market Average")

        if self.cro in selected_agents:
            agent_outputs["cro"] = self.cro.optimize_cro("Current Landing Page", agent_outputs.get("neuro", "General Friction"))

        # 3. Construct Unified Response
        response_parts = [f"I've coordinated with the **{', '.join(involved_agents)}**."]

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
