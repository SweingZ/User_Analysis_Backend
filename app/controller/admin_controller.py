from fastapi import APIRouter, HTTPException, Query,status
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

@admin_route.put("/admin/verify")
async def verify_admin(
    admin_id: str, 
    account_status: str = Query(..., regex="^(ACCEPTED|REJECTED)$")  
):
    """
    Endpoint to verify an admin account by updating its status.
    """
    try:
        result = await AdminService.verify_admin(admin_id, account_status)
        return {"message": "Admin status updated successfully.", "data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred."
        )