from datetime import date, datetime

from fastapi.testclient import TestClient
import pytest

from mcp_server.main import app, client as hrms_client
from mcp_server.leaves.models import ApplyLeaveData, ApplyLeaveRequest, ApplyLeaveResponse

client = TestClient(app)


@pytest.fixture
def mock_apply_comp_off(monkeypatch):
    sample = ApplyLeaveResponse(
        statusCode=200,
        statusMessage="Document created successfully",
        data=ApplyLeaveData(
            id="123",
            leaveDate=date(2025, 6, 1),
            leaveCount=1.0,
            comments="worked upon agentic ai",
            category="Comp-Off",
            type="Credit",
            status="Pending Approval",
            employeeFinancialYearId="fy1",
            employeeId="emp1",
            appliedDate=date(2025, 6, 2),
            updatedAt=datetime(2025, 6, 2, 10, 0, 0),
            createdAt=datetime(2025, 6, 2, 10, 0, 0),
        ),
    )

    async def _mock(payload: ApplyLeaveRequest, auth_header: str) -> ApplyLeaveResponse:
        return sample

    monkeypatch.setattr(hrms_client, "apply_comp_off", _mock)


payload = {
    "type": "Credit",
    "category": "Comp-Off",
    "leaveCount": 1.0,
    "leaveDate": "2025-06-01",
    "comments": "worked upon agentic ai",
    "status": "Pending Approval",
}


def test_apply_comp_off_endpoint(mock_apply_comp_off):
    response = client.post(
        "/leaves/apply/comp-off",
        json=payload,
        headers={"Authorization": "Bearer token"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["data"]["category"] == "Comp-Off"
    assert body["statusMessage"] == "Document created successfully"

