import asyncio
from typing import Dict
from fastapi import HTTPException
from app.model.content_model import Content
from app.repo.admin_repo import AdminRepo
from app.repo.dashboard_repo import DashboardRepo
from datetime import datetime, timedelta
from app.utils.shared_state import active_connections
from collections import Counter, defaultdict

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
        total_visitors, total_visits, average_session_time, page_view_analysis, bounce_count, total_visits_change_rate, avg_session_time_change_rate, user_joined_change_rate, bounce_counts_per_page = await asyncio.gather(
            DashboardRepo.get_total_visitors(domain_name),
            DashboardRepo.get_total_visits(domain_name),
            DashboardService.get_avg_session_time(domain_name),
            DashboardRepo.get_page_view_analysis(domain_name),
            DashboardRepo.get_bounce_count(domain_name),
            DashboardService.get_total_visits_change_rate(domain_name),
            DashboardService.get_avg_session_time_change_rate(domain_name),
            DashboardService.get_user_joined_change_rate(domain_name),
            DashboardRepo.get_bounce_counts_per_page(domain_name)
        )

        # Fetch active users for the domain
        active_users_count = len(active_connections.get(domain_name, []))

        # Calculate bounce rate
        if bounce_count:
            bounce_rate = (bounce_count["bounce_counts"] / total_visits) * 100 if total_visits else 0  # Avoid division by zero
        else:
            bounce_rate = 0

        # Return data in a structured dictionary
        return {
            "total_visits": total_visits,
            "total_visitors": total_visitors,
            "avg_session_time": average_session_time,
            "page_view_analysis": page_view_analysis["page_counts"],
            "bounce_rate": bounce_rate,
            "bounce_counts_per_page": bounce_counts_per_page["bounce_counts_per_page"],
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
        
        # Extract locations and referrers
        locations = [item.get("location") for item in location_and_referrer_data if "location" in item]
        referrers = [
            (
                referrer.get("utm_source"), 
                referrer.get("utm_medium"), 
                referrer.get("utm_campaign")
            )
            for item in location_and_referrer_data if "referrer" in item
            for referrer in [item.get("referrer")]
            if referrer and all(field is not None for field in (referrer.get("utm_source"), referrer.get("utm_medium"), referrer.get("utm_campaign")))
        ]
        
        # Count referrers grouped by (utm_source, utm_medium, utm_campaign)
        referrer_counts = Counter(referrers)
        
        # Format the results as a list of dictionaries for easier consumption
        formatted_referrer_counts = [
            {
                "utm_source": key[0],
                "utm_medium": key[1],
                "utm_campaign": key[2],
                "count": count
            }
            for key, count in referrer_counts.items()
        ]
        
        return {
            "os_counts": counts_data.get("os_counts", {}),
            "browser_counts": counts_data.get("browser_counts", {}),
            "device_counts": counts_data.get("device_counts", {}),
            "location_data": locations,
            "referrers": formatted_referrer_counts  # List of dictionaries with counts
        }


    @staticmethod
    async def get_content_metrics_data(admin_id: str) -> Dict:
        # Get the domain name using the admin_id
        domain_name = await DashboardService.get_domain_name(admin_id)

        # Fetch the content data as a dictionary
        content_data = await DashboardRepo.get_content_data(domain_name)

        if not content_data or not content_data.get("metrics"):
            return {
                "video_metrics": {},
                "content_metrics": {},
                "button_clicks": {}
            }

        # Initialize data structures for metrics
        video_metrics = defaultdict(dict)
        content_metrics = defaultdict(dict)
        button_clicks = defaultdict(int)

        # Process the metrics from the content data
        metrics = content_data["metrics"]
        for metric in metrics:
            if metric["type"] == "VIDEO":
                video_metrics[metric["title"]] = {
                    "views": metric.get("views", 0),
                    "likes": metric.get("likes", 0),
                    "cta_clicks": metric.get("cta_clicks", 0),
                    "subscribers": metric.get("subscribers", 0),
                    "child_buttons": metric.get("child_buttons",{}),
                    "avg_watch_time": (metric.get("sum_watch_time", 0) / metric["views"]) if metric.get("views") else 0,
                    "avg_completion_rate": (metric.get("sum_completion_rate", 0) / metric["views"]) if metric.get("views") else 0,
                    "subscription_rate": (metric.get("subscribers", 0) / metric["views"]) if metric.get("views") else 0,
                    "like_rate": (metric.get("likes", 0) / metric["views"]) if metric.get("views") else 0
                }
            elif metric["type"] == "CONTENT":
                content_metrics[metric["title"]] = {
                    "views": metric.get("views", 0),
                    "likes": metric.get("likes", 0),
                    "cta_clicks": metric.get("cta_clicks", 0),
                    "subscribers": metric.get("subscribers", 0),
                    "child_buttons": metric.get("child_buttons",{}),
                    "avg_scroll_depth": (metric.get("sum_scroll_depth", 0) / metric["views"]) if metric.get("views") else 0,
                    "avg_watch_time": (metric.get("sum_watch_time", 0) / metric["views"]) if metric.get("views") else 0,
                    "avg_completion_rate": (metric.get("sum_completion_rate", 0) / metric["views"]) if metric.get("views") else 0,
                    "subscription_rate": (metric.get("subscribers", 0) / metric["views"]) if metric.get("views") else 0,
                    "like_rate": (metric.get("likes", 0) / metric["views"]) if metric.get("views") else 0
                }
            elif metric["type"] == "BUTTON":
                button_clicks[metric["title"]] += metric.get("clicks", 0)

        # Return structured metrics
        return {
            "video_metrics": dict(video_metrics),
            "content_metrics": dict(content_metrics),
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

        


