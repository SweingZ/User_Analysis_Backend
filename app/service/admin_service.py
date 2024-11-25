from fastapi import HTTPException
from app.model.admin_model import Admin
from app.repo.admin_repo import AdminRepo


class AdminService:

    @staticmethod
    async def register_admin(admin: Admin):
        result = await AdminRepo.insert_user(admin)
        if result:
            return "Admin Registered"
        raise HTTPException(status_code=404,detail="Error Occured")