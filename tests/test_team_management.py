from datetime import date, datetime

import pytest
from fastapi.testclient import TestClient

from xmcp.main import app
from xmcp.tools.team_management.models import (
    LedgerEntry,
    LeaveBalance,
    TeamLedgerResponse,
)
from xmcp.tools.team_management.router import client as team_client
from xmcp.tools.team_management.tools import create_langchain_tools

client = TestClient(app)


@pytest.fixture
def mock_team_ledger(monkeypatch):
    sample = TeamLedgerResponse(
        statusCode=200,
        statusMessage="OK",
        data=[
            LedgerEntry(
                id="1",
                category="Leave",
                type="Debit",
                status="Approved",
                employeeFinancialYearId="fy1",
                leaveDate=date(2025, 5, 1),
                leaveCount=1.0,
                createdAt=datetime(2025, 5, 1, 9, 0, 0),
                updatedAt=datetime(2025, 5, 1, 9, 0, 0),
            )
        ],
        leaveBalance=LeaveBalance(
            leavesAccured=1,
            leavesConsumed=0,
            leavesRemaining=1,
            overConsumedLeaves=0,
            compOffAccrued=0,
            compOffConsumed=0,
            compOffLapsed=0,
            rhBalance=0,
            compOffRemaining=0,
            paternityRemaining=0,
            maternityRemaining=0,
            maternityConsumed=0,
        ),
    )

    async def _mock(empId: str, fy: str, auth_header: str) -> TeamLedgerResponse:
        return sample

    monkeypatch.setattr(team_client, "get_team_ledger", _mock)


def test_team_ledger_endpoint(mock_team_ledger):
    response = client.get(
        "/team-management/ledger",
        params={"empId": "e1", "fy": "2024-2025"},
        headers={"Authorization": "Bearer token"},
    )
    assert response.status_code == 200
    assert response.json()["data"][0]["Id"] == "1"


@pytest.fixture
def http_client():
    return TestClient(app)


@pytest.fixture
def tools(http_client):
    return create_langchain_tools(
        "http://testserver", lambda: "Bearer token", client=http_client
    )


def test_team_ledger_tool(mock_team_ledger, tools):
    tool = next(t for t in tools if t.name == "get_team_ledger")
    result = tool.invoke({"empId": "e1", "fy": "2024-2025"})
    assert result["data"][0]["Id"] == "1"
