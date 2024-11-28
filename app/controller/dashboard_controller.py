from fastapi import APIRouter

from app.service.dashboard_service import DashboardService

dashboard_route = APIRouter()

@dashboard_route.get("/dashboard")
async def get_dashboard_data(page_name: str, admin_id: str):
    return await DashboardService.get_dashboard_data(page_name, admin_id)
