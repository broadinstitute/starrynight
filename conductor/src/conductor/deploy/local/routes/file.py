"""File streaming routes."""

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

file_router = APIRouter(prefix="/file", tags=["file"])


@file_router.get("/")
def get_file(file_path: str) -> FileResponse:
    """Get file."""
    return FileResponse(Path(file_path).absolute().__str__())
