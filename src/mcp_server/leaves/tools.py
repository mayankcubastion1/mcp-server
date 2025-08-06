from __future__ import annotations

"""Tools for interacting with leave-related MCP server endpoints."""

from typing import Callable, List, Optional

import httpx
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from ..tools.base import ToolSpec
from .models import ApplyLeaveRequest


class HolidaysInput(BaseModel):
    """Input schema for the get_holidays tool."""

    year: int = Field(..., description="Year for which to fetch holidays")


class LeavesInput(BaseModel):
    """Input schema for the get_leaves tool."""

    fyId: str = Field(..., description="Financial year identifier")


def create_tool_specs(
    base_url: str,
    auth_header_getter: Callable[[], str],
    client: Optional[httpx.Client] = None,
) -> List[ToolSpec]:
    """Create framework-agnostic tool specifications for leave APIs."""

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

    return [
        ToolSpec(
            name="get_holidays",
            description="Fetch holidays for the provided year.",
            args_schema=HolidaysInput,
            func=_get_holidays,
        ),
        ToolSpec(
            name="get_leaves",
            description="Fetch leave records for a financial year.",
            args_schema=LeavesInput,
            func=_get_leaves,
        ),
        ToolSpec(
            name="apply_leave",
            description="Apply for a leave or comp-off.",
            args_schema=ApplyLeaveRequest,
            func=_apply_leave,
        ),
    ]


def create_langchain_tools(
    base_url: str,
    auth_header_getter: Callable[[], str],
    client: Optional[httpx.Client] = None,
) -> List[StructuredTool]:
    """Create LangChain StructuredTool instances for leave APIs."""

    specs = create_tool_specs(base_url, auth_header_getter, client)
    return [
        StructuredTool.from_function(
            func=spec.func,
            name=spec.name,
            description=spec.description,
            args_schema=spec.args_schema,
        )
        for spec in specs
    ]
