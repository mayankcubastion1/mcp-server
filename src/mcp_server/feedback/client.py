import os

import httpx

from .models import AddFeedbackRequest, AddFeedbackResponse


class FeedbackClient:
    """Client for interacting with feedback related APIs."""

    def __init__(self, base_url: str | None = None, timeout: float = 10.0) -> None:
        self.base_url = base_url or os.getenv("HRMS_API_BASE_URL")
        if not self.base_url:
            raise RuntimeError("HRMS_API_BASE_URL is not configured")
        self.timeout = timeout

    async def add_feedback(
        self, payload: AddFeedbackRequest, auth_header: str
    ) -> AddFeedbackResponse:
        """Submit feedback for a team member."""

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/app/employeeNotes/addgenericNote",
                json=payload.model_dump(),
                headers={"Authorization": auth_header},
            )
            response.raise_for_status()
            return AddFeedbackResponse.model_validate(response.json())
