from datetime import datetime, timezone
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import asynccontextmanager
from app.config.db_config import mongodb,MONGO_URI,DATABASE_NAME
from app.model.session_data import SessionData
from app.config.db_config import mongodb

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

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


# WebSocket endpoint to handle session data
@app.websocket("/ws/session")
async def websocket_session(websocket: WebSocket):
    await websocket.accept()  # Accept the WebSocket connection
    try:
        while True:
            # Wait for data from the frontend
            data = await websocket.receive_json()
            session_data = SessionData(**data)  # Parse the data into the SessionData model

            # Insert session data into MongoDB
            document = session_data.dict()
            document["session_start"] = document["session_start"] or datetime.now(timezone.utc).isoformat()
            document["session_end"] = document["session_end"] or datetime.now(timezone.utc).isoformat()

            await mongodb.collections["session_data"].insert_one(document)
            print(f"Session data saved: {document}")

    except WebSocketDisconnect:
        print("WebSocket connection closed")