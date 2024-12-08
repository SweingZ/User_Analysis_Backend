import random
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta

# Connect to MongoDB
client = MongoClient('mongodb+srv://spandanbhattarai79:spandan123@spandan.ey3fvll.mongodb.net/')
db = client['USER_ANALYSIS']  # Replace 'spandan' with your database name

# Admin document
admin_data = {
    "_id": ObjectId("67515996bfea3e4a63ee5022"),
    "username": "spandan123",
    "password": "spandan123",
    "domain_name": "www.spandan.com",
    "users_list": [
        ObjectId("67515854bfea3e4a63ee5021"),
        ObjectId("6735c4b4120139a7ad0bb182"),
        ObjectId("6735aae7641555331ce0a330")
    ]
}

# Content document
content_data = {
    "_id": ObjectId("67515854758e0dc499de7d2f"),
    "domain_name": "www.spandan.com",
    "metrics": [
        {
            "title": "Impact Video",
            "type": "VIDEO",
            "views": 3,
            "sum_watch_time": 19.163,
            "sum_completion_rate": 77,
            "referrer": "www.twitter.com",
            "cta_clicks": 100,
            "likes": 89,
            "subscribers": 78
        },
        {
            "title": "Our Impact on It worldy",
            "type": "CONTENT",
            "views": 9,
            "sum_scroll_depth": 80,
            "sum_watch_time": 28.645,
            "sum_completion_rate": 67,
            "cta_clicks": 1000,
            "likes": 899,
            "subscribers": 100,
            "referrer": "No Source",
            "child_buttons": {
                "click_me": 20,
                "hi": 41
            }
        },
        {
            "title": "Our Achievements",
            "type": "CONTENT",
            "views": 9,
            "sum_scroll_depth": 100,
            "sum_watch_time": 28.643,
            "sum_completion_rate": 90,
            "cta_clicks": 105,
            "likes": 19999,
            "subscribers": 100,
            "referrer": "No Source",
            "child_buttons": {
                "click_me": 76,
                "hi": 41
            }        
        },
        {
            "title": "Start Project Button",
            "type": "BUTTON",
            "clicks": 22
        }
    ]
}

# Counts document
counts_data = {
    "_id": ObjectId("67515855758e0dc499de7d30"),
    "domain_name": "www.spandan.com",
    "browser_counts": {
        "Chrome": 11,
        "Edge": 4
    },
    "device_counts": {
        "Mobile": 9,
        "Desktop": 6
    },
    "os_counts": {
        "Linux": 7,
        "Windows": 6,
        "macOS": 2
    },
    "page_counts": {
        "/Home": 13,
        "/Services": 2,
        "/": 2,
        "/About": 1,
        "/Contact": 1
    },
    "bounce_counts": 4,
    "bounce_counts_per_page": {
        "/Home": 3,
        "/": 1
    }
}


# Insert documents into their respective collections
db.admin.delete_many({})
db.admin.insert_one(admin_data)
db.content.delete_many({})
db.content.insert_one(content_data)
db.counts.delete_many({})
db.counts.insert_one(counts_data)

# Predefined lists for generating realistic data
BROWSERS = ['Chrome', 'Firefox', 'Safari', 'Edge', 'Opera']
OS_LIST = ['Windows', 'macOS', 'Linux', 'Android', 'iOS']
DEVICE_TYPES = ['Desktop', 'Mobile', 'Tablet']
PAGES = ['/Home', '/Services', '/About', '/Contact', '/Projects', '/Portfolio']
CONTENT_TITLES = [
    'Impact Video', 
    'Our Impact on It worldy', 
    'Our Achievements', 
    'Company Mission', 
    'Technology Overview', 
    'Success Stories'
]
BUTTON_TITLES = [
    'Start Project Button', 
    'Contact Us', 
    'Download Brochure', 
    'Request Demo', 
    'Subscribe Newsletter'
]
LOCATIONS = [
    {'city': 'Kathmandu', 'latitude': 27.6975, 'longitude': 85.3240},
    {'city': 'Pokhara', 'latitude': 28.2096, 'longitude': 83.9856},
    {'city': 'Lalitpur', 'latitude': 27.6618, 'longitude': 85.3225},
    {'city': 'Bhaktapur', 'latitude': 27.6710, 'longitude': 85.4298},
    {'city': 'Biratnagar', 'latitude': 26.4675, 'longitude': 87.2734}
]
UTM_SOURCES = ['google', 'facebook', 'twitter', 'linkedin', 'direct']
UTM_MEDIUMS = ['cpc', 'organic', 'social', 'email', 'referral']
UTM_CAMPAIGNS = ['summer_sale', 'winter_promo', 'brand_awareness', 'product_launch']

