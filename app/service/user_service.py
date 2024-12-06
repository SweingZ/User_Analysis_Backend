from fastapi import HTTPException, status
from app.dto.user_dto import UserResponseDTO
from app.model.user_model import User
from app.repo.user_repo import UserRepo


class UserService:

    @staticmethod
    async def register_user(user: User):
        result = await UserRepo.insert_user(user)
        if result:
            return "User Registered"
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Error Occured")
    
    @staticmethod
    async def get_top_users():
        result = await UserRepo.find_users()
        if result:
            return [UserResponseDTO(**doc) for doc in result]
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Error Occured")
