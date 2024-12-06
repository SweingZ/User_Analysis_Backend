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
