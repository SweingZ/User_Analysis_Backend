from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class DeviceStats(BaseModel):
    deviceType: Optional[str] = None
    browser: Optional[str] = None
    os: Optional[str] = None

class Location(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class VideoSessionInfo(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    completed: Optional[bool] = None

class VideoData(BaseModel):
    content_type: Optional[str] = None
    title: Optional[str] = None
    started_watching: Optional[datetime] = None
    last_interaction: Optional[datetime] = None
    total_watch_time: Optional[float] = None
    session_information: Optional[List[VideoSessionInfo]] = None
    ended: Optional[bool] = None

class ButtonData(BaseModel):
    content_type: Optional[str] = None
    click: Optional[int] = None
    content_title: Optional[str] = None
    contents_type: Optional[str] = None

class ContentData(BaseModel):
    content_type: Optional[str] = None
    content_title: Optional[str] = None
    start_watch_time: Optional[datetime] = None
    ended_watch_time: Optional[datetime] = None
    scrolled_depth: Optional[str] = None
    isactive: Optional[bool] = None

class ChildButtonsData(BaseModel):
    content_type: Optional[str] = None
    click: Optional[int] = None
    content_title: Optional[str] = None
    contents_type: Optional[str] = None
    parent_content_title: Optional[str] = None

class Interaction(BaseModel):
    video_data: Optional[List[VideoData]] = None
    button_data: Optional[List[ButtonData]] = None
    contents_data: Optional[List[ContentData]] = None
    child_buttons_data: Optional[List[ChildButtonsData]] = None

class SessionData(BaseModel):
    event: Optional[str] = None
    user_id: Optional[str] = None
    username: Optional[str] = None
    session_start: Optional[datetime] = None
    session_end: Optional[datetime] = None
    path_history: Optional[List[str]] = None
    bounce: Optional[bool] = None
    domain_name: Optional[str] = None
    location: Optional[Location] = None
    device_stats: Optional[DeviceStats] = None
    interaction: Optional[Interaction] = None
