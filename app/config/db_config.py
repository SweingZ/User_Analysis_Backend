import motor.motor_asyncio

class MongoDB:
    def __init__(self):
        self.client = None
        self.database = None
        self.collections = {}
        

    async def connect(self, uri: str, db_name: str):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(uri)   
        self.database = self.client[db_name]
        collection_names = ['user','session_data']
        self.collections = {name: self.database[name] for name in collection_names}
        print("MongoDB connected")


    async def close(self):
        self.client.close()
        print("MongoDB connection closed")

# MongoDB connection details
MONGO_URI = 'mongodb+srv://spandanbhattarai79:spandan123@spandan.ey3fvll.mongodb.net/'
DATABASE_NAME = 'USER_ANALYSIS'

mongodb = MongoDB()
