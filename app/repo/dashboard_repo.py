from app.config.db_config import mongodb
from datetime import datetime


class DashboardRepo:
    @staticmethod
    async def get_total_visitors():
        return await mongodb.collections["user"].count_documents({})

    @staticmethod
    async def get_total_visits():
        return await mongodb.collections["session_data"].count_documents({})

    @staticmethod
    async def get_session_data():
        return await mongodb.collections["session_data"].find({}).to_list(length=None)

    @staticmethod
    async def get_page_view_analysis():
        return await mongodb.collections["counts"].find_one({}, {"page_counts": 1, "_id": 0})

    @staticmethod
    async def get_bounce_count():
        return await mongodb.collections["counts"].find_one({}, {"bounce_counts": 1, "_id": 0})

    @staticmethod
    async def get_total_visits_in_range(start_date: datetime, end_date: datetime):
        return await mongodb.collections["session_data"].count_documents({
            "session_start": {"$gte": start_date},
            "session_end": {"$lte": end_date},
        })

    @staticmethod
    async def get_session_data_in_range(start_date: datetime, end_date: datetime):
        return await mongodb.collections["session_data"].find({
            "session_start": {"$gte": start_date},
            "session_end": {"$lte": end_date},
        }).to_list(length=None)
    
    @staticmethod
    async def get_users_joined_in_range(start_date, end_date):
        return await mongodb.collections["user"].count_documents(
            {"date_joined": {"$gte": start_date, "$lte": end_date}}
        )

