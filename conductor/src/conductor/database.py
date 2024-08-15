"""Database manager."""

# pyright: reportUnusedImport=false

from functools import partial

from fastapi import Request
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from conductor.models.base import BaseSQLModel

# Import all the tables: required for BaseSQLModel to pickup tables for DDL
from conductor.models.project import Project  # noqa: F401
from conductor.models.step import Step  # noqa: F401


def get_db_session(db_uri: str) -> Session:
    """Get db session."""
    return Session(create_engine(db_uri, echo=True))


def add_db_session_to_req(db_uri: str, request: Request) -> None:
    """Add db session to request state.

    Parameters
    ----------
    request : Request
        FastAPI request.
    db_uri : str
        Databse URI

    """
    request.state.db_session = partial(get_db_session, db_uri)


def create_tables(db_uri: str) -> None:
    """Create all tables."""
    with create_engine(db_uri, echo=True).begin() as conn:
        BaseSQLModel.metadata.create_all(conn)
