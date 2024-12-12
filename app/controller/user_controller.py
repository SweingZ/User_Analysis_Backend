from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from app.model.user_model import User
from app.service.user_service import UserService
from app.config.db_config import mongodb
from app.utils.jwt_utils import feature_access_verification


user_route = APIRouter()

@user_route.post("/register")
async def register_user(user: User):
    result = await UserService.register_user(user)
    return result

@user_route.get("/create_user")
async def get_id():
    user = await mongodb.collections["user"].insert_one({"session_ids": []})  
    return {"user_id": str(user.inserted_id)}  

@user_route.get("/get_top_users/{admin_id}")
async def get_top_users(admin_id: str):
    await feature_access_verification(page_name="USER_STATS")
    users = await UserService.get_top_users(admin_id)
    return users

@user_route.get("/sessions/{user_id}")
async def get_user_session( 
    user_id: str,
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None)
):
    await feature_access_verification(page_name="USER_STATS")
    session = await UserService.get_user_session(user_id, year, month)        
    return session
