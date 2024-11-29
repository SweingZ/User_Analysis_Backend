from fastapi import HTTPException
from app.repo.admin_repo import AdminRepo
from app.repo.dashboard_repo import DashboardRepo
from datetime import datetime, timedelta
from app.utils.shared_state import active_connections


class DashboardService:
    @staticmethod
    async def get_dashboard_data(page_name: str, admin_id: str):
        if page_name == "MAIN":
            result = await DashboardService.get_main_data(admin_id)
            return result
        elif page_name == "DEVICE_STATS":
            result = await DashboardService.get_device_stats_data(admin_id)
            return result

    ####### HELPER METHODS #############
    @staticmethod
    async def get_main_data(admin_id: str):
        # Fetch domain name
        domain_name = await DashboardService.get_domain_name(admin_id)

        # Fetch active users for the domain
        active_users_count = len(active_connections.get(domain_name, []))

        # Fetch current metrics
        total_visitors = await DashboardRepo.get_total_visitors(domain_name)
        total_visits = await DashboardRepo.get_total_visits(domain_name)
        average_session_time = await DashboardService.get_avg_session_time(domain_name)
        page_view_analysis = await DashboardRepo.get_page_view_analysis(domain_name)
        bounce_count = await DashboardRepo.get_bounce_count(domain_name)

        # Fetch comparison metrics
        total_visits_change_rate = await DashboardService.get_total_visits_change_rate(domain_name)
        avg_session_time_change_rate = await DashboardService.get_avg_session_time_change_rate(domain_name)
        user_joined_change_rate = await DashboardService.get_user_joined_change_rate(domain_name)

        # Calculate bounce rate
        bounce_rate = (bounce_count["bounce_counts"] / total_visits) * 100 if total_visits else 0  # Avoid division by zero

        # Return data in a structured dictionary
        return {
            "total_visits": total_visits,
            "total_visitors": total_visitors,
            "avg_session_time": average_session_time,
            "page_view_analysis": page_view_analysis["page_counts"],
            "bounce_rate": bounce_rate,
            "total_visits_change_rate": total_visits_change_rate,
            "avg_session_time_change_rate": avg_session_time_change_rate,
            "total_visitors_change_rate": user_joined_change_rate,
            "total_active_users": active_users_count
        }
    
    @staticmethod
    async def get_domain_name(admin_id: str):
        admin_data = await AdminRepo.find_admin_by_id(admin_id)
        if not admin_data:
            raise HTTPException(status_code=404,detail="Admin not found")
        domain_name = admin_data["domain_name"]
        return domain_name
    
    @staticmethod
    async def get_device_stats_data(admin_id: str):
        # Fetch domain name
        domain_name = await DashboardService.get_domain_name(admin_id)
        counts_data = await DashboardRepo.get_count_data(domain_name)
        location_data = await DashboardRepo.get_location_data(domain_name)

        return {
            "os_counts": counts_data.get("os_counts", {}),
            "browser_counts": counts_data.get("browser_counts", {}),
            "device_counts": counts_data.get("device_counts", {}),
            "location_data": location_data,
            "referers": [
                {"source": "Google", "count": 5200},
                {"source": "Facebook", "count": 2800},
                {"source": "Instagram", "count": 2100},
                {"source": "Twitter", "count": 1800},
                {"source": "LinkedIn", "count": 1500},
                {"source": "Direct", "count": 3600}
            ]
        }


    @staticmethod
    async def get_avg_session_time(domain_name: str):
        session_data = await DashboardRepo.get_session_data(domain_name)
        total_duration = sum(
            (session["session_end"] - session["session_start"]).total_seconds()
            for session in session_data
        )

        if len(session_data) > 0:
            average_duration = total_duration / len(session_data)
            avg_minutes, avg_seconds = divmod(average_duration, 60)
            avg_hours, avg_minutes = divmod(avg_minutes, 60)
            return f"{int(avg_hours)} hours, {int(avg_minutes)} minutes, {int(avg_seconds)} seconds"
        else:
            return "No Session Data Available"

    @staticmethod
    async def get_total_visits_change_rate(domain_name: str):
        # Define current and previous month ranges
        now = datetime.utcnow()
        start_of_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_of_last_month = (start_of_this_month - timedelta(days=1)).replace(day=1)
        end_of_last_month = start_of_this_month - timedelta(seconds=1)

        # Get current and last month's total visits
        current_month_visits = await DashboardRepo.get_total_visits_in_range(start_of_this_month, now, domain_name)
        last_month_visits = await DashboardRepo.get_total_visits_in_range(start_of_last_month, end_of_last_month, domain_name)

        if last_month_visits == 0:
            return 0
        change_rate = ((current_month_visits - last_month_visits) / last_month_visits) * 100
        return change_rate

    @staticmethod
    async def get_avg_session_time_change_rate(domain_name: str):
        # Define current and previous month ranges
        now = datetime.utcnow()
        start_of_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_of_last_month = (start_of_this_month - timedelta(days=1)).replace(day=1)
        end_of_last_month = start_of_this_month - timedelta(seconds=1)

        # Get average session time for current and last month
        current_avg_time = await DashboardService.get_avg_session_time_in_range(start_of_this_month, now, domain_name)
        last_avg_time = await DashboardService.get_avg_session_time_in_range(start_of_last_month, end_of_last_month, domain_name)

        if last_avg_time == 0:
            return 0
        change_rate = ((current_avg_time - last_avg_time) / last_avg_time) * 100
        return change_rate

    @staticmethod
    async def get_avg_session_time_in_range(start_date, end_date, domain_name):
        session_data = await DashboardRepo.get_session_data_in_range(start_date, end_date, domain_name)
        total_duration = sum(
            (session["session_end"] - session["session_start"]).total_seconds()
            for session in session_data
        )

        if len(session_data) > 0:
            return total_duration / len(session_data)
        else:
            return 0
        

    @staticmethod
    async def get_user_joined_change_rate(domain_name: str):
        now = datetime.utcnow()
        start_of_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_of_last_month = (start_of_this_month - timedelta(days=1)).replace(day=1)
        end_of_last_month = start_of_this_month - timedelta(seconds=1)

        # Fetch current and previous month user join counts
        users_joined_this_month = await DashboardRepo.get_users_joined_in_range(start_of_this_month, now, domain_name)
        users_joined_last_month = await DashboardRepo.get_users_joined_in_range(start_of_last_month, end_of_last_month, domain_name)

        if users_joined_last_month == 0:
            return 0
        change_rate = ((users_joined_this_month - users_joined_last_month) / users_joined_last_month) * 100
        return change_rate
