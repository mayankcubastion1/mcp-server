
import httpx

class AttendanceClient:  # NOTE: merge these methods into your existing class
    async def apply_comp_off(self, payload: dict, auth_header: str) -> dict:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(
                f"{self.base_url}/api/v2/attendance/leaves/apply/comp-off",
                json=payload,
                headers={"Authorization": auth_header},
            )
            r.raise_for_status()
            return r.json()

    async def approve_leave(self, payload: dict, auth_header: str) -> dict:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.put(
                f"{self.base_url}/api/v2/attendance/leaves/employee/approval",
                json=payload,
                headers={"Authorization": auth_header},
            )
            r.raise_for_status()
            return r.json()

    async def approve_comp_off(self, payload: dict, auth_header: str) -> dict:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(
                f"{self.base_url}/api/v2/attendance/leaves/approval/comp-off",
                json=payload,
                headers={"Authorization": auth_header},
            )
            r.raise_for_status()
            return r.json()
