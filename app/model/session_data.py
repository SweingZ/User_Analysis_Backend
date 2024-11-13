from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class SessionData(BaseModel):
    session_start : Optional[datetime] = None
    session_end : Optional[datetime] = None
    path_history : Optional[List[str]] = None
    bounce : Optional[bool] = None
