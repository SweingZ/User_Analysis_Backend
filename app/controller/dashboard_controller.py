from fastapi import APIRouter, Depends
from app.service.dashboard_service import DashboardService
from app.utils.jwt_utils import feature_access_verification

dashboard_route = APIRouter()

@dashboard_route.get("/dashboard")
async def get_dashboard_data(page_name: str, admin_id: str):
    await feature_access_verification(page_name)
    return await DashboardService.get_dashboard_data(page_name, admin_id)
