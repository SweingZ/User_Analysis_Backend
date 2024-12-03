from bson import ObjectId
from app.config.db_config import mongodb
from datetime import datetime


class DashboardRepo:
    @staticmethod
    async def get_total_visitors(domain_name: str):
        return await mongodb.collections["user"].count_documents({"domain_name":domain_name})

    @staticmethod
    async def get_total_visits(domain_name: str):
        return await mongodb.collections["session_data"].count_documents({"domain_name": domain_name})

    @staticmethod
    async def get_session_data(domain_name: str):
        return await mongodb.collections["session_data"].find({"domain_name": domain_name}).to_list(length=None)

    @staticmethod
    async def get_page_view_analysis(domain_name: str):
        return await mongodb.collections["counts"].find_one({"domain_name": domain_name}, {"page_counts": 1, "_id": 0})

    @staticmethod
    async def get_bounce_count(domain_name: str):
        return await mongodb.collections["counts"].find_one({"domain_name": domain_name}, {"bounce_counts": 1, "_id": 0})
    
    @staticmethod
    async def get_count_data(domain_name: str):
        return await mongodb.collections["counts"].find_one({"domain_name":domain_name})
    
    @staticmethod
    async def get_content_data(domain_name: str):
        return await mongodb.collections["content"].find_one({"domain_name":domain_name})

    @staticmethod
    async def get_total_visits_in_range(start_date: datetime, end_date: datetime, domain_name: str):
        return await mongodb.collections["session_data"].count_documents({
            "session_start": {"$gte": start_date},
            "session_end": {"$lte": end_date},
            "domain_name": domain_name
        })

    @staticmethod
    async def get_session_data_in_range(start_date: datetime, end_date: datetime, domain_name: str):
        return await mongodb.collections["session_data"].find({
            "session_start": {"$gte": start_date},
            "session_end": {"$lte": end_date},
            "domain_name": domain_name
        }).to_list(length=None)
    
    @staticmethod
    async def get_users_joined_in_range(start_date, end_date, domain_name):
        return await mongodb.collections["user"].count_documents(
            {
                "date_joined": {"$gte": start_date, "$lte": end_date},
                "domain_name": domain_name
            }
        )
    
    @staticmethod
    async def get_location_and_referrer_data(domain_name: str):
        return await mongodb.collections["session_data"].find(
            {"domain_name": domain_name},  # Filter by domain_name
            {"_id": 0, "location": 1,"referrer": 1}      # Project only the location field
        ).to_list(length=None)


