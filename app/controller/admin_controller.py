from fastapi import APIRouter

from app.model.admin_model import Admin
from app.service.admin_service import AdminService

admin_route = APIRouter()

@admin_route.post("/admin/register")
async def register_admin(admin: Admin):
    result = await AdminService.register_admin(admin)
    return result