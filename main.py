from datetime import datetime, timezone
from typing import List
from bson import ObjectId
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import asynccontextmanager
from app.config.db_config import mongodb,MONGO_URI,DATABASE_NAME
from app.model.session_data import SessionData
from app.config.db_config import mongodb
from app.controller.user_controller import user_route
from app.controller.dashboard_controller import dashboard_route

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(user_route,tags=["User"])
app.include_router(dashboard_route,tags=["Dashboard"])

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to MongoDB on startup
    await mongodb.connect(MONGO_URI, DATABASE_NAME)
    yield
    # Disconnect from MongoDB on shutdown
    await mongodb.close()

# Register the lifespan event with FastAPI
app.router.lifespan_context = lifespan


# Example route to test connection
@app.get("/")
async def root():
    return {"message": "Hello, MongoDB connected successfully!"}


active_connections: List[WebSocket] = []


# WebSocket endpoint to handle session data
@app.websocket("/ws/session")
async def websocket_session(websocket: WebSocket):
    await websocket.accept()  # Accept the WebSocket connection
    active_connections.append(websocket)
    print(f"Connected: {len(active_connections)} active connections")
    try:
        while True:
            # Wait for data from the frontend
            data = await websocket.receive_json()

            if data["event"] == "on_close":
                user_id = data["user_id"]
                print(data)

                # Parse incoming data into the SessionData model
                session_data = SessionData(**data)
                website = data.get("website")

                # Prepare the session data document
                document = session_data.dict()
                document["session_start"] = document["session_start"] or datetime.now(timezone.utc)
                document["session_end"] = document["session_end"] or datetime.now(timezone.utc)

                # Insert the session document and get the new session ID
                session_result = await mongodb.collections["session_data"].insert_one(document)
                session_id = session_result.inserted_id

                # Update the user document by pushing the session ID into the session_ids list
                await mongodb.collections["user"].update_one(
                    {"_id": ObjectId(user_id)},
                    {"$push": {"session_ids": session_id}}
                )
                
                # Upsert counts in the counts collection
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
                    device_name = session_data.device_stats.device
                    
                    if os_name:
                        update_query["$inc"][f"os_counts.{os_name}"] = 1
                    if browser_name:
                        update_query["$inc"][f"browser_counts.{browser_name}"] = 1
                    if device_name:
                        update_query["$inc"][f"device_counts.{device_name}"] = 1

                # Upsert Query for counts collection
                await mongodb.collections["counts"].update_one(
                    {"website": website},
                    update_query,
                    upsert=True
                )

                print(f"Session data saved: {document}")

    except WebSocketDisconnect:
        active_connections.remove(websocket)
        print(f"Disconnected: {len(active_connections)} active connections")