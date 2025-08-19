from fastapi.testclient import TestClient
import httpx
from mcp_server.main import app, client as hrms_client
import pytest

client = TestClient(app)


@pytest.fixture(autouse=True)
def set_base_url(monkeypatch):
    monkeypatch.setenv("SERVER_EXTERNAL_BASE_URL", "http://testserver")
    # Use the in-process FastAPI app for HTTP requests
    monkeypatch.setattr("mcp_server.leaves.tools.httpx.Client", lambda *args, **kwargs: client)


@pytest.fixture
def mock_holidays_error(monkeypatch):
    async def _mock(year: int, auth_header: str):
        raise httpx.HTTPError("upstream fail")
    monkeypatch.setattr(hrms_client, "get_holidays", _mock)


def test_call_tool_propagates_http_error(mock_holidays_error):
    response = client.post(
        "/mcp-compat/call",
        json={"name": "get_holidays", "arguments": {"year": 2025}},
        headers={"Authorization": "Bearer token"},
    )
    assert response.status_code == 502
    assert response.json()["detail"] == "upstream fail"

