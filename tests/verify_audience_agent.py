import json
from unittest.mock import MagicMock, patch
import os

# Set dummy key for testing
os.environ["GEMINI_API_KEY"] = "test_key"

from agents.specialized_agents import AudienceAgent

@patch("google.generativeai.GenerativeModel")
def test_audience_agent_derive_multipliers(mock_model_class):
    # Setup mock response
    mock_response = MagicMock()
    mock_response.text = '{"Attention": 1.2, "Emotion": 0.8, "Reward": 1.5, "Memory": 1.0, "CognitiveLoad": 0.7, "VisualEngagement": 1.1}'

    mock_model_instance = MagicMock()
    mock_model_instance.generate_content.return_value = mock_response
    mock_model_class.return_value = mock_model_instance

    agent = AudienceAgent()
    # Ensure it's using our mock model
    agent.model = mock_model_instance

    multipliers = agent.derive_multipliers("Eco-conscious Gen Z minimalist")

    assert multipliers["Attention"] == 1.2
    assert multipliers["Emotion"] == 0.8
    assert multipliers["Reward"] == 1.5
    assert multipliers["CognitiveLoad"] == 0.7
    assert len(multipliers) == 6

def test_audience_agent_fallback():
    # Test fallback on invalid JSON response
    with patch("agents.specialized_agents.AudienceAgent._generate") as mock_gen:
        mock_gen.return_value = "Not a JSON"
        agent = AudienceAgent()
        multipliers = agent.derive_multipliers("Invalid Persona")

        assert multipliers["Attention"] == 1.0
        assert len(multipliers) == 6
