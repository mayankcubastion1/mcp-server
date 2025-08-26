from datetime import date

import pytest
from fastapi.testclient import TestClient

from xmcp.main import app
from xmcp.tools.feedback.models import (
    AddFeedbackRequest,
    AddFeedbackResponse,
    RMFeedbacksResponse,
    FeedbackLevelsResponse,
)
from xmcp.tools.feedback.router import client as feedback_client
from xmcp.tools.feedback.tools import create_langchain_tools

client = TestClient(app)


@pytest.fixture
def mock_add_feedback(monkeypatch):
    sample = AddFeedbackResponse(
        statusCode=200,
        statusMessage="Created",
        data={"id": "fb1"},
    )

    async def _mock(payload: AddFeedbackRequest, auth_header: str) -> AddFeedbackResponse:
        return sample

    monkeypatch.setattr(feedback_client, "add_feedback", _mock)


def test_add_feedback_endpoint(mock_add_feedback):
    payload = {
        "nextFollowUpDate": "2025-05-01",
        "employeeId": "emp1",
        "description": "Great work",
        "outcome": "Positive",
        "stars": 5,
        "type": "appreciation",
        "year": 2025,
        "month": 5,
    }
    response = client.post(
        "/feedback/add", json=payload, headers={"Authorization": "Bearer token"}
    )
    assert response.status_code == 200
    assert response.json()["data"]["id"] == "fb1"


@pytest.fixture
def mock_rm_feedbacks(monkeypatch):
    sample = RMFeedbacksResponse(
        statusCode=200,
        statusMessage="OK",
        data=[{"id": "1"}],
        paginate=None,
    )

    async def _mock(auth_header: str, id: str) -> RMFeedbacksResponse:
        return sample

    monkeypatch.setattr(feedback_client, "get_rm_feedbacks", _mock)


def test_rm_feedbacks_endpoint(mock_rm_feedbacks):
    response = client.get(
        "/feedback/rm-feedbacks",
        params={"id": "emp1"},
        headers={"Authorization": "Bearer token"},
    )
    assert response.status_code == 200
    assert response.json()["data"][0]["id"] == "1"


@pytest.fixture
def mock_feedback_levels(monkeypatch):
    sample = FeedbackLevelsResponse(
        statusCode=200,
        statusMessage="OK",
        data=[{"employeeId": "emp1"}],
    )

    async def _mock(auth_header: str) -> FeedbackLevelsResponse:
        return sample

    monkeypatch.setattr(feedback_client, "get_feedback_levels", _mock)


def test_feedback_levels_endpoint(mock_feedback_levels):
    response = client.get(
        "/feedback/levels", headers={"Authorization": "Bearer token"}
    )
    assert response.status_code == 200
    assert response.json()["data"][0]["employeeId"] == "emp1"


@pytest.fixture
def http_client():
    return TestClient(app)


@pytest.fixture
def tools(http_client):
    return create_langchain_tools(
        "http://testserver", lambda: "Bearer token", client=http_client
    )


def test_add_feedback_tool(mock_add_feedback, tools):
    tool = next(t for t in tools if t.name == "add_feedback")
    payload = {
        "nextFollowUpDate": "2025-05-01",
        "employeeId": "emp1",
        "description": "Great work",
        "outcome": "Positive",
        "stars": 5,
        "type": "appreciation",
        "year": 2025,
        "month": 5,
    }
    result = tool.invoke(payload)
    assert result["data"]["id"] == "fb1"


def test_rm_feedbacks_tool(mock_rm_feedbacks, tools):
    tool = next(t for t in tools if t.name == "get_rm_feedbacks")
    result = tool.invoke({"id": "emp1"})
    assert result["data"][0]["id"] == "1"


def test_feedback_levels_tool(mock_feedback_levels, tools):
    tool = next(t for t in tools if t.name == "get_feedback_levels")
    result = tool.invoke({})
    assert result["data"][0]["employeeId"] == "emp1"
