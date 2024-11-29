from pymongo import MongoClient
from datetime import datetime, timedelta
from bson import ObjectId

# Connect to MongoDB
client = MongoClient("mongodb+srv://spandanbhattarai79:spandan123@spandan.ey3fvll.mongodb.net/")
db = client["USER_ANALYSIS"]

# Dummy data for "admin" collection
admin_data = [
    {
        "username": "admin1",
        "password": "password1",
        "domain_name": "example.com",
        "users_list": ["user1", "user2"]
    },
    {
        "username": "admin2",
        "password": "password2",
        "domain_name": "example2.com",
        "users_list": ["user3"]
    }
]
db.admin.insert_many(admin_data)

# Dummy data for "count_model" collection
count_model_data = [
    {
        "domain_name": "example.com",
        "page_counts": {"home": 100, "about": 50, "contact": 30},
        "os_counts": {"Windows": 80, "MacOS": 60, "Linux": 30},
        "browser_counts": {"Chrome": 120, "Firefox": 40, "Safari": 20},
        "device_counts": {"Mobile": 100, "Desktop": 70, "Tablet": 30},
        "bounce_counts": 10,
        "bounce_counts_per_page": {"home": 5, "about": 3, "contact": 2}
    },
    {
        "domain_name": "example2.com",
        "page_counts": {"home": 200, "about": 80, "contact": 50},
        "os_counts": {"Windows": 150, "MacOS": 90, "Linux": 60},
        "browser_counts": {"Chrome": 220, "Firefox": 70, "Safari": 30},
        "device_counts": {"Mobile": 180, "Desktop": 100, "Tablet": 40},
        "bounce_counts": 20,
        "bounce_counts_per_page": {"home": 12, "about": 6, "contact": 2}
    }
]
db.counts.insert_many(count_model_data)

# Additional static session data
additional_session_data = [
    {
        "event": "video_watch",
        "user_id": "user1",
        "username": "user1",
        "session_start": datetime(2024, 10, 15, 10, 0, 0),
        "session_end": datetime(2024, 10, 15, 11, 0, 0),
        "path_history": ["/videos", "/home"],
        "bounce": False,
        "domain_name": "example.com",
        "location": {"latitude": 37.7749, "longitude": -122.4194},
        "device_stats": {"deviceType": "Tablet", "browser": "Safari", "os": "iOS"},
        "interaction": {
            "video_data": [
                {
                    "content_type": "video",
                    "title": "Intro to Example",
                    "started_watching": datetime(2024, 10, 15, 10, 0, 0),
                    "last_interaction": datetime(2024, 10, 15, 10, 30, 0),
                    "total_watch_time": 30.0,
                    "session_information": [
                        {
                            "start_time": datetime(2024, 10, 15, 10, 0, 0),
                            "end_time": datetime(2024, 10, 15, 10, 30, 0),
                            "duration": 30.0,
                            "completed": True
                        }
                    ],
                    "ended": True
                }
            ],
            "button_data": [
                {"content_type": "button", "click": 5, "content_title": "Subscribe", "contents_type": "cta"}
            ],
            "contents_data": [
                {
                    "content_type": "article",
                    "content_title": "Learn More About Us",
                    "start_watch_time": datetime(2024, 10, 15, 9, 50, 0),
                    "ended_watch_time": datetime(2024, 10, 15, 10, 0, 0),
                    "scrolled_depth": "75%",
                    "isactive": True
                }
            ],
            "child_buttons_data": []
        }
    },
    {
        "event": "page_view",
        "user_id": "user3",
        "username": "user3",
        "session_start": datetime(2024, 9, 10, 14, 0, 0),
        "session_end": datetime(2024, 9, 10, 14, 30, 0),
        "path_history": ["/home", "/features", "/contact"],
        "bounce": False,
        "domain_name": "example2.com",
        "location": {"latitude": 51.5074, "longitude": -0.1278},
        "device_stats": {"deviceType": "Mobile", "browser": "Chrome", "os": "Android"},
        "interaction": {
            "video_data": [],
            "button_data": [
                {"content_type": "button", "click": 3, "content_title": "Contact Us", "contents_type": "navigation"}
            ],
            "contents_data": [],
            "child_buttons_data": []
        }
    },
    {
        "event": "page_scroll",
        "user_id": "user2",
        "username": "user2",
        "session_start": datetime(2024, 8, 20, 16, 0, 0),
        "session_end": datetime(2024, 8, 20, 16, 30, 0),
        "path_history": ["/home", "/products", "/details"],
        "bounce": False,
        "domain_name": "example.com",
        "location": {"latitude": 48.8566, "longitude": 2.3522},
        "device_stats": {"deviceType": "Desktop", "browser": "Firefox", "os": "Linux"},
        "interaction": {
            "video_data": [],
            "button_data": [],
            "contents_data": [
                {
                    "content_type": "product",
                    "content_title": "Product A",
                    "start_watch_time": datetime(2024, 8, 20, 16, 10, 0),
                    "ended_watch_time": datetime(2024, 8, 20, 16, 15, 0),
                    "scrolled_depth": "90%",
                    "isactive": True
                }
            ],
            "child_buttons_data": []
        }
    },
    {
        "event": "video_watch",
        "user_id": "user1",
        "username": "user1",
        "session_start": datetime(2024, 7, 5, 10, 0, 0),
        "session_end": datetime(2024, 7, 5, 10, 20, 0),
        "path_history": ["/home", "/videos", "/tutorial"],
        "bounce": False,
        "domain_name": "example.com",
        "location": {"latitude": 40.7306, "longitude": -73.9352},
        "device_stats": {"deviceType": "Desktop", "browser": "Edge", "os": "Windows"},
        "interaction": {
            "video_data": [
                {
                    "content_type": "video",
                    "title": "Advanced Tutorial",
                    "started_watching": datetime(2024, 7, 5, 10, 0, 0),
                    "last_interaction": datetime(2024, 7, 5, 10, 10, 0),
                    "total_watch_time": 10.0,
                    "session_information": [
                        {
                            "start_time": datetime(2024, 7, 5, 10, 0, 0),
                            "end_time": datetime(2024, 7, 5, 10, 10, 0),
                            "duration": 10.0,
                            "completed": False
                        }
                    ],
                    "ended": False
                }
            ],
            "button_data": [],
            "contents_data": [],
            "child_buttons_data": []
        }
    }
]

# Insert additional session data into the collection
session_result = db.session_data.insert_many(additional_session_data)


# Dummy data for "user" collection
user_data = [
    {
        "user_id": "user1",
        "username": "user1",
        "domain_name": "example.com",
        "date_joined": datetime.now(),
        "session_ids": [str(session_result.inserted_ids[0]),str(session_result.inserted_ids[1])]
    },
    {
        "user_id": "user2",
        "username": "user2",
        "domain_name": "example.com",
        "date_joined": datetime.now().replace(
            year=datetime.now().year - 1, month=12
        ) if datetime.now().month == 1 else datetime.now().replace(
            month=datetime.now().month - 1
        ),
        "session_ids": [str(session_result.inserted_ids[2]), str(session_result.inserted_ids[3])]
    },
    {
        "user_id": "user3",
        "username": "user3",
        "domain_name": "example2.com",
        "date_joined": datetime.now(),
        "session_ids": []
    }
]
db.user.insert_many(user_data)
