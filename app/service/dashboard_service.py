from app.repo.dashboard_repo import DashboardRepo


class DashboardService:
    @staticmethod
    async def get_dashboard_data(page_name: str):
        if (page_name == "MAIN"):
            result = await DashboardService.get_main_data()
            return result
    
    ####### HELPER METHODS #############
    @staticmethod
    async def get_main_data():
        # Fetch data from various methods
        total_visitors = await DashboardRepo.get_total_visitors()
        total_visits = await DashboardRepo.get_total_visits()
        average_session_time = await DashboardService.get_avg_session_time()
        page_view_analysis = await DashboardRepo.get_page_view_analysis()
        bounce_count = await DashboardRepo.get_bounce_count()
        
        # Calculate bounce rate
        bounce_rate = (bounce_count["bounce_counts"] / total_visits) * 100 if total_visits else 0  # Avoid division by zero

        # Return data in a structured dictionary
        return {
            "total_visits": total_visits,
            "total_visitors": total_visitors,
            "avg_session_time": average_session_time,  # Fixed the typo
            "page_view_analysis": page_view_analysis["page_counts"],  # Include the page view analysis result
            "bounce_rate": bounce_rate,
        }



    @staticmethod
    async def get_avg_session_time():
        session_data = await DashboardRepo.get_session_data()

        total_duration = 0

        for session in session_data:
            session_start = session["session_start"]
            session_end = session["session_end"]
            session_duration = session_end - session_start
            total_duration += session_duration.total_seconds()
        
        if len(session_data) > 0:
            average_duration = total_duration / len(session_data)
            avg_minutes, avg_seconds = divmod(average_duration, 60)
            avg_hours, avg_minutes = divmod(avg_minutes, 60)
            return f"{int(avg_hours)} hours, {int(avg_minutes)} minutes, {int(avg_seconds)} seconds"
        
        else:
            return "No Session Data Available"
        
