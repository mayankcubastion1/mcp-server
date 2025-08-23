"""Helpers to expose MCP server endpoints as AI agent tools."""

from typing import Callable, List, Optional

import httpx
from langchain_core.tools import StructuredTool

from .base import ToolSpec
from ..tools.attendance import tools as attendance_tools
from ..tools.feedback import tools as feedback_tools
from ..tools.leaves import tools as leaves_tools
from ..tools.miscellaneous import tools as misc_tools
from ..tools.team_management import tools as team_tools
from ..tools.tickets import tools as tickets_tools


def create_tool_specs(
    base_url: str,
    auth_header_getter: Callable[[], str],
    client: Optional[httpx.Client] = None,
) -> List[ToolSpec]:
    """Aggregate ToolSpec definitions from all API groups."""

    specs: List[ToolSpec] = []
    specs.extend(misc_tools.create_tool_specs(base_url, auth_header_getter, client))
    specs.extend(leaves_tools.create_tool_specs(base_url, auth_header_getter, client))
    specs.extend(attendance_tools.create_tool_specs(base_url, auth_header_getter, client))
    specs.extend(feedback_tools.create_tool_specs(base_url, auth_header_getter, client))
    specs.extend(tickets_tools.create_tool_specs(base_url, auth_header_getter, client))
    specs.extend(team_tools.create_tool_specs(base_url, auth_header_getter, client))
    return specs


def create_langchain_tools(
    base_url: str,
    auth_header_getter: Callable[[], str],
    client: Optional[httpx.Client] = None,
) -> List[StructuredTool]:
    """Return LangChain StructuredTools for all API groups."""

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

# Backwards compatibility for previous function name
create_hrms_tools = create_langchain_tools
