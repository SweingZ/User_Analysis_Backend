from typing import List, Optional
from pydantic import BaseModel

class User(BaseModel):
    user_id: str
    username: str
    domain_name: str
    session_ids : Optional[List[str]] = None