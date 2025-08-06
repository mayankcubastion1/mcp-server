from fastapi import FastAPI, Header, HTTPException, Query
import httpx

from .hrms_client import HRMSClient
from .models import (
    ApplyLeaveRequest,
    ApplyLeaveResponse,
    HolidaysResponse,
    LeavesResponse,
)

app = FastAPI(title="MCP Server")
client = HRMSClient()


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/holidays", response_model=HolidaysResponse)
async def holidays(
    year: int = Query(..., ge=1900, le=2100),
    authorization: str = Header(...),
) -> HolidaysResponse:
    """Retrieve holidays for a given year."""
    try:
        return await client.get_holidays(year, authorization)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/leaves", response_model=LeavesResponse)
async def leaves(
    fy_id: str = Query(..., alias="fyId"),
    authorization: str = Header(...),
) -> LeavesResponse:
    """Retrieve leave entries for the provided financial year identifier."""
    try:
        return await client.get_leaves(fy_id, authorization)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/leaves/apply", response_model=ApplyLeaveResponse)
async def apply_leave(
    body: ApplyLeaveRequest, authorization: str = Header(...)
) -> ApplyLeaveResponse:
    """Apply for a leave or comp-off."""
    try:
        return await client.apply_leave(body, authorization)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
