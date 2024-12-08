from datetime import datetime, timezone
from typing import Optional
from bson import ObjectId
from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect
from app.model.session_data import SessionData
from app.service.websocket_service import WebsocketService
from app.utils.shared_state import active_connections
from app.config.db_config import mongodb

websocket_route = APIRouter()

@websocket_route.websocket("/ws/session")
async def websocket_session(
    websocket: WebSocket,
    domain_name: str = Query(...),
    user_id: str = Query(...)
):
    """
    WebSocket endpoint that tracks active users by domain.
    
    Args:
        websocket (WebSocket): The WebSocket connection object.
        domain_name (str): Domain name passed as a query parameter.
        user_id (str): User ID passed as a query parameter.
    """
    if not domain_name or not user_id:
        raise HTTPException(status_code=400, detail="Missing domain_name or user_id")

    # Accept the WebSocket connection
    await websocket.accept()

    # Add the user_id to the active_connections dictionary for the specific domain
    if domain_name not in active_connections:
        active_connections[domain_name] = []
    if user_id not in active_connections[domain_name]:
        active_connections[domain_name].append(user_id)

    print(f"Connected: {domain_name} - {user_id}")
    print(f"Active connections: {active_connections}")

    try:
        while True:
            data = await websocket.receive_json()
            session_data =  SessionData(**data)
            await WebsocketService.handle_session_data(session_data)
            print(f"Received message from {user_id} on {domain_name}: {data}")

    except WebSocketDisconnect:
        # Remove user from the active connections on disconnect
        if domain_name in active_connections and user_id in active_connections[domain_name]:
            active_connections[domain_name].remove(user_id)
            if not active_connections[domain_name]:  # Remove domain if no users are left
                del active_connections[domain_name]

        print(f"Disconnected: {domain_name} - {user_id}")
        print(f"Remaining connections: {active_connections}")

