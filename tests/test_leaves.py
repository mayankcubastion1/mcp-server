from datetime import date, datetime

from fastapi.testclient import TestClient
import pytest

from mcp_server.main import app
from mcp_server.leaves import api as leaves_api
from mcp_server.leaves.models import LeaveEntry, LeavesResponse

client = TestClient(app)


@pytest.fixture
def mock_get_leaves(monkeypatch):
    sample = LeavesResponse(
        statusCode=200,
        statusMessage="Document Found",
        data=[
            LeaveEntry(
                id="1",
                category="Leave",
                type="Debit",
                status="Pending Approval",
                leaveDate=date(2025, 5, 1),
                leaveCount=1.0,
                comments="Sick leave",
                salaryYear=None,
                salaryMonth=None,
                subStatus=None,
                appliedDate=date(2025, 4, 25),
                approvedDate=None,
                employeeId="emp1",
                employeeFinancialYearId="roxq0g78pis7ia9",
                createdAt=datetime(2025, 4, 25, 10, 0, 0),
                updatedAt=datetime(2025, 4, 25, 10, 0, 0),
            )
        ],
    )

    async def _mock(fy_id: str, auth_header: str) -> LeavesResponse:
        return sample

    monkeypatch.setattr(leaves_api.client, "get_leaves", _mock)


def test_leaves_endpoint(mock_get_leaves):
    response = client.get(
        "/leaves",
        params={"fyId": "roxq0g78pis7ia9"},
        headers={"Authorization": "Bearer token"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["statusCode"] == 200
    assert body["data"][0]["employeeFinancialYearId"] == "roxq0g78pis7ia9"
