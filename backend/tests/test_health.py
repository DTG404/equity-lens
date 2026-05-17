from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint_reports_service_identity():
    client = TestClient(app)

    response = client.get('/api/health')

    assert response.status_code == 200
    assert response.json() == {
        'service': 'equity-lens-api',
        'status': 'ok',
        'mode': 'local-first',
    }
