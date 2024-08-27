"""Database manager."""

# pyright: reportUnusedImport=false
# Import all the tables: required for BaseSQLModel to pickup tables for DDL

from functools import partial

from fastapi import Request, WebSocket
from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session

from conductor.models.base import BaseSQLModel
from conductor.models.job import Job  # noqa: F401
from conductor.models.project import Project  # noqa: F401
from conductor.models.run import Run  # noqa: F401
from conductor.models.step import Step  # noqa: F401


def get_db_session(db_uri: str) -> Session:
    """Get db session."""
    return Session(create_engine(db_uri, echo=True))


def add_db_session_to_req(db_uri: str, request: Request) -> None:
    """Add db session to request state.

    Parameters
    ----------
    db_uri : str
        Databse URI
    request : Request
        FastAPI request.

    """
    request.state.db_session = partial(get_db_session, db_uri)


def add_db_session_to_ws(db_uri: str, websocket: WebSocket) -> None:
    """Add db session to request state.

    Parameters
    ----------
    db_uri : str
        Databse URI
    websocket : WebSocket
        FastAPI websocket.

    """
    websocket.state.db_session = partial(get_db_session, db_uri)


def create_tables(db_uri: str) -> None:
    """Create all tables."""
    if "sqlite" in db_uri:
        event.listen(
            Engine, "connect", lambda c, _: c.execute("pragma foreign_keys=on")
        )
    with create_engine(db_uri, echo=True).begin() as conn:
        # BaseSQLModel.metadata.drop_all(conn)
        BaseSQLModel.metadata.create_all(conn)
