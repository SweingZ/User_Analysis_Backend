from typing import List, Optional
from pydantic import BaseModel

class User(BaseModel):
    session_ids : Optional[List[str]] = None