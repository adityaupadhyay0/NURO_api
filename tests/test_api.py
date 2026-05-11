import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import os
import sys

# Ensure the root directory is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from core.database import init_db

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    init_db()
    yield

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "Pro 10x engine is active"}

@patch("app.NeuroEngine")
@patch("app.CampaignBrain")
def test_analyze_text_mocked(mock_brain, mock_engine):
    # Mock behavior
    mock_engine_instance = mock_engine.return_value
    mock_engine_instance.analyze_media.return_value = {
        "timestamps": [0],
        "neuro_metrics": {"Attention": [50]},
        "marketing_kpis": {"ScrollStopRate": [50]},
        "winning_probability": 50,
        "creative_fatigue": {"fatigue_index": 10, "estimated_days": 20},
        "vibe_analysis": "Trust",
        "moi_analysis": []
    }

    mock_brain_instance = mock_brain.return_value
    mock_brain_instance.run_campaign_optimization.return_value = {
        "neuro_intelligence": "Good",
        "creative_strategy": "Keep going",
        "media_buying_plan": "Spend money",
        "cro_optimization": None,
        "summary": "Mocked report"
    }

    # We need to ensure get_engine uses our mock if it's already initialized or not
    # In app.py, get_engine() checks if 'engine' is None.
    with patch("app.engine", mock_engine_instance):
        response = client.post(
            "/analyze",
            params={
                "media_type": "text",
                "text_content": "Test ad copy",
                "campaign_name": "Test Campaign"
            }
        )

    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "processing"

def test_get_campaigns():
    response = client.get("/campaigns")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@patch("app.NeuroEngine")
def test_analyze_batch_mocked(mock_engine):
    mock_engine_instance = mock_engine.return_value
    # Minimal mock return
    mock_engine_instance.analyze_media.return_value = {
        "timestamps": [0],
        "neuro_metrics": {"Attention": [50]},
        "marketing_kpis": {"ScrollStopRate": [50]},
        "winning_probability": 50
    }

    # Prepare mock files
    files = [
        ("files", ("video1.mp4", b"content1", "video/mp4")),
        ("files", ("video2.mp4", b"content2", "video/mp4"))
    ]

    with patch("app.engine", mock_engine_instance):
        response = client.post(
            "/analyze_batch",
            params={"media_type": "video", "campaign_name": "Batch Test"},
            files=files
        )

    assert response.status_code == 200
    data = response.json()
    assert "task_ids" in data
    assert len(data["task_ids"]) == 2
