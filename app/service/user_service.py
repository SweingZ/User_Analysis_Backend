from typing import Optional
from fastapi import HTTPException, status
from app.dto.user_dto import UserResponseDTO
from app.model.user_model import User
from app.repo.user_repo import UserRepo
from app.service.dashboard_service import DashboardService


class UserService:

    @staticmethod
    async def register_user(user: User):
        result = await UserRepo.insert_user(user)
        if result:
            return "User Registered"
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Error Occured")
    
    @staticmethod
    async def get_top_users(admin_id: str):
        domain_name = await DashboardService.get_domain_name(admin_id)
        result = await UserRepo.find_users(domain_name)
        if result:
            return [UserResponseDTO(**doc) for doc in result]
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Error Occured")
    
    @staticmethod
    async def get_user_session(user_id: str, year: Optional[int], month: Optional[int]):
        session = await UserRepo.find_session_by_user_id(user_id, year, month)
        if not session:
            return {"error": "Session not found for the given user_id"}
        return session