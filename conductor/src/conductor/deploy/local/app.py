"""Local app deployment."""

from functools import partial

from fastapi import Depends, FastAPI
from pydantic import BaseModel

from conductor.database import add_db_session_to_req, create_tables
from conductor.deploy.local.routes import register_routes


class AppConfig(BaseModel):
    """Application configuration.

    Attributes
    ----------
    db_uri : Database URI.
    name : Name of the Application.

    """

    db_uri: str
    name: str = "StarryNight"


def create_app(app_config: AppConfig) -> FastAPI:
    """Create fastapi app.

    Parameters
    ----------
    app_config : AppConfig
        Application configuration.

    Returns
    -------
    FastAPI
        Fastapi configured app.

    """
    app = FastAPI(
        title=app_config.name,
        dependencies=[Depends(partial(add_db_session_to_req, app_config.db_uri))],
    )
    register_routes(app)
    create_tables(db_uri=app_config.db_uri)
    return app
