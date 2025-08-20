# MCP Server

This project exposes selected HRMS APIs through a [Model Context Protocol (MCP)] host built with FastAPI.  It mounts the MCP server at `/mcp` and provides a REST compatibility shim at `/mcp-compat` for simple HTTP clients.  All incoming requests must include an `Authorization: Bearer <token>` header, which is forwarded to the HRMS backend.

## Architecture

`main.py` initialises the FastAPI app, stores request headers in a context variable so tools can access them, mounts the MCP server, then registers routers for each HRMS domain (leaves, attendance, feedback, tickets, team management, miscellaneous and referrals).  The miscellaneous router also supplies the `/health` endpoint.

## Requirements

- Python 3.12+
- Environment variables:
  - `HRMS_API_BASE_URL` – base URL of the HRMS portal APIs.
  - `SERVER_EXTERNAL_BASE_URL` – optional external base URL used when generating MCP tool links.

Install dependencies:

```bash
pip install -r requirements.txt
```

## Running locally

Set the base URL and start the server:

```bash
export HRMS_API_BASE_URL="https://devxnet2api.cubastion.net/api/v2"
PYTHONPATH=src uvicorn mcp_server.main:app --reload
```

The service listens on `http://localhost:8000`.  The MCP host is served from `/mcp` and the REST shim from `/mcp-compat`.  A health check is available at `/health`.

### Example requests

```bash
curl -H "Authorization: Bearer $TOKEN" 'http://localhost:8000/holidays?year=2025'
curl -H "Authorization: Bearer $TOKEN" 'http://localhost:8000/leaves?fyId=roxq0g78pis7ia9'
curl -X POST -H 'Authorization: Bearer $TOKEN' -H 'Content-Type: application/json' \
  -d '{"type":"Debit","category":"Leave","leaveCount":2,"leaveDate":"2025-08-24","comments":"Not feeling well","status":"Pending Approval"}' \
  'http://localhost:8000/leaves/apply'
curl -X POST -H 'Authorization: Bearer $TOKEN' -H 'Content-Type: application/json' \
  -d '{"type":"Credit","category":"Comp-Off","leaveCount":1,"leaveDate":"2025-06-01","comments":"worked upon agentic ai","status":"Pending Approval"}' \
  'http://localhost:8000/leaves/apply/comp-off'
```

## API overview

### Miscellaneous
- `GET /health` – basic health check.
- `GET /financial-years` – list financial years for the current employee.
- `GET /employees/{employee_id}` – retrieve an employee profile.

### Leaves
- `GET /holidays?year=YYYY` – retrieve holiday data.
- `GET /leaves?fyId=<id>` – list leave entries for a financial year.
- `POST /leaves/apply` – apply for a leave or comp‑off.
- `POST /leaves/apply/comp-off` – apply for a comp‑off credit.

### Attendance
- `POST /attendance/my-attendance` – monthly attendance records.
- `GET /api/v2/attendance/attendances/employee/attendance-date` – attendance for a specific date.
- `GET /api/v2/attendance/attendances/my-regularized-attendance` – regularised attendance entries.
- `POST /api/v2/attendance/attendances/regularisation/project` – submit an attendance regularisation request (supports file upload).
- `POST /api/v2/attendance/leaves/apply` – submit an attendance leave application.

### Feedback
- `POST /feedback/add` – submit feedback.
- `GET /feedback/rm-feedbacks` – view RM feedbacks.
- `GET /feedback/levels` – list feedback levels/users.

### Tickets
- `GET /tickets/my` – list tickets for the authenticated employee.
- `POST /tickets/draft` – create a draft ticket.
- `POST /tickets/submit` – submit a ticket.

### Team management
- `GET /team-management/ledger` – view a team member's leave/comp‑off ledger.

### Referrals
- `POST /api/v2/elastic/es/search/All_Openings` – search open positions.
- `POST /api/v2/hr/candidates/add` – add a referral candidate.
- `PUT /api/v2/hr/candidates/updateProfile` – upload a candidate résumé.
- `POST /api/v2/hr/applications` – create a referral application.

## MCP tool support

Every router also exposes ToolSpec definitions.  The server mounts these as MCP tools under `/mcp`, and a REST shim at `/mcp-compat` lists and invokes them.  Utilities in `mcp_server.tools` convert these ToolSpecs to frameworks such as LangChain:

```python
from mcp_server.tools import create_langchain_tools

tools = create_langchain_tools(
    base_url="http://localhost:8000",
    auth_header_getter=lambda: "Bearer <token>",
)
```

## Testing

Run the unit tests:

```bash
pytest
```

## Docker

```bash
docker build -t mcp-server .
docker run -p 8000:8000 -e HRMS_API_BASE_URL="https://devxnet2api.cubastion.net/api/v2" mcp-server
```

The service will be available at `http://localhost:8000`.
