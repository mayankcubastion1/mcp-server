# src/mcp_server/main.py
from fastapi import FastAPI, Request
from .mcp_runtime import build_mcp_server
from .auth_context import set_request_headers
from .compat_rest import router as compat_router
from .leaves.router import router as leaves_router, client as leaves_client
from .attendance.router import router as attendance_router, client as attendance_client
from .feedback.router import router as feedback_router, client as feedback_client
from .tickets.router import router as tickets_router, client as tickets_client
from .team_management.router import router as team_router, client as team_client
from .miscellaneous.router import router as misc_router, client as misc_client
from .referrals.router import router as referrals_router, client as referrals_client

app = FastAPI(title="XAgent HR MCP Host")

# Put headers into a contextvar so tools (or compat) can read them
@app.middleware("http")
async def _stash_headers(request: Request, call_next):
    # capture for both /mcp (real MCP) and /mcp-compat (Postman/curl shim)
    if request.url.path.startswith("/mcp") or request.url.path.startswith("/mcp-compat"):
        set_request_headers(dict(request.headers))
    return await call_next(request)

# Mount MCP server (streamable HTTP → HTTP → SSE)
mcp = build_mcp_server()
mounted = False
for method in ("streamable_http_app", "http_app", "sse_app"):
    mount = getattr(mcp, method, None)
    if callable(mount):
        app.mount("/mcp", mount())
        print(f"[mcp] Mounted {method} at /mcp")
        mounted = True
        break
if not mounted:
    raise RuntimeError("FastMCP has no HTTP/SSE mount; upgrade `mcp` package.")

# Register domain routers so endpoints like /holidays or /leaves exist
app.include_router(misc_router)
app.include_router(leaves_router)
app.include_router(attendance_router)
app.include_router(feedback_router)
app.include_router(tickets_router)
app.include_router(team_router)
app.include_router(referrals_router)

# Expose HRMS clients for tests to monkeypatch
client = leaves_client
# Others are available as attendance_client, feedback_client, tickets_client, team_client, misc_client, referrals_client

# Optional REST shim for Postman/curl sanity checks
app.include_router(compat_router)

# Optional: a quick health route
@app.get("/health")
def health():
    return {"ok": True}
