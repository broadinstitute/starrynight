"""Local status route."""

from fastapi import APIRouter

from conductor.handlers.status import get_status

status_router = APIRouter()


@status_router.get("/status", tags=["status"])
async def local_get_status() -> str:
    """Local route for get status."""
    return get_status()
