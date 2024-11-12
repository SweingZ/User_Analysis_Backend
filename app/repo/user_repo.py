from app.model.user_model import User
from app.config.db_config import mongodb

class UserRepo:

    @staticmethod
    async def insert_user(user: User):
        result = await mongodb.collections["user"].insert_one(user.dict())
        return result