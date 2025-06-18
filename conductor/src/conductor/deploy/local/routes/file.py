"""File streaming routes."""

from cloudpathlib import AnyPath
from fastapi import APIRouter, UploadFile
from fastapi.responses import FileResponse

file_router = APIRouter(prefix="/file", tags=["file"])


@file_router.get("/")
async def get_file(file_path: str) -> FileResponse:
    """Get file."""
    return FileResponse(AnyPath(file_path).absolute().__str__())


@file_router.post("/")
async def post_file(file_path: str, file: UploadFile) -> dict:
    """Post file."""
    # TODO: Hack for now. Solve it properly later
    AnyPath(file_path).write_bytes(file.file.read())
    return {"msg": "File uploaded successfully"}
