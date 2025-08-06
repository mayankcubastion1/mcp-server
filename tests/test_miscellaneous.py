from datetime import date

import pytest
from fastapi.testclient import TestClient

from mcp_server.main import app
from mcp_server.miscellaneous.models import (
    FinancialYear,
    FinancialYearsResponse,
    ProfileResponse,
)
from mcp_server.miscellaneous.router import client as misc_client
from mcp_server.miscellaneous.tools import create_langchain_tools

client = TestClient(app)


@pytest.fixture
def mock_financial_years(monkeypatch):
    sample = FinancialYearsResponse(
        statusCode=200,
        statusMessage="OK",
        data=[
            FinancialYear(
                id="fy1",
                fyStartDate=date(2024, 4, 1),
                fyEndDate=date(2025, 3, 31),
                financialYear="2024-2025",
                employeeId="emp1",
            )
        ],
    )

    async def _mock(auth_header: str) -> FinancialYearsResponse:
        return sample

    monkeypatch.setattr(misc_client, "get_financial_years", _mock)


def test_financial_years_endpoint(mock_financial_years):
    response = client.get(
        "/financial-years", headers={"Authorization": "Bearer token"}
    )
    assert response.status_code == 200
    assert response.json()["data"][0]["Id"] == "fy1"


@pytest.fixture
def mock_employee_profile(monkeypatch):
    sample = ProfileResponse(
        statusCode=200,
        statusMessage="OK",
        data={"employeeId": "emp1"},
    )

    async def _mock(employee_id: str, auth_header: str) -> ProfileResponse:
        return sample

    monkeypatch.setattr(misc_client, "get_employee_profile", _mock)


def test_employee_profile_endpoint(mock_employee_profile):
    response = client.get(
        "/employees/emp1", headers={"Authorization": "Bearer token"}
    )
    assert response.status_code == 200
    assert response.json()["data"]["employeeId"] == "emp1"


@pytest.fixture
def http_client():
    return TestClient(app)


@pytest.fixture
def tools(http_client):
    return create_langchain_tools(
        "http://testserver", lambda: "Bearer token", client=http_client
    )


def test_health_tool(tools):
    tool = next(t for t in tools if t.name == "health")
    result = tool.invoke({})
    assert result == {"status": "ok"}


def test_financial_years_tool(mock_financial_years, tools):
    tool = next(t for t in tools if t.name == "get_financial_years")
    result = tool.invoke({})
    assert result["data"][0]["Id"] == "fy1"


def test_employee_profile_tool(mock_employee_profile, tools):
    tool = next(t for t in tools if t.name == "get_employee_profile")
    result = tool.invoke({"employee_id": "emp1"})
    assert result["data"]["employeeId"] == "emp1"
