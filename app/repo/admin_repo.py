from bson import ObjectId
from app.model.admin_model import Admin
from app.config.db_config import mongodb

class AdminRepo:

    @staticmethod
    async def insert_user(admin: Admin):
        result = await mongodb.collections["admin"].insert_one(admin.dict(exclude_unset=True))
        return result
    
    @staticmethod
    async def find_admin(username: str):
        result = await mongodb.collections["admin"].find_one({"username":username})
        return result
    
    @staticmethod
    async def find_admin_by_id(admin_id: str):
        result = await mongodb.collections["admin"].find_one({"_id":ObjectId(admin_id)})
        return result
    
    @staticmethod
    async def update_admin_status(admin_id: str, new_status: str):
        """Update the admin's status."""
        result = await mongodb.collections["admin"].update_one(
            {"_id": ObjectId(admin_id)},
            {"$set": {"status": new_status}}
        )
        return result.modified_count > 0
    
    @staticmethod
    async def update_admin(admin_id: str, update_dict: dict):
        result = await mongodb.collections["admin"].update_one(
            {"_id": ObjectId(admin_id)},
            {"$set": update_dict}
        )

    @staticmethod
    async def get_all_admins():
        result = await mongodb.collections["admin"].find({"role":"ADMIN"}).to_list(length=None)
        return result