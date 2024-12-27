from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from app.service.dashboard_service import DashboardService
from app.utils.jwt_utils import feature_access_verification

dashboard_route = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@dashboard_route.get("/dashboard")
async def get_dashboard_data(page_name: str, admin_id: str, token: str = Depends(oauth2_scheme)):
    await feature_access_verification(page_name, token)
    
    # Once verification passes, retrieve the dashboard data
    return await DashboardService.get_dashboard_data(page_name, admin_id)
