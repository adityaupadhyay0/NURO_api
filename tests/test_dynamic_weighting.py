import pytest
import numpy as np
from unittest.mock import MagicMock, patch
import os

# Mock the TribeModel before importing NeuroEngine
with patch('tribev2.TribeModel.from_pretrained') as mock_pretrained:
    from core.neuro_engine import NeuroEngine

@pytest.fixture
def mock_neuro_engine():
    with patch('tribev2.TribeModel.from_pretrained') as mock_pretrained:
        mock_model = MagicMock()
        mock_pretrained.return_value = mock_model
        with patch('nilearn.datasets.fetch_atlas_surf_destrieux') as mock_atlas:
            mock_atlas.return_value = {
                'map_left': np.zeros(10242),
                'map_right': np.zeros(10242)
            }
            engine = NeuroEngine()
            return engine

def test_dynamic_persona_weighting(mock_neuro_engine):
    engine = mock_neuro_engine

    kpis = {
        "ScrollStopRate": [50.0],
        "PurchaseIntent": [50.0],
        "Clarity": [50.0]
    }

    # Mock AudienceAgent response
    persona_multipliers = {
        "Attention": 1.5,
        "Reward": 0.8,
        "CognitiveLoad": 1.2
    }

    with patch.object(engine.audience_agent, 'derive_multipliers', return_value=persona_multipliers):
        params = {"persona": "High-attention but skeptical buyer"}
        adjusted = engine._apply_audience_weighting(kpis, params)

        # ScrollStopRate: 50 * 1.5 * 1.1 (default awareness=Cold) = 82.5
        assert adjusted["ScrollStopRate"][0] == pytest.approx(82.5)

        # PurchaseIntent: 50 * 0.8 * 0.7 (default awareness=Cold) = 28.0
        assert adjusted["PurchaseIntent"][0] == pytest.approx(28.0)

        # Clarity: 50 * (2.0 - 1.2) = 40.0
        assert adjusted["Clarity"][0] == pytest.approx(40.0)

if __name__ == "__main__":
    pytest.main([__file__])
