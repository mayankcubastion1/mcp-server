from __future__ import annotations

"""Utilities for calling leave-related MCP endpoints.

This module exposes plain Python callables that can be used by any agentic AI
framework.  It also provides helper functions to convert them into LangChain
`StructuredTool` instances for backwards compatibility.  ``StructuredTool`` is
being deprecated in the LangChain ecosystem, but we keep it here as an example
and for frameworks that still rely on it.
"""

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


def create_callables(
    base_url: str,
    auth_header_getter: Callable[[], str],
    client: Optional[httpx.Client] = None,
) -> List[Callable]:
    """Return simple callables for each leave-related endpoint."""

    http_client = client or httpx.Client(base_url=base_url)

    def get_holidays(year: int) -> dict:
        """Fetch holidays for the provided year."""

        response = http_client.get(
            "/holidays",
            params={"year": year},
            headers={"Authorization": auth_header_getter()},
        )
        response.raise_for_status()
        return response.json()

    def get_leaves(fyId: str) -> dict:
        """Fetch leave records for the given financial year id."""

        response = http_client.get(
            "/leaves",
            params={"fyId": fyId},
            headers={"Authorization": auth_header_getter()},
        )
        response.raise_for_status()
        return response.json()

    def apply_leave(**payload: dict) -> dict:
        """Apply for a leave or comp-off."""

        req = ApplyLeaveRequest(**payload)
        response = http_client.post(
            "/leaves/apply",
            json=req.model_dump(mode="json"),
            headers={"Authorization": auth_header_getter()},
        )
        response.raise_for_status()
        return response.json()

    return [get_holidays, get_leaves, apply_leave]


def create_structured_tools(
    base_url: str,
    auth_header_getter: Callable[[], str],
    client: Optional[httpx.Client] = None,
) -> List[StructuredTool]:
    """Create LangChain ``StructuredTool`` objects for the leave callables."""

    callables = create_callables(base_url, auth_header_getter, client)
    get_holidays, get_leaves, apply_leave = callables

    holidays_tool = StructuredTool.from_function(
        func=get_holidays,
        name="get_holidays",
        description="Fetch holidays for the provided year.",
        args_schema=HolidaysInput,
    )

    leaves_tool = StructuredTool.from_function(
        func=get_leaves,
        name="get_leaves",
        description="Fetch leave records for a financial year.",
        args_schema=LeavesInput,
    )

    apply_leave_tool = StructuredTool.from_function(
        func=apply_leave,
        name="apply_leave",
        description="Apply for a leave or comp-off.",
        args_schema=ApplyLeaveRequest,
    )

    return [holidays_tool, leaves_tool, apply_leave_tool]
