from datetime import date, datetime

import pytest
from fastapi.testclient import TestClient

from mcp_server.main import app
from mcp_server.leaves import api as leaves_api
from mcp_server.leaves.models import (
    ApplyLeaveData,
    ApplyLeaveRequest,
    ApplyLeaveResponse,
    Holiday,
    HolidaysResponse,
)
from mcp_server.leaves.tools import create_structured_tools


@pytest.fixture
def http_client():
    """Test client bound to the FastAPI app for in-process requests."""
    return TestClient(app)


@pytest.fixture
def tools(http_client):
    return create_structured_tools(
        "http://testserver", lambda: "Bearer token", client=http_client
    )


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

    monkeypatch.setattr(leaves_api.client, "get_holidays", _mock)


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


def test_get_holidays_tool(mock_get_holidays, tools):
    holidays_tool = next(t for t in tools if t.name == "get_holidays")
    result = holidays_tool.invoke({"year": 2025})
    assert result["statusCode"] == 200
    assert result["data"][0]["descText"] == "Republic Day"


def test_apply_leave_tool(mock_apply_leave, tools):
    apply_tool = next(t for t in tools if t.name == "apply_leave")
    payload = {
        "type": "Debit",
        "category": "Leave",
        "leaveCount": 2.0,
        "leaveDate": "2025-08-24",
        "comments": "Not feeling well",
        "status": "Pending Approval",
    }
    result = apply_tool.invoke(payload)
    assert result["statusMessage"] == "Document created successfully"
    assert result["data"]["category"] == "Leave"
