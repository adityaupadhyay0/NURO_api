import pytest
from unittest.mock import MagicMock, patch
from services.brain_orchestrator import CampaignBrain
import json

@pytest.mark.asyncio
async def test_process_goal_dynamic_selection():
    brain = CampaignBrain()

    # Mock LLM Orchestrator response
    mock_plan = ["Neuro-Analyst", "Creative Strategist"]

    with patch.object(brain, "_orchestrate_plan", return_value=mock_plan):
        with patch.object(brain.analyst, "analyze", return_value="Neuro Analysis Output") as mock_analyze:
            with patch.object(brain.strategist, "develop_strategy", return_value="Strategy Output") as mock_strategy:

                goal = "Analyze my luxury skincare ad bottlenecks"
                result = await brain.process_goal(goal)

                # Check if correct agents were involved
                assert "Neuro-Analyst Scientist" in result["involved_agents"]
                assert "10x Creative Director" in result["involved_agents"]

                # Check if agents were called with context
                mock_analyze.assert_called_once()
                assert "context" in mock_analyze.call_args.kwargs

                mock_strategy.assert_called_once()
                assert "context" in mock_strategy.call_args.kwargs
                assert "Neuro Analysis Output" in mock_strategy.call_args.kwargs["context"]

@pytest.mark.asyncio
async def test_orchestrate_plan_fallback():
    brain = CampaignBrain()

    # Even if model is None, it should fallback
    brain.strategist.model = None
    plan = brain._orchestrate_plan("Some goal")
    assert plan == ["Creative Strategist", "Media Buyer"] # Default fallback

    # If model exists but fails
    brain.strategist.model = MagicMock()
    brain.strategist.model.generate_content.side_effect = Exception("API Error")
    plan = brain._orchestrate_plan("Some goal")
    assert plan == ["Creative Strategist", "Media Buyer"]
