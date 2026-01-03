#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 TELEGRAM FILE SHARING BOT - UPDATED WITH ENHANCED AUTO-DELETE
Only deletes conversation messages, preserves file and instruction messages
FIXED VERSION - All issues resolved
"""

# ===================================
# SECTION 1: IMPORTS & SETUP (UPDATED)
# ===================================

import os
import re
import sys
import json
import time
import base64
import random
import asyncio
import logging
import datetime
import traceback
from typing import List, Dict, Tuple, Optional, Union
from urllib.parse import urlparse

# Pyrogram imports
from pyrogram import Client, filters, enums
from pyrogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery, InputMediaPhoto, ChatPermissions,
    ChatJoinRequest, BotCommand, BotCommandScopeAllPrivateChats,
    ChatInviteLink
)
from pyrogram.errors import (
    FloodWait, UserNotParticipant, UserIsBlocked,
    InputUserDeactivated, PeerIdInvalid, ChannelInvalid,
    ChatAdminRequired, MessageNotModified, MessageIdInvalid,
    MessageDeleteForbidden
)

# MongoDB imports
import motor.motor_asyncio
from pymongo import MongoClient
from bson.objectid import ObjectId

# Web server imports
import aiohttp
from aiohttp import web

# Additional imports
import aiofiles
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ASCII Art Banner
BANNER = r"""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║ ██████╗░███████╗░█████╗░████████╗░░░█████╗░███╗░░██╗██╗███╗░░░███╗███████╗  ║
║ ██╔══██╗██╔════╝██╔══██╗╚══██╔══╝░░██╔══██╗████╗░██║██║████╗░████║██╔════╝   ║
║ ██████╦╝█████╗░░███████║░░░██║░░░░░███████║██╔██╗██║██║██╔████╔██║█████╗░░   ║
║ ██╔══██╗██╔══╝░░██╔══██║░░░██║░░░░░██╔══██║██║╚████║██║██║╚██╔╝██║██╔══╝░░   ║
║ ██████╦╝███████╗██║░░██║░░░██║░░░░░██║░░██║██║░╚███║██║██║░╚═╝░██║███████╗   ║
║ ╚═════╝░╚══════╝╚═╝░░╚═╝░░░╚═╝░░░░░╚═╝░░╚═╝╚═╝░░╚══╝╚═╝╚═╝░░░░░╚═╝╚══════╝   ║
║                                                                             ║
║               𝙁𝙄𝙇𝙀 𝙎𝙃𝘼𝙍𝙄𝙉𝙂 𝘽𝙊𝙏 - 𝙀𝙉𝙃𝘼𝙉𝘾𝙀𝘿 𝘼𝙐𝙏𝙊-𝘿𝙀𝙇𝙀𝙏𝙀                       ║
║               𝙊𝙉𝙇𝙔 𝘾𝙊𝙉𝙑𝙀𝙍𝙎𝘼𝙏𝙄𝙊𝙉 𝙈𝙀𝙎𝙎𝘼𝙂𝙀𝙎, 𝙋𝙍𝙀𝙎𝙀𝙍𝙑𝙀𝙎 𝙁𝙄𝙇𝙀𝙎                  ║
╚════════════════════════════════════════════════════════════════════════════╝
"""

# Global constants
MAX_BATCH_SIZE = 100
MAX_SPECIAL_FILES = 50
MAX_CUSTOM_BATCH = 50
AUTO_DELETE_TIMES = [60, 300, 600, 1800, 3600]  # 1min, 5min, 10min, 30min, 1hour
DEFAULT_BOT_PICS = [
    "https://ibb.co/k6BPTc45",
    "https://ibb.co/JRnGc1cK",
    "https://ibb.co/0p5gtzGj",
    "https://ibb.co/hRjvvcZF"
]

# Start Command Reactions
REACTIONS = ["😍", "😇", "😘", "😊", "👋", "😀", "😎", "🥰", "😜", "🤩", "🤗"]

# Bot Commands Configuration
BOT_COMMANDS = {
    "all_users": [
        BotCommand("start", "Check bot status"),
        BotCommand("help", "Get help"),
        BotCommand("ping", "Check bot ping")
    ],
    "admins": [
        BotCommand("getlink", "Generate file link"),
        BotCommand("batch", "Store multiple files"),
        BotCommand("custom_batch", "Store files with custom message"),
        BotCommand("stats", "View bot statistics"),
        BotCommand("refresh", "Refresh statistics"),
        BotCommand("logs", "View bot logs"),
        BotCommand("setchannel", "Set database channel"),
        BotCommand("settings", "Bot settings"),
        BotCommand("genlink", "Generate file link"),
        BotCommand("special_link", "Create special link"),
        BotCommand("about", "About bot"),
        BotCommand("users", "User statistics"),
        BotCommand("broadcast", "Broadcast message"),
        BotCommand("ban", "Ban user"),
        BotCommand("unban", "Unban user"),
        BotCommand("admin_list", "List admins"),
        BotCommand("add_admins", "Add admins"),
        BotCommand("del_admins", "Delete admins"),
        BotCommand("banuser_list", "List banned users"),
        BotCommand("add_banuser", "Ban users"),
        BotCommand("del_banuser", "Unban users"),
        BotCommand("files", "File settings"),
        BotCommand("auto_del", "Auto delete settings"),
        BotCommand("req_fsub", "Request FSub settings"),
        BotCommand("forcesub", "Force sub commands"),
        BotCommand("botsettings", "Bot settings"),
        BotCommand("cmd", "Command list"),
        BotCommand("shortener", "URL shortener"),
        BotCommand("font", "Change font style"),
        BotCommand("checkchannel", "Check channel"),
        BotCommand("removechannel", "Remove channel"),
        BotCommand("fsub_chnl", "Force sub channels"),
        BotCommand("add_fsub", "Add force sub channel"),
        BotCommand("del_fsub", "Delete force sub channel"),
        BotCommand("done", "Finish operation")
    ]
}

# ===================================
# SECTION 2: CONFIGURATION CLASS (FIXED)
# ===================================

class Config:
    """Configuration class for environment variables"""
    
    # Telegram API - BOT
    API_ID = int(os.environ.get("API_ID", 0))
    API_HASH = os.environ.get("API_HASH", "")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
    
    # Telegram API - USER ACCOUNT (for reactions)
    USER_SESSION = os.environ.get("USER_SESSION", "")
    USER_PHONE = os.environ.get("USER_PHONE", "")
    USER_PASSWORD = os.environ.get("USER_PASSWORD", "")
    
    # Database
    DATABASE_URL = os.environ.get("DATABASE_URL", "")
    DATABASE_NAME = os.environ.get("DATABASE_NAME", "")
    
    # Bot settings
    BOT_NAME = os.environ.get("BOT_NAME", "Beat #2")
    BOT_USERNAME = os.environ.get("BOT_USERNAME", "").lstrip('@')
    OWNER_ID = int(os.environ.get("OWNER_ID", 0))
    
    # Admins (comma-separated)
    ADMINS = [int(x.strip()) for x in os.environ.get("ADMINS", "").split(",") if x.strip()]
    if OWNER_ID and OWNER_ID not in ADMINS:
        ADMINS.append(OWNER_ID)
    
    # Channels
    UPDATE_CHANNEL = os.environ.get("UPDATE_CHANNEL", "").lstrip('@')
    SUPPORT_CHAT = os.environ.get("SUPPORT_CHAT", "").lstrip('@')
    
    # Force subscribe channels (comma-separated with format: channel_id:username)
    FORCE_SUB_CHANNELS_RAW = [x.strip() for x in os.environ.get("FORCE_SUB_CHANNELS", "").split(",") if x.strip()]
    FORCE_SUB_CHANNELS = []
    
    # Welcome images (comma-separated URLs)
    BOT_PICS = [x.strip() for x in os.environ.get("BOT_PICS", "").split(",") if x.strip()]
    if not BOT_PICS:
        BOT_PICS = DEFAULT_BOT_PICS
    
    # Panel specific images
    WELCOME_PICS = [x.strip() for x in os.environ.get("WELCOME_PICS", "").split(",") if x.strip()]
    if not WELCOME_PICS:
        WELCOME_PICS = BOT_PICS
    
    HELP_PICS = [x.strip() for x in os.environ.get("HELP_PICS", "").split(",") if x.strip()]
    if not HELP_PICS:
        HELP_PICS = BOT_PICS
    
    FILES_PICS = [x.strip() for x in os.environ.get("FILES_PICS", "").split(",") if x.strip()]
    if not FILES_PICS:
        FILES_PICS = BOT_PICS
    
    AUTO_DEL_PICS = [x.strip() for x in os.environ.get("AUTO_DEL_PICS", "").split(",") if x.strip()]
    if not AUTO_DEL_PICS:
        AUTO_DEL_PICS = BOT_PICS
    
    FORCE_SUB_PICS = [x.strip() for x in os.environ.get("FORCE_SUB_PICS", "").split(",") if x.strip()]
    if not FORCE_SUB_PICS:
        FORCE_SUB_PICS = BOT_PICS
    
    # Web server
    PORT = int(os.environ.get("PORT", 8080))
    WEB_SERVER = os.environ.get("WEB_SERVER", "true").lower() == "true"
    
    # URL Shortener
    SHORTENER_API = os.environ.get("SHORTENER_API", "")
    SHORTENER_URL = os.environ.get("SHORTENER_URL", "")
    
    # Default settings
    PROTECT_CONTENT = os.environ.get("PROTECT_CONTENT", "true").lower() == "true"
    AUTO_DELETE = os.environ.get("AUTO_DELETE", "false").lower() == "true"
    AUTO_DELETE_TIME = int(os.environ.get("AUTO_DELETE_TIME", 300))
    REQUEST_FSUB = os.environ.get("REQUEST_FSUB", "false").lower() == "true"
    
    # New settings
    AUTO_APPROVE_MODE = os.environ.get("AUTO_APPROVE_MODE", "false").lower() == "true"
    
    # Auto-delete settings - ENHANCED FOR PM CLEANING
    AUTO_DELETE_BOT_MESSAGES = os.environ.get("AUTO_DELETE_BOT_MESSAGES", "true").lower() == "true"
    AUTO_DELETE_TIME_BOT = int(os.environ.get("AUTO_DELETE_TIME_BOT", 30))
    
    # Auto-clean join requests after 24 hours
    AUTO_CLEAN_JOIN_REQUESTS = os.environ.get("AUTO_CLEAN_JOIN_REQUESTS", "true").lower() == "true"
    AUTO_CLEAN_INTERVAL = int(os.environ.get("AUTO_CLEAN_INTERVAL", 86400))
    
    @classmethod
    def parse_force_sub_channels(cls):
        """Parse force subscribe channels from environment variable"""
        channels = []
        for channel_str in cls.FORCE_SUB_CHANNELS_RAW:
            if ':' in channel_str:
                channel_id_str, username = channel_str.split(':', 1)
                try:
                    channel_id = int(channel_id_str.strip())
                    username = username.strip().lstrip('@')
                    channels.append({
                        "channel_id": channel_id,
                        "channel_username": username
                    })
                except ValueError:
                    logger.error(f"Invalid channel ID format: {channel_id_str}")
            else:
                try:
                    channel_id = int(channel_str.strip())
                    channels.append({
                        "channel_id": channel_id,
                        "channel_username": None
                    })
                except ValueError:
                    logger.error(f"Invalid channel ID format: {channel_str}")
        
        cls.FORCE_SUB_CHANNELS = channels
        return channels
    
    # Validation
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        errors = []
        
        if not cls.API_ID:
            errors.append("API_ID is required")
        if not cls.API_HASH:
            errors.append("API_HASH is required")
        if not cls.BOT_TOKEN:
            errors.append("BOT_TOKEN is required")
        if not cls.DATABASE_URL:
            errors.append("DATABASE_URL is required")
        if not cls.OWNER_ID:
            errors.append("OWNER_ID is required")
        
        if not cls.USER_SESSION and not cls.USER_PHONE:
            logger.warning("⚠️  User account not configured - reactions will be disabled")
        
        if errors:
            logger.error("Configuration errors:")
            for error in errors:
                logger.error(f"  - {error}")
            return False
        
        logger.info("✓ Configuration validated successfully")
        return True
    
    @classmethod
    def print_config(cls):
        """Print configuration (without sensitive data)"""
        logger.info(f"Bot Name: {cls.BOT_NAME}")
        logger.info(f"Bot Username: @{cls.BOT_USERNAME}")
        logger.info(f"Owner ID: {cls.OWNER_ID}")
        logger.info(f"Admins: {len(cls.ADMINS)} users")
        logger.info(f"Database: {cls.DATABASE_NAME}")
        logger.info(f"Update Channel: @{cls.UPDATE_CHANNEL}")
        logger.info(f"Support Chat: @{cls.SUPPORT_CHAT}")
        logger.info(f"Force Sub Channels: {len(cls.FORCE_SUB_CHANNELS)} channels")
        logger.info(f"Auto Delete Bot Messages: {cls.AUTO_DELETE_BOT_MESSAGES}")
        logger.info(f"Auto Delete Time (Bot): {cls.AUTO_DELETE_TIME_BOT} seconds")
        logger.info("✓ Enhanced Auto-Delete: Only deletes conversation messages")

# ===================================
# SECTION 3: DATABASE CLASS (FIXED - Admin check)
# ===================================

class Database:
    """MongoDB database operations"""
    
    def __init__(self):
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
    
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(Config.DATABASE_URL)
            self.db = self.client[Config.DATABASE_NAME]
            
            # Collections
            self.users = self.db.users
            self.banned = self.db.banned
            self.settings = self.db.settings
            self.special_links = self.db.special_links
            self.channels = self.db.channels
            self.force_sub = self.db.force_sub
            self.admins = self.db.admins
            self.join_requests = self.db.join_requests
            
            # Create indexes
            await self.users.create_index("user_id", unique=True)
            await self.banned.create_index("user_id", unique=True)
            await self.settings.create_index("key", unique=True)
            await self.special_links.create_index("link_id", unique=True)
            await self.channels.create_index("channel_id", unique=True)
            await self.force_sub.create_index("channel_id", unique=True)
            await self.admins.create_index("user_id", unique=True)
            await self.join_requests.create_index([("user_id", 1), ("channel_id", 1)], unique=True)
            
            logger.info("✓ Connected to MongoDB")
            return True
            
        except Exception as e:
            logger.error(f"✗ MongoDB connection failed: {e}")
            return False
    
    async def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
    
    # ===== USER OPERATIONS =====
    
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
        return await self.users.find_one({"user_id": user_id})
    
    async def update_user_activity(self, user_id: int):
        """Update user's last active time"""
        await self.users.update_one(
            {"user_id": user_id},
            {"$set": {"last_active": datetime.datetime.now(datetime.timezone.utc)}}
        )
    
    async def is_user_exist(self, user_id: int):
        """Check if user exists"""
        user = await self.get_user(user_id)
        return user is not None
    
    async def total_users_count(self):
        """Get total users count"""
        return await self.users.count_documents({})
    
    async def get_all_users(self):
        """Get all user IDs"""
        cursor = self.users.find({}, {"user_id": 1})
        user_ids = []
        async for doc in cursor:
            user_ids.append(doc["user_id"])
        return user_ids
    
    async def delete_user(self, user_id: int):
        """Delete user from database"""
        await self.users.delete_one({"user_id": user_id})
    
    # ===== BAN OPERATIONS =====
    
    async def ban_user(self, user_id: int, reason: str = None):
        """Ban a user"""
        ban_data = {
            "user_id": user_id,
            "reason": reason,
            "banned_date": datetime.datetime.now(datetime.timezone.utc)
        }
        
        await self.banned.update_one(
            {"user_id": user_id},
            {"$set": ban_data},
            upsert=True
        )
        return True
    
    async def unban_user(self, user_id: int):
        """Unban a user"""
        result = await self.banned.delete_one({"user_id": user_id})
        return result.deleted_count > 0
    
    async def is_user_banned(self, user_id: int):
        """Check if user is banned"""
        ban = await self.banned.find_one({"user_id": user_id})
        return ban is not None
    
    async def get_banned_users(self):
        """Get all banned users"""
        cursor = self.banned.find({})
        banned = []
        async for doc in cursor:
            banned.append(doc)
        return banned
    
    async def get_banned_count(self):
        """Get banned users count"""
        return await self.banned.count_documents({})
    
    # ===== SETTINGS OPERATIONS =====
    
    async def save_settings(self, settings: dict):
        """Save bot settings"""
        await self.settings.update_one(
            {"key": "bot_settings"},
            {"$set": settings},
            upsert=True
        )
    
    async def get_settings(self):
        """Get bot settings"""
        settings = await self.settings.find_one({"key": "bot_settings"})
        if not settings:
            # Default settings
            default_settings = {
                "protect_content": Config.PROTECT_CONTENT,
                "hide_caption": False,
                "channel_button": True,
                "auto_delete": Config.AUTO_DELETE,
                "auto_delete_time": Config.AUTO_DELETE_TIME,
                "request_fsub": Config.REQUEST_FSUB,
                "custom_button": "",
                "bot_pics": Config.BOT_PICS,
                "welcome_text": "",
                "help_text": "I AM A PRIVATE FILE SHARING BOT, MEANT TO PROVIDE FILES AND NECESSARY STUFF THROUGH SPECIAL LINK FOR SPECIFIC CHANNELS.",
                "about_text": "",
                "db_channel_id": None,
                "auto_approve": Config.AUTO_APPROVE_MODE,
                "auto_delete_bot_messages": Config.AUTO_DELETE_BOT_MESSAGES,
                "auto_delete_time_bot": Config.AUTO_DELETE_TIME_BOT,
                "auto_clean_join_requests": Config.AUTO_CLEAN_JOIN_REQUESTS,
                "welcome_pics": Config.WELCOME_PICS,
                "help_pics": Config.HELP_PICS,
                "files_pics": Config.FILES_PICS,
                "auto_del_pics": Config.AUTO_DEL_PICS,
                "force_sub_pics": Config.FORCE_SUB_PICS
            }
            await self.save_settings(default_settings)
            return default_settings
        return settings
    
    async def update_setting(self, key: str, value):
        """Update a specific setting"""
        await self.settings.update_one(
            {"key": "bot_settings"},
            {"$set": {key: value}}
        )
    
    async def get_db_channel(self):
        """Get database channel ID"""
        settings = await self.get_settings()
        return settings.get("db_channel_id")
    
    async def set_db_channel(self, channel_id: int):
        """Set database channel ID"""
        await self.update_setting("db_channel_id", channel_id)
    
    async def remove_db_channel(self):
        """Remove database channel"""
        await self.update_setting("db_channel_id", None)
    
    # ===== SPECIAL LINKS =====
    
    async def save_special_link(self, link_id: str, message: str, files: list):
        """Save special link with custom message"""
        link_data = {
            "link_id": link_id,
            "message": message,
            "files": files,
            "created_date": datetime.datetime.now(datetime.timezone.utc)
        }
        
        await self.special_links.update_one(
            {"link_id": link_id},
            {"$set": link_data},
            upsert=True
        )
    
    async def get_special_link(self, link_id: str):
        """Get special link data"""
        return await self.special_links.find_one({"link_id": link_id})
    
    async def delete_special_link(self, link_id: str):
        """Delete special link"""
        await self.special_links.delete_one({"link_id": link_id})
    
    # ===== FORCE SUBSCRIBE =====
    
    async def add_force_sub_channel(self, channel_id: int, channel_username: str = None):
        """Add force subscribe channel"""
        channel_data = {
            "channel_id": channel_id,
            "channel_username": channel_username,
            "added_date": datetime.datetime.now(datetime.timezone.utc)
        }
        
        await self.force_sub.update_one(
            {"channel_id": channel_id},
            {"$set": channel_data},
            upsert=True
        )
    
    async def remove_force_sub_channel(self, channel_id: int):
        """Remove force subscribe channel"""
        await self.force_sub.delete_one({"channel_id": channel_id})
    
    async def get_force_sub_channels(self):
        """Get all force subscribe channels"""
        cursor = self.force_sub.find({})
        channels = []
        async for doc in cursor:
            channels.append({
                "channel_id": doc["channel_id"],
                "channel_username": doc.get("channel_username")
            })
        return channels
    
    async def clear_force_sub_channels(self):
        """Clear all force subscribe channels"""
        await self.force_sub.delete_many({})
    
    # ===== ADMIN OPERATIONS =====
    
    async def add_admin(self, user_id: int):
        """Add admin to database"""
        admin_data = {
            "user_id": user_id,
            "added_date": datetime.datetime.now(datetime.timezone.utc)
        }
        
        await self.admins.update_one(
            {"user_id": user_id},
            {"$set": admin_data},
            upsert=True
        )
    
    async def remove_admin(self, user_id: int):
        """Remove admin from database"""
        await self.admins.delete_one({"user_id": user_id})
    
    async def get_admins(self):
        """Get all admins"""
        cursor = self.admins.find({})
        admins = []
        async for doc in cursor:
            admins.append(doc["user_id"])
        return admins
    
    async def is_admin(self, user_id: int):
        """Check if user is admin - FIXED VERSION"""
        # First check if user is in Config.ADMINS (includes owner)
        if user_id in Config.ADMINS:
            return True
        
        # Then check database
        admin = await self.admins.find_one({"user_id": user_id})
        if admin:
            return True
        
        return False
    
    # ===== JOIN REQUESTS =====
    
    async def save_join_request(self, user_id: int, channel_id: int, status: str = "pending"):
        """Save join request"""
        request_data = {
            "user_id": user_id,
            "channel_id": channel_id,
            "status": status,
            "request_date": datetime.datetime.now(datetime.timezone.utc),
            "processed_date": None if status == "pending" else datetime.datetime.now(datetime.timezone.utc)
        }
        
        await self.join_requests.update_one(
            {"user_id": user_id, "channel_id": channel_id},
            {"$set": request_data},
            upsert=True
        )
    
    async def get_pending_requests(self, channel_id: int = None):
        """Get pending join requests"""
        query = {"status": "pending"}
        if channel_id:
            query["channel_id"] = channel_id
        
        cursor = self.join_requests.find(query)
        requests = []
        async for doc in cursor:
            requests.append(doc)
        return requests
    
    async def update_request_status(self, user_id: int, channel_id: int, status: str):
        """Update join request status"""
        await self.join_requests.update_one(
            {"user_id": user_id, "channel_id": channel_id},
            {"$set": {"status": status, "processed_date": datetime.datetime.now(datetime.timezone.utc)}}
        )
    
    async def clean_old_join_requests(self):
        """Clean join requests older than 24 hours"""
        try:
            cutoff_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=24)
            
            result = await self.join_requests.delete_many({
                "request_date": {"$lt": cutoff_time}
            })
            
            if result.deleted_count > 0:
                logger.info(f"✓ Auto-cleaned {result.deleted_count} old join requests")
                return result.deleted_count
            else:
                logger.info("✓ No old join requests to clean")
                return 0
                
        except Exception as e:
            logger.error(f"✗ Error cleaning old join requests: {e}")
            return 0

