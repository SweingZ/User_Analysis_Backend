from datetime import datetime, timezone
from typing import Dict, List, Optional
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
from app.utils.shared_state import active_connections

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
    user_id = session_data.user_id
    domain_name = session_data.domain_name

    if not user_id or not domain_name:
        print("Invalid session data. Skipping...")
        return

    # Process content metrics
    await save_content_metrics(session_data)

    # Update admin user list
    await update_admin_user_list(user_id, domain_name)
    
    # Save session data and update counts
    session_id = await save_session_data(session_data, user_id)
    await update_counts(session_data, domain_name)
    
    print(f"Processed session for user: {user_id}, domain: {domain_name}")


async def save_content_metrics(session_data: SessionData):
    """Save or update content metrics based on the session data."""

    domain_name = session_data.domain_name
    interaction = session_data.interaction
    bulk_updates = []

    # Process video metrics
    if interaction.video_data:
        for video in interaction.video_data:
            update_query = {
                "domain_name": domain_name,
                "metrics.title": video.title,
                "metrics.type": "VIDEO"
            }
            update_data = {
                "$set": {"domain_name": domain_name},
                "$inc": {
                    "metrics.$.views": 1,
                    "metrics.$.sum_watch_time": video.total_watch_time or 0,
                    "metrics.$.sum_completion_rate": 100 if video.ended else 0,
                }
            }
            bulk_updates.append({
                "update_one": {
                    "filter": update_query,
                    "update": update_data,
                    "upsert": True
                }
            })

    # Process button metrics
    if interaction.button_data:
        for button in interaction.button_data:
            update_query = {
                "domain_name": domain_name,
                "metrics.title": button.content_title,
                "metrics.type": "BUTTON"
            }
            update_data = {
                "$set": {"domain_name": domain_name},
                "$inc": {"metrics.$.clicks": button.click or 1}
            }
            bulk_updates.append({
                "update_one": {
                    "filter": update_query,
                    "update": update_data,
                    "upsert": True
                }
            })

    # Process content metrics
    if interaction.contents_data:
        for content in interaction.contents_data:
            watch_time = (
                (content.ended_watch_time - content.start_watch_time).total_seconds()
                if content.start_watch_time and content.ended_watch_time
                else 0
            )

            # Calculate the completion rate
            completion_rate = calculate_content_completion_rate(
                word_count=content.word_count,
                scrolled_depth=content.scrolled_depth,
                watch_time=watch_time
            )

            cta_clicks = 0

            # Check for child buttons matching the parent_content_title
            if interaction.child_buttons_data:
                for child_button in interaction.child_buttons_data:
                    if child_button.parent_content_title == content.content_title:
                        cta_clicks += child_button.click or 0 

            update_query = {
                "domain_name": domain_name,
                "metrics.title": content.content_title,
                "metrics.type": "CONTENT"
            }
            update_data = {
                "$set": {"domain_name": domain_name},
                "$inc": {
                    "metrics.$.views": 1,
                    "metrics.$.sum_scroll_depth": content.scrolled_depth or 0,
                    "metrics.$.sum_watch_time": watch_time,
                    "metrics.$.sum_completion_rate": completion_rate,
                    "metrics.$.cta_clicks": cta_clicks  
                }
            }
            bulk_updates.append({
                "update_one": {
                    "filter": update_query,
                    "update": update_data,
                    "upsert": True
                }
            })


    # Process child button metrics
    if interaction.child_buttons_data:
        for child_button in interaction.child_buttons_data:
            update_query = {
                "domain_name": domain_name,
                "metrics.title": child_button.content_title,
                "metrics.type": "BUTTON"
            }
            update_data = {
                "$set": {"domain_name": domain_name},
                "$inc": {"metrics.$.clicks": child_button.click or 1}
            }
            bulk_updates.append({
                "update_one": {
                    "filter": update_query,
                    "update": update_data,
                    "upsert": True
                }
            })

    # Execute bulk operations if there are updates
    if bulk_updates:
        # Use Motor's bulk_write method
        result = await mongodb.collections["content"].bulk_write(bulk_updates)
        print(f"Updated content metrics for domain: {domain_name}, modified count: {result.modified_count}")
    else:
        print("No updates required for content metrics.")


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
    document = session_data.dict(exclude={"username"})
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
            "date_joined": datetime.utcnow(),
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

def calculate_content_completion_rate(
    word_count: Optional[int],
    scrolled_depth: Optional[float],
    watch_time: Optional[float]
) -> float:
    avg_reading_speed = 200
    estimated_reading_time = (word_count / avg_reading_speed) * 60 if word_count else 0
    
    scroll_completion = (scrolled_depth / 100) if scrolled_depth is not None else 0
    time_completion = (
        min(watch_time / estimated_reading_time, 1.0) if estimated_reading_time > 0 else 0
    )
    
    if scroll_completion == 1 and time_completion < 1:
        total_completion = time_completion

    elif scroll_completion < 1 and time_completion == 1:
        total_completion = scroll_completion

    elif scroll_completion < 1 and time_completion < 1:
        total_completion = scroll_completion + time_completion / 2

    else:
        total_completion = 1
    
    return total_completion * 100


    


