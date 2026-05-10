import pytest
import numpy as np
from unittest.mock import MagicMock, patch
import torch

# Mock the TribeModel before importing NeuroEngine to avoid heavy weight loading
with patch('tribev2.TribeModel.from_pretrained') as mock_pretrained:
    from core.neuro_engine import NeuroEngine

@pytest.fixture
def mock_neuro_engine():
    with patch('tribev2.TribeModel.from_pretrained') as mock_pretrained:
        mock_model = MagicMock()
        mock_pretrained.return_value = mock_model

        # Mock nilearn dataset to avoid downloads
        with patch('nilearn.datasets.fetch_atlas_surf_destrieux') as mock_atlas:
            # Create an atlas where some vertices belong to our ROIs
            fake_left = np.zeros(10242, dtype=int)
            fake_right = np.zeros(10242, dtype=int)
            # Assign some vertices to 'Attention' (indices 16, 55, 15, 54)
            fake_left[0:10] = 16
            fake_right[0:10] = 24 # 'Reward'

            mock_atlas.return_value = {
                'map_left': fake_left,
                'map_right': fake_right
            }
            engine = NeuroEngine()
            return engine, mock_model

def test_roi_mapping_consistency(mock_neuro_engine):
    engine, _ = mock_neuro_engine
    # Check if ROI map contains expected marketing dimensions
    expected_rois = ["Attention", "Emotion", "Reward", "Memory", "CognitiveLoad", "VisualEngagement"]
    for roi in expected_rois:
        assert roi in engine.roi_map
        assert isinstance(engine.roi_map[roi], list)

def test_process_predictions_logic(mock_neuro_engine):
    engine, _ = mock_neuro_engine

    # Create fake prediction data (n_timesteps=2, n_vertices=20484)
    preds = np.random.rand(2, 20484).astype(np.float32)
    segments = {"onset": np.array([0.0, 1.0])}

    results = engine._process_predictions(preds, segments)

    assert "neuro_metrics" in results
    assert "marketing_kpis" in results
    assert "winning_probability" in results
    assert "creative_fatigue" in results

    # Check specific marketing KPI existence
    assert "ScrollStopRate" in results["marketing_kpis"]
    assert "PurchaseIntent" in results["marketing_kpis"]

def test_audience_weighting_meta_tiktok(mock_neuro_engine):
    engine, _ = mock_neuro_engine

    kpis = {
        "ScrollStopRate": [50.0],
        "ViralPotential": [50.0]
    }

    # TikTok + Gen Z should trigger multipliers
    params = {"platform": "TikTok", "age": "18-24"}
    adjusted = engine._apply_audience_weighting(kpis, params)

    # Based on _apply_audience_weighting:
    # ScrollStopRate multiplier = 0.75
    # ViralPotential multiplier = 1.3
    # Wait, the code says np.prod(multipliers) if multipliers else 1.0
    # Let's check:
    # if platform == "TikTok" and age == "18-24":
    #    if kpi_name == "ScrollStopRate": multipliers.append(0.75)
    #    if kpi_name == "ViralPotential": multipliers.append(1.3)
    # if awareness == "Cold": (default in _apply_audience_weighting is "Cold")
    #    if kpi_name == "ScrollStopRate": multipliers.append(1.1)

    # For ScrollStopRate: 0.75 * 1.1 = 0.825.  50 * 0.825 = 41.25
    # For ViralPotential: 1.3 * 1.0 = 1.3. 50 * 1.3 = 65.0

    assert adjusted["ScrollStopRate"][0] == pytest.approx(41.25)
    assert adjusted["ViralPotential"][0] == pytest.approx(65.0)

def test_winning_probability_calculation(mock_neuro_engine):
    engine, _ = mock_neuro_engine

    # Create two timesteps with variation to allow normalization
    preds = np.random.rand(2, 20484).astype(np.float32)
    segments = {"onset": np.array([0.0, 1.0])}

    results = engine._process_predictions(preds, segments)

    # If all activations are 1, normalized metrics should be 100
    # Winning Probability = SSR * 0.3 + PI * 0.7
    # SSR = Attention * 0.7 + VisualEngagement * 0.3
    # PI = Reward * 0.6 + Emotion * 0.4 - CognitiveLoad * 0.2

    assert results["winning_probability"] > 0
    assert results["winning_probability"] <= 100
