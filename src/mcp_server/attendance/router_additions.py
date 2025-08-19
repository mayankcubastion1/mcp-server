
from fastapi import APIRouter, Header, HTTPException, Query, UploadFile, File, Form, Body
import httpx
from .client import AttendanceClient

router = APIRouter(prefix="/api/v2/attendance")
client = AttendanceClient()

@router.post("/leaves/apply/comp-off")
async def apply_comp_off(
    body: dict = Body(...),
    authorization: str = Header(...),
) -> dict:
    try:
        return await client.apply_comp_off(body, authorization)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

@router.put("/leaves/employee/approval")
async def approve_leave(
    body: dict = Body(...),
    authorization: str = Header(...),
) -> dict:
    try:
        return await client.approve_leave(body, authorization)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

@router.post("/leaves/approval/comp-off")
async def approve_comp_off(
    body: dict = Body(...),
    authorization: str = Header(...),
) -> dict:
    try:
        return await client.approve_comp_off(body, authorization)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
