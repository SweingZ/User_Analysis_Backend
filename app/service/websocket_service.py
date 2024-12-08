from datetime import datetime, timezone
from typing import Optional
from bson import ObjectId
from app.model.session_data import SessionData
from app.config.db_config import mongodb

class WebsocketService:

    @staticmethod
    async def handle_session_data(session_data: SessionData):
        """Main handler for session data processing."""
        user_id = session_data.user_id
        domain_name = session_data.domain_name

        if not user_id or not domain_name:
            print("Invalid session data. Skipping...")
            return

        # Process content metrics
        await WebsocketService.save_content_metrics(session_data)

        # Update admin user list
        await WebsocketService.update_admin_user_list(user_id, domain_name)
        
        # Save session data and update counts
        session_id = await WebsocketService.save_session_data(session_data, user_id)
        await WebsocketService.update_counts(session_data, domain_name)
        
        print(f"Processed session for user: {user_id}, domain: {domain_name}")

    @staticmethod
    async def save_content_metrics(session_data: SessionData):
        """Save or update content metrics based on the session data."""
        domain_name = session_data.domain_name
        interaction = session_data.interaction
        referrer_source = session_data.referrer.utm_source if session_data.referrer else None

        try:
            # Process video metrics
            if interaction.video_data:
                for video in interaction.video_data:
                    cta_clicks, likes, subscribers, child_buttons = WebsocketService.process_child_buttons(
                        interaction.child_buttons_data, video.title
                    )

                    update_query = {
                        "domain_name": domain_name,
                        "metrics": {
                            "$elemMatch": {
                                "title": video.title,
                                "type": "VIDEO"
                            }
                        }
                    }
                    existing_doc = await mongodb.collections["content"].find_one(update_query)

                    if existing_doc:
                        # Retrieve the existing child_buttons dictionary or initialize it
                        existing_child_buttons = next(
                            (metric.get("child_buttons", {}) for metric in existing_doc.get("metrics", [])
                            if metric["title"] == video.title and metric["type"] == "VIDEO"),
                            {}
                        )

                        # Merge existing and new child_buttons
                        for button_name, clicks in child_buttons.items():
                            child_buttons[button_name] = (
                                existing_child_buttons.get(button_name, 0) + clicks
                            )

                        update_data = {
                            "$inc": {
                                "metrics.$.views": 1,
                                "metrics.$.sum_watch_time": video.total_watch_time or 0,
                                "metrics.$.sum_completion_rate": 100 if video.ended else 0,
                                "metrics.$.cta_clicks": cta_clicks,
                                "metrics.$.likes": likes,
                                "metrics.$.subscribers": subscribers,
                            },
                            "$set": {"metrics.$.child_buttons": child_buttons}
                        }
                        if referrer_source:
                            update_data["$set"] = {
                                "metrics.$.referrer": referrer_source
                            }
                        await mongodb.collections["content"].update_one(update_query, update_data)
                    else:
                        update_data = {
                            "$push": {
                                "metrics": {
                                    "title": video.title,
                                    "type": "VIDEO",
                                    "views": 1,
                                    "likes": likes,
                                    "subscribers": subscribers,
                                    "cta_clicks": cta_clicks,
                                    "sum_watch_time": video.total_watch_time or 0,
                                    "sum_completion_rate": 100 if video.ended else 0,
                                    "referrer": referrer_source or "",
                                    "child_buttons": child_buttons
                                }
                            }
                        }
                        await mongodb.collections["content"].update_one(
                            {"domain_name": domain_name},
                            update_data,
                            upsert=True
                        )

            # Process button metrics
            if interaction.button_data:
                for button in interaction.button_data:
                    update_query = {
                        "domain_name": domain_name,
                        "metrics": {
                            "$elemMatch": {
                                "title": button.content_title,
                                "type": "BUTTON"
                            }
                        }
                    }
                    existing_doc = await mongodb.collections["content"].find_one(update_query)

                    if existing_doc:
                        update_data = {
                            "$inc": {"metrics.$.clicks": button.click or 1}
                        }
                        await mongodb.collections["content"].update_one(update_query, update_data)
                    else:
                        update_data = {
                            "$push": {
                                "metrics": {
                                    "title": button.content_title,
                                    "type": "BUTTON",
                                    "clicks": button.click or 1
                                }
                            }
                        }
                        await mongodb.collections["content"].update_one(
                            {"domain_name": domain_name},
                            update_data,
                            upsert=True
                        )

            # Process content metrics
            if interaction.contents_data:
                for content in interaction.contents_data:
                    watch_time = (
                        (content.ended_watch_time - content.start_watch_time).total_seconds()
                        if content.start_watch_time and content.ended_watch_time
                        else 0
                    )
                    completion_rate = WebsocketService.calculate_content_completion_rate(
                        word_count=content.word_count,
                        scrolled_depth=content.scrolled_depth,
                        watch_time=watch_time
                    )

                    cta_clicks, likes, subscribers, child_buttons = WebsocketService.process_child_buttons(
                        interaction.child_buttons_data, content.content_title
                    )

                    update_query = {
                        "domain_name": domain_name,
                        "metrics": {
                            "$elemMatch": {
                                "title": content.content_title,
                                "type": "CONTENT"
                            }
                        }
                    }
                    existing_doc = await mongodb.collections["content"].find_one(update_query)

                    if existing_doc:
                        # Retrieve the existing child_buttons dictionary or initialize it
                        existing_child_buttons = next(
                            (metric.get("child_buttons", {}) for metric in existing_doc.get("metrics", [])
                            if metric["title"] == content.content_title and metric["type"] == "CONTENT"),
                            {}
                        )

                        # Merge existing and new child_buttons
                        for button_name, clicks in child_buttons.items():
                            child_buttons[button_name] = (
                                existing_child_buttons.get(button_name, 0) + clicks
                            )

                        update_data = {
                            "$inc": {
                                "metrics.$.views": 1,
                                "metrics.$.sum_scroll_depth": content.scrolled_depth or 0,
                                "metrics.$.sum_watch_time": watch_time,
                                "metrics.$.sum_completion_rate": completion_rate,
                                "metrics.$.cta_clicks": cta_clicks,
                                "metrics.$.likes": likes,
                                "metrics.$.subscribers": subscribers,
                            },
                            "$set": {"metrics.$.child_buttons": child_buttons}
                        }
                        if referrer_source:
                            update_data["$set"]["metrics.$.referrer"] = referrer_source

                        await mongodb.collections["content"].update_one(update_query, update_data)
                    else:
                        # Create a new document with all the necessary fields
                        update_data = {
                            "$push": {
                                "metrics": {
                                    "title": content.content_title,
                                    "type": "CONTENT",
                                    "views": 1,
                                    "sum_scroll_depth": content.scrolled_depth or 0,
                                    "sum_watch_time": watch_time,
                                    "sum_completion_rate": completion_rate,
                                    "cta_clicks": cta_clicks,
                                    "likes": likes,
                                    "subscribers": subscribers,
                                    "referrer": referrer_source or "",
                                    "child_buttons": child_buttons
                                }
                            }
                        }
                        await mongodb.collections["content"].update_one(
                            {"domain_name": domain_name},
                            update_data,
                            upsert=True
                        )


        except Exception as e:
            print(f"Error updating content metrics for domain: {domain_name}: {e}")

    @staticmethod
    async def update_admin_user_list(user_id: str, domain_name: str):
        """Update the users_list of the Admin document."""
        admin_doc = await mongodb.collections["admin"].find_one({"domain_name": domain_name})
        if admin_doc:
            existing_users = set(admin_doc.get("users_list", []))
            existing_users.add(ObjectId(user_id))
            await mongodb.collections["admin"].update_one(
                {"domain_name": domain_name},
                {"$set": {"users_list": list(existing_users)}}
            )
        else:
            print(f"Admin document for domain {domain_name} not found. Skipping user update.")

    @staticmethod
    async def save_session_data(session_data: SessionData, user_id: str) -> ObjectId:
        """Save the session data to the database and handle the user's session IDs."""
        # Prepare the session document
        document = session_data.dict(exclude={"username"})
        document["session_start"] = document["session_start"] or datetime.now(timezone.utc)
        document["session_end"] = document["session_end"] or datetime.now(timezone.utc)

        # Insert the session document into the "session_data" collection
        session_result = await mongodb.collections["session_data"].insert_one(document)
        session_id = session_result.inserted_id

        # Check if the user exists in the "user" collection
        existing_user = await mongodb.collections["user"].find_one({"_id": ObjectId(user_id)})

        if existing_user:
            # If user exists, push the session ID into their "session_ids"
            await mongodb.collections["user"].update_one(
                {"_id": ObjectId(user_id)},
                {"$push": {"session_ids": session_id}}
            )
        else:
            # If user does not exist, create a new user document
            new_user = {
                "_id": ObjectId(user_id),
                "username": session_data.username,
                "domain_name": session_data.domain_name,
                "date_joined": datetime.utcnow(),
                "session_ids": [session_id],
            }
            await mongodb.collections["user"].insert_one(new_user)

        return session_id

    @staticmethod
    async def update_counts(session_data: SessionData, domain_name: str):
        """Update or insert counts in the counts collection."""
        update_query = {
            "$inc": {
                f"page_counts.{path}": 1 for path in session_data.path_history or []
            }
        }

        if session_data.bounce:
            # Increment overall bounce counts
            update_query["$inc"]["bounce_counts"] = 1

            # Increment bounce count for the single page in path_history
            if session_data.path_history:
                bounce_page = session_data.path_history[0]
                update_query["$inc"][f"bounce_counts_per_page.{bounce_page}"] = 1

        if session_data.device_stats:
            os_name = session_data.device_stats.os
            browser_name = session_data.device_stats.browser
            device_name = session_data.device_stats.deviceType

            if os_name:
                update_query["$inc"][f"os_counts.{os_name}"] = 1
            if browser_name:
                update_query["$inc"][f"browser_counts.{browser_name}"] = 1
            if device_name:
                update_query["$inc"][f"device_counts.{device_name}"] = 1

        await mongodb.collections["counts"].update_one(
            {"domain_name": domain_name},
            update_query,
            upsert=True
        )

    @staticmethod
    def calculate_content_completion_rate(
        word_count: Optional[int],
        scrolled_depth: Optional[float],
        watch_time: Optional[float]
    ) -> float:
        avg_reading_speed = 200
        estimated_reading_time = (word_count / avg_reading_speed) * 60 if word_count else 0
        
        scroll_completion = (scrolled_depth / 100) if scrolled_depth is not None else 0
        time_completion = (
            min(watch_time / estimated_reading_time, 1.0) if estimated_reading_time > 0 else 0
        )
        
        if scroll_completion == 1 and time_completion < 1:
            total_completion = time_completion

        elif scroll_completion < 1 and time_completion == 1:
            total_completion = scroll_completion

        elif scroll_completion < 1 and time_completion < 1:
            total_completion = scroll_completion + time_completion / 2

        else:
            total_completion = 1
        
        return total_completion * 100
    
    @staticmethod
    def process_child_buttons(child_buttons_data, parent_content_title):
        """Process child buttons data for a given parent content."""
        cta_clicks = 0
        likes = 0
        subscribers = 0
        child_buttons = {}

        if child_buttons_data:
            for child_button in child_buttons_data:
                if child_button.parent_content_title == parent_content_title:
                    # Increment CTA clicks
                    cta_clicks += child_button.click or 0
                    
                    # Check for LIKE and SUBSCRIBE types
                    if child_button.content_title == "LIKE" and (child_button.click or 0) % 2 != 0:
                        likes += 1
                    elif child_button.content_title == "SUBSCRIBE" and (child_button.click or 0) % 2 != 0:
                        subscribers += 1
                    else:
                        # Add to child_buttons dictionary for unmatched content types
                        child_buttons[child_button.content_title] = (
                            child_buttons.get(child_button.content_title, 0) + (child_button.click or 0)
                        )
        return cta_clicks, likes, subscribers, child_buttons

