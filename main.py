from datetime import datetime, timezone
from typing import List
from bson import ObjectId
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
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
active_connections: List[WebSocket] = []


@app.websocket("/ws/session")
async def websocket_session(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    print(f"Connected: {len(active_connections)} active connections")
    try:
        while True:
            data = await websocket.receive_json()
            if data["event"] == "on_close":
                session_data = SessionData(**data)
                await handle_session_data(session_data)
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        print(f"Disconnected: {len(active_connections)} active connections")


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
    """Save the session data to the database and return the session ID."""
    document = session_data.dict()
    document["session_start"] = document["session_start"] or datetime.now(timezone.utc)
    document["session_end"] = document["session_end"] or datetime.now(timezone.utc)

    session_result = await mongodb.collections["session_data"].insert_one(document)
    session_id = session_result.inserted_id

    await mongodb.collections["user"].update_one(
        {"_id": ObjectId(user_id)},
        {"$push": {"session_ids": session_id}}
    )
    return session_id


async def update_counts(session_data: SessionData, domain_name: str):
    """Update or insert counts in the counts collection."""
    update_query = {
        "$inc": {
            f"page_counts.{path}": 1 for path in session_data.path_history or []
        }
    }

    if session_data.bounce:
        update_query["$inc"]["bounce_counts"] = 1

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
