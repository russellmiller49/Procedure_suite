from httpx import AsyncClient
import pytest

pytestmark = pytest.mark.asyncio


async def test_ui_index(api_client: AsyncClient):
    response = await api_client.get("/ui/")
    assert response.status_code == 200
    assert "Procedure Suite Workbench" in response.text

async def test_api_root_json(api_client: AsyncClient):
    # Default behavior (no Accept: text/html) should be JSON
    response = await api_client.get("/", headers={"Accept": "application/json"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Procedure Suite API"

async def test_api_root_redirects_browser(api_client: AsyncClient):
    # Browser behavior (Accept: text/html) should redirect
    response = await api_client.get("/", headers={"Accept": "text/html"}, follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/ui/"
