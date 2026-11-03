
from fastapi.testclient import TestClient
from backend.api import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True
    assert data["model_type"]


def test_model_info_endpoint():
    response = client.get("/model-info")

    assert response.status_code == 200

    data = response.json()
    assert data["number_of_features"] == 13
    assert len(data["feature_names"]) == 13


def test_predict_endpoint():
    applicant = {
        "age": 35,
        "income": 60000,
        "loan_amount": 200000,
        "loan_tenure_months": 36,
        "credit_history": "Existing borrower",
        "avg_dpd_per_delinquency": 0,
        "delinquency_ratio": 0,
        "credit_utilization_ratio": 30,
        "num_open_accounts": 3,
        "residence_type": "Owned",
        "loan_purpose": "Home",
        "loan_type": "Secured"
    }

    response = client.post("/predict", json=applicant)

    assert response.status_code == 200

    data = response.json()
    assert data["predicted_class"] in [0, 1]
    assert 0 <= data["default_probability"] <= 1
    assert 300 <= data["credit_score"] <= 900
    assert data["rating"] in ["Poor", "Average", "Good", "Excellent"]


def test_predict_rejects_invalid_age():
    applicant = {
        "age": 17,
        "income": 60000,
        "loan_amount": 200000,
        "loan_tenure_months": 36,
        "credit_history": "Existing borrower",
        "avg_dpd_per_delinquency": 0,
        "delinquency_ratio": 0,
        "credit_utilization_ratio": 30,
        "num_open_accounts": 3,
        "residence_type": "Owned",
        "loan_purpose": "Home",
        "loan_type": "Secured"
    }

    response = client.post("/predict", json=applicant)

    assert response.status_code == 422
