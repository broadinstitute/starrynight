"""Local app deployment."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from conductor.database import (
    create_tables,
)
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
        separate_input_output_schemas=False,
    )
    origins = ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_routes(app, app_config)
    create_tables(db_uri=app_config.db_uri)
    return app
