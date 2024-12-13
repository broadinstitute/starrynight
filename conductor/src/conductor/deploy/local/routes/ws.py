"""Websocket routes."""

import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from conductor.handlers.run import fetch_run_log

ws_router = APIRouter(prefix="/ws", tags=["websocket"])


class ConnectionManager:
    """Manages a collection of active WebSocket connections.

    Attributes
    ----------
    active_connections : list[WebSocket]
        The list of currently active WebSocket connections.

    """

    def __init__(self) -> None:
        """Initialize an empty connection manager."""
        self.active_connections: list[WebSocket] = []
        self.log_read_map: dict[WebSocket, list[str]] = {}

    async def connect(self, websocket: WebSocket) -> None:
        """Establish a new WebSocket connection.

        Parameters
        ----------
        websocket : WebSocket
            The WebSocket object to establish a connection with.

        Notes
        -----
        This method accepts the incoming connection and adds it to active connections.

        """
        await websocket.accept()
        self.active_connections.append(websocket)
        self.log_read_map[websocket] = []

    def disconnect(self, websocket: WebSocket) -> None:
        """Remove an existing WebSocket connection.

        Parameters
        ----------
        websocket : WebSocket
            The WebSocket object to remove from the list of active connections.

        Notes
        -----
        This method removes the specified WebSocket connection from active connections.

        """
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket) -> None:
        """Send a personal message to a specific WebSocket client.

        Parameters
        ----------
        message : str
            The text message to be sent to the client.
        websocket : WebSocket
            The WebSocket object representing the target client connection.

        Notes
        -----
        This method sends the specified text message to the specified client.

        """
        await websocket.send_text(message)

    async def broadcast(self, message: str) -> None:
        """Send a message to all active WebSocket clients.

        Parameters
        ----------
        message : str
            The text message to be sent to all connected clients.

        Notes
        -----
        This method sends the specified text message to all currently active clients.

        """
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


class LogMessage(BaseModel):
    """Log message model.

    Attributes
    ----------
    message :  Message

    """

    message: str


@ws_router.websocket("/run/log/{run_id}")
async def ws_run_log(ws: WebSocket, run_id: int) -> None:
    """Stream run log handler."""
    await manager.connect(ws)
    try:
        while True:
            await asyncio.sleep(3)
            try:
                log = fetch_run_log(ws.state.db_session, run_id)
                diff = list(set(log) - set(manager.log_read_map[ws]))
                if diff != []:
                    manager.log_read_map[ws] = log
                    message = LogMessage(message="\n".join(log))
                    await manager.send_personal_message(message.model_dump_json(), ws)
            except Exception:
                log = ["Unable to fetch log."]
                message = LogMessage(message="\n".join(log))
                await manager.send_personal_message(message.model_dump_json(), ws)
    except WebSocketDisconnect:
        manager.disconnect(ws)
