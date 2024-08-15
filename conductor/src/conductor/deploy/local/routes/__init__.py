"""Local routes."""

from fastapi import FastAPI

from conductor.deploy.local.routes.project import project_router
from conductor.deploy.local.routes.status import status_router


def register_routes(app: FastAPI) -> None:
    """Register available routes with the app.

    Parameters
    ----------
    app : FastAPI
        FastAPI app.

    """
    app.include_router(status_router)
    app.include_router(project_router)
