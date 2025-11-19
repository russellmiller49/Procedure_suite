from fastapi.testclient import TestClient
from modules.api.fastapi_app import app

client = TestClient(app)

def test_ui_index():
    response = client.get("/ui/")
    assert response.status_code == 200
    assert "Procedure Suite Workbench" in response.text

def test_api_root_json():
    # Default behavior (no Accept: text/html) should be JSON
    response = client.get("/", headers={"Accept": "application/json"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Procedure Suite API"

def test_api_root_redirects_browser():
    # Browser behavior (Accept: text/html) should redirect
    response = client.get("/", headers={"Accept": "text/html"}, follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/ui/"