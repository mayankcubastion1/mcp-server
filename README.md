# MCP Server

This repository contains a [Model Context Protocol (MCP)] server exposing selected HRMS portal APIs over HTTP so they can be safely consumed by LLM and chatbot applications.

## Features

- **Health check** endpoint at `/health`.
- **Holiday data** proxy at `/holidays?year=YYYY` forwarding to the HRMS `app/employees/holidays` API.
- **Leave records** proxy at `/leaves?fyId=<financial_year_id>` forwarding to the HRMS `attendance/leaves/my-leaves` API.
- **Apply leave** proxy at `/leaves/apply` forwarding POST requests to the HRMS `attendance/leaves/apply` API.
- Built with [FastAPI](https://fastapi.tiangolo.com/) and packaged using Docker.

## Configuration

The HRMS base URL can be configured via the `HRMS_API_BASE_URL` environment variable. It defaults to `https://devxnet2api.cubastion.net/api/v2` which hosts the production APIs.

## Development

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application locally:

```bash
uvicorn mcp_server.main:app --reload
```

Example requests:

```bash
curl 'http://localhost:8000/holidays?year=2025'
curl 'http://localhost:8000/leaves?fyId=roxq0g78pis7ia9'
curl -X POST 'http://localhost:8000/leaves/apply' \
  -H 'Content-Type: application/json' \
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
docker run -p 8000:8000 -e HRMS_API_BASE_URL=https://devxnet2api.cubastion.net/api/v2 mcp-server
```

The service will be available at `http://localhost:8000`.

## Adding new APIs

1. **Create a client method** in `hrms_client.py` that calls the desired HRMS endpoint and returns a typed response model.
2. **Expose a route** in `main.py` that invokes the client method and validates inputs.
3. **Document the endpoint** in this README and add unit tests under `tests/`.
4. **Run `pytest`** to ensure the new integration works before committing.

This workflow keeps the server maintainable while allowing new HRMS capabilities to be surfaced quickly.
