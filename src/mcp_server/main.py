from fastapi import FastAPI

from .leaves.api import router as leaves_router

app = FastAPI(title="MCP Server")
app.include_router(leaves_router)


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
