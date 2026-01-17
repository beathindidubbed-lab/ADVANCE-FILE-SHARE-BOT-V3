"""
Database Handler - MongoDB Operations
Complete version matching bot.py requirements
"""

import motor.motor_asyncio
import datetime
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class Database:
    """MongoDB database operations for File Sharing Bot"""
    
    def __init__(self, database_url: str, database_name: str):
        self.client = None
        self.db = None
        self.users = None
        self.banned = None
        self.settings = None
        self.special_links = None
        self.channels = None
        self.force_sub = None
        self.admins = None
        self.join_requests = None
        self.database_url = database_url
        self.database_name = database_name
    
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(self.database_url)
            self.db = self.client[self.database_name]
            
            # Collections
            self.users = self.db.users
            self.banned = self.db.banned
            self.settings = self.db.settings
            self.special_links = self.db.special_links
            self.channels = self.db.channels
            self.force_sub = self.db.force_sub
            self.admins = self.db.admins
            self.join_requests = self.db.join_requests
            
            # Create indexes for performance
            await self.users.create_index("user_id", unique=True)
            await self.banned.create_index("user_id", unique=True)
            await self.settings.create_index("key", unique=True)
            await self.special_links.create_index("link_id", unique=True)
            await self.channels.create_index("channel_id", unique=True)
            await self.force_sub.create_index("channel_id", unique=True)
            await self.admins.create_index("user_id", unique=True)
            await self.join_requests.create_index([("user_id", 1), ("channel_id", 1)], unique=True)
            
            logger.info("✅ Connected to MongoDB successfully")
            return True
            
        except Exception as e:
            logger.error(f"✗ MongoDB connection failed: {e}")
            return False
    
    async def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            logger.info("✅ MongoDB connection closed")
    
    # ===================================
    # USER OPERATIONS
    # ===================================
    
    async def add_user(self, user_id: int, first_name: str, username: str = None):
        """Add new user to database"""
        user_data = {
            "user_id": user_id,
            "first_name": first_name,
            "username": username,
            "joined_date": datetime.datetime.now(datetime.timezone.utc),
            "last_active": datetime.datetime.now(datetime.timezone.utc)
        }
        
        try:
            await self.users.update_one(
                {"user_id": user_id},
                {"$set": user_data},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error adding user {user_id}: {e}")
            return False
    
    async def get_user(self, user_id: int):
        """Get user data"""
        try:
            return await self.users.find_one({"user_id": user_id})
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    async def update_user_activity(self, user_id: int):
        """Update user's last active time"""
        try:
            await self.users.update_one(
                {"user_id": user_id},
                {"$set": {"last_active": datetime.datetime.now(datetime.timezone.utc)}}
            )
        except Exception as e:
            logger.error(f"Error updating user activity for {user_id}: {e}")
    
    async def is_user_exist(self, user_id: int):
        """Check if user exists"""
        user = await self.get_user(user_id)
        return user is not None
    
    async def total_users_count(self):
        """Get total users count"""
        try:
            return await self.users.count_documents({})
        except Exception as e:
            logger.error(f"Error getting user count: {e}")
            return 0
    
    async def get_all_users(self):
        """Get all user IDs"""
        try:
            cursor = self.users.find({}, {"user_id": 1})
            user_ids = []
            async for doc in cursor:
                user_ids.append(doc["user_id"])
            return user_ids
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
    async def delete_user(self, user_id: int):
        """Delete user from database"""
        try:
            await self.users.delete_one({"user_id": user_id})
            return True
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {e}")
            return False
    
    # ===================================
    # BAN OPERATIONS
    # ===================================
    
    async def ban_user(self, user_id: int, reason: str = None):
        """Ban a user"""
        ban_data = {
            "user_id": user_id,
            "reason": reason,
            "banned_date": datetime.datetime.now(datetime.timezone.utc)
        }
        
        try:
            await self.banned.update_one(
                {"user_id": user_id},
                {"$set": ban_data},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error banning user {user_id}: {e}")
            return False
    
    async def unban_user(self, user_id: int):
        """Unban a user"""
        try:
            result = await self.banned.delete_one({"user_id": user_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error unbanning user {user_id}: {e}")
            return False
    
    async def is_user_banned(self, user_id: int):
        """Check if user is banned"""
        try:
            ban = await self.banned.find_one({"user_id": user_id})
            return ban is not None
        except Exception as e:
            logger.error(f"Error checking ban status for {user_id}: {e}")
            return False
    
    async def get_banned_users(self):
        """Get all banned users"""
        try:
            cursor = self.banned.find({})
            banned = []
            async for doc in cursor:
                banned.append(doc)
            return banned
        except Exception as e:
            logger.error(f"Error getting banned users: {e}")
            return []
    
    async def get_banned_count(self):
        """Get banned users count"""
        try:
            return await self.banned.count_documents({})
        except Exception as e:
            logger.error(f"Error getting banned count: {e}")
            return 0
    
    # ===================================
    # SETTINGS OPERATIONS
    # ===================================
    
    async def save_settings(self, settings: dict):
        """Save bot settings"""
        try:
            await self.settings.update_one(
                {"key": "bot_settings"},
                {"$set": settings},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            return False
    
    async def get_settings(self):
        """Get bot settings with THREE separate auto-delete features"""
        try:
            settings = await self.settings.find_one({"key": "bot_settings"})
            if not settings:
                # Default settings with THREE SEPARATE AUTO-DELETE FEATURES
                default_settings = {
                    "key": "bot_settings",
                    
                    # File protection settings
                    "protect_content": True,
                    "hide_caption": False,
                    "channel_button": True,
                    
                    # THREE SEPARATE AUTO-DELETE FEATURES
                    "clean_conversation": True,  # Feature 1: Delete previous bot message
                    "auto_delete": False,         # Feature 2: Auto delete file messages
                    "auto_delete_time": 300,      # Feature 2: Delete timer (5 minutes)
                    "show_instruction": True,     # Feature 3: Show instruction after deletion
                    
                    # Force subscribe settings
                    "request_fsub": False,
                    
                    # Custom buttons and texts
                    "custom_button": "",
                    "welcome_text": "",
                    "help_text": "",
                    "about_text": "",
                    
                    # Images for different panels
                    "bot_pics": [],
                    "welcome_pics": [],
                    "help_pics": [],
                    "files_pics": [],
                    "auto_del_pics": [],
                    "force_sub_pics": [],
                    
                    # Database channel
                    "db_channel_id": None,
                    
                    # Auto approve join requests
                    "auto_approve": False,
                    
                    # Auto clean old join requests
                    "auto_clean_join_requests": True
                }
                await self.save_settings(default_settings)
                logger.info("✅ Created default settings with THREE auto-delete features")
                return default_settings
            return settings
        except Exception as e:
            logger.error(f"Error getting settings: {e}")
            return {}
    
    async def update_setting(self, key: str, value):
        """Update a specific setting"""
        try:
            await self.settings.update_one(
                {"key": "bot_settings"},
                {"$set": {key: value}},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error updating setting {key}: {e}")
            return False
    
    async def get_setting(self, key: str):
        """Get a specific setting"""
        try:
            settings = await self.get_settings()
            return settings.get(key)
        except Exception as e:
            logger.error(f"Error getting setting {key}: {e}")
            return None
    
    async def get_db_channel(self):
        """Get database channel ID"""
        try:
            settings = await self.get_settings()
            return settings.get("db_channel_id")
        except Exception as e:
            logger.error(f"Error getting db channel: {e}")
            return None
    
    async def set_db_channel(self, channel_id: int):
        """Set database channel ID"""
        return await self.update_setting("db_channel_id", channel_id)
    
    async def remove_db_channel(self):
        """Remove database channel"""
        return await self.update_setting("db_channel_id", None)
    
    # ===================================
    # SPECIAL LINKS OPERATIONS
    # ===================================
    
    async def save_special_link(self, link_id: str, message: str, files: list):
        """Save special link with custom message"""
        link_data = {
            "link_id": link_id,
            "message": message,
            "files": files,
            "created_date": datetime.datetime.now(datetime.timezone.utc)
        }
        
        try:
            await self.special_links.update_one(
                {"link_id": link_id},
                {"$set": link_data},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error saving special link {link_id}: {e}")
            return False
    
    async def get_special_link(self, link_id: str):
        """Get special link data"""
        try:
            return await self.special_links.find_one({"link_id": link_id})
        except Exception as e:
            logger.error(f"Error getting special link {link_id}: {e}")
            return None
    
    async def delete_special_link(self, link_id: str):
        """Delete special link"""
        try:
            await self.special_links.delete_one({"link_id": link_id})
            return True
        except Exception as e:
            logger.error(f"Error deleting special link {link_id}: {e}")
            return False
    
    # ===================================
    # FORCE SUBSCRIBE OPERATIONS
    # ===================================
    
    async def add_force_sub_channel(self, channel_id: int, channel_username: str = None):
        """Add force subscribe channel"""
        channel_data = {
            "channel_id": channel_id,
            "channel_username": channel_username,
            "added_date": datetime.datetime.now(datetime.timezone.utc)
        }
        
        try:
            await self.force_sub.update_one(
                {"channel_id": channel_id},
                {"$set": channel_data},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error adding force sub channel {channel_id}: {e}")
            return False
    
    async def remove_force_sub_channel(self, channel_id: int):
        """Remove force subscribe channel"""
        try:
            await self.force_sub.delete_one({"channel_id": channel_id})
            return True
        except Exception as e:
            logger.error(f"Error removing force sub channel {channel_id}: {e}")
            return False
    
    async def get_force_sub_channels(self):
        """Get all force subscribe channels"""
        try:
            cursor = self.force_sub.find({})
            channels = []
            async for doc in cursor:
                channels.append({
                    "channel_id": doc["channel_id"],
                    "channel_username": doc.get("channel_username")
                })
            return channels
        except Exception as e:
            logger.error(f"Error getting force sub channels: {e}")
            return []
    
    async def clear_force_sub_channels(self):
        """Clear all force subscribe channels"""
        try:
            await self.force_sub.delete_many({})
            return True
        except Exception as e:
            logger.error(f"Error clearing force sub channels: {e}")
            return False
    
    # ===================================
    # ADMIN OPERATIONS
    # ===================================
    
    async def add_admin(self, user_id: int):
        """Add admin to database"""
        admin_data = {
            "user_id": user_id,
            "added_date": datetime.datetime.now(datetime.timezone.utc)
        }
        
        try:
            await self.admins.update_one(
                {"user_id": user_id},
                {"$set": admin_data},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error adding admin {user_id}: {e}")
            return False
    
    async def remove_admin(self, user_id: int):
        """Remove admin from database"""
        try:
            await self.admins.delete_one({"user_id": user_id})
            return True
        except Exception as e:
            logger.error(f"Error removing admin {user_id}: {e}")
            return False
    
    async def get_admins(self):
        """Get all admins from database"""
        try:
            cursor = self.admins.find({})
            admins = []
            async for doc in cursor:
                admins.append(doc["user_id"])
            return admins
        except Exception as e:
            logger.error(f"Error getting admins: {e}")
            return []
    
    async def is_admin(self, user_id: int):
        """Check if user is admin in database"""
        try:
            admin = await self.admins.find_one({"user_id": user_id})
            return admin is not None
        except Exception as e:
            logger.error(f"Error checking admin status for {user_id}: {e}")
            return False
    
    # ===================================
    # JOIN REQUESTS OPERATIONS
    # ===================================
    
    async def save_join_request(self, user_id: int, channel_id: int, status: str = "pending"):
        """Save join request"""
        request_data = {
            "user_id": user_id,
            "channel_id": channel_id,
            "status": status,
            "request_date": datetime.datetime.now(datetime.timezone.utc),
            "processed_date": None if status == "pending" else datetime.datetime.now(datetime.timezone.utc)
        }
        
        try:
            await self.join_requests.update_one(
                {"user_id": user_id, "channel_id": channel_id},
                {"$set": request_data},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error saving join request for {user_id}: {e}")
            return False
    
    async def get_pending_requests(self, channel_id: int = None):
        """Get pending join requests"""
        try:
            query = {"status": "pending"}
            if channel_id:
                query["channel_id"] = channel_id
            
            cursor = self.join_requests.find(query)
            requests = []
            async for doc in cursor:
                requests.append(doc)
            return requests
        except Exception as e:
            logger.error(f"Error getting pending requests: {e}")
            return []
    
    async def update_request_status(self, user_id: int, channel_id: int, status: str):
        """Update join request status"""
        try:
            await self.join_requests.update_one(
                {"user_id": user_id, "channel_id": channel_id},
                {"$set": {
                    "status": status,
                    "processed_date": datetime.datetime.now(datetime.timezone.utc)
                }}
            )
            return True
        except Exception as e:
            logger.error(f"Error updating request status for {user_id}: {e}")
            return False
    
    async def clean_old_join_requests(self):
        """Clean join requests older than 24 hours"""
        try:
            cutoff_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=24)
            
            result = await self.join_requests.delete_many({
                "request_date": {"$lt": cutoff_time}
            })
            
            if result.deleted_count > 0:
                logger.info(f"✅ Auto-cleaned {result.deleted_count} old join requests")
                return result.deleted_count
            else:
                logger.info("✅ No old join requests to clean")
                return 0
                
        except Exception as e:
            logger.error(f"✗ Error cleaning old join requests: {e}")
            return 0
