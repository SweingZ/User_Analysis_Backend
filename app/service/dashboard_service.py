from app.repo.dashboard_repo import DashboardRepo
from datetime import datetime, timedelta


class DashboardService:
    @staticmethod
    async def get_dashboard_data(page_name: str):
        if page_name == "MAIN":
            result = await DashboardService.get_main_data()
            return result
        elif page_name == "DEVICE_STATS":
            result = await DashboardService.get_device_stats_data()
            return result

    ####### HELPER METHODS #############
    @staticmethod
    async def get_main_data():
        # Fetch current metrics
        total_visitors = await DashboardRepo.get_total_visitors()
        total_visits = await DashboardRepo.get_total_visits()
        average_session_time = await DashboardService.get_avg_session_time()
        page_view_analysis = await DashboardRepo.get_page_view_analysis()
        bounce_count = await DashboardRepo.get_bounce_count()

        # Fetch comparison metrics
        total_visits_change_rate = await DashboardService.get_total_visits_change_rate()
        avg_session_time_change_rate = await DashboardService.get_avg_session_time_change_rate()
        user_joined_change_rate = await DashboardService.get_user_joined_change_rate()

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
            "total_active_users": 1
        }
    
    @staticmethod
    async def get_device_stats_data():
        counts_data = await DashboardRepo.get_count_data()

        return {
            "os_counts": counts_data.get("os_counts", {}),
            "browser_counts": counts_data.get("browser_counts", {}),
            "device_counts": counts_data.get("device_counts", {}),
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
    async def get_avg_session_time():
        session_data = await DashboardRepo.get_session_data()
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
    async def get_total_visits_change_rate():
        # Define current and previous month ranges
        now = datetime.utcnow()
        start_of_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_of_last_month = (start_of_this_month - timedelta(days=1)).replace(day=1)
        end_of_last_month = start_of_this_month - timedelta(seconds=1)

        # Get current and last month's total visits
        current_month_visits = await DashboardRepo.get_total_visits_in_range(start_of_this_month, now)
        last_month_visits = await DashboardRepo.get_total_visits_in_range(start_of_last_month, end_of_last_month)

        if last_month_visits == 0:
            return 0
        change_rate = ((current_month_visits - last_month_visits) / last_month_visits) * 100
        return change_rate

    @staticmethod
    async def get_avg_session_time_change_rate():
        # Define current and previous month ranges
        now = datetime.utcnow()
        start_of_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_of_last_month = (start_of_this_month - timedelta(days=1)).replace(day=1)
        end_of_last_month = start_of_this_month - timedelta(seconds=1)

        # Get average session time for current and last month
        current_avg_time = await DashboardService.get_avg_session_time_in_range(start_of_this_month, now)
        last_avg_time = await DashboardService.get_avg_session_time_in_range(start_of_last_month, end_of_last_month)

        if last_avg_time == 0:
            return 0
        change_rate = ((current_avg_time - last_avg_time) / last_avg_time) * 100
        return change_rate

    @staticmethod
    async def get_avg_session_time_in_range(start_date, end_date):
        session_data = await DashboardRepo.get_session_data_in_range(start_date, end_date)
        total_duration = sum(
            (session["session_end"] - session["session_start"]).total_seconds()
            for session in session_data
        )

        if len(session_data) > 0:
            return total_duration / len(session_data)
        else:
            return 0
        

    @staticmethod
    async def get_user_joined_change_rate():
        now = datetime.utcnow()
        start_of_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_of_last_month = (start_of_this_month - timedelta(days=1)).replace(day=1)
        end_of_last_month = start_of_this_month - timedelta(seconds=1)

        # Fetch current and previous month user join counts
        users_joined_this_month = await DashboardRepo.get_users_joined_in_range(start_of_this_month, now)
        users_joined_last_month = await DashboardRepo.get_users_joined_in_range(start_of_last_month, end_of_last_month)

        if users_joined_last_month == 0:
            return 0
        change_rate = ((users_joined_this_month - users_joined_last_month) / users_joined_last_month) * 100
        return change_rate
