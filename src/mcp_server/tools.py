from __future__ import annotations

"""LangChain tools for interacting with the MCP server endpoints."""

from typing import Callable, List, Optional

import httpx
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from .models import ApplyLeaveRequest


class HolidaysInput(BaseModel):
    """Input schema for the get_holidays tool."""

    year: int = Field(..., description="Year for which to fetch holidays")


class LeavesInput(BaseModel):
    """Input schema for the get_leaves tool."""

    fyId: str = Field(..., description="Financial year identifier")


def create_hrms_tools(
    base_url: str,
    auth_header_getter: Callable[[], str],
    client: Optional[httpx.Client] = None,
) -> List[StructuredTool]:
    """Create LangChain tools wrapping the MCP server endpoints.

    Parameters
    ----------
    base_url:
        Base URL of the running MCP server (e.g. ``"http://localhost:8000"``).
    auth_header_getter:
        Callable that returns the value for the ``Authorization`` header.
    client:
        Optional ``httpx.Client`` instance.  If omitted, a new client will be
        created using the given ``base_url``.
    """

    http_client = client or httpx.Client(base_url=base_url)

    def _get_holidays(year: int) -> dict:
        """Fetch holidays for the provided year."""

        response = http_client.get(
            "/holidays",
            params={"year": year},
            headers={"Authorization": auth_header_getter()},
        )
        response.raise_for_status()
        return response.json()

    def _get_leaves(fyId: str) -> dict:
        """Fetch leave records for the given financial year id."""

        response = http_client.get(
            "/leaves",
            params={"fyId": fyId},
            headers={"Authorization": auth_header_getter()},
        )
        response.raise_for_status()
        return response.json()

    def _apply_leave(**payload: dict) -> dict:
        """Apply for a leave or comp-off."""

        req = ApplyLeaveRequest(**payload)
        response = http_client.post(
            "/leaves/apply",
            json=req.model_dump(mode="json"),
            headers={"Authorization": auth_header_getter()},
        )
        response.raise_for_status()
        return response.json()

    holidays_tool = StructuredTool.from_function(
        func=_get_holidays,
        name="get_holidays",
        description="Fetch holidays for the provided year.",
        args_schema=HolidaysInput,
    )

    leaves_tool = StructuredTool.from_function(
        func=_get_leaves,
        name="get_leaves",
        description="Fetch leave records for a financial year.",
        args_schema=LeavesInput,
    )

    apply_leave_tool = StructuredTool.from_function(
        func=_apply_leave,
        name="apply_leave",
        description="Apply for a leave or comp-off.",
        args_schema=ApplyLeaveRequest,
    )

    return [holidays_tool, leaves_tool, apply_leave_tool]
