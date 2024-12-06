from fastapi import APIRouter
from app.model.user_model import User
from app.service.user_service import UserService
from app.config.db_config import mongodb


user_route = APIRouter()

@user_route.post("/register")
async def register_user(user: User):
    result = await UserService.register_user(user)
    return result

@user_route.get("/create_user")
async def get_id():
    user = await mongodb.collections["user"].insert_one({"session_ids": []})  # Await the insert operation
    return {"user_id": str(user.inserted_id)}  # Convert ObjectId to string

@user_route.get("/get_top_users/{admin_id}")
async def get_top_users(admin_id: str):
    users = await UserService.get_top_users(admin_id)
    return users
