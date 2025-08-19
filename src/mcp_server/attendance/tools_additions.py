
from __future__ import annotations
from typing import Callable, List, Optional
import httpx
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool
from ..tools.base import ToolSpec

class ApplyCompOffInput(BaseModel):
    # Mirror your Postman payload; add/adjust fields accordingly
    workDate: str | None = Field(None, description="YYYY-MM-DD if required by HRMS")
    hoursWorked: float | None = None
    reason: str | None = None

class ApprovalPayload(BaseModel):
    payload: dict

def create_tool_specs(base_url: str, auth_header_getter: Callable[[], str], client: Optional[httpx.Client] = None) -> List[ToolSpec]:
    http_client = client or httpx.Client(base_url=base_url, timeout=20.0)

    # Existing attendance tools should already be defined.
    # We append new ones below:

    def _apply_comp_off(**payload) -> dict:
        r = http_client.post(
            "/api/v2/attendance/leaves/apply/comp-off",
            json=payload,
            headers={"Authorization": auth_header_getter()},
        )
        r.raise_for_status()
        return r.json()

    def _approve_leave(payload: dict) -> dict:
        r = http_client.put(
            "/api/v2/attendance/leaves/employee/approval",
            json=payload,
            headers={"Authorization": auth_header_getter()},
        )
        r.raise_for_status()
        return r.json()

    def _approve_comp_off(payload: dict) -> dict:
        r = http_client.post(
            "/api/v2/attendance/leaves/approval/comp-off",
            json=payload,
            headers={"Authorization": auth_header_getter()},
        )
        r.raise_for_status()
        return r.json()

    return [
        ToolSpec("apply_comp_off", "Apply for a Comp-Off.", ApplyCompOffInput, _apply_comp_off),
        ToolSpec("approve_leave", "Approve/Reject a leave request.", ApprovalPayload, _approve_leave),
        ToolSpec("approve_comp_off", "Approve/Reject a comp-off request.", ApprovalPayload, _approve_comp_off),
    ]

def create_langchain_tools(base_url: str, auth_header_getter: Callable[[], str], client: Optional[httpx.Client] = None):
    specs = create_tool_specs(base_url, auth_header_getter, client)
    return [StructuredTool.from_function(func=s.func, name=s.name, description=s.description, args_schema=s.args_schema) for s in specs]
