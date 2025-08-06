from __future__ import annotations

"""Tools for interacting with attendance-related endpoints."""

from typing import Callable, List, Optional

import httpx
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from ..tools.base import ToolSpec


class AttendanceInput(BaseModel):
    """Input schema for retrieving attendance."""

    year: int = Field(..., description="Target year")
    month: int = Field(..., ge=1, le=12, description="Target month")


def create_tool_specs(
    base_url: str,
    auth_header_getter: Callable[[], str],
    client: Optional[httpx.Client] = None,
) -> List[ToolSpec]:
    """Create tool specifications for attendance APIs."""

    http_client = client or httpx.Client(base_url=base_url)

    def _get_attendance(year: int, month: int) -> dict:
        response = http_client.post(
            "/attendance/my-attendance",
            params={"year": year, "month": month},
            headers={"Authorization": auth_header_getter()},
        )
        response.raise_for_status()
        return response.json()

    return [
        ToolSpec(
            name="get_attendance",
            description="Fetch attendance records for a given year and month.",
            args_schema=AttendanceInput,
            func=_get_attendance,
        )
    ]


def create_langchain_tools(
    base_url: str,
    auth_header_getter: Callable[[], str],
    client: Optional[httpx.Client] = None,
) -> List[StructuredTool]:
    """Create LangChain StructuredTool instances for attendance APIs."""

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