# ===================================
# SECTION 4: HELPER FUNCTIONS (FIXED - is_subscribed)
# ===================================

async def encode(string: str) -> str:
    """Base64 URL-safe encoding"""
    string_bytes = string.encode("ascii")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    return base64_bytes.decode("ascii")

async def decode(base64_string: str) -> str:
    """Base64 URL-safe decoding"""
    base64_bytes = base64_string.encode("ascii")
    string_bytes = base64.urlsafe_b64decode(base64_bytes)
    return string_bytes.decode("ascii")

async def is_subscribed(client, user_id: int, channel_ids: list) -> bool:
    """Check if user is subscribed to channels - FIXED VERSION"""
    if not channel_ids:
        return True
    
    for channel in channel_ids:
        try:
            channel_id = channel.get("channel_id")
            channel_username = channel.get("channel_username")
            
            if not channel_id and not channel_username:
                continue
            
            # Try different methods to check subscription
            success = False
            
            # Method 1: Try with channel username first (most reliable)
            if channel_username:
                try:
                    # Remove @ if present
                    username = channel_username.lstrip('@')
                    member = await client.get_chat_member(username, user_id)
                    if member.status not in ["kicked", "left", "restricted"]:
                        success = True
                        continue  # User is subscribed to this channel
                    else:
                        return False  # User is not subscribed
                except (UserNotParticipant, PeerIdInvalid, ChannelInvalid, ValueError) as e:
                    logger.debug(f"Could not check via username {channel_username}: {e}")
                    success = False
                except Exception as e:
                    logger.error(f"Error checking via username {channel_username}: {e}")
                    success = False
            
            # Method 2: Try with channel ID
            if not success and channel_id:
                try:
                    # Convert to proper format if needed
                    if isinstance(channel_id, str):
                        channel_id = int(channel_id)
                    
                    member = await client.get_chat_member(channel_id, user_id)
                    if member.status not in ["kicked", "left", "restricted"]:
                        success = True
                        continue  # User is subscribed
                    else:
                        return False  # User is not subscribed
                except (UserNotParticipant, PeerIdInvalid, ChannelInvalid, ValueError) as e:
                    logger.debug(f"Could not check via channel ID {channel_id}: {e}")
                    # Try to get channel info to create invite link
                    try:
                        chat = await client.get_chat(channel_id)
                        if hasattr(chat, 'username') and chat.username:
                            # Try with the username from chat info
                            member = await client.get_chat_member(chat.username, user_id)
                            if member.status not in ["kicked", "left", "restricted"]:
                                success = True
                                continue
                            else:
                                return False
                    except Exception as e2:
                        logger.error(f"Could not get channel info {channel_id}: {e2}")
                        return False
                except Exception as e:
                    logger.error(f"Error checking via channel ID {channel_id}: {e}")
                    return False
            
            # If both methods failed, user is not subscribed
            if not success:
                return False
                
        except Exception as e:
            logger.error(f"Error in is_subscribed for channel {channel}: {e}")
            return False
    
    return True

def format_file_size(size_in_bytes: int) -> str:
    """Format file size to human readable format"""
    if size_in_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_in_bytes >= 1024 and i < len(size_names) - 1:
        size_in_bytes /= 1024.0
        i += 1
    
    return f"{size_in_bytes:.2f} {size_names[i]}"

def format_time(seconds: int) -> str:
    """Format seconds to human readable time"""
    if seconds < 60:
        return f"{seconds} seconds"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''}"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''}"
    else:
        days = seconds // 86400
        return f"{days} day{'s' if days != 1 else ''}"

def parse_button_string(button_string: str):
    """Parse button configuration string"""
    if not button_string:
        return []
    
    buttons = []
    rows = button_string.strip().split('\n')
    
    for row in rows:
        row_buttons = []
        button_pairs = row.split(' : ')
        
        for pair in button_pairs:
            if ' | ' in pair:
                text, url = pair.split(' | ', 1)
                row_buttons.append(InlineKeyboardButton(text.strip(), url=url.strip()))
        
        if row_buttons:
            buttons.append(row_buttons)
    
    return buttons

def get_media_type(message: Message) -> str:
    """Get media type of message"""
    if message.photo:
        return "photo"
    elif message.video:
        return "video"
    elif message.document:
        return "document"
    elif message.audio:
        return "audio"
    elif message.voice:
        return "voice"
    elif message.sticker:
        return "sticker"
    elif message.animation:
        return "animation"
    else:
        return "text"

def get_random_pic(pics_list: list) -> str:
    """Get random picture from list"""
    if not pics_list:
        return random.choice(DEFAULT_BOT_PICS)
    return random.choice(pics_list)

def get_random_reaction() -> str:
    """Get random reaction emoji"""
    return random.choice(REACTIONS)

