
from __future__ import annotations
from typing import Callable, List, Optional, Dict, Any
import httpx
from pydantic import BaseModel
from langchain_core.tools import StructuredTool
from ..tools.base import ToolSpec

class Empty(BaseModel): pass

STATIC_CATEGORY2_OPTIONS: Dict[str, list[str]] = {
    # Fill with your real mapping
    "HR": ["ID Card", "Payroll", "Leave Policy", "Onboarding"],
    "IT": ["Laptop Issue", "Email/SSO", "Access Request", "Software Install"],
    "Admin": ["Stationery", "Travel Desk", "Cafeteria"],
}

def create_tool_specs(base_url: str, auth_header_getter: Callable[[], str], client: Optional[httpx.Client] = None) -> List[ToolSpec]:
    def _get_ticket_categories() -> Dict[str, Any]:
        return {"categories": STATIC_CATEGORY2_OPTIONS}
    return [ToolSpec("get_ticket_categories", "Department → sub-category map for tickets.", Empty, _get_ticket_categories)]

def create_langchain_tools(base_url: str, auth_header_getter: Callable[[], str], client: Optional[httpx.Client] = None):
    specs = create_tool_specs(base_url, auth_header_getter, client)
    return [StructuredTool.from_function(func=s.func, name=s.name, description=s.description, args_schema=s.args_schema) for s in specs]
