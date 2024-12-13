"""Local routes."""

from functools import partial

from fastapi import Depends, FastAPI
from pydantic import BaseModel

from conductor.database import add_db_session_to_req, add_db_session_to_ws
from conductor.deploy.local.routes.file import file_router
from conductor.deploy.local.routes.job import job_router
from conductor.deploy.local.routes.project import project_router
from conductor.deploy.local.routes.run import run_router
from conductor.deploy.local.routes.status import status_router
from conductor.deploy.local.routes.step import step_router
from conductor.deploy.local.routes.ws import ws_router


def register_routes(app: FastAPI, app_config: BaseModel) -> None:
    """Register available routes with the app.

    Parameters
    ----------
    app : FastAPI
        FastAPI app.
    app_config : BaseModel
        FastAPI app config.

    """
    req_routers = [
        status_router,
        project_router,
        step_router,
        job_router,
        run_router,
        file_router,
    ]
    ws_routers = [ws_router]
    for router in req_routers:
        app.include_router(
            router,
            dependencies=[
                Depends(partial(add_db_session_to_req, app_config.db_uri)),  # pyright: ignore
            ],
        )
    for router in ws_routers:
        app.include_router(
            router,
            dependencies=[
                Depends(partial(add_db_session_to_ws, app_config.db_uri)),  # pyright: ignore
            ],
        )
