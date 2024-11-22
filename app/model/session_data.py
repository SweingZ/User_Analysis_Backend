from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class DeviceStats(BaseModel):
    os : Optional[str] = None
    browser : Optional[str] = None
    device : Optional[str] = None

class Location(BaseModel):
    latitude : Optional[float] = None
    longitude : Optional[float] = None

class ContentData(BaseModel):
    content_type:  Optional[str] = None
    content_title:  Optional[str] = None
    start_watch_time:  Optional[str] = None
    ended_watch_time: Optional[str] = None
    scrolled_depth: Optional[str] = None

class SessionData(BaseModel):
    session_start : Optional[datetime] = None
    session_end : Optional[datetime] = None
    path_history : Optional[List[str]] = None
    bounce : Optional[bool] = None
    device_stats : Optional[DeviceStats] = None
    location : Optional[Location] = None
    contents_data: Optional[List[ContentData]] = None


