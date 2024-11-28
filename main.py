from datetime import datetime, timezone
from typing import Dict, List
from bson import ObjectId
from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import asynccontextmanager
from app.config.db_config import mongodb, MONGO_URI, DATABASE_NAME
from app.model.session_data import SessionData
from app.config.db_config import mongodb
from app.controller.user_controller import user_route
from app.controller.dashboard_controller import dashboard_route
from app.controller.admin_controller import admin_route

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(user_route, tags=["User"])
app.include_router(dashboard_route, tags=["Dashboard"])
app.include_router(admin_route, tags=["Admin"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    await mongodb.connect(MONGO_URI, DATABASE_NAME)  # Connect to MongoDB
    yield
    await mongodb.close()  # Disconnect from MongoDB


app.router.lifespan_context = lifespan

@app.get("/")
async def root():
    return {"message": "Hello, MongoDB connected successfully!"}


# WebSocket endpoint
active_connections: Dict[str,List[str]] = {}

@app.websocket("/ws/session")
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
    # Check for valid query parameters
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
            # Listen for messages from the client
            data = await websocket.receive_text()
            session_data =  SessionData(**data)
            await handle_session_data(session_data)
            print(f"Received message from {user_id} on {domain_name}: {data}")

    except WebSocketDisconnect:
        # Remove user from the active connections on disconnect
        if domain_name in active_connections and user_id in active_connections[domain_name]:
            active_connections[domain_name].remove(user_id)
            if not active_connections[domain_name]:  # Remove domain if no users are left
                del active_connections[domain_name]

        print(f"Disconnected: {domain_name} - {user_id}")
        print(f"Remaining connections: {active_connections}")


# Utility Functions

async def handle_session_data(session_data: SessionData):
    """Main handler for session data processing."""
    user_id = session_data.get("user_id")
    domain_name = session_data.get("domain_name")

    if not user_id or not domain_name:
        print("Invalid session data. Skipping...")
        return

    await update_admin_user_list(user_id, domain_name)
    session_id = await save_session_data(session_data, user_id)
    await update_counts(session_data, domain_name)
    print(f"Processed session for user: {user_id}, domain: {domain_name}")


async def update_admin_user_list(user_id: str, domain_name: str):
    """Update the users_list of the Admin document."""
    admin_doc = await mongodb.collections["admin"].find_one({"domain_name": domain_name})
    if admin_doc:
        existing_users = set(admin_doc.get("users_list", []))
        existing_users.add(ObjectId(user_id))
        await mongodb.collections["admin"].update_one(
            {"domain_name": domain_name},
            {"$set": {"users_list": list(existing_users)}}
        )
    else:
        print(f"Admin document for domain {domain_name} not found. Skipping user update.")


async def save_session_data(session_data: SessionData, user_id: str) -> ObjectId:
    """Save the session data to the database and handle the user's session IDs."""
    # Prepare the session document
    document = session_data.dict()
    document["session_start"] = document["session_start"] or datetime.now(timezone.utc)
    document["session_end"] = document["session_end"] or datetime.now(timezone.utc)

    # Insert the session document into the "session_data" collection
    session_result = await mongodb.collections["session_data"].insert_one(document)
    session_id = session_result.inserted_id

    # Check if the user exists in the "user" collection
    existing_user = await mongodb.collections["user"].find_one({"_id": ObjectId(user_id)})

    if existing_user:
        # If user exists, push the session ID into their "session_ids"
        await mongodb.collections["user"].update_one(
            {"_id": ObjectId(user_id)},
            {"$push": {"session_ids": session_id}}
        )
    else:
        # If user does not exist, create a new user document
        new_user = {
            "_id": ObjectId(user_id),
            "username": session_data.username,
            "domain_name": session_data.domain_name,
            "session_ids": [session_id],
        }
        await mongodb.collections["user"].insert_one(new_user)

    return session_id



async def update_counts(session_data: SessionData, domain_name: str):
    """Update or insert counts in the counts collection."""
    update_query = {
        "$inc": {
            f"page_counts.{path}": 1 for path in session_data.path_history or []
        }
    }

    if session_data.bounce:
        # Increment overall bounce counts
        update_query["$inc"]["bounce_counts"] = 1

        # Increment bounce count for the single page in path_history
        if session_data.path_history:
            bounce_page = session_data.path_history[0]
            update_query["$inc"][f"bounce_counts_per_page.{bounce_page}"] = 1

    if session_data.device_stats:
        os_name = session_data.device_stats.os
        browser_name = session_data.device_stats.browser
        device_name = session_data.device_stats.deviceType

        if os_name:
            update_query["$inc"][f"os_counts.{os_name}"] = 1
        if browser_name:
            update_query["$inc"][f"browser_counts.{browser_name}"] = 1
        if device_name:
            update_query["$inc"][f"device_counts.{device_name}"] = 1

    await mongodb.collections["counts"].update_one(
        {"domain_name": domain_name},
        update_query,
        upsert=True
    )
