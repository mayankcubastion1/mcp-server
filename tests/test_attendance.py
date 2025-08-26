from datetime import date, datetime

import pytest
from fastapi.testclient import TestClient

from xmcp.main import app
from xmcp.tools.attendance.models import (
    AttendanceEntry,
    Paginate,
    AttendanceResponse,
)
from xmcp.tools.attendance.router import client as attendance_client
from xmcp.tools.attendance.tools import create_langchain_tools

client = TestClient(app)


@pytest.fixture
def mock_get_attendance(monkeypatch):
    sample = AttendanceResponse(
        statusCode=200,
        statusMessage="Success",
        data=[
            AttendanceEntry(
                id="1",
                attendanceDate=date(2025, 5, 1),
                createdAt=datetime(2025, 5, 1, 9, 0, 0),
                updatedAt=datetime(2025, 5, 1, 9, 0, 0),
            )
        ],
        paginate=Paginate(
            totalRecords=1,
            totalPerpage=10,
            totalPage=1,
            currentPage=1,
        ),
    )

    async def _mock(year: int, month: int, auth_header: str) -> AttendanceResponse:
        return sample

    monkeypatch.setattr(attendance_client, "get_my_attendance", _mock)


def test_attendance_endpoint(mock_get_attendance):
    response = client.post(
        "/attendance/my-attendance",
        params={"year": 2025, "month": 5},
        headers={"Authorization": "Bearer token"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["data"][0]["Id"] == "1"


@pytest.fixture
def http_client():
    return TestClient(app)


@pytest.fixture
def tools(http_client):
    return create_langchain_tools(
        "http://testserver", lambda: "Bearer token", client=http_client
    )


def test_attendance_tool(mock_get_attendance, tools):
    tool = next(t for t in tools if t.name == "get_attendance")
    result = tool.invoke({"year": 2025, "month": 5})
    assert result["statusCode"] == 200
    assert result["data"][0]["Id"] == "1"
