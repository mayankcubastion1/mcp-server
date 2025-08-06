from fastapi import FastAPI
from dotenv import load_dotenv
from .attendance.router import router as attendance_router
from .feedback.router import router as feedback_router
from .leaves.router import router as leaves_router, client as client
from .miscellaneous.router import router as misc_router
from .tickets.router import router as tickets_router
from .team_management.router import router as team_management_router

app = FastAPI(title="MCP Server")

load_dotenv()

# Core routes
app.include_router(misc_router)
app.include_router(leaves_router)

# Placeholder routers for future expansion
app.include_router(attendance_router)
app.include_router(feedback_router)
app.include_router(tickets_router)
app.include_router(team_management_router)
