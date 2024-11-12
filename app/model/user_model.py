from typing import List, Optional
from pydantic import BaseModel

class User(BaseModel):
    email : Optional[str] = None
    password : Optional[str] = None
    session_ids : Optional[List[str]] = None