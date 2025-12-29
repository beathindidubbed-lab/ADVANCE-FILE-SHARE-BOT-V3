"""
Database Handler - MongoDB Operations
"""

import motor.motor_asyncio
from config import DATABASE_URI, DATABASE_NAME

class Database:
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(DATABASE_URI)
        self.db = self.client[DATABASE_NAME]
        self.users = self.db.users
        self.banned = self.db.banned
        self.settings = self.db.settings

    async def connect(self):
        """Test database connection"""
        await self.client.server_info()

    # ========== USER MANAGEMENT ==========
    async def add_user(self, user_id):
        """Add user to database"""
        try:
            await self.users.insert_one({"_id": user_id})
            return True
        except:
            return False

    async def is_user_exist(self, user_id):
        """Check if user exists"""
        user = await self.users.find_one({"_id": user_id})
        return bool(user)

    async def total_users_count(self):
        """Get total users"""
        return await self.users.count_documents({})

    async def get_all_users(self):
        """Get all user IDs"""
        return [user['_id'] async for user in self.users.find({})]

    async def delete_user(self, user_id):
        """Delete user"""
        await self.users.delete_one({"_id": user_id})

    # ========== BAN MANAGEMENT ==========
    async def ban_user(self, user_id):
        """Ban a user"""
        try:
            await self.banned.insert_one({"_id": user_id})
            return True
        except:
            return False

    async def unban_user(self, user_id):
        """Unban a user"""
        await self.banned.delete_one({"_id": user_id})

    async def is_user_banned(self, user_id):
        """Check if user is banned"""
        user = await self.banned.find_one({"_id": user_id})
        return bool(user)

    async def get_banned_users(self):
        """Get all banned user IDs"""
        return [user['_id'] async for user in self.banned.find({})]

    # ========== SETTINGS MANAGEMENT ==========
    async def get_settings(self):
        """Get bot settings"""
        settings = await self.settings.find_one({"_id": "bot_settings"})
        if not settings:
            # Default settings
            default_settings = {
                "_id": "bot_settings",
                "protect_content": True,
                "hide_caption": False,
                "channel_button": True,
                "auto_delete": False,
                "auto_delete_time": 300,
                "request_fsub": False,
                "custom_button": ""
            }
            await self.settings.insert_one(default_settings)
            return default_settings
        return settings

    async def update_setting(self, key, value):
        """Update a specific setting"""
        await self.settings.update_one(
            {"_id": "bot_settings"},
            {"$set": {key: value}},
            upsert=True
        )

    async def get_setting(self, key):
        """Get a specific setting"""
        settings = await self.get_settings()
        return settings.get(key)
