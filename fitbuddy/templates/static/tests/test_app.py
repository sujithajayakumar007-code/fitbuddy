import os

os.environ["DEMO_MODE"] = "true"
os.environ["GEMINI_API_KEY"] = ""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_home_page(client):

    response = client.get("/")

    assert response.status_code == 200
    assert "FitBuddy" in response.text


def test_admin_page(client):

    response = client.get("/view-all-users")

    assert response.status_code == 200
    assert "All FitBuddy Users" in response.text


def test_health(client):

    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"


def test_create_plan_api(client):

    response = client.post(
        "/api/plans",
        json={
            "user_id": "test-user-001",
            "name": "Test User",
            "age": 25,
            "weight": 70,
            "goal": "general wellness",
            "intensity": "medium",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert data["user_id"] == "test-user-001"
    assert "workout_plan" in data
    assert "nutrition_tip" in data


def test_feedback_api(client):

    response = client.post(
        "/api/plans/feedback",
        json={
            "user_id": "test-user-001",
            "feedback": "Please add more cardio.",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert "updated_plan" in data