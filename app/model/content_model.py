from typing import List, Optional
from pydantic import BaseModel, Field

class Metric(BaseModel):
    type: str  # 'content', 'video', 'button', etc.
    title: str
    views: Optional[int] = Field(default=None, ge=0)
    likes: Optional[int] = Field(default=None, ge=0)
    avg_scroll_depth: Optional[float] = Field(default=None, ge=0)
    avg_watch_time: Optional[float] = Field(default=None, ge=0)
    avg_completion_rate: Optional[float] = Field(default=None, ge=0, le=100)
    clicks: Optional[int] = Field(default=None, ge=0)

class Content(BaseModel):
    domain_name: str
    metrics: List[Metric]

    class Config:
        schema_extra = {
            "example": {
                "domain_name": "example.com",
                "metrics": [
                    {
                        "type": "content",
                        "title": "Apple",
                        "views": 10,
                        "likes": 4,
                        "avg_scroll_depth": 80.12,
                        "avg_completion_rate": 77,
                    },
                    {
                        "type": "video",
                        "title": "Cat in a Hat",
                        "views": 1009,
                        "likes": 900,
                        "avg_watch_time": 90,
                        "avg_completion_rate": 100
                    },
                    {
                        "type": "button",
                        "title": "Click Me",
                        "clicks": 100
                    }
                ]
            }
        }
