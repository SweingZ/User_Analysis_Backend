from typing import Dict
from pydantic import BaseModel

class CountModel(BaseModel):
    website: str
    page_counts: Dict[str, int]
    os_counts: Dict[str, int]
    browser_counts: Dict[str, int]
    device_counts: Dict[str, int]

    class Config:
        schema_extra = {
            "example": {
                "website": "example.com",
                "page_counts": {
                    "home": 120,
                    "about": 45,
                    "contact": 30
                },
                "os_counts": {
                    "Windows": 80,
                    "MacOS": 60,
                    "Linux": 55
                },
                "browser_counts": {
                    "Chrome": 150,
                    "Firefox": 40,
                    "Safari": 20
                },
                "device_counts": {
                    "Mobile": 100,
                    "Desktop": 110,
                    "Tablet": 10
                }
            }
        }
