
from fastapi import APIRouter, Header, HTTPException, Query, Body
import httpx
from .client import FeedbackClient

router = APIRouter(prefix="/api/v2/app/employeeNotes")
client = FeedbackClient()

@router.get("/feedbackLevels")
async def feedback_levels(authorization: str = Header(...)) -> dict:
    try:
        return await client.feedback_levels(authorization)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

@router.get("/genericNotes")
async def generic_notes(id: str = Query(""), tab: str = Query("RMFeedbacks"), authorization: str = Header(...)) -> dict:
    try:
        return await client.generic_notes(id, tab, authorization)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

@router.post("/addgenericNote")
async def add_generic_note(body: dict = Body(...), authorization: str = Header(...)) -> dict:
    try:
        return await client.add_generic_note(body, authorization)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
