from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query,status
from app.dto.login_dto import LoginRequestDTO
from app.model.admin_model import Admin
from app.service.admin_service import AdminService
from app.utils.jwt_utils import super_admin_verification

admin_route = APIRouter()

@admin_route.post("/admin/register")
async def register_admin(admin: Admin):
    result = await AdminService.register_admin(admin)
    return result

@admin_route.post("/admin/login")
async def login_admin(loginRequestDTO: LoginRequestDTO):
    result = await AdminService.login_admin(loginRequestDTO)
    return result

@admin_route.get("/admin")
async def get_all_admins(token: str = Depends(super_admin_verification)):
    result = await AdminService.get_all_admins()
    return result

@admin_route.put("/admin/verify")
async def verify_admin(
    admin_id: str, 
    account_status: str = Query(..., regex="^(ACCEPTED|REJECTED)$"),
    payload=  Depends(super_admin_verification)
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

@admin_route.put("/admin/feature_access/{admin_id}")
async def assign_feature_access(admin_id: str, feature_list: List[str], token: str =  Depends(super_admin_verification)):
    result = await AdminService.assign_feature_access(admin_id, feature_list)
    return result