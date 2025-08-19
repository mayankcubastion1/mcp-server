from __future__ import annotations
from fastapi import APIRouter, Body, HTTPException, Request
from typing import Any, Dict, List
from pydantic import BaseModel
import os
from .tool_registry import all_tool_specs
from .auth_context import set_request_headers, auth_header_getter

router = APIRouter(prefix="/mcp-compat", tags=["mcp-compat"])

def _specs(request: Request):
    # ensure per-request headers are available to tools
    set_request_headers(dict(request.headers))
    base = os.getenv("SERVER_EXTERNAL_BASE_URL", "http://localhost:8000").rstrip("/")
    return list(all_tool_specs(base, auth_header_getter))

class CallBody(BaseModel):
    name: str
    arguments: Dict[str, Any] | None = None

@router.get("/tools")
def list_tools(request: Request):
    out: List[Dict[str, Any]] = [{"name": "ping", "description": "health check", "args_schema": None}]
    for s in _specs(request):
        schema = None
        if getattr(s, "args_schema", None):
            try:
                schema = s.args_schema.model_json_schema()
            except Exception:
                schema = {"title": s.args_schema.__name__}
        out.append({"name": s.name, "description": s.description, "args_schema": schema})
    return {"tools": out}

@router.post("/call")
def call_tool(body: CallBody = Body(...), request: Request = None):
    # make sure headers from this HTTP request are visible to tools
    if request is not None:
        set_request_headers(dict(request.headers))
    if body.name == "ping":
        return {"result": "pong"}
    specs = _specs(request)
    by_name = {s.name: s for s in specs}
    if body.name not in by_name:
        raise HTTPException(status_code=404, detail=f"Tool '{body.name}' not found")
    spec = by_name[body.name]
    args = body.arguments or {}
    if getattr(spec, "args_schema", None):
        args = spec.args_schema(**args).model_dump()
    return {"result": spec.func(**args)}
