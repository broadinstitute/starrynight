"""Route handlers."""

from fastapi import FastAPI

from conductor.handlers.status import get_status


def register_routes(app: FastAPI) -> None:
    pass
