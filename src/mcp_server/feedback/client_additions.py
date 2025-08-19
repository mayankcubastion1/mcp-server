
import httpx

class FeedbackClient:  # merge into your existing class
    async def feedback_levels(self, auth_header: str) -> dict:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.get(
                f"{self.base_url}/api/v2/app/employeeNotes/feedbackLevels",
                headers={"Authorization": auth_header},
            )
            r.raise_for_status()
            return r.json()

    async def generic_notes(self, id: str, tab: str, auth_header: str) -> dict:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.get(
                f"{self.base_url}/api/v2/app/employeeNotes/genericNotes",
                params={"id": id, "tab": tab},
                headers={"Authorization": auth_header},
            )
            r.raise_for_status()
            return r.json()

    async def add_generic_note(self, body: dict, auth_header: str) -> dict:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(
                f"{self.base_url}/api/v2/app/employeeNotes/addgenericNote",
                json=body,
                headers={"Authorization": auth_header},
            )
            r.raise_for_status()
            return r.json()
