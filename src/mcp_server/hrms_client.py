import os

import httpx

from .models import HolidaysResponse, LeavesResponse


class HRMSClient:
    """Client for interacting with the HRMS portal API."""

    def __init__(self, base_url: str | None = None, timeout: float = 10.0) -> None:
        self.base_url = base_url or os.getenv(
            "HRMS_API_BASE_URL", "https://devxnet2api.cubastion.net/api/v2"
        )
        self.timeout = timeout

    async def get_holidays(self, year: int) -> HolidaysResponse:
        """Retrieve holiday information for the given year."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/app/employees/holidays", params={"year": year}
            )
            response.raise_for_status()
            return HolidaysResponse.model_validate(response.json())

    async def get_leaves(self, fy_id: str) -> LeavesResponse:
        """Retrieve leave entries for the specified financial year id."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/attendance/leaves/my-leaves", params={"fyId": fy_id}
            )
            response.raise_for_status()
            return LeavesResponse.model_validate(response.json())