def generate_user_data(num_users=20):
    users = []
    for i in range(num_users):
        user_id = ObjectId()
        date_joined = datetime(2024, 12, 5, 7, 37, 57, 200) + timedelta(days=random.randint(0, 30))
        
        user = {
            "_id": user_id,
            "username": f"user_{random.randint(1000, 9999)}",
            "domain_name": "www.spandan.com",
            "date_joined": date_joined,
            "session_ids": []  # Will be populated later
        }
        users.append(user)
    return users

def generate_session_data(users, num_sessions_per_user=3):
    all_sessions = []
    for user in users:
        for _ in range(random.randint(1, num_sessions_per_user)):
            location = random.choice(LOCATIONS)
            device_stats = {
                "deviceType": random.choice(DEVICE_TYPES),
                "browser": random.choice(BROWSERS),
                "os": random.choice(OS_LIST)
            }
            
            session_start = datetime(2024, 12, 5, 7, 37, 57, 200) + timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            session_end = session_start + timedelta(minutes=random.randint(5, 30))
            
            session = {
                "_id": ObjectId(),
                "event": "on_close",
                "user_id": str(user['_id']),
                "session_start": session_start,
                "session_end": session_end,
                "path_history": random.sample(PAGES, random.randint(1, 3)),
                "bounce": random.random() < 0.2,  # 20% bounce rate
                "domain_name": "www.spandan.com",
                "location": {
                    "latitude": location['latitude'],
                    "longitude": location['longitude']
                },
                "device_stats": device_stats,
                "interaction": {
                    "video_data": generate_video_interactions(),
                    "button_data": generate_button_interactions(),
                    "contents_data": generate_content_interactions(),
                    "child_buttons_data": generate_child_button_interactions()
                },
                "referrer": {
                    "utm_source": random.choice(UTM_SOURCES),
                    "utm_medium": random.choice(UTM_MEDIUMS),
                    "utm_campaign": random.choice(UTM_CAMPAIGNS)
                }
            }
            
            # Update user's session_ids
            user['session_ids'].append(session['_id'])
            
            all_sessions.append(session)
    
    return all_sessions

def generate_video_interactions():
    if random.random() < 0.7:  # 70% chance of video interaction
        video = {
            "content_type": "video",
            "title": random.choice(CONTENT_TITLES),
            "started_watching": datetime.now(),
            "last_interaction": datetime.now(),
            "total_watch_time": round(random.uniform(1, 10), 3),
            "session_information": [
                {
                    "start_time": datetime.now(),
                    "end_time": datetime.now(),
                    "duration": round(random.uniform(0.5, 3), 3),
                    "completed": random.random() < 0.5
                }
            ],
            "ended": random.random() < 0.5
        }
        return [video]
    return []

def generate_button_interactions():
    if random.random() < 0.6:  # 60% chance of button interaction
        return [{
            "content_type": "button",
            "click": random.randint(1, 15),
            "content_title": random.choice(BUTTON_TITLES),
            "contents_type": "button"
        }]
    return []

def generate_content_interactions():
    if random.random() < 0.8:  # 80% chance of content interaction
        return [{
            "content_type": random.choice(["Achievements", "Our impact", "Blog", "Case Study"]),
            "content_title": random.choice(CONTENT_TITLES),
            "word_count": random.randint(100, 1000),
            "start_watch_time": datetime.now(),
            "ended_watch_time": datetime.now() if random.random() < 0.5 else None,
            "scrolled_depth": random.randint(10, 100),
            "isactive": random.random() < 0.6
        }]
    return []

def generate_child_button_interactions():
    if random.random() < 0.5:  # 50% chance of child button interaction
        return [{
            "content_type": "button",
            "click": random.randint(1, 10),
            "content_title": random.choice(["click button", "learn more", "download"]),
            "contents_type": "button",
            "parent_content_title": random.choice(CONTENT_TITLES)
        }]
    return []

# Generate users and sessions
users = generate_user_data(20)
sessions = generate_session_data(users)

# Clear existing data (optional, be careful!)
db.user.delete_many({})
db.session_data.delete_many({})

# Insert documents into their respective collections
db.user.insert_many(users)
db.session_data.insert_many(sessions)

print(f"Inserted {len(users)} users and {len(sessions)} sessions successfully!")


print("Data inserted successfully!")
