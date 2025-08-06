from __future__ import annotations

"""Tools for interacting with feedback endpoints."""

from typing import Callable, List, Optional

import httpx
from langchain_core.tools import StructuredTool
from pydantic import BaseModel

from ..tools.base import ToolSpec
from .models import AddFeedbackRequest


def create_tool_specs(
    base_url: str,
    auth_header_getter: Callable[[], str],
    client: Optional[httpx.Client] = None,
) -> List[ToolSpec]:
    """Create tool specifications for feedback APIs."""

    http_client = client or httpx.Client(base_url=base_url)

    def _add_feedback(**payload: dict) -> dict:
        req = AddFeedbackRequest(**payload)
        response = http_client.post(
            "/feedback/add",
            json=req.model_dump(mode="json"),
            headers={"Authorization": auth_header_getter()},
        )
        response.raise_for_status()
        return response.json()

    return [
        ToolSpec(
            name="add_feedback",
            description="Submit feedback for a team member.",
            args_schema=AddFeedbackRequest,
            func=_add_feedback,
        )
    ]


def create_langchain_tools(
    base_url: str,
    auth_header_getter: Callable[[], str],
    client: Optional[httpx.Client] = None,
) -> List[StructuredTool]:
    """Create LangChain StructuredTool instances for feedback APIs."""

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
