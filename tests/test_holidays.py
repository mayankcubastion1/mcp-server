from datetime import date

from fastapi.testclient import TestClient
import pytest

from mcp_server.main import app, client as hrms_client
from mcp_server.tools.leaves.models import Holiday, HolidaysResponse

client = TestClient(app)


@pytest.fixture
def mock_get_holidays(monkeypatch):
    sample = HolidaysResponse(
        statusCode=200,
        statusMessage="Document Found",
        data=[
            Holiday(holidayDate=date(2025, 1, 26), descText="Republic Day", type="GH"),
        ],
        rhBalance=2,
    )

    async def _mock(year: int, auth_header: str) -> HolidaysResponse:
        return sample

    monkeypatch.setattr(hrms_client, "get_holidays", _mock)


def test_holidays_endpoint(mock_get_holidays):
    response = client.get(
        "/holidays",
        params={"year": 2025},
        headers={"Authorization": "Bearer token"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["statusCode"] == 200
    assert body["data"][0]["descText"] == "Republic Day"
