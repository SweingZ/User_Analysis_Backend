from bson import ObjectId
from app.model.admin_model import Admin
from app.config.db_config import mongodb

class AdminRepo:

    @staticmethod
    async def insert_user(admin: Admin):
        result = await mongodb.collections["admin"].insert_one(admin.dict())
        return result
    
    @staticmethod
    async def find_admin(username: str):
        result = await mongodb.collections["admin"].find_one({"username":username})
        return result
    
    @staticmethod
    async def find_admin_by_id(admin_id: str):
        result = await mongodb.collections["admin"].find_one({"_id":ObjectId(admin_id)})
        return result