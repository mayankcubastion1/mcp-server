
from __future__ import annotations
from typing import Callable, List, Optional
import httpx
from pydantic import BaseModel
from langchain_core.tools import StructuredTool
from ..tools.base import ToolSpec

class Empty(BaseModel): pass

FEEDBACK_DOMAINS = [
    "Performance", "Collaboration", "Communication", "Ownership", "Learning", "Leadership"
]

def create_tool_specs(base_url: str, auth_header_getter: Callable[[], str], client: Optional[httpx.Client] = None) -> List[ToolSpec]:
    http_client = client or httpx.Client(base_url=base_url, timeout=20.0)

    def _get_feedback_process() -> dict:
        # Replace with HRMS-driven config if available
        return {"domains": FEEDBACK_DOMAINS}

    return [
        ToolSpec("get_feedback_process", "List allowed feedback domains.", Empty, _get_feedback_process),
    ]

def create_langchain_tools(base_url: str, auth_header_getter: Callable[[], str], client: Optional[httpx.Client] = None):
    specs = create_tool_specs(base_url, auth_header_getter, client)
    return [StructuredTool.from_function(func=s.func, name=s.name, description=s.description, args_schema=s.args_schema) for s in specs]
