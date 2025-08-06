import os
from dotenv import load_dotenv
import httpx

from .models import AttendanceResponse

load_dotenv()

class AttendanceClient:
    """Client for interacting with attendance related APIs."""

    def __init__(self, base_url: str | None = None, timeout: float = 10.0) -> None:
        self.base_url = base_url or os.getenv("HRMS_API_BASE_URL")
        if not self.base_url:
            raise RuntimeError("HRMS_API_BASE_URL is not configured")
        self.timeout = timeout

    async def get_my_attendance(
        self, year: int, month: int, auth_header: str
    ) -> AttendanceResponse:
        """Retrieve attendance records for a specific year and month."""

        payload = {
            "name": "My_Attendance",
            "index": "attendances",
            "page": 1,
            "pageSize": 30,
            "searchString": "",
            "sort": {"keyName": "", "order": ""},
            "filters": [
                {"keyName": "year", "value": str(year), "operator": "eq"},
                {
                    "keyName": "month",
                    "value": f"{month:02d}",
                    "operator": "eq",
                },
            ],
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/elastic/es/search/My_Attendance",
                json=payload,
                headers={"Authorization": auth_header},
            )
            response.raise_for_status()
            return AttendanceResponse.model_validate(response.json())
