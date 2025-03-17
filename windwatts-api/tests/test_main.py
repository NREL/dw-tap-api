import sys
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_read_root():
    print(sys.executable)
    response = client.get("/healthcheck")
    assert response.status_code == 200
    assert response.json() == {"status": "up"}
