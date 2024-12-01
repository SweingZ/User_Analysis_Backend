import asyncio
from fastapi import HTTPException
from app.repo.admin_repo import AdminRepo
from app.repo.dashboard_repo import DashboardRepo
from datetime import datetime, timedelta
from app.utils.shared_state import active_connections
from collections import defaultdict

class DashboardService:
    @staticmethod
    async def get_dashboard_data(page_name: str, admin_id: str):
        if page_name == "MAIN":
            result = await DashboardService.get_main_data(admin_id)
            return result
        elif page_name == "DEVICE_STATS":
            result = await DashboardService.get_device_stats_data(admin_id)
            return result
        elif page_name == "CONTENT":
            result = await DashboardService.get_content_metrics_data(admin_id)
            return result

    ####### HELPER METHODS #############
    @staticmethod
    async def get_main_data(admin_id: str):
        # Fetch domain name
        domain_name = await DashboardService.get_domain_name(admin_id)

        # Use asyncio.gather to fetch data concurrently
        total_visitors, total_visits, average_session_time, page_view_analysis, bounce_count, total_visits_change_rate, avg_session_time_change_rate, user_joined_change_rate = await asyncio.gather(
            DashboardRepo.get_total_visitors(domain_name),
            DashboardRepo.get_total_visits(domain_name),
            DashboardService.get_avg_session_time(domain_name),
            DashboardRepo.get_page_view_analysis(domain_name),
            DashboardRepo.get_bounce_count(domain_name),
            DashboardService.get_total_visits_change_rate(domain_name),
            DashboardService.get_avg_session_time_change_rate(domain_name),
            DashboardService.get_user_joined_change_rate(domain_name)
        )

        # Fetch active users for the domain
        active_users_count = len(active_connections.get(domain_name, []))

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
    async def get_device_stats_data(admin_id: str):
        domain_name = await DashboardService.get_domain_name(admin_id)
        
        counts_data = await DashboardRepo.get_count_data(domain_name)
        
        location_and_referrer_data = await DashboardRepo.get_location_and_referrer_data(domain_name)
        
        locations = (item.get("location") for item in location_and_referrer_data if "location" in item)
        referrers = (item.get("referrer") for item in location_and_referrer_data if "referrer" in item)

        return {
            "os_counts": counts_data.get("os_counts", {}),
            "browser_counts": counts_data.get("browser_counts", {}),
            "device_counts": counts_data.get("device_counts", {}),
            "location_data": locations,
            "referrers": referrers
        }


    @staticmethod
    async def get_content_metrics_data(admin_id: str):
        # Fetch domain name
        domain_name = await DashboardService.get_domain_name(admin_id)

        # Fetch session data for the domain
        session_data = await DashboardRepo.get_session_data(domain_name)

        # Initialize data structures to hold content metrics
        video_view_count = defaultdict(int)
        total_watch_time = defaultdict(float)
        content_view_count = defaultdict(int)
        content_scroll_depths = defaultdict(list)  
        button_clicks = defaultdict(int)

        # Iterate through session data to aggregate the required metrics
        for session in session_data:
            # For each session, extract relevant information
            interaction = session.get("interaction", {})
            video_data = interaction.get("video_data", [])
            button_data = interaction.get("button_data", [])
            contents_data = interaction.get("contents_data", [])

            # Count video views and accumulate total watch time per video
            for video in video_data:
                video_id = video.get("title")  # Using video title as video ID
                if video_id:
                    video_view_count[video_id] += 1
                    total_watch_time[video_id] += video.get("total_watch_time", 0.0)

            # Count content views and accumulate scroll depths for each content
            for content in contents_data:
                content_id = content.get("content_title")  # Using content title as content ID
                if content_id:
                    content_view_count[content_id] += 1
                    scroll_depth = content.get("scrolled_depth", 0)
                    if scroll_depth is not None:
                        # Store scroll depth for each content
                        content_scroll_depths[content_id].append(scroll_depth)

            # Count button clicks
            for button in button_data:
                button_title = button.get("content_title")
                if button_title:
                    button_clicks[button_title] += button.get("click", 0)

        # Calculate average watch time per video
        avg_watch_time_per_video = {
            video_id: total_watch_time[video_id] / video_view_count[video_id]
            if video_view_count[video_id] > 0 else 0
            for video_id in total_watch_time
        }

        # Calculate average scroll depth per content
        avg_scroll_depth_per_content = {
            content_id: sum(depths) / len(depths) if depths else 0
            for content_id, depths in content_scroll_depths.items()
        }

        # Return the structured content metrics data
        return {
            "video_view_count": dict(video_view_count),
            "avg_watch_time_per_video": avg_watch_time_per_video,
            "content_view_count": dict(content_view_count),
            "avg_scroll_depth_per_content": avg_scroll_depth_per_content,
            "button_clicks": dict(button_clicks)
        }
    
    @staticmethod
    async def get_domain_name(admin_id: str):
        admin_data = await AdminRepo.find_admin_by_id(admin_id)
        if not admin_data:
            raise HTTPException(status_code=404,detail="Admin not found")
        domain_name = admin_data["domain_name"]
        return domain_name
    


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
        now, start_of_this_month, start_of_last_month, end_of_last_month = DashboardService.get_month_range()

        # Get current and last month's total visits
        current_month_visits = await DashboardRepo.get_total_visits_in_range(start_of_this_month, now, domain_name)
        last_month_visits = await DashboardRepo.get_total_visits_in_range(start_of_last_month, end_of_last_month, domain_name)

        if last_month_visits == 0:
            return 0
        change_rate = ((current_month_visits - last_month_visits) / last_month_visits) * 100
        return change_rate
    
    @staticmethod
    async def get_user_joined_change_rate(domain_name: str):
        now, start_of_this_month, start_of_last_month, end_of_last_month = DashboardService.get_month_range()

        # Fetch current and previous month user join counts
        users_joined_this_month = await DashboardRepo.get_users_joined_in_range(start_of_this_month, now, domain_name)
        users_joined_last_month = await DashboardRepo.get_users_joined_in_range(start_of_last_month, end_of_last_month, domain_name)

        if users_joined_last_month == 0:
            return 0
        change_rate = ((users_joined_this_month - users_joined_last_month) / users_joined_last_month) * 100
        return change_rate

    @staticmethod
    async def get_avg_session_time_change_rate(domain_name: str):
        now, start_of_this_month, start_of_last_month, end_of_last_month = DashboardService.get_month_range()

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
    def get_month_range():
        now = datetime.utcnow()
        start_of_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_of_last_month = (start_of_this_month - timedelta(days=1)).replace(day=1)
        end_of_last_month = start_of_this_month - timedelta(seconds=1)
        return now, start_of_this_month, start_of_last_month, end_of_last_month

        