def validate_url(url: str) -> bool:
    """Validate URL format"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

# ===================================
# SECTION 5: BOT CLASS WITH ENHANCED AUTO-DELETE (FIXED)
# ===================================

class Bot(Client):
    """Main Bot Class with Enhanced Auto-Delete"""
    
    def __init__(self):
        super().__init__(
            name="auto_filter_bot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            workers=100,
            sleep_threshold=10
        )
        
        self.db = Database()
        self.settings = {}
        self.force_sub_channels = []
        self.db_channel = None
        
        # User Account for reactions
        self.user_client = None
        
        # State management
        self.batch_state = {}
        self.custom_batch_state = {}
        self.special_link_state = {}
        self.button_setting_state = {}
        self.text_setting_state = {}
        
        # ENHANCED: Store last bot message per user with type tracking
        # Types: "conversation", "file", "instruction"
        self.user_last_messages = {}
        
        # Track user file history for resend capability
        self.user_file_history = {}
        
        # Admin cache for faster access
        self.admin_cache = set()
        
        logger.info("✓ Bot instance created with enhanced auto-delete")
    
    async def is_user_admin(self, user_id: int) -> bool:
        """Check if user is admin - FIXED VERSION"""
        # Check cache first
        if user_id in self.admin_cache:
            return True
        
        # Check Config.ADMINS (includes owner)
        if user_id in Config.ADMINS:
            self.admin_cache.add(user_id)
            return True
        
        # Check database
        try:
            is_admin = await self.db.is_admin(user_id)
            if is_admin:
                self.admin_cache.add(user_id)
            return is_admin
        except Exception as e:
            logger.error(f"Error checking admin status for {user_id}: {e}")
            
            # Fallback to Config.ADMINS
            return user_id in Config.ADMINS
    
    async def refresh_admin_cache(self):
        """Refresh admin cache from database"""
        try:
            self.admin_cache.clear()
            
            # Add Config.ADMINS
            for admin_id in Config.ADMINS:
                self.admin_cache.add(admin_id)
            
            # Add database admins
            db_admins = await self.db.get_admins()
            for admin_id in db_admins:
                self.admin_cache.add(admin_id)
                
            logger.info(f"✓ Admin cache refreshed: {len(self.admin_cache)} admins")
        except Exception as e:
            logger.error(f"Error refreshing admin cache: {e}")
    
    async def start_user_account(self):
        """Start user account for reactions"""
        if Config.USER_SESSION:
            try:
                self.user_client = Client(
                    name="user_account",
                    api_id=Config.API_ID,
                    api_hash=Config.API_HASH,
                    session_string=Config.USER_SESSION,
                    workers=50,
                    sleep_threshold=10
                )
                await self.user_client.start()
                
                user_me = await self.user_client.get_me()
                logger.info(f"✓ User account started: @{user_me.username} (ID: {user_me.id})")
                return True
                
            except Exception as e:
                logger.error(f"✗ Failed to start user account: {e}")
                self.user_client = None
                return False
        
        elif Config.USER_PHONE:
            try:
                self.user_client = Client(
                    name="user_account",
                    api_id=Config.API_ID,
                    api_hash=Config.API_HASH,
                    phone_number=Config.USER_PHONE,
                    password=Config.USER_PASSWORD if Config.USER_PASSWORD else None,
                    workers=50,
                    sleep_threshold=10
                )
                await self.user_client.start()
                
                user_me = await self.user_client.get_me()
                logger.info(f"✓ User account started: @{user_me.username} (ID: {user_me.id})")
                return True
                
            except Exception as e:
                logger.error(f"✗ Failed to start user account: {e}")
                self.user_client = None
                return False
        
        else:
            logger.warning("⚠️  No user account configured - reactions will be disabled")
            return False
    
    async def stop_user_account(self):
        """Stop user account"""
        if self.user_client:
            await self.user_client.stop()
            logger.info("✓ User account stopped")
    
    async def send_reaction(self, chat_id: int, message_id: int):
        """Send reaction using user account"""
        if not self.user_client:
            return False
        
        try:
            reaction = get_random_reaction()
            
            await self.user_client.send_reaction(
                chat_id=chat_id,
                message_id=message_id,
                emoji=reaction
            )
            
            logger.info(f"✓ Reaction sent: {reaction} to message {message_id}")
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to send reaction: {e}")
            return False
    
    # ===================================
    # ENHANCED AUTO-DELETE METHODS
    # ===================================
    
    async def delete_previous_message(self, user_id: int):
        """
        Delete previous bot message for user
        
        Only deletes conversation messages, preserves file and instruction messages
        """
        if user_id in self.user_last_messages:
            try:
                msg_info = self.user_last_messages[user_id]
                
                # Only delete if it's a conversation message
                if msg_info.get("type") == "conversation":
                    await self.delete_messages(user_id, msg_info["message_id"])
                    logger.info(f"✓ Deleted previous conversation message for user {user_id}")
                
                # Remove from tracking
                del self.user_last_messages[user_id]
                
            except MessageDeleteForbidden:
                logger.warning(f"Cannot delete message for user {user_id}")
            except MessageIdInvalid:
                logger.warning(f"Message ID invalid for user {user_id}")
            except Exception as e:
                logger.error(f"Error deleting previous message for user {user_id}: {e}")
    
    async def delete_message_after_delay(self, chat_id: int, message_id: int, delay: int, msg_type: str = "conversation"):
        """
        Delete message after specified delay
        
        Only deletes conversation messages, preserves file and instruction messages
        """
        try:
            await asyncio.sleep(delay)
            
            # Double-check the message type before deleting
            user_id = chat_id
            if user_id in self.user_last_messages:
                msg_info = self.user_last_messages[user_id]
                if msg_info.get("message_id") == message_id and msg_info.get("type") == "conversation":
                    await self.delete_messages(chat_id, message_id)
                    logger.info(f"✓ Auto-deleted conversation message {message_id} in chat {chat_id} after {delay}s")
                else:
                    logger.info(f"✗ Skipped auto-delete for non-conversation message {message_id}")
            else:
                # If not tracked, assume it's a conversation message
                await self.delete_messages(chat_id, message_id)
                logger.info(f"✓ Auto-deleted message {message_id} in chat {chat_id} after {delay}s")
                
        except MessageDeleteForbidden:
            logger.warning(f"Cannot auto-delete message {message_id} in chat {chat_id}")
        except MessageIdInvalid:
            logger.warning(f"Message {message_id} already deleted in chat {chat_id}")
        except Exception as e:
            logger.error(f"Error auto-deleting message {message_id}: {e}")
    
    async def store_bot_message(self, user_id: int, message_id: int, msg_type: str = "conversation"):
        """
        Store bot message with type for tracking
        
        Types:
        - conversation: Normal chat messages (will be auto-deleted)
        - file: File messages (will NOT be auto-deleted)
        - instruction: File instruction messages (will NOT be auto-deleted)
        """
        self.user_last_messages[user_id] = {
            "message_id": message_id,
            "type": msg_type,
            "timestamp": datetime.datetime.now(datetime.timezone.utc)
        }
    
    async def track_user_files(self, user_id: int, file_ids: list, message_id: int):
        """Track files sent to user for potential resend"""
        if user_id not in self.user_file_history:
            self.user_file_history[user_id] = []
        
        self.user_file_history[user_id].append({
            "file_ids": file_ids,
            "message_id": message_id,
            "timestamp": datetime.datetime.now(datetime.timezone.utc)
        })
        
        # Keep only last 10 entries per user
        if len(self.user_file_history[user_id]) > 10:
            self.user_file_history[user_id] = self.user_file_history[user_id][-10:]
    
    async def clean_conversation(self, user_id: int):
        """Manually clean all conversation messages for user"""
        try:
            if user_id in self.user_last_messages:
                msg_info = self.user_last_messages[user_id]
                
                if msg_info.get("type") == "conversation":
                    await self.delete_messages(user_id, msg_info["message_id"])
                    del self.user_last_messages[user_id]
                    return True
        except Exception as e:
            logger.error(f"Error cleaning conversation for {user_id}: {e}")
        
        return False
    
    # ===================================
    # BOT STARTUP METHODS (FIXED)
    # ===================================
    
    async def start(self):
        """Start the bot - FIXED VERSION"""
        await super().start()
        
        # Connect to database
        if not await self.db.connect():
            logger.error("Failed to connect to database. Exiting.")
            return False
        
        # Start user account for reactions
        await self.start_user_account()
        
        # Parse force subscribe channels from Config
        Config.parse_force_sub_channels()
        
        # Load settings
        self.settings = await self.db.get_settings()
        
        # Load force sub channels from database AND config
        db_channels = await self.db.get_force_sub_channels()
        config_channels = Config.FORCE_SUB_CHANNELS
        
        # Merge channels (avoid duplicates)
        all_channels = {}
        for channel in db_channels + config_channels:
            channel_id = channel.get("channel_id")
            if channel_id not in all_channels:
                all_channels[channel_id] = channel
        
        self.force_sub_channels = list(all_channels.values())
        
        # Save merged channels back to database
        await self.db.clear_force_sub_channels()
        for channel in self.force_sub_channels:
            await self.db.add_force_sub_channel(
                channel.get("channel_id"),
                channel.get("channel_username")
            )
        
        self.db_channel = await self.db.get_db_channel()
        
        # Initialize admins
        for admin_id in Config.ADMINS:
            await self.db.add_admin(admin_id)
        
        # Refresh admin cache
        await self.refresh_admin_cache()
        
        # Set bot commands - FIXED METHOD
        await self.set_bot_commands()
        
        # Register all handlers
        self.register_all_handlers()
        
        # Start auto-clean task if enabled
        if Config.AUTO_CLEAN_JOIN_REQUESTS:
            asyncio.create_task(self.auto_clean_join_requests())
        
        # Print bot info
        me = await self.get_me()
        Config.BOT_USERNAME = me.username
        logger.info(f"✓ Bot started as @{me.username}")
        logger.info(f"✓ Bot ID: {me.id}")
        logger.info(f"✓ Force Sub Channels: {len(self.force_sub_channels)}")
        logger.info("✓ Enhanced auto-delete: Only deletes conversation messages")
        
        # Send startup message to owner
        await self.send_log_message(
            f"✅ Bot started successfully!\n\n"
            f"📊 **Enhanced Auto-Delete Active**\n"
            f"• Only deletes conversation messages\n"
            f"• Preserves file and instruction messages\n"
            f"• Clean PM experience\n\n"
            f"📢 **Force Subscribe:** {len(self.force_sub_channels)} channels"
        )
        
        return True
    
    async def stop(self, *args):
        """Stop the bot"""
        await self.stop_user_account()
        await self.db.close()
        await super().stop()
        logger.info("✓ Bot stopped")
    
    async def set_bot_commands(self):
        """Set bot commands - FIXED VERSION"""
        try:
            # First set commands for all users
            await self.set_bot_commands(
                commands=BOT_COMMANDS["all_users"],
                scope=BotCommandScopeAllPrivateChats()
            )
            
            # Also set admin commands for admins (they'll be hidden from non-admins)
            for admin_id in Config.ADMINS:
                try:
                    await self.set_bot_commands(
                        commands=BOT_COMMANDS["admins"],
                        scope=BotCommandScopeAllPrivateChats()
                    )
                    break  # Set once is enough
                except:
                    continue
            
            logger.info("✓ Bot commands set successfully")
        except Exception as e:
            logger.error(f"Error setting bot commands: {e}")
    
    def register_all_handlers(self):
        """Register ALL handlers in one place - FIXED VERSION"""
        
        # === START COMMAND ===
        @self.on_message(filters.command("start") & filters.private)
        async def start_handler(client, message):
            await self.start_command(message)
        
        # === HELP COMMAND ===
        @self.on_message(filters.command("help") & filters.private)
        async def help_handler(client, message):
            await self.help_command(message)
        
        # === ABOUT COMMAND ===
        @self.on_message(filters.command("about") & filters.private)
        async def about_handler(client, message):
            await self.about_command(message)
        
        # === ADMIN MANAGEMENT COMMANDS ===
        @self.on_message(filters.command("users") & filters.private)
        async def admin_list_handler(client, message):
            await self.admin_list_command(message)
        
        @self.on_message(filters.command("add_admins") & filters.private)
        async def add_admins_handler(client, message):
            await self.add_admins_command(message)
        
        @self.on_message(filters.command("del_admins") & filters.private)
        async def del_admins_handler(client, message):
            await self.del_admins_command(message)
        
        @self.on_message(filters.command("banuser_list") & filters.private)
        async def banuser_list_handler(client, message):
            await self.banuser_list_command(message)
        
        @self.on_message(filters.command("add_banuser") & filters.private)
        async def add_banuser_handler(client, message):
            await self.add_banuser_command(message)
        
        @self.on_message(filters.command("del_banuser") & filters.private)
        async def del_banuser_handler(client, message):
            await self.del_banuser_command(message)
        
        # === BASIC ADMIN COMMANDS ===
        @self.on_message(filters.command("admin_list") & filters.private)
        async def users_handler(client, message):
            await self.users_command(message)
        
        @self.on_message(filters.command("broadcast") & filters.private)
        async def broadcast_handler(client, message):
            await self.broadcast_command(message)
        
        @self.on_message(filters.command("ban") & filters.private)
        async def ban_handler(client, message):
            await self.ban_command(message)
        
        @self.on_message(filters.command("unban") & filters.private)
        async def unban_handler(client, message):
            await self.unban_command(message)
        
        @self.on_message(filters.command("stats") & filters.private)
        async def stats_handler(client, message):
            await self.stats_command(message)
        
        @self.on_message(filters.command("logs") & filters.private)
        async def logs_handler(client, message):
            await self.logs_command(message)
        
        @self.on_message(filters.command("cmd") & filters.private)
        async def cmd_handler(client, message):
            await self.cmd_command(message)
        
        # === FILE MANAGEMENT COMMANDS ===
        @self.on_message(filters.command("genlink") & filters.private)
        async def genlink_handler(client, message):
            await self.genlink_command(message)
        
        @self.on_message(filters.command("batch") & filters.private)
        async def batch_handler(client, message):
            await self.batch_command(message)
        
        @self.on_message(filters.command("custom_batch") & filters.private)
        async def custom_batch_handler(client, message):
            await self.custom_batch_command(message)
        
        @self.on_message(filters.command("special_link") & filters.private)
        async def special_link_handler(client, message):
            await self.special_link_command(message)
        
        @self.on_message(filters.command("getlink") & filters.private)
        async def getlink_handler(client, message):
            await self.getlink_command(message)
        
        # === CHANNEL MANAGEMENT COMMANDS ===
        @self.on_message(filters.command("setchannel") & filters.private)
        async def setchannel_handler(client, message):
            await self.setchannel_command(message)
        
        @self.on_message(filters.command("checkchannel") & filters.private)
        async def checkchannel_handler(client, message):
            await self.checkchannel_command(message)
        
        @self.on_message(filters.command("removechannel") & filters.private)
        async def removechannel_handler(client, message):
            await self.removechannel_command(message)
        
        # === SETTINGS COMMANDS ===
        @self.on_message(filters.command("settings") & filters.private)
        async def settings_handler(client, message):
            await self.settings_command(message)
        
        @self.on_message(filters.command("files") & filters.private)
        async def files_handler(client, message):
            await self.files_command(message)
        
        @self.on_message(filters.command("auto_del") & filters.private)
        async def auto_del_handler(client, message):
            await self.auto_del_command(message)
        
        @self.on_message(filters.command("forcesub") & filters.private)
        async def forcesub_handler(client, message):
            await self.forcesub_command(message)
        
        @self.on_message(filters.command("req_fsub") & filters.private)
        async def req_fsub_handler(client, message):
            await self.req_fsub_command(message)
        
        @self.on_message(filters.command("botsettings") & filters.private)
        async def botsettings_handler(client, message):
            await self.botsettings_command(message)
        
        # === UTILITY COMMANDS ===
        @self.on_message(filters.command("shortener") & filters.private)
        async def shortener_handler(client, message):
            await self.shortener_command(message)
        
        @self.on_message(filters.command("ping") & filters.private)
        async def ping_handler(client, message):
            await self.ping_command(message)
        
        @self.on_message(filters.command("font") & filters.private)
        async def font_handler(client, message):
            await self.font_command(message)
        
        @self.on_message(filters.command("refresh") & filters.private)
        async def refresh_handler(client, message):
            await self.refresh_command(message)
        
        # === FORCE SUBSCRIBE COMMANDS ===
        @self.on_message(filters.command("fsub_chnl") & filters.private)
        async def fsub_chnl_handler(client, message):
            await self.fsub_chnl_command(message)
        
        @self.on_message(filters.command("add_fsub") & filters.private)
        async def add_fsub_handler(client, message):
            await self.add_fsub_command(message)
        
        @self.on_message(filters.command("del_fsub") & filters.private)
        async def del_fsub_handler(client, message):
            await self.del_fsub_command(message)
        
        # === DONE COMMAND ===
        @self.on_message(filters.command("done") & filters.private)
        async def done_handler(client, message):
            await self.done_command(message)
        
        # === TEXT MESSAGE HANDLERS ===
        @self.on_message(filters.private)
        async def text_handler(client, message):
            await self.text_message_handler(message)
        
        # === ENHANCED AUTO DELETE HANDLER ===
        @self.on_message(filters.private)
        async def auto_delete_handler(client, message):
            await self.enhanced_auto_delete_handler(message)
        
        # === CHAT JOIN REQUEST HANDLER ===
        @self.on_chat_join_request()
        async def join_request_handler(client, join_request: ChatJoinRequest):
            await self.handle_join_request(join_request)
        
        logger.info("✓ All handlers registered with enhanced auto-delete")
    
    async def setup_callbacks(self):
        """Setup callback query handlers"""
        
        @self.on_callback_query()
        async def callback_handler(client, query):
            await self.handle_callback_query(query)
    
    async def enhanced_auto_delete_handler(self, message: Message):
        """Enhanced auto-delete handler - only deletes conversation messages"""
        # Check if auto delete is enabled
        settings = await self.db.get_settings()
        
        if settings.get("auto_delete_bot_messages", False):
            user_id = message.from_user.id
            
            # Get auto-delete delay
            delay = settings.get("auto_delete_time_bot", 30)
            
            # Check if user has a tracked message
            if user_id in self.user_last_messages:
                msg_info = self.user_last_messages[user_id]
                
                # Only delete conversation messages
                if msg_info.get("type") == "conversation":
                    try:
                        # Delete after delay
                        asyncio.create_task(
                            self.delete_message_after_delay(
                                user_id, 
                                msg_info["message_id"], 
                                delay,
                                msg_info.get("type", "conversation")
                            )
                        )
                        logger.info(f"✓ Scheduled auto-delete for conversation message {msg_info['message_id']} for user {user_id}")
                    except Exception as e:
                        logger.error(f"Error scheduling auto-delete: {e}")
                else:
                    logger.info(f"✗ Skipped auto-delete for {msg_info.get('type')} message {msg_info['message_id']}")
                
                # Remove from tracking after scheduling
                del self.user_last_messages[user_id]
    
    async def auto_clean_join_requests(self):
        """Auto-clean join requests every 24 hours"""
        try:
            while True:
                await asyncio.sleep(Config.AUTO_CLEAN_INTERVAL)
                
                # Clean old join requests
                cleaned_count = await self.db.clean_old_join_requests()
                
                if cleaned_count > 0:
                    # Send log to owner
                    await self.send_log_message(
                        f"🧹 **Auto-clean completed!**\n\n"
                        f"Cleaned {cleaned_count} join requests older than 24 hours."
                    )
                    
        except asyncio.CancelledError:
            logger.info("Auto-clean task cancelled")
        except Exception as e:
            logger.error(f"Error in auto-clean task: {e}")
    
    async def send_log_message(self, message: str):
        """Send log message to owner"""
        try:
            await self.send_message(
                Config.OWNER_ID,
                f"📊 **Bot Log**\n\n{message}",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        except Exception as e:
            logger.error(f"Failed to send log message: {e}")
    
    async def handle_start_argument(self, message: Message, start_arg: str):
        """Handle start command arguments"""
        try:
            # Check if it's a special link
            if start_arg.startswith("link_"):
                link_id = start_arg.replace("link_", "")
                await self.handle_special_link(message, link_id)
            # Check if it's a file link
            elif start_arg.startswith("file_"):
                file_id = start_arg.replace("file_", "")
                await self.handle_file_link(message, file_id)
            # Check if it's a batch link
            elif start_arg.startswith("batch_"):
                batch_id = start_arg.replace("batch_", "")
                await self.handle_batch_link(message, batch_id)
        except Exception as e:
            logger.error(f"Error handling start argument: {e}")
            error_msg = await message.reply("❌ Invalid or expired link!")
            await self.store_bot_message(message.from_user.id, error_msg.id, "conversation")
    
    async def handle_special_link(self, message: Message, link_id: str):
        """Handle special link access - DO NOT AUTO-DELETE FILE MESSAGES"""
        try:
            # Get link data from database
            link_data = await self.db.get_special_link(link_id)
            if not link_data:
                error_msg = await message.reply("❌ Link not found or expired!")
                await self.store_bot_message(message.from_user.id, error_msg.id, "conversation")
                return
            
            # Send custom message if available
            if link_data.get("message"):
                msg = await message.reply(link_data["message"], parse_mode=enums.ParseMode.HTML)
                await self.store_bot_message(message.from_user.id, msg.id, "conversation")
            
            # Send files
            files = link_data.get("files", [])
            if files:
                file_ids = []
                for file_id in files[:MAX_SPECIAL_FILES]:
                    try:
                        response = await self.copy_message(
                            chat_id=message.chat.id,
                            from_chat_id=self.db_channel,
                            message_id=file_id,
                            protect_content=self.settings.get("protect_content", True)
                        )
                        file_ids.append(file_id)
                        
                        # Store as file type (won't be auto-deleted)
                        await self.store_bot_message(message.from_user.id, response.id, "file")
                        
                    except Exception as e:
                        logger.error(f"Error sending file {file_id}: {e}")
                
                # Track files for potential resend
                if file_ids:
                    await self.track_user_files(message.from_user.id, file_ids, response.id)
        except Exception as e:
            logger.error(f"Error handling special link: {e}")
            error_msg = await message.reply("❌ Error accessing link!")
            await self.store_bot_message(message.from_user.id, error_msg.id, "conversation")
    
    async def handle_file_link(self, message: Message, file_id: str):
        """Handle single file link - DO NOT AUTO-DELETE FILE MESSAGES"""
        try:
            # Send the file
            response = await self.copy_message(
                chat_id=message.chat.id,
                from_chat_id=self.db_channel,
                message_id=int(file_id),
                protect_content=self.settings.get("protect_content", True)
            )
            
            # Store as file type (won't be auto-deleted)
            await self.store_bot_message(message.from_user.id, response.id, "file")
            
            # Track file for potential resend
            await self.track_user_files(message.from_user.id, [int(file_id)], response.id)
            
        except Exception as e:
            logger.error(f"Error sending file {file_id}: {e}")
            error_msg = await message.reply("❌ File not found or access denied!")
            await self.store_bot_message(message.from_user.id, error_msg.id, "conversation")
    
    async def handle_batch_link(self, message: Message, batch_id: str):
        """Handle batch file link - DO NOT AUTO-DELETE FILE MESSAGES"""
        try:
            # Decode batch data
            decoded = await decode(batch_id.replace("batch_", ""))
            file_ids = [int(x) for x in decoded.split(",") if x.isdigit()]
            
            if not file_ids:
                error_msg = await message.reply("❌ No files found in batch!")
                await self.store_bot_message(message.from_user.id, error_msg.id, "conversation")
                return
            
            # Send files
            sent_file_ids = []
            last_response = None
            
            for file_id in file_ids[:MAX_BATCH_SIZE]:
                try:
                    response = await self.copy_message(
                        chat_id=message.chat.id,
                        from_chat_id=self.db_channel,
                        message_id=file_id,
                        protect_content=self.settings.get("protect_content", True)
                    )
                    sent_file_ids.append(file_id)
                    last_response = response
                    
                    # Store as file type (won't be auto-deleted)
                    await self.store_bot_message(message.from_user.id, response.id, "file")
                    
                except Exception as e:
                    logger.error(f"Error sending file {file_id}: {e}")
            
            # Track files for potential resend
            if sent_file_ids and last_response:
                await self.track_user_files(message.from_user.id, sent_file_ids, last_response.id)
                
            info_msg = await message.reply(f"✅ Sent {len(sent_file_ids)} files!")
            await self.store_bot_message(message.from_user.id, info_msg.id, "conversation")
            
        except Exception as e:
            logger.error(f"Error handling batch link: {e}")
            error_msg = await message.reply("❌ Batch not found or access denied!")
            await self.store_bot_message(message.from_user.id, error_msg.id, "conversation")
    
    async def create_invite_link(self, channel_id: int) -> str:
        """Create 5-minute expire invite link for private channels"""
        try:
            invite_link = await self.create_chat_invite_link(
                chat_id=channel_id,
                expire_date=datetime.datetime.now() + datetime.timedelta(minutes=5),
                member_limit=1
            )
            return invite_link.invite_link
        except Exception as e:
            logger.error(f"Error creating invite link for channel {channel_id}: {e}")
            return None

    # ===================================
    # SECTION 6: START COMMAND (UPDATED - FIXED)
    # ===================================
    
    async def start_command(self, message: Message):
        """Handle /start command - FIXED VERSION"""
        user_id = message.from_user.id
        chat_id = message.chat.id

        # Delete previous conversation message if auto-delete is enabled
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", True):
            await self.delete_previous_message(user_id)

        # Check if user is banned
        if await self.db.is_user_banned(user_id):
            response = await message.reply("🚫 <b>You are banned from using this bot!</b>", parse_mode=enums.ParseMode.HTML)
            await self.store_bot_message(user_id, response.id, "conversation")
            return

        # Add user to database
        await self.db.add_user(
            user_id=user_id,
            first_name=message.from_user.first_name,
            username=message.from_user.username
        )

        # Update activity
        await self.db.update_user_activity(user_id)

        # Send reaction using user account
        try:
            await self.send_reaction(chat_id, message.id)
        except Exception as e:
            logger.error(f"Failed to send reaction: {e}")

        # Check for start arguments
        if len(message.command) > 1:
            start_arg = message.command[1]
            await self.handle_start_argument(message, start_arg)
            return

        # Check force subscribe - ONLY if request_fsub is enabled
        settings = await self.db.get_settings()
        request_fsub = settings.get("request_fsub", False)
        
        if request_fsub and self.force_sub_channels:
            user_is_subscribed = await is_subscribed(self, user_id, self.force_sub_channels)
            if not user_is_subscribed:
                await self.show_force_subscribe(message)
                return

        # Show welcome message
        await self.show_welcome_message(message)

    async def show_welcome_message(self, message: Message):
        """Show welcome message WITH PHOTO"""
        user = message.from_user
    
        # Get settings
        settings = await self.db.get_settings()
        welcome_text = settings.get("welcome_text", "")
        welcome_pics = settings.get("welcome_pics", Config.WELCOME_PICS)
    
        # Get random welcome picture
        welcome_pic = get_random_pic(welcome_pics)
    
        # Default welcome text (FIXED: Removed expandable attribute)
        if not welcome_text:
            welcome_text = (
                f"⚡ <b>Hey, {user.first_name} ~</b>\n\n"
                '<blockquote>'
                "I AM AN ADVANCE FILE SHARE BOT V3.\n"
                "THE BEST PART IS I AM ALSO SUPPORT REQUEST FORCESUB FEATURE.\n"
                "TO KNOW DETAILED INFORMATION CLICK ABOUT ME BUTTON TO KNOW MY ALL ADVANCE FEATURES"
                "</blockquote>"
            )
        else:
            try:
                welcome_text = welcome_text.format(
                    first=user.first_name,
                    last=user.last_name or "",
                    username=f"@{user.username}" if user.username else "None",
                    mention=f"<a href='tg://user?id={user.id}'>{user.first_name}</a>",
                    id=user.id
                )
            except KeyError as e:
                logger.error(f"Invalid placeholder in welcome_text: {e}")
                welcome_text = (
                    f"⚡ <b>Hey, {user.first_name} ~</b>\n\n"
                    '<blockquote>'
                    "I AM AN ADVANCE FILE SHARE BOT V3.\n"
                    "THE BEST PART IS I AM ALSO SUPPORT REQUEST FORCESUB FEATURE.\n"
                    "TO KNOW DETAILED INFORMATION CLICK ABOUT ME BUTTON TO KNOW MY ALL ADVANCE FEATURES"
                    "</blockquote>"
                )
    
        # Create buttons
        buttons = [
            [
                InlineKeyboardButton("⁉️ ʜᴇʟᴘ", callback_data="help_menu"),
                InlineKeyboardButton("ᴀʙᴏᴜᴛ ", callback_data="about_menu")
            ],
            [
                InlineKeyboardButton("ᴄʟᴏsᴇ ✖️", callback_data="close")
            ]
        ]
    
        keyboard = InlineKeyboardMarkup(buttons)
    
        try:
            response = await message.reply_photo(
                photo=welcome_pic,
                caption=welcome_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Error sending welcome photo: {e}")
            response = await message.reply(
                welcome_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML,
                disable_web_page_preview=True
            )
    
        # Store as conversation message (will be auto-deleted)
        await self.store_bot_message(message.from_user.id, response.id, "conversation")
    
    async def show_force_subscribe(self, message: Message):
        """Show force subscribe message WITH PHOTO"""
        user = message.from_user
    
        # Get force sub pictures from settings
        settings = await self.db.get_settings()
        force_sub_pics = settings.get("force_sub_pics", Config.FORCE_SUB_PICS)
    
        # Get random force sub picture
        force_sub_pic = get_random_pic(force_sub_pics)
    
        # Count joined/total channels
        total_channels = len(self.force_sub_channels)
        joined_count = 0
    
        # Check which channels user has joined
        for channel in self.force_sub_channels:
            try:
                user_is_sub = await is_subscribed(self, user.id, [channel])
                if user_is_sub:
                    joined_count += 1
            except:
                pass
    
        # Create buttons for each channel
        buttons = []
        for channel in self.force_sub_channels:
            channel_id = channel.get("channel_id")
            username = channel.get("channel_username")
        
            if username:
                button_text = "ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ"
                button_url = f"https://t.me/{username}"
            else:
                button_text = "ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀɴɴᴇʟ"
                try:
                    invite_link = await self.create_invite_link(channel_id)
                    if invite_link:
                        button_url = invite_link
                    else:
                        button_url = f"t.me/c/{str(channel_id)[4:]}"
                except:
                    button_url = f"t.me/c/{str(channel_id)[4:]}"
        
            buttons.append([InlineKeyboardButton(button_text, url=button_url)])
    
        # Add help button
        buttons.append([
            InlineKeyboardButton("⁉️ ʜᴇʟᴘ", callback_data="help_menu")
        ])
    
        keyboard = InlineKeyboardMarkup(buttons)
    
        # Message text (FIXED: Removed expandable attribute)
        message_text = (
            f"<b>Hey, {user.first_name}</b>\n\n"
            '<blockquote>'
            "<b>"
            f"You haven't joined {joined_count}/{total_channels} channels yet.\n"
            f"Please join the channels provided below, then try again."
            "</b>"
            "</blockquote>\n\n"
            '<blockquote><b>Facing problems, use: /help</b></blockquote>'
        )
    
        try:
            response = await message.reply_photo(
                photo=force_sub_pic,
                caption=message_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Error sending force sub photo: {e}")
            response = await message.reply(
                message_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
    
        # Store as conversation message (will be auto-deleted)
        await self.store_bot_message(message.from_user.id, response.id, "conversation")
    
    # ===================================
    # SECTION 7: HELP & ABOUT COMMANDS (UPDATED)
    # ===================================
    
    async def help_command(self, message: Message):
        """Handle /help command WITH PHOTO"""
        user_id = message.from_user.id
        user = message.from_user
    
        # Delete previous conversation message
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", True):
            await self.delete_previous_message(user_id)
    
        # Get help text and pictures
        help_text = settings.get("help_text", "")
        help_pics = settings.get("help_pics", Config.HELP_PICS)
    
        # Get random help picture
        help_pic = get_random_pic(help_pics)
    
        # Default help text (FIXED: Removed expandable attribute)
        if not help_text:
            help_text = (
                f"<b>⁉️ Hᴇʟʟᴏ {user.first_name} ~</b>\n\n"
                '<blockquote>'
                "<b>"
                "➪ I ᴀᴍ ᴀ ᴘʀɪᴠᴀᴛᴇ ғɪʟᴇ sʜᴀʀɪɴɢ ʙᴏᴛ, ᴍᴇᴀɴᴛ ᴛᴏ ᴘʀᴏᴠɪᴅᴇ ғɪʟᴇs ᴀɴᴅ ɴᴇᴄᴇssᴀʀʏ sᴛᴜғғ ᴛʜʀᴏᴜɢʜ sᴘᴇᴄɪᴀʟ ʟɪɴᴋ ғᴏʀ sᴘᴇᴄɪғɪᴄ ᴄʜᴀɴɴᴇʟs.\n\n"
                "➪ Iɴ ᴏʀᴅᴇʀ ᴛᴏ ɢᴇᴛ ᴛʜᴇ ғɪʟᴇs ʏᴏᴜ ʜᴀᴠᴇ ᴛᴏ ᴊᴏɪɴ ᴛʜᴇ ᴀʟʟ ᴍᴇɴᴛɪᴏɴᴇᴅ ᴄʜᴀɴɴᴇʟ ᴛʜᴀᴛ ɪ ᴘʀᴏᴠɪᴅᴇ ʏᴏᴜ ᴛᴏ ᴊᴏɪɴ. "
                "Yᴏᴜ ᴄᴀɴ ɴᴏᴛ ᴀᴄᴄᴇss ᴏʀ ɢᴇᴛ ᴛʜᴇ ғɪʟᴇs ᴜɴʟᴇss ʏᴏᴜ ᴊᴏɪɴᴇᴅ ᴀʟʟ ᴄʜᴀɴɴᴇʟs.\n\n"
                "➪ Sᴏ ᴊᴏɪɴ Mᴇɴᴛɪᴏɴᴇᴅ Cʜᴀɴɴᴇʟs ᴛᴏ ɢᴇᴛ Fɪʟᴇs ᴏʀ ɪɴɪᴛɪᴀᴛᴇ ᴍᴇssᴀɢᴇs...\n\n"
                "‣ /help - Oᴘᴇɴ ᴛʜɪs ʜᴇʟᴘ ᴍᴇssᴀɢᴇ !"
                "</b>"
                "</blockquote>\n"
                "<b>◈ Sᴛɪʟʟ ʜᴀᴠᴇ ᴅᴏᴜʙᴛs, ᴄᴏɴᴛᴀᴄᴛ ʙᴇʟᴏᴡ ᴘᴇʀsᴏɴs/ɢʀᴏᴜᴘ ᴀs ᴘᴇʀ ʏᴏᴜʀ ɴᴇᴇᴅ !</b>"
            )
    
        # Create buttons
        buttons = [
            [
                InlineKeyboardButton("ᴀɴɪᴍᴇ ᴄʜᴀɴɴᴇʟ", url=f"https://t.me/{Config.UPDATE_CHANNEL}"),
                InlineKeyboardButton("ᴄᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ", url=f"https://t.me/{Config.SUPPORT_CHAT}")
            ],
            [
                InlineKeyboardButton("ᴀʙᴏᴜᴛ ᴍᴇ", callback_data="about_menu"),
                InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="start_menu")
            ],
            [
                InlineKeyboardButton("ᴄʟᴏsᴇ ✖️", callback_data="close")
            ]
        ]
    
        keyboard = InlineKeyboardMarkup(buttons)
    
        try:
            response = await message.reply_photo(
                photo=help_pic,
                caption=help_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Error sending help photo: {e}")
            response = await message.reply(
                help_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
    
        # Store as conversation message
        await self.store_bot_message(user_id, response.id, "conversation")
    
    async def about_command(self, message: Message):
        """Handle /about command"""
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", True):
            await self.delete_previous_message(message.from_user.id)
        
        # Get about text from settings
        settings = await self.db.get_settings()
        about_text = settings.get("about_text", "")
        about_pics = settings.get("welcome_pics", Config.WELCOME_PICS)
        
        # Get random about picture
        about_pic = get_random_pic(about_pics)
        
        # Default about text
        if not about_text:
            about_text = (
                f"ℹ️ <b>About Bot</b>\n\n"
                f"<b>• Bot Name: {Config.BOT_NAME}</b>\n"
                f"<b>• Framework: Pyrogram</b>\n"
                f"<b>• Language: Python 3</b>\n"
                f"<b>• Version: V3.0</b>\n\n"
                f"<b>Developed by @Beat_Anime_Ocean</b>"
            )
        
        buttons = [
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="start_menu")],
            [InlineKeyboardButton("ᴄʟᴏsᴇ ✖️", callback_data="close")]
        ]
        
        keyboard = InlineKeyboardMarkup(buttons)
        
        try:
            response = await message.reply_photo(
                photo=about_pic,
                caption=about_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Error sending about photo: {e}")
            response = await message.reply(
                about_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
        
        # Store as conversation message
        await self.store_bot_message(message.from_user.id, response.id, "conversation")
    
    # ===================================
    # SECTION 8: FILE INSTRUCTION MESSAGE (PRESERVED)
    # ===================================
    
    async def show_deleted_message(self, message: Message):
        """Show deleted message prompt - DO NOT AUTO-DELETE THIS"""
        deleted_text = (
            "<b>PREVIOUS MESSAGE WAS DELETED</b>\n\n"
            "IF YOU WANT TO GET THE FILES AGAIN, THEN CLICK [CLICK HERE] BUTTON BELOW ELSE CLOSE THIS MESSAGE."
        )
        
        buttons = [
            [
                InlineKeyboardButton("CLICK HERE", callback_data="resend_files"),
                InlineKeyboardButton("CLOSE", callback_data="close")
            ]
        ]
        
        keyboard = InlineKeyboardMarkup(buttons)
        
        response = await message.reply(
            deleted_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
        
        # Store as instruction type (WILL NOT be auto-deleted)
        await self.store_bot_message(message.from_user.id, response.id, "instruction")
    
    # ===================================
    # SECTION 9: ADMIN MANAGEMENT COMMANDS (FIXED)
    # ===================================
    
    async def admin_list_command(self, message: Message):
        """Handle /admin_list command - FIXED VERSION"""
        # Check admin permission
        if not await self.is_user_admin(message.from_user.id):
            response = await message.reply("❌ Admin only!")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            return
        
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", True):
            await self.delete_previous_message(message.from_user.id)
        
        try:
            # Get admins
            db_admins = await self.db.get_admins()
            all_admins = list(set(Config.ADMINS + db_admins))
            
            if not all_admins:
                response = await message.reply("❌ No admins found!")
                await self.store_bot_message(message.from_user.id, response.id, "conversation")
                return
            
            # Format message
            admin_text = (
                " <b> 🤖 𝗨𝗦𝗘𝗥 𝗦𝗘𝗧𝗧𝗜𝗡𝗚 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 : </b>\n\n"
                "<b> /admin_list : ᴠɪᴇᴡ ᴛʜᴇ ᴀᴠᴀɪʟᴀʙʟᴇ ᴀᴅᴍɪɴ ʟɪsᴛ (ᴏᴡɴᴇʀ) </b>\n\n"
                "<b> /add_admins : ᴀᴅᴅ ᴏɴᴇ ᴏʀ ᴍᴜʟᴛɪᴘʟᴇ ᴜsᴇʀ ɪᴅs ᴀs ᴀᴅᴍɪɴ (ᴏᴡɴᴇʀ) </b>\n\n"
                "<b> /del_admins : ᴅᴇʟᴇᴛᴇ ᴏɴᴇ ᴏʀ ᴍᴜʟᴛɪᴘʟᴇ ᴜsᴇʀ ɪᴅs ғʀᴏᴍ ᴀᴅᴍɪɴs (ᴏᴡɴᴇʀ) </b>\n\n"
                "<b> /banuser_list : ᴠɪᴇᴡ ᴛʜᴇ ᴀᴠᴀɪʟᴀʙʟᴇ ʙᴀɴɴᴇᴅ ᴜsᴇʀ ʟɪsᴛ (ᴀᴅᴍɪɴs) </b>\n\n"
                "<b> /add_banuser : ᴀᴅᴅ ᴏɴᴇ ᴏʀ ᴍᴜʟᴛɪᴘʟᴇ ᴜsᴇʀ ɪᴅs ɪɴ ʙᴀɴɴᴇᴅ ʟɪsᴛ (ᴀᴅᴍɪɴs) </b>\n\n"
                "<b> /del_banuser : ᴅᴇʟᴇᴛᴇ ᴏɴᴇ ᴏʀ ᴍᴜʟᴛɪᴘʟᴇ ᴜsᴇʀ ɪᴅs ғʀᴏᴇ ʙᴀɴɴᴇᴅ ʟɪsᴛ (ᴀᴅᴍɪɴs) </b>"
            )
            
            buttons = [
                [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="admin_panel")],
                [InlineKeyboardButton("ᴄʟᴏsᴇ ✖️", callback_data="close")]
            ]
            
            keyboard = InlineKeyboardMarkup(buttons)
            
            response = await message.reply(
                admin_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
            
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            
        except Exception as e:
            logger.error(f"Error in admin_list command: {e}")
            response = await message.reply("❌ Error fetching admin list!")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
    
    async def add_admins_command(self, message: Message):
        """Handle /add_admins command - FIXED VERSION"""
        # Check if user is owner
        if message.from_user.id != Config.OWNER_ID:
            response = await message.reply("❌ Owner only!")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            return
        
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", True):
            await self.delete_previous_message(message.from_user.id)
        
        if len(message.command) < 2:
            response = await message.reply(
                " <b> 𝗔𝗗𝗗 𝗔𝗗𝗠𝗜𝗡𝗦 </b>\n\n"
                "Usage: <code>/add_admins user_id1,user_id2</code>\n\n"
                "Example: <code>/add_admins 123456789,987654321</code>",
                parse_mode=enums.ParseMode.HTML
            )
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            return
        
        try:
            args = message.command[1].split(",")
            added_admins = []
            
            for arg in args:
                arg = arg.strip()
                
                try:
                    user_id = int(arg)
                    
                    # Check if user exists
                    try:
                        user = await self.get_users(user_id)
                        
                        # Add to database
                        await self.db.add_admin(user_id)
                        
                        # Add to Config.ADMINS if not already
                        if user_id not in Config.ADMINS:
                            Config.ADMINS.append(user_id)
                        
                        added_admins.append(f"{user.first_name} ({user_id})")
                        
                    except Exception as e:
                        await message.reply(f"❌ Error adding {arg}: {str(e)}")
                        continue
                    
                except ValueError:
                    await message.reply(f"❌ Invalid user ID: {arg}")
                    continue
            
            if added_admins:
                response = await message.reply(
                    f"✅ <b> ᴀᴅᴍɪɴs ᴀᴅᴅᴇᴅ! </b>\n\n"
                    f"ᴀᴅᴅᴇᴅ {len(added_admins)} ᴀᴅᴍɪɴ(s)\n"
                    + "\n".join(f"• {admin}" for admin in added_admins),
                    parse_mode=enums.ParseMode.HTML
                )
            else:
                response = await message.reply("❌ No admins were added!")
            
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
        
        except Exception as e:
            logger.error(f"Error adding admins: {e}")
            response = await message.reply("❌ Error adding admins!")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
    
    async def del_admins_command(self, message: Message):
        """Handle /del_admins command - FIXED VERSION"""
        # Check if user is owner
        if message.from_user.id != Config.OWNER_ID:
            response = await message.reply("❌ Owner only!")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            return
        
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", True):
            await self.delete_previous_message(message.from_user.id)
        
        if len(message.command) < 2:
            response = await message.reply(
                "🗑️ <b> ᴅᴇʟᴇᴛᴇ ᴀᴅᴍɪɴs </b>\n\n"
                "ᴜsᴀɢᴇ: <code>/del_admins ᴜsᴇʀ_ɪᴅ1,ᴜsᴇʀ_ɪᴅ2</code>\n\n"
                "ᴇxᴀᴍᴘʟᴇ: <code>/del_admins 123456789,987654321</code>\n\n"
                "ɴᴏᴛᴇ: ᴄᴀɴɴᴏᴛ ʀᴇᴍᴏᴠᴇ ᴏᴡɴᴇʀ!",
                parse_mode=enums.ParseMode.HTML
            )
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            return
        
        try:
            args = message.command[1].split(",")
            removed_admins = []
            
            for arg in args:
                arg = arg.strip()
                
                try:
                    user_id = int(arg)
                    
                    # Check if trying to remove owner
                    if user_id == Config.OWNER_ID:
                        await message.reply(f"❌ Cannot remove owner ({user_id})!")
                        continue
                    
                    # Remove from database
                    await self.db.remove_admin(user_id)
                    
                    # Remove from Config.ADMINS if present
                    if user_id in Config.ADMINS:
                        Config.ADMINS.remove(user_id)
                    
                    removed_admins.append(str(user_id))
                    
                except ValueError:
                    await message.reply(f"❌ Invalid user ID: {arg}")
                    continue
            
            if removed_admins:
                response = await message.reply(
                    f"✅ <b> Admins Removed! </b>\n\n"
                    f"Removed {len(removed_admins)} admin(s)\n"
                    + "\n".join(f"• {admin}" for admin in removed_admins),
                    parse_mode=enums.ParseMode.HTML
                )
            else:
                response = await message.reply("❌ No admins were removed!")
            
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
        
        except Exception as e:
            logger.error(f"Error removing admins: {e}")
            response = await message.reply("❌ Error removing admins!")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
    
    async def banuser_list_command(self, message: Message):
        """Handle /banuser_list command - FIXED VERSION"""
        # Check admin permission
        if not await self.is_user_admin(message.from_user.id):
            response = await message.reply("❌ Admin only!")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            return
        
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", True):
            await self.delete_previous_message(message.from_user.id)
        
        try:
            # Get banned users
            banned_users = await self.db.get_banned_users()
            
            if not banned_users:
                response = await message.reply("✅ No banned users found!")
                await self.store_bot_message(message.from_user.id, response.id, "conversation")
                return
            
            # Format message
            ban_text = "<b> 𝗕𝗔𝗡𝗡𝗘𝗗 𝗨𝗦𝗘𝗥𝗦 𝗟𝗜𝗦𝗧 </b>\n\n"
            
            for i, ban in enumerate(banned_users[:10], 1):
                user_id = ban["user_id"]
                reason = ban.get("reason", "No reason")
                banned_date = ban.get("banned_date", "").strftime("%Y-%m-%d") if ban.get("banned_date") else "Unknown"
                
                ban_text += f"{i}. ID: <code>{user_id}</code>\n"
                ban_text += f"   Reason: {reason}\n"
                ban_text += f"   Date: {banned_date}\n\n"
            
            ban_text += f"📊 Total Banned: {len(banned_users)}"
            
            buttons = [
                [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="admin_panel")],
                [InlineKeyboardButton("ᴄʟᴏsᴇ ✖️", callback_data="close")]
            ]
            
            keyboard = InlineKeyboardMarkup(buttons)
            
            response = await message.reply(
                ban_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
            
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            
        except Exception as e:
            logger.error(f"Error in banuser_list command: {e}")
            response = await message.reply("❌ Error fetching banned users list!")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
    
    async def add_banuser_command(self, message: Message):
        """Handle /add_banuser command - FIXED VERSION"""
        # Check admin permission
        if not await self.is_user_admin(message.from_user.id):
            response = await message.reply("❌ Admin only!")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            return
        
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", True):
            await self.delete_previous_message(message.from_user.id)
        
        if len(message.command) < 2:
            response = await message.reply(
                "🚫 <b> 𝗕𝗔𝗡𝗡𝗘 𝗨𝗦𝗘𝗥 </b>\n\n"
                "Usage: <code>/add_banuser user_id1,user_id2 [reason]</code>\n\n"
                "Example: <code>/add_banuser 123456789,987654321 Spamming</code>",
                parse_mode=enums.ParseMode.HTML
            )
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            return
        
        try:
            args = message.command[1].split(",")
            reason = " ".join(message.command[2:]) if len(message.command) > 2 else "No reason provided"
            
            banned_users = []
            
            for arg in args:
                arg = arg.strip()
                
                try:
                    user_id = int(arg)
                    
                    # Check if user exists
                    if not await self.db.is_user_exist(user_id):
                        try:
                            user = await self.get_users(user_id)
                            await self.db.add_user(user_id, user.first_name, user.username)
                        except:
                            pass
                    
                    # Ban the user
                    await self.db.ban_user(user_id, reason)
                    banned_users.append(str(user_id))
                    
                    # Try to notify the user
                    try:
                        await self.send_message(
                            user_id,
                            f"🚫 <b> ʏᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ʙᴀɴɴᴇᴅ! </b>\n\n"
                            f"ʀᴇᴀsᴏɴ: {reason}\n"
                            f"ᴄᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ ɪꜰ ᴛʜɪs ɪs ᴀ ᴍɪsᴛᴀᴋᴇ.",
                            parse_mode=enums.ParseMode.HTML
                        )
                    except:
                        pass
                    
                except ValueError:
                    await message.reply(f"❌ Invalid user ID: {arg}")
                    continue
            
            if banned_users:
                response = await message.reply(
                    f"✅ <b> Users Banned! </b>\n\n"
                    f"Banned {len(banned_users)} user(s)\n"
                    + "\n".join(f"• {user_id}" for user_id in banned_users) +
                    f"\n\nReason: {reason}",
                    parse_mode=enums.ParseMode.HTML
                )
            else:
                response = await message.reply("❌ No users were banned!")
            
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
        
        except Exception as e:
            logger.error(f"Error banning users: {e}")
            response = await message.reply("❌ Error banning users!")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
    
    async def del_banuser_command(self, message: Message):
        """Handle /del_banuser command - FIXED VERSION"""
        # Check admin permission
        if not await self.is_user_admin(message.from_user.id):
            response = await message.reply("❌ Admin only!")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            return
        
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", True):
            await self.delete_previous_message(message.from_user.id)
        
        if len(message.command) < 2:
            response = await message.reply(
                "✅ <b> 𝗨𝗡𝗕𝗔𝗡 𝗨𝗦𝗘𝗥 </b>\n\n"
                "Usage: <code>/del_banuser user_id1,user_id2</code>\n\n"
                "Example: <code>/del_banuser 123456789,987654321</code>",
                parse_mode=enums.ParseMode.HTML
            )
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            return
        
        try:
            args = message.command[1].split(",")
            unbanned_users = []
            
            for arg in args:
                arg = arg.strip()
                
                try:
                    user_id = int(arg)
                    
                    # Check if user is banned
                    if not await self.db.is_user_banned(user_id):
                        await message.reply(f"⚠️ User {user_id} is not banned!")
                        continue
                    
                    # Unban the user
                    await self.db.unban_user(user_id)
                    unbanned_users.append(str(user_id))
                    
                    # Try to notify the user
                    try:
                        await self.send_message(
                            user_id,
                            "✅ <bʏ ᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ᴜɴʙᴀɴɴᴇᴅ! </b>\n\n"
                            "ʏᴏᴜ ᴄᴀɴ ɴᴏᴡ ᴜsᴇ ᴛʜᴇ ʙᴏᴛ ᴀɢᴀɪɴ.",
                            parse_mode=enums.ParseMode.HTML
                        )
                    except:
                        pass
                    
                except ValueError:
                    await message.reply(f"❌ Invalid user ID: {arg}")
                    continue
            
            if unbanned_users:
                response = await message.reply(
                    f"✅ <b> Users Unbanned! </b>\n\n"
                    f"Unbanned {len(unbanned_users)} user(s)\n"
                    + "\n".join(f"• {user_id}" for user_id in unbanned_users),
                    parse_mode=enums.ParseMode.HTML
                )
            else:
                response = await message.reply("⚠️ No users were unbanned!")
            
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
        
        except Exception as e:
            logger.error(f"Error unbanning users: {e}")
            response = await message.reply("❌ Error unbanning users!")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
    
    # ===================================
    # SECTION 10: OTHER COMMANDS (UPDATED - FIXED)
    # ===================================
    
    async def users_command(self, message: Message):
        """Handle /users command - FIXED VERSION"""
        # Check admin permission
        if not await self.is_user_admin(message.from_user.id):
            response = await message.reply("❌ Admin only!")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            return
        
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", True):
            await self.delete_previous_message(message.from_user.id)
        
        try:
            # Get counts
            total_users = await self.db.total_users_count()
            banned_users = await self.db.get_banned_count()
            active_users = total_users - banned_users
            
            # Get stats picture
            settings = await self.db.get_settings()
            welcome_pics = settings.get("welcome_pics", Config.WELCOME_PICS)
            stats_pic = get_random_pic(welcome_pics)
            
            # Format message
            stats_text = (
                "👥 <b>USER STATISTICS</b>\n\n"
                f"📊 Total Users: {total_users:,}\n"
                f"✅ Active Users: {active_users:,}\n"
                f"🚫 Banned Users: {banned_users:,}\n\n"
                f"<i>Last updated: {datetime.datetime.now().strftime('%H:%M:%S')}</i>"
            )
            
            buttons = [
                [
                    InlineKeyboardButton("🔄 Refresh", callback_data="refresh_users"),
                    InlineKeyboardButton("📊 Stats", callback_data="stats_menu")
                ],
                [
                    InlineKeyboardButton("⬅️ Back", callback_data="admin_panel"),
                    InlineKeyboardButton("❌ Close", callback_data="close")
                ]
            ]
            
            keyboard = InlineKeyboardMarkup(buttons)
            
            try:
                response = await message.reply_photo(
                    photo=stats_pic,
                    caption=stats_text,
                    reply_markup=keyboard,
                    parse_mode=enums.ParseMode.HTML
                )
            except Exception as e:
                logger.error(f"Error sending stats photo: {e}")
                response = await message.reply(
                    stats_text,
                    reply_markup=keyboard,
                    parse_mode=enums.ParseMode.HTML
                )
            
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            
        except Exception as e:
            logger.error(f"Error in users command: {e}")
            response = await message.reply("❌ Error fetching user statistics!")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
    
    async def stats_command(self, message: Message):
        """Handle /stats command - FIXED VERSION"""
        # Check admin permission
        if not await self.is_user_admin(message.from_user.id):
            response = await message.reply("❌ Admin only!")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            return
        
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", True):
            await self.delete_previous_message(message.from_user.id)
        
        try:
            # Get counts
            total_users = await self.db.total_users_count()
            banned_users = await self.db.get_banned_count()
            active_users = total_users - banned_users
            
            # Get all admins
            db_admins = await self.db.get_admins()
            all_admins = list(set(Config.ADMINS + db_admins))
            
            # Get force sub channels
            force_sub_channels = await self.db.get_force_sub_channels()
            
            # Get db channel
            db_channel = await self.db.get_db_channel()
            
            # Get stats picture
            settings = await self.db.get_settings()
            welcome_pics = settings.get("welcome_pics", Config.WELCOME_PICS)
            stats_pic = get_random_pic(welcome_pics)
            
            # Format message
            stats_text = (
                "📊 <b>BOT STATISTICS</b>\n\n"
                f"👥 Users: {total_users:,}\n"
                f"✅ Active: {active_users:,}\n"
                f"🚫 Banned: {banned_users:,}\n"
                f"👑 Admins: {len(all_admins)}\n"
                f"📢 Force Sub: {len(force_sub_channels)}\n"
                f"💾 DB Channel: {'✅' if db_channel else '❌'}\n\n"
                f"<i>Updated: {datetime.datetime.now().strftime('%H:%M:%S')}</i>"
            )
            
            buttons = [
                [
                    InlineKeyboardButton("👥 Users", callback_data="users_menu"),
                    InlineKeyboardButton("👑 Admins", callback_data="admin_list_menu")
                ],
                [
                    InlineKeyboardButton("🔄 Refresh", callback_data="refresh_stats"),
                    InlineKeyboardButton("📊 More", callback_data="more_stats")
                ],
                [
                    InlineKeyboardButton("⬅️ Back", callback_data="admin_panel"),
                    InlineKeyboardButton("❌ Close", callback_data="close")
                ]
            ]
            
            keyboard = InlineKeyboardMarkup(buttons)
            
            try:
                response = await message.reply_photo(
                    photo=stats_pic,
                    caption=stats_text,
                    reply_markup=keyboard,
                    parse_mode=enums.ParseMode.HTML
                )
            except Exception as e:
                logger.error(f"Error sending stats photo: {e}")
                response = await message.reply(
                    stats_text,
                    reply_markup=keyboard,
                    parse_mode=enums.ParseMode.HTML
                )
            
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            
        except Exception as e:
            logger.error(f"Error in stats command: {e}")
            response = await message.reply("❌ Error fetching statistics!")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
    
    async def broadcast_command(self, message: Message):
        """Handle /broadcast command - FIXED VERSION"""
        # Check admin permission
        if not await self.is_user_admin(message.from_user.id):
            response = await message.reply("❌ Admin only!")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            return
        
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", True):
            await self.delete_previous_message(message.from_user.id)
        
        if not message.reply_to_message:
            response = await message.reply(
                "📢 <b>BROADCAST MESSAGE</b>\n\n"
                "1. Send your message\n"
                "2. Reply with /broadcast\n\n"
                "Example:\n"
                "Your broadcast message...\n"
                "/broadcast",
                parse_mode=enums.ParseMode.HTML
            )
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            return
        
        try:
            # Get all users
            users = await self.db.get_all_users()
            total_users = len(users)
            
            if total_users == 0:
                response = await message.reply("❌ No users to broadcast to!")
                await self.store_bot_message(message.from_user.id, response.id, "conversation")
                return
            
            response = await message.reply(f"📢 Broadcasting to {total_users:,} users...")
            
            success = 0
            failed = 0
            
            # Send to all users
            for user_id in users:
                try:
                    # Skip if user is banned
                    if await self.db.is_user_banned(user_id):
                        failed += 1
                        continue
                    
                    # Forward the message
                    await message.reply_to_message.forward(user_id)
                    success += 1
                    
                    # Small delay to avoid flood
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    failed += 1
                    logger.error(f"Failed to send to {user_id}: {e}")
            
            await response.edit_text(
                f"✅ <b>Broadcast Complete!</b>\n\n"
                f"📊 Total Users: {total_users:,}\n"
                f"✅ Success: {success:,}\n"
                f"❌ Failed: {failed:,}\n"
                f"📈 Success Rate: {(success/total_users*100):.1f}%",
                parse_mode=enums.ParseMode.HTML
            )
            
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            
        except Exception as e:
            logger.error(f"Error in broadcast command: {e}")
            response = await message.reply("❌ Error during broadcast!")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
    
    async def ban_command(self, message: Message):
        """Handle /ban command - FIXED VERSION"""
        # Check admin permission
        if not await self.is_user_admin(message.from_user.id):
            response = await message.reply("❌ Admin only!")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            return
        
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", True):
            await self.delete_previous_message(message.from_user.id)
        
        if len(message.command) < 2:
            response = await message.reply(
                "🚫 <b>BAN USER</b>\n\n"
                "Usage: <code>/ban user_id [reason]</code>\n\n"
                "Example: <code>/ban 123456789 Spamming</code>",
                parse_mode=enums.ParseMode.HTML
            )
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            return
        
        try:
            user_id = int(message.command[1])
            reason = " ".join(message.command[2:]) if len(message.command) > 2 else "No reason provided"
            
            # Check if user exists
            try:
                user = await self.get_users(user_id)
            except:
                response = await message.reply("❌ User not found!")
                await self.store_bot_message(message.from_user.id, response.id, "conversation")
                return
            
            # Ban the user
            await self.db.ban_user(user_id, reason)
            
            # Try to notify the user
            try:
                await self.send_message(
                    user_id,
                    f"🚫 <b>You have been banned!</b>\n\n"
                    f"Reason: {reason}\n"
                    f"Contact admin if this is a mistake.",
                    parse_mode=enums.ParseMode.HTML
                )
            except:
                pass
            
            response = await message.reply(
                f"✅ <b>User Banned!</b>\n\n"
                f"👤 User: {user.first_name}\n"
                f"🆔 ID: {user_id}\n"
                f"📝 Reason: {reason}",
                parse_mode=enums.ParseMode.HTML
            )
            
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            
        except ValueError:
            response = await message.reply("❌ Invalid user ID!")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
        except Exception as e:
            logger.error(f"Error banning user: {e}")
            response = await message.reply("❌ Error banning user!")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
    
    async def unban_command(self, message: Message):
        """Handle /unban command - FIXED VERSION"""
        # Check admin permission
        if not await self.is_user_admin(message.from_user.id):
            response = await message.reply("❌ Admin only!")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            return
        
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", True):
            await self.delete_previous_message(message.from_user.id)
        
        if len(message.command) < 2:
            response = await message.reply(
                "✅ <b>UNBAN USER</b>\n\n"
                "Usage: <code>/unban user_id</code>\n\n"
                "Example: <code>/unban 123456789</code>",
                parse_mode=enums.ParseMode.HTML
            )
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            return
        
        try:
            user_id = int(message.command[1])
            
            # Check if user is banned
            if not await self.db.is_user_banned(user_id):
                response = await message.reply("⚠️ User is not banned!")
                await self.store_bot_message(message.from_user.id, response.id, "conversation")
                return
            
            # Unban the user
            await self.db.unban_user(user_id)
            
            # Try to notify the user
            try:
                await self.send_message(
                    user_id,
                    "✅ <b>You have been unbanned!</b>\n\n"
                    "You can now use the bot again.",
                    parse_mode=enums.ParseMode.HTML
                )
            except:
                pass
            
            response = await message.reply(
                f"✅ <b>User Unbanned!</b>\n\n"
                f"🆔 User ID: {user_id}\n"
                f"✅ Status: Unbanned",
                parse_mode=enums.ParseMode.HTML
            )
            
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            
        except ValueError:
            response = await message.reply("❌ Invalid user ID!")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
        except Exception as e:
            logger.error(f"Error unbanning user: {e}")
            response = await message.reply("❌ Error unbanning user!")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
    
    async def logs_command(self, message: Message):
        """Handle /logs command - FIXED VERSION"""
        # Check admin permission
        if not await self.is_user_admin(message.from_user.id):
            response = await message.reply("❌ Admin only!")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            return
        
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", True):
            await self.delete_previous_message(message.from_user.id)
        
        try:
            # Check if log file exists
            if not os.path.exists('bot.log'):
                response = await message.reply("❌ Log file not found!")
                await self.store_bot_message(message.from_user.id, response.id, "conversation")
                return
            
            # Read last 1000 lines from log file
            with open('bot.log', 'r') as f:
                lines = f.readlines()
                last_lines = lines[-1000:] if len(lines) > 1000 else lines
            
            log_content = ''.join(last_lines)
            
            # Create a temporary file
            log_file = "bot_logs.txt"
            with open(log_file, 'w') as f:
                f.write(log_content)
            
            # Send the log file
            await message.reply_document(
                document=log_file,
                caption="📊 <b>Bot Logs</b>\n\nLast 1000 lines from bot.log",
                parse_mode=enums.ParseMode.HTML
            )
            
            # Clean up
            os.remove(log_file)
            
        except Exception as e:
            logger.error(f"Error in logs command: {e}")
            response = await message.reply(f"❌ Error fetching logs: {str(e)}")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
    
    # ===================================
    # SECTION 11: FILE MANAGEMENT COMMANDS (FIXED)
    # ===================================
    
    async def getlink_command(self, message: Message):
        """Handle /getlink command - FIXED VERSION"""
        if not await self.is_user_admin(message.from_user.id):
            response = await message.reply("❌ Admin only!")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            return
        
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", True):
            await self.delete_previous_message(message.from_user.id)
        
        if message.reply_to_message:
            # Generate link for replied message
            await self.genlink_command(message)
        else:
            response = await message.reply(
                "🔗 <b>GET LINK</b>\n\n"
                "Reply to a file with\n"
                "/getlink to generate\n"
                "a shareable link",
                parse_mode=enums.ParseMode.HTML
            )
            
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
    
    async def genlink_command(self, message: Message):
        """Handle /genlink command - FIXED VERSION"""
        if not await self.is_user_admin(message.from_user.id):
            response = await message.reply("❌ Admin only!")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            return
        
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", True):
            await self.delete_previous_message(message.from_user.id)
        
        if not message.reply_to_message:
            response = await message.reply(
                "🔗 <b>GENERATE LINK</b>\n\n"
                "Reply to a file with\n"
                "/genlink to create\n"
                "a shareable link",
                parse_mode=enums.ParseMode.HTML
            )
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            return
        
        if not self.db_channel:
            response = await message.reply("❌ Set database channel first!")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            return
        
        try:
            # Forward message to database channel
            forwarded = await message.reply_to_message.forward(self.db_channel)
            
            # Generate link
            base64_id = await encode(f"file_{forwarded.id}")
            bot_username = Config.BOT_USERNAME
            link = f"https://t.me/{bot_username}?start={base64_id}"
            
            response = await message.reply(
                f"✅ <b>Link Generated!</b>\n\n"
                f"🔗 Link:\n"
                f"<code>{link}</code>\n\n"
                "Share this link with users",
                parse_mode=enums.ParseMode.HTML,
                disable_web_page_preview=True
            )
            
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            
        except Exception as e:
            logger.error(f"Error generating link: {e}")
            response = await message.reply("❌ Error generating link!")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
    
    # ===================================
    # SECTION 12: SETTINGS COMMANDS (UPDATED - FIXED)
    # ===================================
    
    async def settings_command(self, message: Message):
        """Handle /settings command - FIXED VERSION"""
        # Check admin permission
        if not await self.is_user_admin(message.from_user.id):
            response = await message.reply("❌ Admin only!")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            return
        
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", True):
            await self.delete_previous_message(message.from_user.id)
        
        # Get current settings
        settings = await self.db.get_settings()
        welcome_pics = settings.get("welcome_pics", Config.WELCOME_PICS)
        
        # Get random settings picture
        settings_pic = get_random_pic(welcome_pics)
        
        # Format settings
        settings_text = (
            "⚙️ <b> 𝗕𝗢𝗧 𝗦𝗘𝗧𝗧𝗜𝗡𝗚𝗦 </b>\n\n"
            f"•  ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ: {'✅' if settings.get('protect_content') else '❌'}\n"
            f"•  ʜɪᴅᴇ ᴄᴀᴘᴛɪᴏɴ: {'✅' if settings.get('hide_caption') else '❌'}\n"
            f"•  ᴄʜᴀɴɴᴇʟ ʙᴜᴛᴛᴏɴ: {'✅' if settings.get('channel_button') else '❌'}\n"
            f"•  ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ: {'✅' if settings.get('auto_delete') else '❌'}\n"
            f"•  ғᴏʀᴄᴇ sᴜʙ: {'✅' if settings.get('request_fsub') else '❌'}\n"
            f"•  ʙᴏᴛ ᴍsɢ ᴅᴇʟᴇᴛᴇ: {'✅' if settings.get('auto_delete_bot_messages') else '❌'}\n\n"
            "Select a category to configure:"
        )
        
        # Create button grid
        buttons = [
            [
                InlineKeyboardButton("ғɪʟᴇs", callback_data="files_settings"),
                InlineKeyboardButton("  ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ", callback_data="auto_delete_settings")
            ],
            [
                InlineKeyboardButton("ғᴏʀᴄᴇ sᴜʙ", callback_data="force_sub_settings"),
                InlineKeyboardButton("ʙᴏᴛ ᴍᴇssᴀɢᴇs", callback_data="bot_msg_settings")
            ],
            [
                InlineKeyboardButton(" ʙᴜᴛᴛᴏɴ", callback_data="custom_buttons_menu"),
                InlineKeyboardButton(" Texts", callback_data="custom_texts_menu")
            ],
            [
                InlineKeyboardButton(" 🔙 Back", callback_data="admin_panel"),
                InlineKeyboardButton(" Close ✖️", callback_data="close")
            ]
        ]
        
        keyboard = InlineKeyboardMarkup(buttons)
        
        try:
            response = await message.reply_photo(
                photo=settings_pic,
                caption=settings_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Error sending settings photo: {e}")
            response = await message.reply(
                settings_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
        
        await self.store_bot_message(message.from_user.id, response.id, "conversation")
    
    async def files_command(self, message: Message):
        """Handle /files command - FIXED VERSION"""
        # Check admin permission
        if not await self.is_user_admin(message.from_user.id):
            response = await message.reply("❌ Admin only!")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            return
        
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", True):
            await self.delete_previous_message(message.from_user.id)
    
        # Get current settings
        settings = await self.db.get_settings()
        protect_content = settings.get("protect_content", True)
        hide_caption = settings.get("hide_caption", False)
        channel_button = settings.get("channel_button", True)
        files_pics = settings.get("files_pics", Config.FILES_PICS)
    
        # Get random files picture
        files_pic = get_random_pic(files_pics)
    
        # Format
        protect_status = "ᴅɪsᴀʙʟᴇᴅ ❌" if not protect_content else "ᴇɴᴀʙʟᴇᴅ ✅"
        hide_status = "ᴅɪsᴀʙʟᴇᴅ ❌" if not hide_caption else "ᴇɴᴀʙʟᴇᴅ ✅"
        button_status = "ᴇɴᴀʙʟᴇᴅ ✅" if channel_button else "ᴅɪsᴀʙʟᴇᴅ ❌"
    
        files_text = (
            "<b> 𝗙𝗜𝗟𝗘𝗦 𝗥𝗘𝗟𝗔𝗧𝗘𝗗 𝗦𝗘𝗧𝗧𝗜𝗡𝗚𝗦 </b>\n\n"
            '<blockquote><b>'
            f"🔒ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ: {protect_status}\n"
            f"🫥ʜɪᴅᴇ ᴄᴀᴘᴛɪᴏɴ: {hide_status}\n"
            f"🔘ᴄʜᴀɴɴᴇʟ ʙᴜᴛᴛᴏɴ: {button_status}"
            "</b></blockquote>\n\n"
            "<b> ᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴs ᴛᴏ ᴄʜᴀɴɢᴇ sᴇᴛᴛɪɴɴɢs </b>"
        )

        
        # Create toggle buttons
        buttons = []
        
        # Protect Content toggle
        if protect_content:
            buttons.append([
                InlineKeyboardButton(f"Protect Content: {'✅' if protect_content else '❌'}",callback_data="toggle_protect_content"),
                InlineKeyboardButton(f"Hide Caption: {'✅' if hide_caption else '❌'}",callback_data="toggle_hide_caption")
            ])
        
        # Channel Button toggle
        if channel_button:
            buttons.append([
        InlineKeyboardButton(f"Channel Button: {'✅' if channel_button else '❌'}",callback_data="toggle_channel_button"),
        InlineKeyboardButton("🔘 CUSTOM BUTTON", callback_data="custom_buttons_menu")
        ])
        
        buttons.append([
            InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings_menu"),
            InlineKeyboardButton("ᴄʟᴏsᴇ ✖️", callback_data="close")
        ])
        
        keyboard = InlineKeyboardMarkup(buttons)
        
        try:
            response = await message.reply_photo(
                photo=files_pic,
                caption=files_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Error sending files photo: {e}")
            response = await message.reply(
                files_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
        
        await self.store_bot_message(message.from_user.id, response.id, "conversation")
    
    async def auto_del_command(self, message: Message):
        """Handle /auto_del command - FIXED VERSION"""
        # Check admin permission
        if not await self.is_user_admin(message.from_user.id):
            response = await message.reply("❌ Admin only!")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            return
    
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", True):
            await self.delete_previous_message(message.from_user.id)
    
        # Get current settings
        settings = await self.db.get_settings()
        auto_delete = settings.get("auto_delete", False)
        auto_delete_time = settings.get("auto_delete_time", 300)
        auto_del_pics = settings.get("auto_del_pics", Config.AUTO_DEL_PICS)
    
        # Get random auto delete picture
        auto_del_pic = get_random_pic(auto_del_pics)
    
        # Format
        status = "ENABLED" if auto_delete else "DISABLED"
        time_text = format_time(auto_delete_time)
    
        auto_del_text = (
            "<b> 🤖 𝗔𝗨𝗧𝗢 𝗗𝗘𝗟𝗘𝗧𝗘 𝗦𝗘𝗧𝗧𝗜𝗡𝗚𝗦 ⚙️ </b>\n\n"
            '<blockquote><b>'
            f"🗑️ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴍᴏᴅᴇ: {status}\n"
            f"⏱️ ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇʀ: {time_text}\n"
            "</b></blockquote>\n"
            "<b> ᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴs ᴛᴏ ᴄʜᴀɴɢᴇ sᴇᴛᴛɪɴɢs </b>"
        )
        
        buttons = []

        # Auto Delete toggle button
        buttons.append([
               InlineKeyboardButton(f"Auto Delete: {'✅' if auto_delete else '❌'}", callback_data="toggle_auto_delete"),
               InlineKeyboardButton("Set Timer ⏱️", callback_data="set_timer")])

        # Time buttons (only show if auto delete is enabled)
        if auto_delete:
            time_buttons = []
            for time_sec in AUTO_DELETE_TIMES:
                time_display = format_time(time_sec)
                time_buttons.append([InlineKeyboardButton(time_display, callback_data=f"autodel_{time_sec}")])

            # Add time buttons in rows
            buttons.append(time_buttons[:3])
            if len(time_buttons) > 3:
                buttons.append(time_buttons[3:])
        
        buttons.append([
            InlineKeyboardButton("ʀᴇғʀᴇsʜ", callback_data="refresh_autodel"),
            InlineKeyboardButton("ᴄʟᴏsᴇ ✖️", callback_data="close")
        ])
        
        keyboard = InlineKeyboardMarkup(buttons)
        
        try:
            response = await message.reply_photo(
                photo=auto_del_pic,
                caption=auto_del_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Error sending auto delete photo: {e}")
            response = await message.reply(
                auto_del_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
        
        await self.store_bot_message(message.from_user.id, response.id, "conversation")
    
    async def req_fsub_command(self, message: Message):
        """Handle /req_fsub command - FIXED VERSION"""
        # Check admin permission
        if not await self.is_user_admin(message.from_user.id):
            response = await message.reply("❌ Admin only!")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            return
        
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", True):
            await self.delete_previous_message(message.from_user.id)
        
        # Get current settings
        settings = await self.db.get_settings()
        request_fsub = settings.get("request_fsub", False)
        force_sub_pics = settings.get("force_sub_pics", Config.FORCE_SUB_PICS)
        
        # Get random force sub picture
        force_sub_pic = get_random_pic(force_sub_pics)
        
        # Format
        status = "ENABLED" if request_fsub else "DISABLED"
        
        req_fsub_text = (
            "<b> REQUEST FSUB SETTINGS </b>\n\n"
            f"REQUEST FSUB MODE: {status}\n\n"
            "CLICK BELOW BUTTONS TO CHANGE SETTINGS"
        )
        
        # Create toggle buttons
        buttons = []
        
        if request_fsub:
            buttons.append([
                InlineKeyboardButton(" ᴏғғ 🔴", callback_data="reqfsub_off"),
            InlineKeyboardButton("ᴍᴏʀᴇ sᴇᴛᴛɪɴɢs", callback_data="fsub_chnl_menu")  # FIXED: Changed to fsub_chnl_menu
        ])
        else:
            buttons.append([
                InlineKeyboardButton("ᴏɴ 🟢", callback_data="reqfsub_on"),
            InlineKeyboardButton("ᴍᴏʀᴇ sᴇᴛᴛɪɴɢs", callback_data="fsub_chnl_menu")  # FIXED: Changed to fsub_chnl_menu
        ])
        
        buttons.append([
            InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings_menu"),
            InlineKeyboardButton("ᴄʟᴏsᴇ ✖️", callback_data="close")
        ])
        
        keyboard = InlineKeyboardMarkup(buttons)
        
        try:
            response = await message.reply_photo(
                photo=force_sub_pic,
                caption=req_fsub_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Error sending force sub photo: {e}")
            response = await message.reply(
                req_fsub_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
        
        await self.store_bot_message(message.from_user.id, response.id, "conversation")
    
    async def botsettings_command(self, message: Message):
        """Handle /botsettings command - Enhanced auto-delete info - FIXED VERSION"""
        # Check admin permission
        if not await self.is_user_admin(message.from_user.id):
            response = await message.reply("❌ Admin only!")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            return
            
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", True):
            await self.delete_previous_message(message.from_user.id)
        
        # Get current settings
        settings = await self.db.get_settings()
        auto_delete_bot = settings.get("auto_delete_bot_messages", False)
        auto_delete_time = settings.get("auto_delete_time_bot", 30)
        welcome_pics = settings.get("welcome_pics", Config.WELCOME_PICS)
        
        # Get random picture
        settings_pic = get_random_pic(welcome_pics)
        
        status = "ENABLED" if auto_delete_bot else "DISABLED"
        
        settings_text = (
            "🤖 <b>BOT MESSAGE SETTINGS</b>\n\n"
            f"🗑️ Auto Delete: {status}\n"
            f"⏱️ Delete After: {auto_delete_time}s\n\n"
            "<b>Enhanced Auto-Delete:</b>\n"
            "✅ Only deletes conversation messages\n"
            "✅ Preserves file messages\n"
            "✅ Preserves instruction messages\n"
            "✅ Clean PM experience"
        )
        
        buttons = []
        
        # Toggle button
        if auto_delete_bot:
            buttons.append([
                InlineKeyboardButton("❌ DISABLE", callback_data="toggle_auto_delete_bot")
            ])
        else:
            buttons.append([
                InlineKeyboardButton("✅ ENABLE", callback_data="toggle_auto_delete_bot")
            ])
        
        # Time buttons
        time_buttons = []
        time_options = [10, 30, 60, 120, 300]
        
        for time_sec in time_options:
            time_display = f"{time_sec}s"
            time_buttons.append(
                InlineKeyboardButton(time_display, callback_data=f"botmsg_time_{time_sec}")
            )
        
        # Split into rows
        for i in range(0, len(time_buttons), 3):
            row = time_buttons[i:i+3]
            buttons.append(row)
        
        # Back and Close
        buttons.append([
            InlineKeyboardButton("⬅️ Back", callback_data="settings_menu"),
            InlineKeyboardButton("❌ Close", callback_data="close")
        ])
        
        keyboard = InlineKeyboardMarkup(buttons)
        
        try:
            response = await message.reply_photo(
                photo=settings_pic,
                caption=settings_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Error sending bot settings photo: {e}")
            response = await message.reply(
                settings_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
        
        await self.store_bot_message(message.from_user.id, response.id, "conversation")
    
    # ===================================
    # SECTION 13: CALLBACK HANDLERS (FIXED - COMPLETE)
    # ===================================
    
    async def handle_callback_query(self, query: CallbackQuery):
        """Handle all callback queries - FIXED VERSION"""
        try:
            data = query.data
            
            # Check admin status for admin-only callbacks
            admin_callbacks = [
                "admin_panel", "settings_menu", "files_settings", "auto_delete_settings",
                "force_sub_settings", "bot_msg_settings", "fsub_chnl_menu", "add_fsub_menu",
                "del_fsub_menu", "refresh_fsub", "test_fsub", "reqfsub_on", "reqfsub_off",
                "users_menu", "stats_menu", "admin_list_menu", "refresh_users", "refresh_stats",
                "refresh_autodel", "toggle_protect_content", "toggle_hide_caption", "toggle_channel_button",
                "toggle_auto_delete", "toggle_auto_delete_bot", "custom_buttons_menu", "custom_texts_menu",
                "more_stats"
            ]
            
            if data in admin_callbacks:
                if not await self.is_user_admin(query.from_user.id):
                    await query.answer("Admin only!", show_alert=True)
                    return
            
            # Navigation callbacks
            if data == "start_menu":
                await query.answer()
                await self.show_welcome_message(query.message)
            
            elif data == "help_menu":
                await query.answer()
                await self.help_command(query.message)
            
            elif data == "about_menu":
                await query.answer()
                await self.about_command(query.message)
            
            elif data == "admin_panel":
                await query.answer()
                await self.cmd_command(query.message)
            
            elif data == "settings_menu":
                await query.answer()
                await self.settings_command(query.message)
            
            elif data == "files_settings":
                await query.answer()
                await self.files_command(query.message)
            
            elif data == "auto_delete_settings":
                await query.answer()
                await self.auto_del_command(query.message)
            
            elif data == "force_sub_settings":
                await query.answer()
                await self.forcesub_command(query.message)
            
            elif data == "bot_msg_settings":
                await query.answer()
                await self.botsettings_command(query.message)
            
            elif data == "fsub_chnl_menu":
                await query.answer()
                await self.fsub_chnl_command(query.message)
            
            elif data == "add_fsub_menu":
                await query.answer()
                await self.add_fsub_menu(query.message)
            
            elif data == "del_fsub_menu":
                await query.answer()
                await self.del_fsub_menu(query.message)
            
            elif data == "users_menu":
                await query.answer()
                await self.users_command(query.message)
            
            elif data == "stats_menu":
                await query.answer()
                await self.stats_command(query.message)
            
            elif data == "admin_list_menu":
                await query.answer()
                await self.admin_list_command(query.message)
            
            # Force Subscribe callbacks
            elif data == "reqfsub_on":
                await query.answer()
                await self.handle_reqfsub_on(query)
            
            elif data == "reqfsub_off":
                await query.answer()
                await self.handle_reqfsub_off(query)
            
            elif data == "refresh_fsub":
                await query.answer("Refreshing...")
                await self.forcesub_command(query.message)
            
            elif data == "test_fsub":
                await query.answer("Testing force subscribe...")
                await self.test_force_sub(query)
            
            # Resend files callback
            elif data == "resend_files":
                await query.answer("Resending files...")
                await self.resend_files_callback(query)
            
            # Toggle callbacks
            elif data.startswith("toggle_"):
                await query.answer()
                await self.handle_toggle_callback(query)
            
            # Auto delete time callbacks
            elif data.startswith("autodel_"):
                await query.answer()
                await self.handle_autodel_callback(query)
            
            # Bot message time callbacks
            elif data.startswith("botmsg_time_"):
                await query.answer()
                await self.handle_botmsg_time_callback(query)
            
            # Refresh callbacks
            elif data.startswith("refresh_"):
                await query.answer("Refreshing...")
                await self.refresh_callback(query)
            
            # Close callback
            elif data == "close":
                await query.answer("Closed!")
                await query.message.delete()
            
            else:
                await query.answer("Button not configured!", show_alert=True)
        
        except Exception as e:
            logger.error(f"Error handling callback: {e}")
            await query.answer("Error processing request!", show_alert=True)
    
    async def handle_toggle_callback(self, query: CallbackQuery):
        """Handle toggle callbacks"""
        data = query.data.replace("toggle_", "")
        
        # Get current settings
        settings = await self.db.get_settings()
        current_value = settings.get(data, False)
        
        # Toggle the value
        new_value = not current_value
        
        # Update in database
        await self.db.update_setting(data, new_value)
        
        # Update local settings
        self.settings[data] = new_value
        
        await query.answer(f"{'Enabled' if new_value else 'Disabled'}")
        
        # Refresh the settings page
        if data in ["protect_content", "hide_caption", "channel_button"]:
            await self.files_command(query.message)
        elif data == "auto_delete":
            await self.auto_del_command(query.message)
        elif data == "auto_delete_bot_messages":
            await self.botsettings_command(query.message)
    
    async def handle_autodel_callback(self, query: CallbackQuery):
        """Handle auto delete time callbacks"""
        try:
            seconds = int(query.data.replace("autodel_", ""))
            
            # Update auto delete time
            await self.db.update_setting("auto_delete_time", seconds)
            
            # Update local settings
            self.settings["auto_delete_time"] = seconds
            
            await query.answer(f"Time set to {format_time(seconds)}")
            
            # Refresh the auto delete settings page
            await self.auto_del_command(query.message)
        
        except Exception as e:
            logger.error(f"Error in autodel callback: {e}")
            await query.answer("Error setting time!")
    
    async def handle_reqfsub_callback(self, query: CallbackQuery):
        """Handle request FSub callbacks"""
        action = query.data.replace("reqfsub_", "")
        new_value = (action == "on")
        
        # Update setting
        await self.db.update_setting("request_fsub", new_value)
        self.settings["request_fsub"] = new_value
        
        await query.answer(f"{'Enabled' if new_value else 'Disabled'}")
        
        # Refresh the settings page
        await self.req_fsub_command(query.message)
    
    async def handle_botmsg_time_callback(self, query: CallbackQuery):
        """Handle bot message time callbacks"""
        try:
            seconds = int(query.data.replace("botmsg_time_", ""))
            
            # Update bot message delete time
            await self.db.update_setting("auto_delete_time_bot", seconds)
            
            # Update local settings
            self.settings["auto_delete_time_bot"] = seconds
            
            await query.answer(f"Bot message delete time set to {seconds}s")
            
            # Refresh the settings page
            await self.botsettings_command(query.message)
        
        except Exception as e:
            logger.error(f"Error in botmsg_time callback: {e}")
            await query.answer("Error setting time!")
    
    async def refresh_callback(self, query: CallbackQuery):
        """Handle refresh callback"""
        await query.answer("Refreshing...")
        
        # Delete previous bot message if auto-delete is enabled
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", True):
            await self.delete_previous_message(query.from_user.id)
        
        # Check what type of page we're on
        message_text = query.message.text or ""
        
        if "USER STATISTICS" in message_text or "👥" in message_text:
            await self.users_command(query.message)
        elif "FILE SETTINGS" in message_text or "📁" in message_text:
            await self.files_command(query.message)
        elif "AUTO DELETE SETTINGS" in message_text or "🗑️" in message_text:
            await self.auto_del_command(query.message)
        elif "FORCE SUBSCRIBE" in message_text or "👥" in message_text:
            await self.req_fsub_command(query.message)
        elif "BOT STATISTICS" in message_text or "📊" in message_text:
            await self.stats_command(query.message)
        elif "BOT SETTINGS" in message_text or "⚙️" in message_text:
            await self.settings_command(query.message)
        else:
            # Default: delete and show start
            await query.message.delete()
            await self.show_welcome_message(query.message)
    
    async def resend_files_callback(self, query: CallbackQuery):
        """Resend files after deletion"""
        await query.answer("Resending files...")
        
        user_id = query.from_user.id
        
        try:
            # Check if user has file history
            if user_id in self.user_file_history:
                # Get the most recent file entry
                recent_files = self.user_file_history[user_id][-1]
                file_ids = recent_files.get("file_ids", [])
                
                if file_ids:
                    # Resend files
                    for file_id in file_ids[:MAX_SPECIAL_FILES]:
                        try:
                            response = await self.copy_message(
                                chat_id=query.message.chat.id,
                                from_chat_id=self.db_channel,
                                message_id=file_id,
                                protect_content=self.settings.get("protect_content", True)
                            )
                            
                            # Store as file type (won't be auto-deleted)
                            await self.store_bot_message(user_id, response.id, "file")
                            
                        except Exception as e:
                            logger.error(f"Error resending file {file_id}: {e}")
                    
                    await query.message.edit_text(
                        "✅ <b>Files resent!</b>\n\n"
                        f"Sent {len(file_ids)} files",
                        parse_mode=enums.ParseMode.HTML
                    )
                else:
                    await query.message.edit_text(
                        "❌ <b>No files to resend!</b>\n\n"
                        "Please use the original link again.",
                        parse_mode=enums.ParseMode.HTML
                    )
            else:
                await query.message.edit_text(
                    "❌ <b>No file history found!</b>\n\n"
                    "Please use the original link again.",
                    parse_mode=enums.ParseMode.HTML
                )
            
        except Exception as e:
            logger.error(f"Error in resend files callback: {e}")
            await query.answer("Error resending files!", show_alert=True)
    
    # ===================================
    # SECTION 14: UTILITY COMMANDS (FIXED)
    # ===================================
    
    async def ping_command(self, message: Message):
        """Handle /ping command"""
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", True):
            await self.delete_previous_message(message.from_user.id)
        
        start_time = time.time()
        response = await message.reply("🏓 Pinging...")
        end_time = time.time()
        
        ping_time = round((end_time - start_time) * 1000, 2)
        
        await response.edit_text(
            f"🏓 <b>Pong!</b>\n\n"
            f"📡 Ping: {ping_time}ms\n"
            f"⏰ Time: {datetime.datetime.now().strftime('%H:%M:%S')}",
            parse_mode=enums.ParseMode.HTML
        )
        
        await self.store_bot_message(message.from_user.id, response.id, "conversation")
    
    async def refresh_command(self, message: Message):
        """Handle /refresh command - FIXED VERSION"""
        if not await self.is_user_admin(message.from_user.id):
            response = await message.reply("❌ Admin only!")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            return
        
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", True):
            await self.delete_previous_message(message.from_user.id)
        
        response = await message.reply("🔄 Refreshing...")
        
        # Get updated counts
        total_users = await self.db.total_users_count()
        banned_users = await self.db.get_banned_count()
        active_users = total_users - banned_users
        
        await response.edit_text(
            f"✅ <b>Refreshed!</b>\n\n"
            f"👥 Users: {total_users:,}\n"
            f"✅ Active: {active_users:,}\n"
            f"🚫 Banned: {banned_users:,}\n\n"
            f"Updated: {datetime.datetime.now().strftime('%H:%M:%S')}",
            parse_mode=enums.ParseMode.HTML
        )
        
        await self.store_bot_message(message.from_user.id, response.id, "conversation")
    
    async def cmd_command(self, message: Message):
        """Handle /cmd command - FIXED VERSION"""
        # Check admin permission
        if not await self.is_user_admin(message.from_user.id):
            response = await message.reply("❌ Admin only!")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            return
        
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", True):
            await self.delete_previous_message(message.from_user.id)
        
        # Check if user is admin
        is_admin = await self.is_user_admin(message.from_user.id)
        
        # Get cmd picture
        settings_data = await self.db.get_settings()
        welcome_pics = settings_data.get("welcome_pics", Config.WELCOME_PICS)
        cmd_pic = get_random_pic(welcome_pics)
        
        cmd_text = (
            "📋 <b>BOT COMMANDS</b>\n\n"
            "✨ <b>BASIC COMMANDS:</b>\n"
            "• /start - Start bot\n"
            "• /help - Show help\n"
            "• /ping - Check status\n"
            "• /about - About bot\n"
        )
        
        if is_admin:
            cmd_text += (
                "\n👑 <b>ADMIN COMMANDS:</b>\n"
                "• /settings - Bot settings\n"
                "• /stats - View statistics\n"
                "• /users - User stats\n"
                "• /genlink - Generate link\n"
                "• /batch - Store files\n"
                "• /broadcast - Send message\n"
                "• /ban - Ban user\n"
                "• /unban - Unban user\n"
                "• /logs - View logs\n"
                "• /shortener - URL shortener\n"
            )
        
        buttons = []
        
        # Basic commands
        buttons.append([
            InlineKeyboardButton("/start", callback_data="send_start"),
            InlineKeyboardButton("/help", callback_data="send_help")
        ])
        
        if is_admin:
            # Admin commands
            buttons.append([
                InlineKeyboardButton("/settings", callback_data="send_settings"),
                InlineKeyboardButton("/stats", callback_data="send_stats")
            ])
            
            buttons.append([
                InlineKeyboardButton("/users", callback_data="send_users"),
                InlineKeyboardButton("/genlink", callback_data="send_genlink")
            ])
        
        buttons.append([
            InlineKeyboardButton("⬅️ Back", callback_data="start_menu"),
            InlineKeyboardButton("❌ Close", callback_data="close")
        ])
        
        keyboard = InlineKeyboardMarkup(buttons)
        
        try:
            response = await message.reply_photo(
                photo=cmd_pic,
                caption=cmd_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Error sending cmd photo: {e}")
            response = await message.reply(
                cmd_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
        
        await self.store_bot_message(message.from_user.id, response.id, "conversation")
    
    # ===================================
    # SECTION 15: FORCE SUBSCRIBE COMMANDS (FIXED - COMPLETE)
    # ===================================
    
    async def forcesub_command(self, message: Message):
        """Handle /forcesub command - FIXED VERSION"""
        # Check admin permission using new method
        if not await self.is_user_admin(message.from_user.id):
            response = await message.reply("❌ Admin only!")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            return
        
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", True):
            await self.delete_previous_message(message.from_user.id)
        
        # Get current force sub channels
        force_sub_channels = await self.db.get_force_sub_channels()
        
        # Get force sub pictures
        force_sub_pics = settings.get("force_sub_pics", Config.FORCE_SUB_PICS)
        force_sub_pic = get_random_pic(force_sub_pics)
        
        # Check request_fsub setting
        request_fsub = settings.get("request_fsub", False)
        request_status = "✅ ENABLED" if request_fsub else "❌ DISABLED"
        
        # Format message
        if force_sub_channels:
            channels_text = "<b>📢 FORCE SUBSCRIBE SETTINGS</b>\n\n"
            channels_text += f"🔄 Request FSub: {request_status}\n\n"
            channels_text += "<b>Current Channels:</b>\n"
            
            for i, channel in enumerate(force_sub_channels, 1):
                channel_id = channel.get("channel_id")
                username = channel.get("channel_username", "No username")
                
                channels_text += f"{i}. Channel ID: <code>{channel_id}</code>\n"
                channels_text += f"   Username: @{username}\n\n"
            
            channels_text += f"📊 Total Channels: {len(force_sub_channels)}"
        else:
            channels_text = "<b>📢 FORCE SUBSCRIBE SETTINGS</b>\n\n"
            channels_text += f"🔄 Request FSub: {request_status}\n\n"
            channels_text += "No force subscribe channels configured.\n"
            channels_text += "Use /add_fsub to add channels."
        
        # Create buttons
        buttons = []
        
        # Toggle Request FSub
        if request_fsub:
            buttons.append([
                InlineKeyboardButton("❌ DISABLE FSUB", callback_data="reqfsub_off"),
                InlineKeyboardButton("⚙️ CHANNELS", callback_data="fsub_chnl_menu")
            ])
        else:
            buttons.append([
                InlineKeyboardButton("✅ ENABLE FSUB", callback_data="reqfsub_on"),
                InlineKeyboardButton("⚙️ CHANNELS", callback_data="fsub_chnl_menu")
            ])
        
        # Management buttons
        buttons.append([
            InlineKeyboardButton("➕ ADD CHANNEL", callback_data="add_fsub_menu"),
            InlineKeyboardButton("➖ REMOVE CHANNEL", callback_data="del_fsub_menu")
        ])
        
        buttons.append([
            InlineKeyboardButton("🔄 REFRESH", callback_data="refresh_fsub"),
            InlineKeyboardButton("📊 TEST", callback_data="test_fsub")
        ])
        
        buttons.append([
            InlineKeyboardButton("🔙 BACK", callback_data="settings_menu"),
            InlineKeyboardButton("❌ CLOSE", callback_data="close")
        ])
        
        keyboard = InlineKeyboardMarkup(buttons)
        
        try:
            response = await message.reply_photo(
                photo=force_sub_pic,
                caption=channels_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Error sending forcesub photo: {e}")
            response = await message.reply(
                channels_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
        
        await self.store_bot_message(message.from_user.id, response.id, "conversation")
    
    async def fsub_chnl_command(self, message: Message):
        """Handle /fsub_chnl command - Fixed version"""
        if not await self.is_user_admin(message.from_user.id):
            response = await message.reply("❌ Admin only!")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            return
        
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", True):
            await self.delete_previous_message(message.from_user.id)
        
        # Get force sub channels
        force_sub_channels = await self.db.get_force_sub_channels()
        
        # Get force sub pictures
        force_sub_pics = settings.get("force_sub_pics", Config.FORCE_SUB_PICS)
        force_sub_pic = get_random_pic(force_sub_pics)
        
        # Format message
        if force_sub_channels:
            channels_text = "<b>📢 FORCE SUBSCRIBE CHANNELS</b>\n\n"
            
            for i, channel in enumerate(force_sub_channels, 1):
                channel_id = channel.get("channel_id")
                username = channel.get("channel_username", "No username")
                
                channels_text += f"{i}. Channel ID: <code>{channel_id}</code>\n"
                channels_text += f"   Username: @{username}\n\n"
            
            channels_text += f"📊 Total Channels: {len(force_sub_channels)}"
        else:
            channels_text = "<b>📢 FORCE SUBSCRIBE CHANNELS</b>\n\n"
            channels_text += "No force subscribe channels configured.\n"
            channels_text += "Use /add_fsub to add channels."
        
        # Create buttons
        buttons = []
        
        if force_sub_channels:
            buttons.append([
                InlineKeyboardButton("➕ Add Channel", callback_data="add_fsub_menu"),
                InlineKeyboardButton("➖ Remove Channel", callback_data="del_fsub_menu")
            ])
        else:
            buttons.append([
                InlineKeyboardButton("➕ Add Channel", callback_data="add_fsub_menu")
            ])
        
        buttons.append([
            InlineKeyboardButton("🔄 Refresh", callback_data="refresh_fsub"),
            InlineKeyboardButton("🔙 Back", callback_data="force_sub_settings")
        ])
        
        buttons.append([
            InlineKeyboardButton("❌ Close", callback_data="close")
        ])
        
        keyboard = InlineKeyboardMarkup(buttons)
        
        try:
            response = await message.reply_photo(
                photo=force_sub_pic,
                caption=channels_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Error sending fsub channels photo: {e}")
            response = await message.reply(
                channels_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
        
        await self.store_bot_message(message.from_user.id, response.id, "conversation")
    
    async def add_fsub_menu(self, message: Message):
        """Show add force sub channel menu"""
        if not await self.is_user_admin(message.from_user.id):
            response = await message.reply("❌ Admin only!")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            return
        
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", True):
            await self.delete_previous_message(message.from_user.id)
        
        help_text = (
            "➕ <b>ADD FORCE SUB CHANNEL</b>\n\n"
            "To add a force subscribe channel:\n\n"
            "1. <b>For Public Channels:</b>\n"
            "   <code>/add_fsub -100123456789 @username</code>\n\n"
            "2. <b>For Private Channels:</b>\n"
            "   <code>/add_fsub -100123456789</code>\n\n"
            "📝 <b>How to get Channel ID:</b>\n"
            "• Add @RawDataBot to your channel\n"
            "• Send any message\n"
            "• Copy the chat_id (it will be negative)\n\n"
            "⚠️ <b>Important:</b>\n"
            "• Bot must be admin in the channel\n"
            "• Channel ID must start with -100"
        )
        
        buttons = [
            [InlineKeyboardButton("🔙 BACK", callback_data="force_sub_settings")],
            [InlineKeyboardButton("❌ CLOSE", callback_data="close")]
        ]
        
        keyboard = InlineKeyboardMarkup(buttons)
        
        response = await message.reply(
            help_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
        
        await self.store_bot_message(message.from_user.id, response.id, "conversation")

    async def del_fsub_menu(self, message: Message):
        """Show delete force sub channel menu"""
        if not await self.is_user_admin(message.from_user.id):
            response = await message.reply("❌ Admin only!")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            return
        
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", True):
            await self.delete_previous_message(message.from_user.id)
        
        # Get current channels
        force_sub_channels = await self.db.get_force_sub_channels()
        
        if not force_sub_channels:
            response = await message.reply(
                "❌ No force subscribe channels to remove!",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 BACK", callback_data="force_sub_settings")]
                ])
            )
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            return
        
        # Create buttons for each channel
        buttons = []
        for channel in force_sub_channels:
            channel_id = channel.get("channel_id")
            username = channel.get("channel_username", "No username")
            
            button_text = f"Remove: {channel_id}"
            if username != "No username":
                button_text = f"Remove: @{username}"
            
            buttons.append([
                InlineKeyboardButton(button_text, callback_data=f"remove_channel_{channel_id}")
            ])
        
        buttons.append([
            InlineKeyboardButton("🔙 BACK", callback_data="force_sub_settings"),
            InlineKeyboardButton("❌ CLOSE", callback_data="close")
        ])
        
        keyboard = InlineKeyboardMarkup(buttons)
        
        response = await message.reply(
            "🗑️ <b>SELECT CHANNEL TO REMOVE</b>\n\n"
            f"Total channels: {len(force_sub_channels)}",
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
        
        await self.store_bot_message(message.from_user.id, response.id, "conversation")

    async def handle_reqfsub_on(self, query: CallbackQuery):
        """Enable request force subscribe"""
        await self.db.update_setting("request_fsub", True)
        self.settings["request_fsub"] = True
        
        await query.answer("✅ Request FSub Enabled!")
        
        # Refresh the page
        await self.forcesub_command(query.message)

    async def handle_reqfsub_off(self, query: CallbackQuery):
        """Disable request force subscribe"""
        await self.db.update_setting("request_fsub", False)
        self.settings["request_fsub"] = False
        
        await query.answer("❌ Request FSub Disabled!")
        
        # Refresh the page
        await self.forcesub_command(query.message)

    async def test_force_sub(self, query: CallbackQuery):
        """Test force subscribe functionality"""
        user_id = query.from_user.id
        
        # Get force sub channels
        force_sub_channels = await self.db.get_force_sub_channels()
        
        if not force_sub_channels:
            await query.answer("❌ No force subscribe channels configured!", show_alert=True)
            return
        
        # Check subscription status
        is_subscribed = await is_subscribed(self, user_id, force_sub_channels)
        
        if is_subscribed:
            await query.answer("✅ You are subscribed to all channels!", show_alert=True)
        else:
            # Show which channels are missing
            missing_channels = []
            for channel in force_sub_channels:
                channel_id = channel.get("channel_id")
                username = channel.get("channel_username", f"Channel {channel_id}")
                
                try:
                    # Check this specific channel
                    channel_check = await is_subscribed(self, user_id, [channel])
                    if not channel_check:
                        missing_channels.append(username)
                except:
                    missing_channels.append(username)
            
            message = f"❌ You need to join {len(missing_channels)} channel(s):\n"
            for channel in missing_channels[:5]:  # Show max 5
                message += f"• @{channel}\n"
            
            if len(missing_channels) > 5:
                message += f"... and {len(missing_channels) - 5} more"
            
            await query.answer(message, show_alert=True)
    
    async def add_fsub_command(self, message: Message):
        """Handle /add_fsub command - FIXED VERSION"""
        if not await self.is_user_admin(message.from_user.id):
            response = await message.reply("❌ Admin only!")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            return
        
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", True):
            await self.delete_previous_message(message.from_user.id)
        
        if len(message.command) < 2:
            response = await message.reply(
                "➕ <b>ADD FORCE SUB CHANNEL</b>\n\n"
                "Usage: <code>/add_fsub channel_id [username]</code>\n\n"
                "Example: <code>/add_fsub -100123456789 @channel_username</code>\n\n"
                "Note: Channel ID must be negative for groups/channels",
                parse_mode=enums.ParseMode.HTML
            )
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            return
        
        try:
            channel_id = int(message.command[1])
            username = message.command[2] if len(message.command) > 2 else None
            
            if username:
                username = username.lstrip('@')
            
            # Add channel to database
            await self.db.add_force_sub_channel(channel_id, username)
            
            # Update local cache
            self.force_sub_channels = await self.db.get_force_sub_channels()
            
            response = await message.reply(
                f"✅ <b>Channel Added!</b>\n\n"
                f"📢 Channel ID: <code>{channel_id}</code>\n"
                f"👤 Username: @{username if username else 'None'}\n\n"
                f"Total channels: {len(self.force_sub_channels)}",
                parse_mode=enums.ParseMode.HTML
            )
            
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            
        except ValueError:
            response = await message.reply("❌ Invalid channel ID! Must be a number.")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
        except Exception as e:
            logger.error(f"Error adding force sub channel: {e}")
            response = await message.reply("❌ Error adding channel!")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
    
    async def del_fsub_command(self, message: Message):
        """Handle /del_fsub command - FIXED VERSION"""
        if not await self.is_user_admin(message.from_user.id):
            response = await message.reply("❌ Admin only!")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            return
        
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", True):
            await self.delete_previous_message(message.from_user.id)
        
        if len(message.command) < 2:
            response = await message.reply(
                "➖ <b>REMOVE FORCE SUB CHANNEL</b>\n\n"
                "Usage: <code>/del_fsub channel_id</code>\n\n"
                "Example: <code>/del_fsub -100123456789</code>",
                parse_mode=enums.ParseMode.HTML
            )
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            return
        
        try:
            channel_id = int(message.command[1])
            
            # Remove channel from database
            await self.db.remove_force_sub_channel(channel_id)
            
            # Update local cache
            self.force_sub_channels = await self.db.get_force_sub_channels()
            
            response = await message.reply(
                f"✅ <b>Channel Removed!</b>\n\n"
                f"📢 Channel ID: <code>{channel_id}</code>\n\n"
                f"Remaining channels: {len(self.force_sub_channels)}",
                parse_mode=enums.ParseMode.HTML
            )
            
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
            
        except ValueError:
            response = await message.reply("❌ Invalid channel ID!")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
        except Exception as e:
            logger.error(f"Error removing force sub channel: {e}")
            response = await message.reply("❌ Error removing channel!")
            await self.store_bot_message(message.from_user.id, response.id, "conversation")
    
    # ===================================
    # SECTION 16: JOIN REQUEST HANDLER (FIXED)
    # ===================================
    
    async def handle_join_request(self, join_request: ChatJoinRequest):
        """Handle chat join requests"""
        try:
            user_id = join_request.from_user.id
            chat_id = join_request.chat.id
            
            # Save join request to database
            await self.db.save_join_request(user_id, chat_id)
            
            # Get auto approve setting
            settings = await self.db.get_settings()
            auto_approve = settings.get("auto_approve", Config.AUTO_APPROVE_MODE)
            
            if auto_approve:
                # Auto approve the request
                try:
                    await join_request.approve()
                    await self.db.update_request_status(user_id, chat_id, "approved")
                    
                    # Notify user
                    try:
                        await self.send_message(
                            user_id,
                            f"✅ <b>Request Approved!</b>\n\n"
                            f"You have been added to the channel.",
                            parse_mode=enums.ParseMode.HTML
                        )
                    except:
                        pass
                    
                    logger.info(f"Auto-approved join request from {user_id}")
                    
                except Exception as e:
                    logger.error(f"Error auto-approving join request: {e}")
            
            else:
                # Notify admins about pending request
                for admin_id in Config.ADMINS:
                    try:
                        await self.send_message(
                            admin_id,
                            f"📨 <b>New Join Request</b>\n\n"
                            f"👤 User: {join_request.from_user.first_name}\n"
                            f"🆔 ID: <code>{user_id}</code>\n"
                            f"📺 Channel: {join_request.chat.title}\n\n"
                            f"Use /approve_{user_id}_{chat_id} to approve",
                            parse_mode=enums.ParseMode.HTML
                        )
                    except:
                        pass
            
        except Exception as e:
            logger.error(f"Error handling join request: {e}")

    # ===================================
    # SECTION 17: ADDITIONAL COMMAND HANDLERS (FIXED)
    # ===================================
    
    async def text_message_handler(self, message: Message):
        """Handle text messages from admins"""
        # Check if user is admin
        if not await self.is_user_admin(message.from_user.id):
            return
        
        # Check if message is a reply
        if message.reply_to_message:
            # Handle batch commands
            if message.from_user.id in self.batch_state:
                await self.handle_batch_state(message)
            elif message.from_user.id in self.custom_batch_state:
                await self.handle_custom_batch_state(message)
            elif message.from_user.id in self.special_link_state:
                await self.handle_special_link_state(message)
            elif message.from_user.id in self.button_setting_state:
                await self.handle_button_setting_state(message)
            elif message.from_user.id in self.text_setting_state:
                await self.handle_text_setting_state(message)
    
    async def handle_batch_state(self, message: Message):
        """Handle batch state"""
        user_id = message.from_user.id
        
        if user_id in self.batch_state:
            state = self.batch_state[user_id]
            
            # Get replied message
            replied = message.reply_to_message
            
            # Forward to database channel
            try:
                forwarded = await replied.forward(self.db_channel)
                state["files"].append(forwarded.id)
                
                # Update count
                state["count"] += 1
                
                if state["count"] >= state["limit"]:
                    # Generate batch link
                    file_ids = ",".join(str(fid) for fid in state["files"])
                    encoded = await encode(file_ids)
                    bot_username = Config.BOT_USERNAME
                    link = f"https://t.me/{bot_username}?start=batch_{encoded}"
                    
                    await message.reply(
                        f"✅ <b>Batch Complete!</b>\n\n"
                        f"📁 Files: {len(state['files'])}\n"
                        f"🔗 Link:\n"
                        f"<code>{link}</code>",
                        parse_mode=enums.ParseMode.HTML
                    )
                    
                    # Clear state
                    del self.batch_state[user_id]
                else:
                    await message.reply(
                        f"📁 File {state['count']}/{state['limit']} added!\n"
                        f"Reply with next file or send /done to finish.",
                        parse_mode=enums.ParseMode.HTML
                    )
                    
            except Exception as e:
                logger.error(f"Error in batch state: {e}")
                await message.reply("❌ Error processing file!")
    
    async def handle_custom_batch_state(self, message: Message):
        """Handle custom batch state"""
        user_id = message.from_user.id
        
        if user_id in self.custom_batch_state:
            state = self.custom_batch_state[user_id]
            
            if state["step"] == "waiting_message":
                # Store custom message
                state["message"] = message.text
                state["step"] = "waiting_files"
                
                await message.reply(
                    f"✅ Custom message saved!\n\n"
                    f"Now reply with files (max {MAX_CUSTOM_BATCH}).\n"
                    f"Send /done when finished.",
                    parse_mode=enums.ParseMode.HTML
                )
            
            elif state["step"] == "waiting_files":
                # Get replied message
                replied = message.reply_to_message
                
                # Forward to database channel
                try:
                    forwarded = await replied.forward(self.db_channel)
                    state["files"].append(forwarded.id)
                    
                    # Update count
                    state["count"] += 1
                    
                    if state["count"] >= MAX_CUSTOM_BATCH:
                        # Create special link
                        link_id = f"special_{random.randint(10000, 99999)}"
                        await self.db.save_special_link(link_id, state["message"], state["files"])
                        
                        bot_username = Config.BOT_USERNAME
                        link = f"https://t.me/{bot_username}?start=link_{link_id}"
                        
                        await message.reply(
                            f"✅ <b>Custom Batch Complete!</b>\n\n"
                            f"📁 Files: {len(state['files'])}\n"
                            f"💬 Custom message added\n"
                            f"🔗 Link:\n"
                            f"<code>{link}</code>",
                            parse_mode=enums.ParseMode.HTML
                        )
                        
                        # Clear state
                        del self.custom_batch_state[user_id]
                    else:
                        await message.reply(
                            f"📁 File {state['count']}/{MAX_CUSTOM_BATCH} added!\n"
                            f"Reply with next file or send /done to finish.",
                            parse_mode=enums.ParseMode.HTML
                        )
                        
                except Exception as e:
                    logger.error(f"Error in custom batch: {e}")
                    await message.reply("❌ Error processing file!")
    
    async def handle_special_link_state(self, message: Message):
        """Handle special link state"""
        user_id = message.from_user.id
        
        if user_id in self.special_link_state:
            state = self.special_link_state[user_id]
            
            if state["step"] == "waiting_message":
                # Store custom message
                state["message"] = message.text
                state["step"] = "waiting_files"
                
                await message.reply(
                    f"✅ Custom message saved!\n\n"
                    f"Now reply with files (max {MAX_SPECIAL_FILES}).\n"
                    f"Send /done when finished.",
                    parse_mode=enums.ParseMode.HTML
                )
            
            elif state["step"] == "waiting_files":
                # Get replied message
                replied = message.reply_to_message
                
                # Forward to database channel
                try:
                    forwarded = await replied.forward(self.db_channel)
                    state["files"].append(forwarded.id)
                    
                    # Update count
                    state["count"] += 1
                    
                    if state["count"] >= MAX_SPECIAL_FILES:
                        # Create special link
                        link_id = state.get("link_id", f"special_{random.randint(10000, 99999)}")
                        await self.db.save_special_link(link_id, state["message"], state["files"])
                        
                        bot_username = Config.BOT_USERNAME
                        link = f"https://t.me/{bot_username}?start=link_{link_id}"
                        
                        await message.reply(
                            f"✅ <b>Special Link Created!</b>\n\n"
                            f"📁 Files: {len(state['files'])}\n"
                            f"💬 Custom message included\n"
                            f"🔗 Link:\n"
                            f"<code>{link}</code>",
                            parse_mode=enums.ParseMode.HTML
                        )
                        
                        # Clear state
                        del self.special_link_state[user_id]
                    else:
                        await message.reply(
                            f"📁 File {state['count']}/{MAX_SPECIAL_FILES} added!\n"
                            f"Reply with next file or send /done to finish.",
                            parse_mode=enums.ParseMode.HTML
                        )
                        
                except Exception as e:
                    logger.error(f"Error in special link: {e}")
                    await message.reply("❌ Error processing file!")
    
    async def handle_button_setting_state(self, message: Message):
        """Handle button setting state"""
        user_id = message.from_user.id
        
        if user_id in self.button_setting_state:
            button_text = message.text
            
            # Parse button configuration
            buttons = parse_button_string(button_text)
            
            if buttons:
                # Save button configuration
                await self.db.update_setting("custom_button", button_text)
                
                await message.reply(
                    f"✅ <b>Custom Buttons Saved!</b>\n\n"
                    f"Total buttons: {sum(len(row) for row in buttons)}",
                    parse_mode=enums.ParseMode.HTML
                )
            else:
                await message.reply(
                    "❌ Invalid button format!\n\n"
                    "Format:\n"
                    "Button Text | URL : Button Text 2 | URL2\n"
                    "Button Text 3 | URL3",
                    parse_mode=enums.ParseMode.HTML
                )
            
            # Clear state
            del self.button_setting_state[user_id]
    
    async def handle_text_setting_state(self, message: Message):
        """Handle text setting state"""
        user_id = message.from_user.id
        
        if user_id in self.text_setting_state:
            text_type = self.text_setting_state[user_id]["type"]
            text_content = message.text
            
            # Save text setting
            await self.db.update_setting(text_type, text_content)
            
            await message.reply(
                f"✅ <b>{text_type.replace('_', ' ').title()} Updated!</b>",
                parse_mode=enums.ParseMode.HTML
            )
            
            # Clear state
            del self.text_setting_state[user_id]
    
    async def done_command(self, message: Message):
        """Handle /done command"""
        user_id = message.from_user.id
        
        # Check which state user is in
        if user_id in self.batch_state:
            state = self.batch_state[user_id]
            
            if state["files"]:
                # Generate batch link
                file_ids = ",".join(str(fid) for fid in state["files"])
                encoded = await encode(file_ids)
                bot_username = Config.BOT_USERNAME
                link = f"https://t.me/{bot_username}?start=batch_{encoded}"
                
                await message.reply(
                    f"✅ <b>Batch Complete!</b>\n\n"
                    f"📁 Files: {len(state['files'])}\n"
                    f"🔗 Link:\n"
                    f"<code>{link}</code>",
                    parse_mode=enums.ParseMode.HTML
                )
            else:
                await message.reply("❌ No files added to batch!")
            
            # Clear state
            del self.batch_state[user_id]
        
        elif user_id in self.custom_batch_state:
            state = self.custom_batch_state[user_id]
            
            if state["files"]:
                # Create special link
                link_id = f"special_{random.randint(10000, 99999)}"
                await self.db.save_special_link(link_id, state["message"], state["files"])
                
                bot_username = Config.BOT_USERNAME
                link = f"https://t.me/{bot_username}?start=link_{link_id}"
                
                await message.reply(
                    f"✅ <b>Custom Batch Complete!</b>\n\n"
                    f"📁 Files: {len(state['files'])}\n"
                    f"💬 Custom message included\n"
                    f"🔗 Link:\n"
                    f"<code>{link}</code>",
                    parse_mode=enums.ParseMode.HTML
                )
            else:
                await message.reply("❌ No files added to custom batch!")
            
            # Clear state
            del self.custom_batch_state[user_id]
        
        elif user_id in self.special_link_state:
            state = self.special_link_state[user_id]
            
            if state["files"]:
                # Create special link
                link_id = state.get("link_id", f"special_{random.randint(10000, 99999)}")
                await self.db.save_special_link(link_id, state["message"], state["files"])
                
                bot_username = Config.BOT_USERNAME
                link = f"https://t.me/{bot_username}?start=link_{link_id}"
                
                await message.reply(
                    f"✅ <b>Special Link Created!</b>\n\n"
                    f"📁 Files: {len(state['files'])}\n"
                    f"💬 Custom message included\n"
                    f"🔗 Link:\n"
                    f"<code>{link}</code>",
                    parse_mode=enums.ParseMode.HTML
                )
            else:
                await message.reply("❌ No files added to special link!")
            
            # Clear state
            del self.special_link_state[user_id]
        
        else:
            await message.reply("ℹ️ No operation in progress.")

# ===================================
# SECTION 18: WEB SERVER
# ===================================

async def start_web_server():
    """Start aiohttp web server for Render deployment"""
    app = web.Application()
    
    async def handle_root(request):
        return web.Response(
            text="🤖 Telegram Bot is Online!\n\n"
                 "Enhanced Auto-Delete: Only conversation messages are deleted\n"
                 "File and instruction messages are preserved\n"
                 "Clean PM experience",
            content_type="text/plain"
        )
    
    async def handle_health(request):
        return web.Response(
            text="✅ Bot is running with enhanced auto-delete!",
            content_type="text/plain"
        )
    
    app.router.add_get("/", handle_root)
    app.router.add_get("/health", handle_health)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", Config.PORT)
    
    logger.info(f"🌐 Web server started on port {Config.PORT}")
    await site.start()
    
    # Keep server running
    while True:
        await asyncio.sleep(3600)

# ===================================
# SECTION 19: MAIN FUNCTION (FIXED)
# ===================================

async def main():
    """Main function to start the bot - FIXED VERSION"""
    print(BANNER)
    logger.info("🚀 Starting File Sharing Bot with Enhanced Auto-Delete...")
    
    # Validate configuration
    if not Config.validate():
        logger.error("Configuration validation failed. Exiting.")
        return
    
    # Parse force subscribe channels
    Config.parse_force_sub_channels()
    
    # Print configuration
    Config.print_config()
    
    # Create bot instance
    bot = Bot()
    
    try:
        # Start the bot
        if not await bot.start():
            logger.error("Failed to start bot. Exiting.")
            return
        
        # Set up callback handler
        await bot.setup_callbacks()
        
        logger.info("✅ Bot is now running with Enhanced Auto-Delete!")
        logger.info("✅ Only deletes conversation messages")
        logger.info("✅ Preserves file messages")
        logger.info("✅ Preserves instruction messages")
        logger.info("✅ Clean PM experience")
        logger.info(f"✅ Force Subscribe Channels: {len(bot.force_sub_channels)}")
        
        # Start web server if enabled
        if Config.WEB_SERVER:
            web_server_task = asyncio.create_task(start_web_server())
        
        # Keep the bot running
        await asyncio.Event().wait()
        
    except KeyboardInterrupt:
        logger.info("👋 Received stop signal, shutting down...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        traceback.print_exc()
    finally:
        # Stop the bot
        await bot.stop()
        
        if Config.WEB_SERVER and 'web_server_task' in locals():
            web_server_task.cancel()
        
        logger.info("👋 Bot stopped successfully.")

if __name__ == "__main__":
    # Run the bot
    asyncio.run(main())
