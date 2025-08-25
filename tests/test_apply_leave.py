from datetime import date, datetime

from fastapi.testclient import TestClient
import pytest

from mcp_server.main import app, client as hrms_client
from mcp_server.tools.leaves.models import (
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

    monkeypatch.setattr(hrms_client, "apply_leave", _mock)


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


def test_apply_leave_defaults(monkeypatch):
    sample = ApplyLeaveResponse(
        statusCode=200,
        statusMessage="Document created successfully",
        data=ApplyLeaveData(
            id="123",
            leaveDate=date(2025, 8, 24),
            leaveCount=1.0,
            comments="personal work",
            category="Leave",
            type="Debit",
            status="Pending Approval",
            employeeFinancialYearId="fy1",
            employeeId="emp1",
            appliedDate=date(2025, 8, 6),
            updatedAt=datetime(2025, 8, 6, 10, 0, 0),
            createdAt=datetime(2025, 8, 6, 10, 0, 0),
        ),
    )

    captured: dict = {}

    async def _mock(payload: ApplyLeaveRequest, auth_header: str) -> ApplyLeaveResponse:
        captured["payload"] = payload
        return sample

    monkeypatch.setattr(hrms_client, "apply_leave", _mock)

    minimal_payload = {
        "leaveCount": 1.0,
        "leaveDate": "2025-08-24",
        "comments": "personal work",
    }
    response = client.post(
        "/leaves/apply",
        json=minimal_payload,
        headers={"Authorization": "Bearer token"},
    )
    assert response.status_code == 200
    assert captured["payload"].category == "Debit"
    assert captured["payload"].status == "Pending Approval"
