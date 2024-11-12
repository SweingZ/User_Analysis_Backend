from fastapi import HTTPException
from app.model.user_model import User
from app.repo.user_repo import UserRepo


class UserService:

    @staticmethod
    async def register_user(user: User):
        result = await UserRepo.insert_user(user)
        if result:
            return "User Registered"
        raise HTTPException(status_code=404,detail="Error Occured")