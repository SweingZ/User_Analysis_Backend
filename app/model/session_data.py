from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class SessionData(BaseModel):
    user_id : Optional[str] = None
    session_start : Optional[datetime] = None
    session_end : Optional[datetime] = None
