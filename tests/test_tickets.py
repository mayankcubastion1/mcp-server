import pytest
from fastapi.testclient import TestClient

from mcp_server.main import app
from mcp_server.tools.tickets.models import (
    TicketEntry,
    Paginate,
    TicketsResponse,
    TicketOperationResponse,
)
from mcp_server.tools.tickets.router import client as tickets_client
from mcp_server.tools.tickets.tools import create_langchain_tools

client = TestClient(app)


@pytest.fixture
def mock_get_tickets(monkeypatch):
    sample = TicketsResponse(
        statusCode=200,
        statusMessage="OK",
        data=[
            TicketEntry(id="t1", category="General", status="Draft")
        ],
        paginate=Paginate(
            totalRecords=1,
            totalPerpage=10,
            totalPage=1,
            currentPage=1,
        ),
    )

    async def _mock(id: str, status: str, page: int, auth_header: str) -> TicketsResponse:
        return sample

    monkeypatch.setattr(tickets_client, "get_my_tickets", _mock)


def test_get_tickets_endpoint(mock_get_tickets):
    response = client.get(
        "/tickets/my",
        params={"id": "emp1", "status": "Draft", "page": 1},
        headers={"Authorization": "Bearer token"},
    )
    assert response.status_code == 200
    assert response.json()["data"][0]["Id"] == "t1"


@pytest.fixture
def mock_raise_ticket(monkeypatch):
    sample = TicketOperationResponse(
        statusCode=200,
        statusMessage="Draft Created",
        data={"id": "t1"},
    )

    async def _mock(auth_header: str) -> TicketOperationResponse:
        return sample

    monkeypatch.setattr(tickets_client, "raise_ticket", _mock)


def test_raise_ticket_endpoint(mock_raise_ticket):
    response = client.post(
        "/tickets/draft", headers={"Authorization": "Bearer token"}
    )
    assert response.status_code == 200
    assert response.json()["data"]["id"] == "t1"


@pytest.fixture
def mock_submit_ticket(monkeypatch):
    sample = TicketOperationResponse(
        statusCode=200,
        statusMessage="Submitted",
        data={"id": "t1"},
    )

    async def _mock(id: str, auth_header: str) -> TicketOperationResponse:
        return sample

    monkeypatch.setattr(tickets_client, "submit_ticket", _mock)


def test_submit_ticket_endpoint(mock_submit_ticket):
    response = client.post(
        "/tickets/submit",
        params={"id": "t1"},
        headers={"Authorization": "Bearer token"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["id"] == "t1"


@pytest.fixture
def http_client():
    return TestClient(app)


@pytest.fixture
def tools(http_client):
    return create_langchain_tools(
        "http://testserver", lambda: "Bearer token", client=http_client
    )


def test_get_tickets_tool(mock_get_tickets, tools):
    tool = next(t for t in tools if t.name == "get_tickets")
    result = tool.invoke({"id": "emp1", "status": "Draft", "page": 1})
    assert result["data"][0]["Id"] == "t1"


def test_raise_ticket_tool(mock_raise_ticket, tools):
    tool = next(t for t in tools if t.name == "raise_ticket")
    result = tool.invoke({})
    assert result["data"]["id"] == "t1"


def test_submit_ticket_tool(mock_submit_ticket, tools):
    tool = next(t for t in tools if t.name == "submit_ticket")
    result = tool.invoke({"id": "t1"})
    assert result["data"]["id"] == "t1"
