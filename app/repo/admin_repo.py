from app.model.admin_model import Admin
from app.config.db_config import mongodb

class AdminRepo:

    @staticmethod
    async def insert_user(admin: Admin):
        result = await mongodb.collections["admin"].insert_one(admin.dict())
        return result