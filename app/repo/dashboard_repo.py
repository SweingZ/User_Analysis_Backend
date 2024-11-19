from app.config.db_config import mongodb

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
        return await mongodb.collections["counts"].find_one({},{"page_counts": 1, "_id": 0})
    
    @staticmethod
    async def get_bounce_count():
        return await mongodb.collections["counts"].find_one({},{"bounce_counts": 1, "_id":0})
    
        