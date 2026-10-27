import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Legal Metrology" in data["service"]

def test_auth_login():
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "inspector@gov.in", "password": "demo"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "inspector@gov.in"

def test_inspection_crud_and_demo():
    # 1. Test Seed Demo data
    seed_res = client.post("/api/v1/demo/seed")
    assert seed_res.status_code == 200

    # 2. Test List Inspections
    list_res = client.get("/api/v1/inspections")
    assert list_res.status_code == 200
    inspections = list_res.json()
    assert len(inspections) >= 1

    # 3. Test Get Detail
    insp_id = inspections[0]["id"]
    detail_res = client.get(f"/api/v1/inspections/{insp_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert "inspection_number" in detail

    # 4. Test Dashboard summary
    dash_res = client.get("/api/v1/dashboard/summary")
    assert dash_res.status_code == 200
    dash_data = dash_res.json()
    assert dash_data["total_inspections"] >= 1
