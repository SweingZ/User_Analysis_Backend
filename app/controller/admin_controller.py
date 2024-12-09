from fastapi import APIRouter

from app.dto.login_dto import LoginRequestDTO
from app.model.admin_model import Admin
from app.service.admin_service import AdminService

admin_route = APIRouter()

@admin_route.post("/admin/register")
async def register_admin(admin: Admin):
    result = await AdminService.register_admin(admin)
    return result

@admin_route.post("/admin/login")
async def login_admin(loginRequestDTO: LoginRequestDTO):
    result = await AdminService.login_admin(loginRequestDTO)
    return result