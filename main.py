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
from app.controller.websocket_controller import websocket_route
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
app.include_router(websocket_route, tags=["WEBSOCKET"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    await mongodb.connect(MONGO_URI, DATABASE_NAME)  # Connect to MongoDB
    yield
    await mongodb.close()  # Disconnect from MongoDB


app.router.lifespan_context = lifespan

@app.get("/")
async def root():
    return {"message": "Hello, MongoDB connected successfully!"}



    


