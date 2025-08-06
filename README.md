# MCP Server

This repository contains a [Model Context Protocol (MCP)] server exposing selected HRMS portal APIs over HTTP so they can be safely consumed by LLM and chatbot applications.

## Features

- **Health check** endpoint at `/health`.
- **Holiday data** proxy at `/holidays?year=YYYY` forwarding to the HRMS `app/employees/holidays` API.
- **Leave records** proxy at `/leaves?fyId=<financial_year_id>` forwarding to the HRMS `attendance/leaves/my-leaves` API.
- **Apply leave** proxy at `/leaves/apply` forwarding POST requests to the HRMS `attendance/leaves/apply` API.
- All HRMS calls transparently forward the incoming `Authorization: Bearer <token>` header.
- Built with [FastAPI](https://fastapi.tiangolo.com/) and packaged using Docker.

## Configuration

Create a `.env` file (see `.env.example`) or set environment variables:

- `HRMS_API_BASE_URL` – base URL of the HRMS portal APIs (e.g. `https://devxnet2api.cubastion.net/api/v2`).

Every request to the MCP server **must** include a valid `Authorization` header containing the user's bearer token, which is forwarded unchanged to the HRMS APIs.

## Development

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application locally:

```bash
uvicorn mcp_server.main:app --reload
```

Example requests (replace `$TOKEN` with the user's bearer token):

```bash
curl 'http://localhost:8000/holidays?year=2025' -H "Authorization: Bearer $TOKEN"
curl 'http://localhost:8000/leaves?fyId=roxq0g78pis7ia9' -H "Authorization: Bearer $TOKEN"
curl -X POST 'http://localhost:8000/leaves/apply' \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"type":"Debit","category":"Leave","leaveCount":2,"leaveDate":"2025-08-24","comments":"Not feeling well","status":"Pending Approval"}'
```

## Testing

The repository includes unit tests under `tests/`:

- `test_health.py`
- `test_holidays.py`
- `test_leaves.py`
- `test_apply_leave.py`

Run all tests with:

```bash
pytest
```

## Docker

Build the container image:

```bash
docker build -t mcp-server .
```

Run the server in Docker:

```bash
docker run -p 8000:8000 mcp-server
```

The service will be available at `http://localhost:8000`.

## Project structure

APIs and tools are organised by domain under the `mcp_server` package.  At the
moment only the **leaves** APIs are implemented, but empty packages exist for
future `feedback`, `tickets`, `attendance`, `misc` and `team_management`
domains.  Each domain contains its own models, FastAPI routes and optional tool
wrappers.

To add a new endpoint to a domain:

1. **Define Pydantic models** in the domain's `models.py`.
2. **Add client logic** in `client.py` for calling the upstream HRMS API.
3. **Expose the endpoint** via an `APIRouter` in `api.py` and include the router
   in `main.py`.
4. **Document the endpoint** in this README and add a corresponding test under
   `tests/` that patches the new client method.
5. **Run `pytest`** before committing to verify everything works.

## Using from agent frameworks

The leaves package provides generic callables as well as LangChain-compatible
wrappers so you can use these APIs from any agent framework including
LangGraph and future LangChain releases:

```python
from mcp_server.leaves.tools import (
    create_callables,
    create_structured_tools,
)

# Framework-agnostic Python callables
funcs = create_callables(
    base_url="http://localhost:8000",
    auth_header_getter=lambda: "Bearer <token>",
)

# Optional: deprecated LangChain StructuredTool wrappers
structured_tools = create_structured_tools(
    base_url="http://localhost:8000",
    auth_header_getter=lambda: "Bearer <token>",
)
```

`StructuredTool` is being deprecated in the LangChain ecosystem, but it remains
available here for backwards compatibility.  The simple callables can be
wrapped by any agentic AI framework.
