import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    # Gunakan session client agar manajemen cookie otomatis
    with TestClient(app) as c:
        # Reset rate limit store sebelum setiap test
        c.post("/test/reset-rate-limit")
        yield c


def test_scenario_a_no_jwt(client):
    response = client.post("/agent/scrape")
    assert response.status_code == 401


def test_scenario_b_valid_jwt(client):
    # 1. Login
    client.post("/agent/login-test")
    # 2. Hit
    response = client.post("/agent/scrape")
    assert response.status_code == 200


def test_scenario_c_rate_limit_abuse(client):
    """
    Scenario C: Mengetes batas 10 request.
    Karena fixture client melakukan reset, kita mulai dari 0.
    """
    client.post("/agent/login-test")

    # Request 1 sampai 10: Harus Berhasil (200)
    for i in range(10):
        response = client.post("/agent/scrape")
        assert response.status_code == 200, f"Request ke-{i+1} gagal"

    # Request 11: Harus Gagal (429)
    response = client.post("/agent/scrape")
    assert response.status_code == 429
    assert response.json()["detail"] == "Rate limit exceeded"
