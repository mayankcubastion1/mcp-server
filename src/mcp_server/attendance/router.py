from fastapi import APIRouter, Header, HTTPException, Query
import httpx

from .client import AttendanceClient
from .models import AttendanceResponse

router = APIRouter(prefix="/attendance")
client = AttendanceClient()


@router.post("/my-attendance", response_model=AttendanceResponse)
async def my_attendance(
    year: int = Query(..., ge=1900, le=2100),
    month: int = Query(..., ge=1, le=12),
    authorization: str = Header(...),
) -> AttendanceResponse:
    """Retrieve attendance records for a specific year and month."""
    try:
        return await client.get_my_attendance(year, month, authorization)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
