import os
import jwt
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

# Import the FastAPI app
from project.backend.app.main import app

client = TestClient(app)

# Helper to generate JWT tokens with custom role
def generate_token(role: str):
    payload = {
        "sub": "test_user",
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    secret = os.getenv("JWT_SECRET", "supersecret")
    token = jwt.encode(payload, secret, algorithm="HS256")
    return token


def test_login_returns_analyst_token():
    response = client.post("/api/v1/login", json={"username": "alice"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    # Decode to verify role
    decoded = jwt.decode(data["access_token"], os.getenv("JWT_SECRET", "supersecret"), algorithms=["HS256"])
    assert decoded["role"] == "analyst"


def test_upload_requires_auth():
    # Attempt without token
    response = client.post(
        "/api/v1/upload",
        files={"file": ("test.csv", "col1,col2\n1,2", "text/csv")},
    )
    assert response.status_code == 401


def test_upload_with_analyst_token():
    token = generate_token("analyst")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/api/v1/upload",
        files={"file": ("test.csv", "col1,col2\n1,2", "text/csv")},
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "dataset_id" in data


def test_analyze_requires_analyst_role():
    # First upload a file to get a dataset_id
    token = generate_token("analyst")
    headers = {"Authorization": f"Bearer {token}"}
    upload_resp = client.post(
        "/api/v1/upload",
        files={"file": ("test.csv", "col1,col2\n1,2", "text/csv")},
        headers=headers,
    )
    dataset_id = upload_resp.json()["dataset_id"]

    # Attempt analysis with a non‑analyst token
    non_analyst_token = generate_token("user")
    bad_headers = {"Authorization": f"Bearer {non_analyst_token}"}
    resp = client.post(f"/api/v1/analyze/{dataset_id}", headers=bad_headers)
    assert resp.status_code == 403

    # Successful analysis with analyst token
    good_resp = client.post(f"/api/v1/analyze/{dataset_id}", headers=headers)
    assert good_resp.status_code == 200
    result = good_resp.json()
    assert "result" in result
    # Verify that the pipeline produced expected keys
    ctx = result["result"]
    assert ctx.get("cleaned") is True
    assert ctx.get("eda_success") is True
    assert ctx.get("business") is not None

