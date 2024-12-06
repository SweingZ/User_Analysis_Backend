from datetime import datetime
from typing import Optional
from app.model.user_model import User
from app.config.db_config import mongodb
from pymongo import DESCENDING

class UserRepo:

    @staticmethod
    async def insert_user(user: User):
        result = await mongodb.collections["user"].insert_one(user.dict())
        return result
    
    @staticmethod
    async def find_users(domain_name: str):
        pipeline = [
            {
                "$match": {
                    "domain_name": domain_name  # Filter by the given domain_name
                }
            },
            {
                "$project": {
                    "user_id": 1,
                    "username": 1,
                    "domain_name": 1,
                    "session_count": {
                        "$size": {
                            "$ifNull": ["$session_ids", []]  # Handle users with no session_ids
                        }
                    }
                }
            },
            {
                "$sort": {
                    "session_count": -1  # Sort in descending order of session_count
                }
            },
            {
                "$limit": 10  # Limit to top 10 users
            }
        ]

        result = mongodb.collections["user"].aggregate(pipeline)
        users = [user async for user in result]  # Convert the cursor to a list
        return users
    
    @staticmethod
    async def find_session_by_user_id(user_id: str, year: Optional[int], month: Optional[int]):
        query = {"user_id": user_id}
        
        # If both year and month are provided, filter sessions by month
        if year and month:
            start_date = datetime(year, month, 1)  # Start of the month
            # Set the end date to the first day of the next month
            end_date = datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1)
            
            query["session_start"] = {"$gte": start_date, "$lt": end_date}
        
        session = await mongodb.collections["session_data"].find(query, {"session_start": 1, "session_end": 1, "path_history": 1, "_id": 0}).to_list(length=None)
        return session
