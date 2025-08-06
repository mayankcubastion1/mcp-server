from datetime import date, datetime

from fastapi.testclient import TestClient
import pytest

from mcp_server.main import app
from mcp_server.leaves import api as leaves_api
from mcp_server.leaves.models import (
    ApplyLeaveData,
    ApplyLeaveRequest,
    ApplyLeaveResponse,
)

client = TestClient(app)


@pytest.fixture
def mock_apply_leave(monkeypatch):
    sample = ApplyLeaveResponse(
        statusCode=200,
        statusMessage="Document created successfully",
        data=ApplyLeaveData(
            id="123",
            leaveDate=date(2025, 8, 24),
            leaveCount=2.0,
            comments="Not feeling well",
            category="Leave",
            type="Debit",
            status="Pending Approval",
            employeeFinancialYearId="roxq0g78pis7ia9",
            employeeId="emp1",
            appliedDate=date(2025, 8, 6),
            updatedAt=datetime(2025, 8, 6, 10, 0, 0),
            createdAt=datetime(2025, 8, 6, 10, 0, 0),
        ),
    )

    async def _mock(payload: ApplyLeaveRequest, auth_header: str) -> ApplyLeaveResponse:
        return sample

    monkeypatch.setattr(leaves_api.client, "apply_leave", _mock)


payload = {
    "type": "Debit",
    "category": "Leave",
    "leaveCount": 2.0,
    "leaveDate": "2025-08-24",
    "comments": "Not feeling well",
    "status": "Pending Approval",
}


def test_apply_leave_endpoint(mock_apply_leave):
    response = client.post(
        "/leaves/apply",
        json=payload,
        headers={"Authorization": "Bearer token"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["data"]["category"] == "Leave"
    assert body["statusMessage"] == "Document created successfully"
