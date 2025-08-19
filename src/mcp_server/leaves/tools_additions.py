
from __future__ import annotations
from typing import Callable, List, Optional, Dict, Any
import httpx
from datetime import datetime
from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool
from ..tools.base import ToolSpec

class WorkingDayInput(BaseModel):
    date: str  # YYYY-MM-DD

class LeaveBalanceRequest(BaseModel):
    leaveType: str
    requestedCount: int
    fyId: int | None = None

def create_tool_specs(base_url: str, auth_header_getter: Callable[[], str], client: Optional[httpx.Client] = None) -> List[ToolSpec]:
    http_client = client or httpx.Client(base_url=base_url, timeout=20.0)

    def _check_working_day(date: str) -> dict:
        year = int(date[:4])
        r = http_client.get("/holidays", params={"year": year}, headers={"Authorization": auth_header_getter()})
        r.raise_for_status()
        data = r.json()
        holidays = set()
        # Accept either {"data":[...]} or raw list
        rows = data.get("data", data)
        for h in rows:
            if (h.get("type") or "").upper() == "GH":
                holidays.add(h.get("holidayDate"))
        dt = datetime.strptime(date, "%Y-%m-%d")
        is_weekend = dt.weekday() >= 5
        is_gh = date in holidays
        return {"date": date, "isWorkingDay": (not is_weekend and not is_gh), "isWeekend": is_weekend, "isGeneralHoliday": is_gh}

    def _sum_balance_for_type(leaves: List[Dict[str, Any]], leave_type: str) -> Dict[str, int]:
        lt = leave_type.lower().strip()
        available = used = 0
        for row in leaves or []:
            t = (row.get("type") or row.get("leaveType") or "").lower().strip()
            if t == lt:
                available += int(row.get("available", 0))
                used      += int(row.get("used", 0))
        return {"available": available, "used": used}

    def _check_leave_balance(leaveType: str, requestedCount: int, fyId: int | None = None) -> dict:
        r = http_client.get("/leaves", params={"fyId": fyId} if fyId is not None else None, headers={"Authorization": auth_header_getter()})
        r.raise_for_status()
        data = r.json()
        leaves = data.get("leaves", data)
        summary = _sum_balance_for_type(leaves, leaveType)
        ok = summary["available"] >= int(requestedCount)
        return {"leaveType": leaveType, "requested": int(requestedCount), "available": summary["available"], "used": summary["used"], "sufficient": ok}

    return [
        ToolSpec("check_working_day", "Check if a date is a working day (not weekend, not GH).", WorkingDayInput, _check_working_day),
        ToolSpec("check_leave_balance", "Return available/used for a leave type and whether it covers the requested count.", LeaveBalanceRequest, _check_leave_balance),
    ]

def create_langchain_tools(base_url: str, auth_header_getter: Callable[[], str], client: Optional[httpx.Client] = None):
    specs = create_tool_specs(base_url, auth_header_getter, client)
    return [StructuredTool.from_function(func=s.func, name=s.name, description=s.description, args_schema=s.args_schema) for s in specs]
