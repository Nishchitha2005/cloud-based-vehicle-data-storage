from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def get_access_token():
    """
    Authenticate with the backend and return a JWT token.
    """

    response = client.post(
        "/login",
        data={
            "username": "admin",
            "password": "admin123"
        }
    )

    assert response.status_code == 200

    response_data = response.json()

    assert "access_token" in response_data
    assert response_data["token_type"] == "bearer"

    return response_data["access_token"]


def test_health_check():
    """
    Verify that the API health endpoint is working.
    """

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy"
    }


def test_root_endpoint():
    """
    Verify that the root endpoint is working.
    """

    response = client.get("/")

    assert response.status_code == 200

    response_data = response.json()

    assert "message" in response_data
    assert "Cloud-Based Vehicle Data Storage API" in response_data["message"]


def test_login_success():
    """
    Verify successful administrator authentication.
    """

    response = client.post(
        "/login",
        data={
            "username": "admin",
            "password": "admin123"
        }
    )

    assert response.status_code == 200

    response_data = response.json()

    assert "access_token" in response_data
    assert response_data["token_type"] == "bearer"


def test_login_invalid_credentials():
    """
    Verify that invalid credentials are rejected.
    """

    response = client.post(
        "/login",
        data={
            "username": "admin",
            "password": "wrong-password"
        }
    )

    assert response.status_code == 401


def test_protected_endpoint_without_token():
    """
    Verify that protected endpoints require authentication.
    """

    response = client.get("/vehicles")

    assert response.status_code == 401


def test_get_vehicles():
    """
    Verify that authenticated users can retrieve vehicles.
    """

    token = get_access_token()

    response = client.get(
        "/vehicles",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_invalid_telemetry_validation():
    """
    Verify that invalid telemetry values are rejected
    by Pydantic validation.
    """

    token = get_access_token()

    invalid_telemetry = {
        "vehicle_id": 1,
        "speed": -20,
        "engine_rpm": 2500,
        "engine_temperature": 88,
        "fuel_level": 72,
        "battery_voltage": 13.6,
        "latitude": 12.2958,
        "longitude": 76.6394
    }

    response = client.post(
        "/telemetry",
        json=invalid_telemetry,
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 422


def test_telemetry_unknown_vehicle():
    """
    Verify that telemetry cannot be submitted
    for a vehicle that does not exist.
    """

    token = get_access_token()

    telemetry = {
        "vehicle_id": 999999,
        "speed": 80,
        "engine_rpm": 2500,
        "engine_temperature": 85,
        "fuel_level": 70,
        "battery_voltage": 13.5,
        "latitude": 12.2958,
        "longitude": 76.6394
    }

    response = client.post(
        "/telemetry",
        json=telemetry,
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Vehicle not found"


def test_analytics_unknown_vehicle():
    """
    Verify that analytics returns 404
    for an unknown vehicle.
    """

    token = get_access_token()

    response = client.get(
        "/analytics/999999",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Vehicle not found"


def test_alerts_unknown_vehicle():
    """
    Verify that alerts returns 404
    for an unknown vehicle.
    """

    token = get_access_token()

    response = client.get(
        "/alerts/999999",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Vehicle not found"