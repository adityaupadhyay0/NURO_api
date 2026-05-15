import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import os
import sys
import uuid

# Ensure the root directory is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from core.database import init_db, SessionLocal, User
from core.auth import get_password_hash

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    init_db()
    db = SessionLocal()
    # Create test users
    if not db.query(User).filter_by(username="admin").first():
        db.add(User(username="admin", hashed_password=get_password_hash("admin123"), role="Admin"))
    if not db.query(User).filter_by(username="marketer").first():
        db.add(User(username="marketer", hashed_password=get_password_hash("marketer123"), role="Marketer"))
    if not db.query(User).filter_by(username="viewer").first():
        db.add(User(username="viewer", hashed_password=get_password_hash("viewer123"), role="Viewer"))
    db.commit()
    db.close()
    yield

def get_token(username, password):
    response = client.post("/auth/token", data={"username": username, "password": password})
    return response.json()["access_token"]

def test_health_unauthorized():
    response = client.get("/health")
    assert response.status_code == 401

def test_health_forbidden():
    token = get_token("marketer", "marketer123")
    response = client.get("/health", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403

def test_health_admin():
    token = get_token("admin", "admin123")
    response = client.get("/health", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == {"status": "Pro 10x engine is active"}

@patch("app.NeuroEngine")
@patch("app.CampaignBrain")
def test_analyze_text_mocked(mock_brain, mock_engine):
    token = get_token("marketer", "marketer123")
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

    with patch("app.engine", mock_engine_instance):
        response = client.post(
            "/analyze",
            params={
                "media_type": "text",
                "text_content": "Test ad copy",
                "campaign_name": "Test Campaign"
            },
            headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "processing"

def test_get_campaigns_viewer():
    token = get_token("viewer", "viewer123")
    response = client.get("/campaigns", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_registration_privilege_escalation_attempt():
    # Attempt to register with a role field (which should now be ignored by the model)
    unique_user = f"hacker_{uuid.uuid4().hex[:8]}"
    response = client.post(
        "/auth/register",
        json={"username": unique_user, "password": "password123", "role": "Admin"}
    )
    assert response.status_code == 200

    # Verify the user was created with the default 'Marketer' role, not 'Admin'
    db = SessionLocal()
    user = db.query(User).filter_by(username=unique_user).first()
    assert user.role == "Marketer"
    db.close()

@patch("app.NeuroEngine")
def test_analyze_batch_mocked(mock_engine):
    token = get_token("marketer", "marketer123")
    mock_engine_instance = mock_engine.return_value
    mock_engine_instance.analyze_media.return_value = {
        "timestamps": [0],
        "neuro_metrics": {"Attention": [50]},
        "marketing_kpis": {"ScrollStopRate": [50]},
        "winning_probability": 50
    }

    files = [
        ("files", ("video1.mp4", b"content1", "video/mp4")),
        ("files", ("video2.mp4", b"content2", "video/mp4"))
    ]

    with patch("app.engine", mock_engine_instance):
        response = client.post(
            "/analyze_batch",
            params={"media_type": "video", "campaign_name": "Batch Test"},
            files=files,
            headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == 200
    data = response.json()
    assert "task_ids" in data
    assert len(data["task_ids"]) == 2
