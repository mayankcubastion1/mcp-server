from fastapi import APIRouter, Header, HTTPException
import httpx

from .client import FeedbackClient
from .models import AddFeedbackRequest, AddFeedbackResponse

router = APIRouter(prefix="/feedback")
client = FeedbackClient()


@router.post("/add", response_model=AddFeedbackResponse)
async def add_feedback(
    body: AddFeedbackRequest, authorization: str = Header(...)
) -> AddFeedbackResponse:
    """Submit feedback for a team member."""
    try:
        return await client.add_feedback(body, authorization)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
