#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 TELEGRAM FILE SHARING BOT - UPDATED TO MATCH SCREENSHOTS
All functions with exact styling from screenshots
WITH PHOTOS ADDED TO ALL PANELS
"""

# ===================================
# SECTION 1: IMPORTS & SETUP (UNCHANGED)
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
║               𝙁𝙄𝙇𝙀 𝙎𝙃𝘼𝙍𝙄𝙉𝙂 𝘽𝙊𝙏 - 𝙐𝙋𝘿𝘼𝙏𝙀𝘿 𝙏𝙊 𝙎𝘾𝙍𝙀𝙀𝙉𝙎𝙃𝙊𝙏𝙎                      ║
║                      ~ 𝙀𝙓𝘼𝘾𝙏 𝙎𝙏𝙔𝙇𝙄𝙉𝙂 ~                             ║
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
REACTIONS = ["😍", "🥰", "🤩", "😱", "👏", "🎉", "⚡️", "😎", "🏆", "🔥"]

# Bot Commands Configuration (Same as before)
BOT_COMMANDS = {
        BotCommand("start", "Check bot status"),
        BotCommand("help", "Get help"),
        BotCommand("ping", "Check bot ping"),
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
}


# ===================================
# SECTION 2: CONFIGURATION CLASS (UPDATED WITH PHOTO TYPES)
# ===================================

class Config:
    """Configuration class for environment variables"""
    
    # Telegram API
    API_ID = int(os.environ.get("API_ID", 0))
    API_HASH = os.environ.get("API_HASH", "")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
    
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
    
    # Force subscribe channels (comma-separated)
    FORCE_SUB_CHANNELS = [x.strip() for x in os.environ.get("FORCE_SUB_CHANNELS", "").split(",") if x.strip()]
    
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
    AUTO_DELETE_TIME = int(os.environ.get("AUTO_DELETE_TIME", 300))  # 5 minutes
    REQUEST_FSUB = os.environ.get("REQUEST_FSUB", "false").lower() == "true"
    
    # New settings from screenshots
    AUTO_APPROVE_MODE = os.environ.get("AUTO_APPROVE_MODE", "false").lower() == "true"
    
    # Auto-delete settings
    AUTO_DELETE_BOT_MESSAGES = os.environ.get("AUTO_DELETE_BOT_MESSAGES", "true").lower() == "true"
    AUTO_DELETE_TIME_BOT = int(os.environ.get("AUTO_DELETE_TIME_BOT", 30))  # 30 seconds
    
    # Auto-clean join requests after 24 hours
    AUTO_CLEAN_JOIN_REQUESTS = os.environ.get("AUTO_CLEAN_JOIN_REQUESTS", "true").lower() == "true"
    AUTO_CLEAN_INTERVAL = int(os.environ.get("AUTO_CLEAN_INTERVAL", 86400))  # 24 hours in seconds
    
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
        logger.info(f"Bot Pics: {len(cls.BOT_PICS)} images")
        logger.info(f"Welcome Pics: {len(cls.WELCOME_PICS)} images")
        logger.info(f"Help Pics: {len(cls.HELP_PICS)} images")
        logger.info(f"Files Pics: {len(cls.FILES_PICS)} images")
        logger.info(f"Auto Del Pics: {len(cls.AUTO_DEL_PICS)} images")
        logger.info(f"Force Sub Pics: {len(cls.FORCE_SUB_PICS)} images")
        logger.info(f"Web Server: {cls.WEB_SERVER}")
        logger.info(f"Port: {cls.PORT}")
        logger.info(f"Auto Approve Mode: {cls.AUTO_APPROVE_MODE}")
        logger.info(f"Auto Delete Bot Messages: {cls.AUTO_DELETE_BOT_MESSAGES}")
        logger.info(f"Auto Delete Time (Bot): {cls.AUTO_DELETE_TIME_BOT} seconds")
        logger.info(f"Auto Clean Join Requests: {cls.AUTO_CLEAN_JOIN_REQUESTS}")
        logger.info(f"Auto Clean Interval: {cls.AUTO_CLEAN_INTERVAL} seconds")


# ===================================
# SECTION 3: DATABASE CLASS (UPDATED FOR PHOTOS)
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
            "joined_date": datetime.datetime.now(datetime.UTC),
            "last_active": datetime.datetime.now(datetime.UTC)
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
            {"$set": {"last_active": datetime.datetime.now(datetime.UTC)}}
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
            "banned_date": datetime.datetime.now(datetime.UTC)
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
            "created_date": datetime.datetime.now(datetime.UTC)
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
            "added_date": datetime.datetime.now(datetime.UTC)
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
            "added_date": datetime.datetime.now(datetime.UTC)
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
        """Check if user is admin"""
        # First check in database
        admin = await self.admins.find_one({"user_id": user_id})
        if admin:
            return True
        # Then check in Config.ADMINS (for initial setup)
        return user_id in Config.ADMINS
    
    # ===== JOIN REQUESTS =====
    
    async def save_join_request(self, user_id: int, channel_id: int, status: str = "pending"):
        """Save join request"""
        request_data = {
            "user_id": user_id,
            "channel_id": channel_id,
            "status": status,
            "request_date": datetime.datetime.now(datetime.UTC),
            "processed_date": None if status == "pending" else datetime.datetime.now(datetime.UTC)
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
            {"$set": {"status": status, "processed_date": datetime.datetime.now(datetime.UTC)}}
        )
    
    async def clean_old_join_requests(self):
        """Clean join requests older than 24 hours"""
        try:
            # Calculate 24 hours ago
            cutoff_time = datetime.datetime.now(datetime.UTC) - datetime.timedelta(hours=24)
            
            # Delete old join requests
            result = await self.join_requests.delete_many({
                "request_date": {"$lt": cutoff_time}
            })
            
            if result.deleted_count > 0:
                logger.info(f"✓ Auto-cleaned {result.deleted_count} old join requests (older than 24 hours)")
                return result.deleted_count
            else:
                logger.info("✓ No old join requests to clean")
                return 0
                
        except Exception as e:
            logger.error(f"✗ Error cleaning old join requests: {e}")
            return 0


# ===================================
# SECTION 4: HELPER FUNCTIONS (UPDATED FOR PHOTOS)
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
    """Check if user is subscribed to channels"""
    if not channel_ids:
        return True
    
    for channel in channel_ids:
        try:
            channel_id = channel.get("channel_id")
            if not channel_id:
                continue
                
            # Try to get chat member
            try:
                member = await client.get_chat_member(channel_id, user_id)
                if member.status in ["kicked", "left", "restricted"]:
                    return False
            except UserNotParticipant:
                return False
            except PeerIdInvalid:
                # Try with username
                username = channel.get("channel_username")
                if username:
                    try:
                        member = await client.get_chat_member(username, user_id)
                        if member.status in ["kicked", "left", "restricted"]:
                            return False
                    except:
                        return False
                else:
                    return False
            except Exception as e:
                logger.error(f"Error checking subscription for channel {channel_id}: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Error in is_subscribed: {e}")
            return False
    
    return True

async def get_messages(client, chat_id: int, message_ids: list):
    """Get multiple messages"""
    messages = []
    for msg_id in message_ids:
        try:
            msg = await client.get_messages(chat_id, msg_id)
            if msg:
                messages.append(msg)
        except Exception as e:
            logger.error(f"Error getting message {msg_id}: {e}")
    return messages

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

def generate_button_string(buttons: list) -> str:
    """Generate button configuration string from button list"""
    rows = []
    for row in buttons:
        row_strings = []
        for button in row:
            if hasattr(button, 'text') and hasattr(button, 'url'):
                row_strings.append(f"{button.text} | {button.url}")
        if row_strings:
            rows.append(' : '.join(row_strings))
    
    return '\n'.join(rows)

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

async def get_file_info(message: Message) -> dict:
    """Extract file information from message"""
    file_info = {
        "type": get_media_type(message),
        "file_name": "",
        "file_size": 0,
        "mime_type": ""
    }
    
    if message.document:
        file_info["file_name"] = message.document.file_name or "Unknown"
        file_info["file_size"] = message.document.file_size
        file_info["mime_type"] = message.document.mime_type
    elif message.video:
        file_info["file_name"] = message.video.file_name or "Video"
        file_info["file_size"] = message.video.file_size
        file_info["mime_type"] = message.video.mime_type
    elif message.audio:
        file_info["file_name"] = message.audio.file_name or "Audio"
        file_info["file_size"] = message.audio.file_size
        file_info["mime_type"] = message.audio.mime_type
    elif message.photo:
        file_info["file_name"] = "Photo"
        file_info["file_size"] = message.photo.file_size
        file_info["mime_type"] = "image/jpeg"
    
    return file_info

def generate_progress_bar(percentage: float, length: int = 10) -> str:
    """Generate a progress bar"""
    filled = int(length * percentage / 100)
    empty = length - filled
    return f"[{'█' * filled}{'░' * empty}] {percentage:.1f}%"

async def shorten_url(long_url: str) -> str:
    """Shorten URL using configured shortener"""
    if not Config.SHORTENER_API or not Config.SHORTENER_URL:
        return long_url
    
    try:
        api_url = Config.SHORTENER_API.replace("{url}", long_url)
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status == 200:
                    short_url = await response.text()
                    return short_url.strip()
    except Exception as e:
        logger.error(f"URL shortening failed: {e}")
    
    return long_url

def validate_url(url: str) -> bool:
    """Validate URL format"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def get_random_pic(pics_list: list) -> str:
    """Get random picture from list"""
    if not pics_list:
        return random.choice(DEFAULT_BOT_PICS)
    return random.choice(pics_list)

def get_random_reaction() -> str:
    """Get random reaction emoji"""
    return random.choice(REACTIONS)

async def send_log_message(client, message: str):
    """Send log message to owner"""
    try:
        await client.send_message(
            Config.OWNER_ID,
            f"📊 **Bot Log**\n\n{message}",
            parse_mode=enums.ParseMode.MARKDOWN
        )
    except Exception as e:
        logger.error(f"Failed to send log message: {e}")


# ===================================
# SECTION 5: BOT CLASS (UPDATED WITH PHOTO SUPPORT)
# ===================================

class Bot(Client):
    """Main Bot Class - WITH PHOTOS IN ALL PANELS"""
    
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
        
        # State management for commands
        self.batch_state = {}
        self.custom_batch_state = {}
        self.special_link_state = {}
        self.button_setting_state = {}
        self.text_setting_state = {}
        self.user_last_messages = {}  # Store last bot message per user for auto-delete
        
        logger.info("✓ Bot instance created")
    
    async def start(self):
        """Start the bot"""
        await super().start()
        
        # Connect to database
        if not await self.db.connect():
            logger.error("Failed to connect to database. Exiting.")
            return False
        
        # Load settings
        self.settings = await self.db.get_settings()
        self.force_sub_channels = await self.db.get_force_sub_channels()
        self.db_channel = await self.db.get_db_channel()
        
        # Initialize admins
        for admin_id in Config.ADMINS:
            await self.db.add_admin(admin_id)
        
        # Set bot commands
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
        
        # Send startup message to owner
        await self.send_log_message(f"✅ Bot started successfully!\n\n📊 **Bot Info:**\n• Name: {me.first_name}\n• Username: @{me.username}\n• ID: {me.id}\n\n⏰ Started at: {datetime.datetime.now()}")
        
        return True
    
    async def stop(self, *args):
        """Stop the bot"""
        await self.db.close()
        await super().stop()
        logger.info("✓ Bot stopped")
    
    async def set_bot_commands(self):
        """Set bot commands"""
        try:
            # Set commands for all users
            await self.set_bot_commands(
                commands=BOT_COMMANDS["all_users"],
                scope=BotCommandScopeAllPrivateChats()
            )
            
            logger.info("✓ Bot commands set successfully")
        except Exception as e:
            logger.error(f"Error setting bot commands: {e}")
    
    async def delete_previous_message(self, user_id: int):
        """Delete previous bot message for user"""
        if user_id in self.user_last_messages:
            try:
                await self.delete_messages(user_id, self.user_last_messages[user_id])
                del self.user_last_messages[user_id]
            except Exception as e:
                logger.error(f"Error deleting previous message: {e}")
    
    def register_all_handlers(self):
        """Register ALL handlers in one place"""
        
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
        @self.on_message(filters.command("admin_list") & filters.private & filters.user([Config.OWNER_ID]))
        async def admin_list_handler(client, message):
            await self.admin_list_command(message)
        
        @self.on_message(filters.command("add_admins") & filters.private & filters.user([Config.OWNER_ID]))
        async def add_admins_handler(client, message):
            await self.add_admins_command(message)
        
        @self.on_message(filters.command("del_admins") & filters.private & filters.user([Config.OWNER_ID]))
        async def del_admins_handler(client, message):
            await self.del_admins_command(message)
        
        @self.on_message(filters.command("banuser_list") & filters.private & filters.user(Config.ADMINS))
        async def banuser_list_handler(client, message):
            await self.banuser_list_command(message)
        
        @self.on_message(filters.command("add_banuser") & filters.private & filters.user(Config.ADMINS))
        async def add_banuser_handler(client, message):
            await self.add_banuser_command(message)
        
        @self.on_message(filters.command("del_banuser") & filters.private & filters.user(Config.ADMINS))
        async def del_banuser_handler(client, message):
            await self.del_banuser_command(message)
        
        # === BASIC ADMIN COMMANDS ===
        @self.on_message(filters.command("users") & filters.private & filters.user(Config.ADMINS))
        async def users_handler(client, message):
            await self.users_command(message)
        
        @self.on_message(filters.command("broadcast") & filters.private & filters.user(Config.ADMINS))
        async def broadcast_handler(client, message):
            await self.broadcast_command(message)
        
        @self.on_message(filters.command("ban") & filters.private & filters.user(Config.ADMINS))
        async def ban_handler(client, message):
            await self.ban_command(message)
        
        @self.on_message(filters.command("unban") & filters.private & filters.user(Config.ADMINS))
        async def unban_handler(client, message):
            await self.unban_command(message)
        
        @self.on_message(filters.command("stats") & filters.private & filters.user(Config.ADMINS))
        async def stats_handler(client, message):
            await self.stats_command(message)
        
        @self.on_message(filters.command("logs") & filters.private & filters.user(Config.ADMINS))
        async def logs_handler(client, message):
            await self.logs_command(message)
        
        @self.on_message(filters.command("cmd") & filters.private & filters.user(Config.ADMINS))
        async def cmd_handler(client, message):
            await self.cmd_command(message)
        
        # === FILE MANAGEMENT COMMANDS ===
        @self.on_message(filters.command("genlink") & filters.private & filters.user(Config.ADMINS))
        async def genlink_handler(client, message):
            await self.genlink_command(message)
        
        @self.on_message(filters.command("batch") & filters.private & filters.user(Config.ADMINS))
        async def batch_handler(client, message):
            await self.batch_command(message)
        
        @self.on_message(filters.command("custom_batch") & filters.private & filters.user(Config.ADMINS))
        async def custom_batch_handler(client, message):
            await self.custom_batch_command(message)
        
        @self.on_message(filters.command("special_link") & filters.private & filters.user(Config.ADMINS))
        async def special_link_handler(client, message):
            await self.special_link_command(message)
        
        @self.on_message(filters.command("getlink") & filters.private & filters.user(Config.ADMINS))
        async def getlink_handler(client, message):
            await self.getlink_command(message)
        
        # === CHANNEL MANAGEMENT COMMANDS ===
        @self.on_message(filters.command("setchannel") & filters.private & filters.user(Config.ADMINS))
        async def setchannel_handler(client, message):
            await self.setchannel_command(message)
        
        @self.on_message(filters.command("checkchannel") & filters.private & filters.user(Config.ADMINS))
        async def checkchannel_handler(client, message):
            await self.checkchannel_command(message)
        
        @self.on_message(filters.command("removechannel") & filters.private & filters.user(Config.ADMINS))
        async def removechannel_handler(client, message):
            await self.removechannel_command(message)
        
        # === SETTINGS COMMANDS ===
        @self.on_message(filters.command("settings") & filters.private & filters.user(Config.ADMINS))
        async def settings_handler(client, message):
            await self.settings_command(message)
        
        @self.on_message(filters.command("files") & filters.private & filters.user(Config.ADMINS))
        async def files_handler(client, message):
            await self.files_command(message)
        
        @self.on_message(filters.command("auto_del") & filters.private & filters.user(Config.ADMINS))
        async def auto_del_handler(client, message):
            await self.auto_del_command(message)
        
        @self.on_message(filters.command("forcesub") & filters.private & filters.user(Config.ADMINS))
        async def forcesub_handler(client, message):
            await self.forcesub_command(message)
        
        @self.on_message(filters.command("req_fsub") & filters.private & filters.user(Config.ADMINS))
        async def req_fsub_handler(client, message):
            await self.req_fsub_command(message)
        
        @self.on_message(filters.command("botsettings") & filters.private & filters.user(Config.ADMINS))
        async def botsettings_handler(client, message):
            await self.botsettings_command(message)
        
        # === UTILITY COMMANDS ===
        @self.on_message(filters.command("shortener") & filters.private & filters.user(Config.ADMINS))
        async def shortener_handler(client, message):
            await self.shortener_command(message)
        
        @self.on_message(filters.command("ping") & filters.private)
        async def ping_handler(client, message):
            await self.ping_command(message)
        
        @self.on_message(filters.command("font") & filters.private & filters.user(Config.ADMINS))
        async def font_handler(client, message):
            await self.font_command(message)
        
        @self.on_message(filters.command("refresh") & filters.private & filters.user(Config.ADMINS))
        async def refresh_handler(client, message):
            await self.refresh_command(message)
        
        # === FORCE SUBSCRIBE COMMANDS ===
        @self.on_message(filters.command("fsub_chnl") & filters.private & filters.user(Config.ADMINS))
        async def fsub_chnl_handler(client, message):
            await self.fsub_chnl_command(message)
        
        @self.on_message(filters.command("add_fsub") & filters.private & filters.user([Config.OWNER_ID]))
        async def add_fsub_handler(client, message):
            await self.add_fsub_command(message)
        
        @self.on_message(filters.command("del_fsub") & filters.private & filters.user([Config.OWNER_ID]))
        async def del_fsub_handler(client, message):
            await self.del_fsub_command(message)
        
        # === DONE COMMAND ===
        @self.on_message(filters.command("done") & filters.private & filters.user(Config.ADMINS))
        async def done_handler(client, message):
            await self.done_command(message)
        
        # === TEXT MESSAGE HANDLERS ===
        @self.on_message(filters.private & filters.user(Config.ADMINS))
        async def text_handler(client, message):
            await self.text_message_handler(message)
        
        # === CHAT JOIN REQUEST HANDLER ===
        @self.on_chat_join_request()
        async def join_request_handler(client, join_request: ChatJoinRequest):
            await self.handle_join_request(join_request)
        
        # === AUTO DELETE HANDLER ===
        @self.on_message(filters.private)
        async def auto_delete_handler(client, message):
            # Check if auto delete is enabled
            settings = await self.db.get_settings()
            if settings.get("auto_delete_bot_messages", False):
                user_id = message.from_user.id
                # Delete previous bot message if exists
                if user_id in self.user_last_messages:
                    try:
                        await self.delete_messages(user_id, self.user_last_messages[user_id])
                    except:
                        pass
        
        logger.info("✓ All handlers registered")
    
    async def setup_callbacks(self):
        """Setup callback query handlers"""
        
        @self.on_callback_query()
        async def callback_handler(client, query):
            await self.handle_callback_query(query)
    
    async def auto_delete_message(self, chat_id: int, message_id: int, delay: int = None):
        """Auto delete message after delay"""
        try:
            if delay is None:
                delay = Config.AUTO_DELETE_TIME_BOT
            
            await asyncio.sleep(delay)
            await self.delete_messages(chat_id, message_id)
            logger.info(f"Auto-deleted message {message_id} in chat {chat_id}")
        except Exception as e:
            logger.error(f"Error auto-deleting message: {e}")
    
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
            await message.reply("❌ Invalid or expired link!")
    
    async def handle_special_link(self, message: Message, link_id: str):
        """Handle special link access"""
        try:
            # Get link data from database
            link_data = await self.db.get_special_link(link_id)
            if not link_data:
                await message.reply("❌ Link not found or expired!")
                return
            
            # Send custom message if available
            if link_data.get("message"):
                await message.reply(link_data["message"], parse_mode=enums.ParseMode.HTML)
            
            # Send files
            files = link_data.get("files", [])
            if files:
                for file_id in files[:MAX_SPECIAL_FILES]:
                    try:
                        await self.copy_message(
                            chat_id=message.chat.id,
                            from_chat_id=self.db_channel,
                            message_id=file_id,
                            protect_content=self.settings.get("protect_content", True)
                        )
                    except Exception as e:
                        logger.error(f"Error sending file {file_id}: {e}")
        except Exception as e:
            logger.error(f"Error handling special link: {e}")
            await message.reply("❌ Error accessing link!")
    
    async def handle_file_link(self, message: Message, file_id: str):
        """Handle single file link"""
        try:
            # Send the file
            await self.copy_message(
                chat_id=message.chat.id,
                from_chat_id=self.db_channel,
                message_id=int(file_id),
                protect_content=self.settings.get("protect_content", True)
            )
        except Exception as e:
            logger.error(f"Error sending file {file_id}: {e}")
            await message.reply("❌ File not found or access denied!")
    
    async def handle_batch_link(self, message: Message, batch_id: str):
        """Handle batch file link"""
        try:
            # This would need to be implemented based on how you store batch files
            # For now, just show a message
            await message.reply("📦 Batch file access coming soon!")
        except Exception as e:
            logger.error(f"Error handling batch link: {e}")
            await message.reply("❌ Batch not found or access denied!")
    
    async def create_invite_link(self, channel_id: int) -> str:
        """Create 5-minute expire invite link for private channels"""
        try:
            # Create invite link that expires in 5 minutes (300 seconds)
            invite_link = await self.create_chat_invite_link(
                chat_id=channel_id,
                expire_date=datetime.datetime.now() + datetime.timedelta(minutes=5),
                member_limit=1  # One-time use
            )
            return invite_link.invite_link
        except Exception as e:
            logger.error(f"Error creating invite link for channel {channel_id}: {e}")
            return None
    
    # ===================================
    # SECTION 6: START COMMAND (WITH PHOTO)
    # ===================================
    
    async def start_command(self, message: Message):
        """Handle /start command with auto-delete - WITH PHOTO"""
        user_id = message.from_user.id
        chat_id = message.chat.id
        
        # Delete previous bot message if auto-delete is enabled
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", False):
            await self.delete_previous_message(user_id)
        
        # Check if user is banned
        if await self.db.is_user_banned(user_id):
            response = await message.reply("🚫 <b>You are banned from using this bot!</b>", parse_mode=enums.ParseMode.HTML)
            # Store message for auto-delete
            self.user_last_messages[user_id] = response.id
            return
        
        # Add user to database
        await self.db.add_user(
            user_id=user_id,
            first_name=message.from_user.first_name,
            username=message.from_user.username
        )
        
        # Update activity
        await self.db.update_user_activity(user_id)
        
        # Add reaction to message
        try:
            reaction = get_random_reaction()
            await message.react(emoji=reaction)
        except Exception as e:
            logger.error(f"Failed to add reaction: {e}")
        
        # Check for start arguments
        if len(message.command) > 1:
            start_arg = message.command[1]
            await self.handle_start_argument(message, start_arg)
            return
        
        # Check force subscribe
        if self.force_sub_channels:
            is_subscribed = await is_subscribed(self, user_id, self.force_sub_channels)
            if not is_subscribed:
                await self.show_force_subscribe(message)
                return
        
        # Show welcome message WITH PHOTO
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
        
        # Default welcome text to match screenshot
        if not welcome_text:
            welcome_text = (
                f"""<b>Hey, {user.first_name} ~</b><\n\n
                <blockqoute expandable>I AM AN ADVANCE FILE SHARE BOT V3.\n
                THE BEST PART IS I AM ALSO SUPPORT REQUEST FORCESUB\n
                FEATURE, TO KNOW DETAILED INFORMATION CLICK ABOUT ME/blockquote>"""
            )
        else:
            # Replace variables
            welcome_text = welcome_text.format(
                first=user.first_name,
                last=user.last_name or "",
                username=f"@{user.username}" if user.username else "None",
                mention=f"<a href='tg://user?id={user.id}'>{user.first_name}</a>",
                id=user.id
            )
        
        # Create buttons - SIMPLE LAYOUT LIKE SCREENSHOT
        buttons = []
        
        # Row 1: Help and About
        buttons.append([
            InlineKeyboardButton("⁉️ ʜᴇʟᴘ", callback_data="help_menu"),
            InlineKeyboardButton("ᴀʙᴏᴜᴛ ", callback_data="about_menu")
        ])
        
        # Row 2: Close button
        buttons.append([
            InlineKeyboardButton(" ᴄʟᴏsᴇ ✖️ ", callback_data="close")
        ])
        
        keyboard = InlineKeyboardMarkup(buttons)
        
        try:
            # Try to send photo with caption
            response = await message.reply_photo(
                photo=welcome_pic,
                caption=welcome_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Error sending welcome photo: {e}")
            # Fallback to text message
            response = await message.reply(
                welcome_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML,
                disable_web_page_preview=True
            )
        
        # Store message for auto-delete
        self.user_last_messages[message.from_user.id] = response.id
        
        # Schedule auto-delete if enabled
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", False):
            delay = settings.get("auto_delete_time_bot", 30)
            asyncio.create_task(self.auto_delete_message(message.chat.id, response.id, delay))
    
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
                is_sub = await is_subscribed(self, user.id, [channel])
                if is_sub:
                    joined_count += 1
            except:
                pass
        
        # Create buttons for each channel
        buttons = []
        for channel in self.force_sub_channels:
            channel_id = channel.get("channel_id")
            username = channel.get("channel_username")
            
            if username:
                # Public channel with username
                button_text = f" ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ "
                button_url = f"https://t.me/{username}"
            else:
                # Private channel - create invite link
                button_text = " ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀɴɴᴇʟ "
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
        
        # Message text matching screenshot
        message_text = (
            f"<b>Hey, {user.first_name}</b>\n\n"
            f"""<blockqoute expandable><b>You haven't joined {joined_count}/{total_channels} channels yet. 
            Please join the channels provided below, then try again.</b></blockquote>\n\n
            <blockqoute expandable><b>Facing problems, use: /help</b></blockquote>"""
        )
        
        try:
            # Try to send photo with caption
            response = await message.reply_photo(
                photo=force_sub_pic,
                caption=message_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Error sending force sub photo: {e}")
            # Fallback to text message
            response = await message.reply(
                message_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
        
        # Store message for auto-delete
        self.user_last_messages[message.from_user.id] = response.id
        
        # Schedule auto-delete if enabled
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", False):
            delay = settings.get("auto_delete_time_bot", 30)
            asyncio.create_task(self.auto_delete_message(message.chat.id, response.id, delay))
    
    # ===================================
    # SECTION 7: HELP & ABOUT COMMANDS (WITH PHOTOS)
    # ===================================
    
    async def help_command(self, message: Message):
        """Handle /help command WITH PHOTO"""
        user_id = message.from_user.id
        
        # Delete previous bot message if auto-delete is enabled
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", False):
            await self.delete_previous_message(user_id)
        
        # Get help text and pictures from settings
        settings = await self.db.get_settings()
        help_text = settings.get("help_text", "")
        help_pics = settings.get("help_pics", Config.HELP_PICS)
        
        # Get random help picture
        help_pic = get_random_pic(help_pics)
        
        # Default help text to match screenshot
        if not help_text:
            help_text = (
                f"<b>⁉️ Hᴇʟʟᴏ {message.from_user.first_name} ~</b>\n\n"

                """<blockqoute expandable><b>➪ I ᴀᴍ ᴀ ᴘʀɪᴠᴀᴛᴇ ғɪʟᴇ sʜᴀʀɪɴɢ ʙᴏᴛ, ᴍᴇᴀɴᴛ ᴛᴏ ᴘʀᴏᴠɪᴅᴇ ғɪʟᴇs ᴀɴᴅ ɴᴇᴄᴇssᴀʀʏ sᴛᴜғғ ᴛʜʀᴏᴜɢʜ sᴘᴇᴄɪᴀʟ ʟɪɴᴋ ғᴏʀ sᴘᴇᴄɪғɪᴄ ᴄʜᴀɴɴᴇʟs.

                ➪ Iɴ ᴏʀᴅᴇʀ ᴛᴏ ɢᴇᴛ ᴛʜᴇ ғɪʟᴇs ʏᴏᴜ ʜᴀᴠᴇ ᴛᴏ ᴊᴏɪɴ ᴛʜᴇ ᴀʟʟ ᴍᴇɴᴛɪᴏɴᴇᴅ ᴄʜᴀɴɴᴇʟ ᴛʜᴀᴛ ɪ ᴘʀᴏᴠɪᴅᴇ ʏᴏᴜ ᴛᴏ ᴊᴏɪɴ. Yᴏᴜ ᴄᴀɴ ɴᴏᴛ ᴀᴄᴄᴇss ᴏʀ ɢᴇᴛ ᴛʜᴇ ғɪʟᴇs ᴜɴʟᴇss ʏᴏᴜ ᴊᴏɪɴᴇᴅ ᴀʟʟ ᴄʜᴀɴɴᴇʟs.

                ➪ Sᴏ ᴊᴏɪɴ Mᴇɴᴛɪᴏɴᴇᴅ Cʜᴀɴɴᴇʟs ᴛᴏ ɢᴇᴛ Fɪʟᴇs ᴏʀ ɪɴɪᴛɪᴀᴛᴇ ᴍᴇssᴀɢᴇs...

                ‣ /help - Oᴘᴇɴ ᴛʜɪs ʜᴇʟᴘ ᴍᴇssᴀɢᴇ !</b></blockquote>
                <b>◈ Sᴛɪʟʟ ʜᴀᴠᴇ ᴅᴏᴜʙᴛs, ᴄᴏɴᴛᴀᴄᴛ ʙᴇʟᴏᴡ ᴘᴇʀsᴏɴs/ɢʀᴏᴜᴘ ᴀs ᴘᴇʀ ʏᴏᴜʀ ɴᴇᴇᴅ !</b>"""
            )
        
        # Create simple buttons
        buttons = [
            [InlineKeyboardButton("⬅️ Back", callback_data="start_menu")],
            [InlineKeyboardButton("❌ Close", callback_data="close")]
        ]
        
        keyboard = InlineKeyboardMarkup(buttons)
        
        try:
            # Try to send photo with caption
            response = await message.reply_photo(
                photo=help_pic,
                caption=help_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.MARKDOWN
            )
        except Exception as e:
            logger.error(f"Error sending help photo: {e}")
            # Fallback to text message
            response = await message.reply(
                help_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.MARKDOWN
            )
        
        # Store message for auto-delete
        self.user_last_messages[user_id] = response.id
        
        # Schedule auto-delete if enabled
        if settings.get("auto_delete_bot_messages", False):
            delay = settings.get("auto_delete_time_bot", 30)
            asyncio.create_task(self.auto_delete_message(message.chat.id, response.id, delay))
    
    async def about_command(self, message: Message):
        """Handle /about command"""
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", False):
            await self.delete_previous_message(message.from_user.id)
        
        # Get about text from settings
        settings = await self.db.get_settings()
        about_text = settings.get("about_text", "")
        about_pics = settings.get("welcome_pics", Config.WELCOME_PICS)  # Use welcome pics for about
        
        # Get random about picture
        about_pic = get_random_pic(about_pics)
        
        # Default about text
        if not about_text:
            about_text = (
                f"ℹ️ <b>About Bot</b>\n\n"
                f"• Bot Name: {Config.BOT_NAME}\n"
                f"• Username: @{Config.BOT_USERNAME}\n"
                f"• Framework: Pyrogram\n"
                f"• Language: Python 3\n"
                f"• Version: V3.0\n\n"
                f"Made with ❤️ for Telegram"
            )
        
        buttons = [
            [InlineKeyboardButton("⬅️ Back", callback_data="start_menu")],
            [InlineKeyboardButton("❌ Close", callback_data="close")]
        ]
        
        keyboard = InlineKeyboardMarkup(buttons)
        
        try:
            # Try to send photo with caption
            response = await message.reply_photo(
                photo=about_pic,
                caption=about_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Error sending about photo: {e}")
            # Fallback to text message
            response = await message.reply(
                about_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
        
        self.user_last_messages[message.from_user.id] = response.id
        
        if settings.get("auto_delete_bot_messages", False):
            delay = settings.get("auto_delete_time_bot", 30)
            asyncio.create_task(self.auto_delete_message(message.chat.id, response.id, delay))
    
    # ===================================
    # SECTION 8: ADMIN MANAGEMENT COMMANDS (UPDATED)
    # ===================================
    
    async def admin_list_command(self, message: Message):
        """Handle /admin_list command"""
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", False):
            await self.delete_previous_message(message.from_user.id)
        
        try:
            # Get admins from database
            db_admins = await self.db.get_admins()
            all_admins = list(set(Config.ADMINS + db_admins))
            
            if not all_admins:
                response = await message.reply("❌ No admins found!")
                self.user_last_messages[message.from_user.id] = response.id
                return
            
            # Format message in screenshot style
            admin_text = (
                "# USER SETTING COMMANDS :\n\n"
                "/admin_list : VIEW THE AVAILABLE ADMIN LIST (OWNER)\n\n"
                "/add_admins : ADD ONE OR MULTIPLE USER IDS AS ADMIN (OWNER)\n\n"
                "/del_admins : DELETE ONE OR MULTIPLE USER IDS FROM ADMINS (OWNER)\n\n"
                "/banuser_list : VIEW THE AVAILABLE BANNED USER LIST (ADMINS)\n\n"
                "/add_banuser : ADD ONE OR MULTIPLE USER IDS IN BANNED LIST (ADMINS)\n\n"
                "/del_banuser : DELETE ONE OR MULTIPLE USER IDS FROM BANNED LIST (ADMINS)"
            )
            
            buttons = [
                [InlineKeyboardButton("⬅️ Back", callback_data="admin_panel")],
                [InlineKeyboardButton("❌ Close", callback_data="close")]
            ]
            
            keyboard = InlineKeyboardMarkup(buttons)
            
            response = await message.reply(
                admin_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.MARKDOWN
            )
            
            self.user_last_messages[message.from_user.id] = response.id
            
        except Exception as e:
            logger.error(f"Error in admin_list command: {e}")
            response = await message.reply("❌ Error fetching admin list!")
            self.user_last_messages[message.from_user.id] = response.id
    
    async def add_admins_command(self, message: Message):
        """Handle /add_admins command"""
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", False):
            await self.delete_previous_message(message.from_user.id)
        
        if len(message.command) < 2:
            response = await message.reply(
                "👑 <b>ADD ADMINS</b>\n\n"
                "Usage: <code>/add_admins user_id1,user_id2</code>\n\n"
                "Example: <code>/add_admins 123456789,987654321</code>",
                parse_mode=enums.ParseMode.HTML
            )
            self.user_last_messages[message.from_user.id] = response.id
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
                    f"✅ <b>Admins Added!</b>\n\n"
                    f"Added {len(added_admins)} admin(s)\n"
                    + "\n".join(f"• {admin}" for admin in added_admins),
                    parse_mode=enums.ParseMode.HTML
                )
            else:
                response = await message.reply("❌ No admins were added!")
            
            self.user_last_messages[message.from_user.id] = response.id
        
        except Exception as e:
            logger.error(f"Error adding admins: {e}")
            response = await message.reply("❌ Error adding admins!")
            self.user_last_messages[message.from_user.id] = response.id
    
    async def del_admins_command(self, message: Message):
        """Handle /del_admins command"""
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", False):
            await self.delete_previous_message(message.from_user.id)
        
        if len(message.command) < 2:
            response = await message.reply(
                "🗑️ <b>DELETE ADMINS</b>\n\n"
                "Usage: <code>/del_admins user_id1,user_id2</code>\n\n"
                "Example: <code>/del_admins 123456789,987654321</code>\n\n"
                "Note: Cannot remove owner!",
                parse_mode=enums.ParseMode.HTML
            )
            self.user_last_messages[message.from_user.id] = response.id
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
                    f"✅ <b>Admins Removed!</b>\n\n"
                    f"Removed {len(removed_admins)} admin(s)\n"
                    + "\n".join(f"• {admin}" for admin in removed_admins),
                    parse_mode=enums.ParseMode.HTML
                )
            else:
                response = await message.reply("❌ No admins were removed!")
            
            self.user_last_messages[message.from_user.id] = response.id
        
        except Exception as e:
            logger.error(f"Error removing admins: {e}")
            response = await message.reply("❌ Error removing admins!")
            self.user_last_messages[message.from_user.id] = response.id
    
    async def banuser_list_command(self, message: Message):
        """Handle /banuser_list command"""
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", False):
            await self.delete_previous_message(message.from_user.id)
        
        try:
            # Get banned users
            banned_users = await self.db.get_banned_users()
            
            if not banned_users:
                response = await message.reply("✅ No banned users found!")
                self.user_last_messages[message.from_user.id] = response.id
                return
            
            # Format message
            ban_text = "🚫 <b>BANNED USERS LIST</b>\n\n"
            
            for i, ban in enumerate(banned_users[:10], 1):
                user_id = ban["user_id"]
                reason = ban.get("reason", "No reason")
                banned_date = ban.get("banned_date", "").strftime("%Y-%m-%d") if ban.get("banned_date") else "Unknown"
                
                ban_text += f"{i}. ID: <code>{user_id}</code>\n"
                ban_text += f"   Reason: {reason}\n"
                ban_text += f"   Date: {banned_date}\n\n"
            
            ban_text += f"📊 Total Banned: {len(banned_users)}"
            
            buttons = [
                [InlineKeyboardButton("⬅️ Back", callback_data="admin_panel")],
                [InlineKeyboardButton("❌ Close", callback_data="close")]
            ]
            
            keyboard = InlineKeyboardMarkup(buttons)
            
            response = await message.reply(
                ban_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
            
            self.user_last_messages[message.from_user.id] = response.id
            
        except Exception as e:
            logger.error(f"Error in banuser_list command: {e}")
            response = await message.reply("❌ Error fetching banned users list!")
            self.user_last_messages[message.from_user.id] = response.id
    
    async def add_banuser_command(self, message: Message):
        """Handle /add_banuser command"""
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", False):
            await self.delete_previous_message(message.from_user.id)
        
        if len(message.command) < 2:
            response = await message.reply(
                "🚫 <b>BAN USER</b>\n\n"
                "Usage: <code>/add_banuser user_id1,user_id2 [reason]</code>\n\n"
                "Example: <code>/add_banuser 123456789,987654321 Spamming</code>",
                parse_mode=enums.ParseMode.HTML
            )
            self.user_last_messages[message.from_user.id] = response.id
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
                        # Add user first
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
                            f"🚫 <b>You have been banned!</b>\n\n"
                            f"Reason: {reason}\n"
                            f"Contact admin if this is a mistake.",
                            parse_mode=enums.ParseMode.HTML
                        )
                    except:
                        pass
                    
                except ValueError:
                    await message.reply(f"❌ Invalid user ID: {arg}")
                    continue
            
            if banned_users:
                response = await message.reply(
                    f"✅ <b>Users Banned!</b>\n\n"
                    f"Banned {len(banned_users)} user(s)\n"
                    + "\n".join(f"• {user_id}" for user_id in banned_users) +
                    f"\n\nReason: {reason}",
                    parse_mode=enums.ParseMode.HTML
                )
            else:
                response = await message.reply("❌ No users were banned!")
            
            self.user_last_messages[message.from_user.id] = response.id
        
        except Exception as e:
            logger.error(f"Error banning users: {e}")
            response = await message.reply("❌ Error banning users!")
            self.user_last_messages[message.from_user.id] = response.id
    
    async def del_banuser_command(self, message: Message):
        """Handle /del_banuser command"""
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", False):
            await self.delete_previous_message(message.from_user.id)
        
        if len(message.command) < 2:
            response = await message.reply(
                "✅ <b>UNBAN USER</b>\n\n"
                "Usage: <code>/del_banuser user_id1,user_id2</code>\n\n"
                "Example: <code>/del_banuser 123456789,987654321</code>",
                parse_mode=enums.ParseMode.HTML
            )
            self.user_last_messages[message.from_user.id] = response.id
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
                            "✅ <b>You have been unbanned!</b>\n\n"
                            "You can now use the bot again.",
                            parse_mode=enums.ParseMode.HTML
                        )
                    except:
                        pass
                    
                except ValueError:
                    await message.reply(f"❌ Invalid user ID: {arg}")
                    continue
            
            if unbanned_users:
                response = await message.reply(
                    f"✅ <b>Users Unbanned!</b>\n\n"
                    f"Unbanned {len(unbanned_users)} user(s)\n"
                    + "\n".join(f"• {user_id}" for user_id in unbanned_users),
                    parse_mode=enums.ParseMode.HTML
                )
            else:
                response = await message.reply("⚠️ No users were unbanned!")
            
            self.user_last_messages[message.from_user.id] = response.id
        
        except Exception as e:
            logger.error(f"Error unbanning users: {e}")
            response = await message.reply("❌ Error unbanning users!")
            self.user_last_messages[message.from_user.id] = response.id
    
    # ===================================
    # SECTION 9: FORCE SUBSCRIBE COMMANDS
    # ===================================
    
    async def forcesub_command(self, message: Message):
        """Handle /forcesub command"""
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", False):
            await self.delete_previous_message(message.from_user.id)
        
        # Format message exactly like screenshot
        forcesub_text = (
            f"<b>{message.from_user.first_name}</b>\n"
            "## /forcesub\n\n"
            "**FORCE SUB COMMANDS :**\n\n"
            "### /fsub_chnl : CHECK CURRENT FORCE SUB CHANNELS (ADMINS)\n\n"
            "### /add_fsub : ADD ONE OR MULTIPLE FORCE SUB CHANNELS (OWNER)\n\n"
            "### /del_fsub : DELETE ONE OR MULTIPLE FORCE SUB CHANNELS (OWNER)"
        )
        
        buttons = [
            [InlineKeyboardButton("⬅️ Back", callback_data="settings_menu")],
            [InlineKeyboardButton("❌ Close", callback_data="close")]
        ]
        
        keyboard = InlineKeyboardMarkup(buttons)
        
        response = await message.reply(
            forcesub_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        
        self.user_last_messages[message.from_user.id] = response.id
    
    async def req_fsub_command(self, message: Message):
        """Handle /req_fsub command WITH PHOTO"""
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", False):
            await self.delete_previous_message(message.from_user.id)
        
        # Get current settings
        settings = await self.db.get_settings()
        request_fsub = settings.get("request_fsub", False)
        force_sub_pics = settings.get("force_sub_pics", Config.FORCE_SUB_PICS)
        
        # Get random force sub picture
        force_sub_pic = get_random_pic(force_sub_pics)
        
        # Format exactly like screenshot
        status = "ENABLED" if request_fsub else "DISABLED"
        
        req_fsub_text = (
            "<b>REQUEST FSUB SETTINGS</b>\n\n"
            f"REQUEST FSUB MODE: {status}\n\n"
            "CLICK BELOW BUTTONS TO CHANGE SETTINGS"
        )
        
        # Create toggle buttons
        buttons = []
        
        if request_fsub:
            buttons.append([
                InlineKeyboardButton("❌ OFF", callback_data="reqfsub_off")
            ])
        else:
            buttons.append([
                InlineKeyboardButton("✅ ON", callback_data="reqfsub_on")
            ])
        
        buttons.append([
            InlineKeyboardButton("MORE SETTINGS", callback_data="force_sub_settings")
        ])
        
        buttons.append([
            InlineKeyboardButton("⬅️ Back", callback_data="settings_menu"),
            InlineKeyboardButton("❌ Close", callback_data="close")
        ])
        
        keyboard = InlineKeyboardMarkup(buttons)
        
        try:
            # Try to send photo with caption
            response = await message.reply_photo(
                photo=force_sub_pic,
                caption=req_fsub_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Error sending force sub photo: {e}")
            # Fallback to text message
            response = await message.reply(
                req_fsub_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
        
        self.user_last_messages[message.from_user.id] = response.id
    
    async def fsub_chnl_command(self, message: Message):
        """Handle /fsub_chnl command"""
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", False):
            await self.delete_previous_message(message.from_user.id)
        
        # Get current channels
        channels = await self.db.get_force_sub_channels()
        
        if not channels:
            response = await message.reply("❌ No force sub channels!")
            self.user_last_messages[message.from_user.id] = response.id
            return
        
        channel_text = "📢 <b>FORCE SUB CHANNELS</b>\n\n"
        
        for i, channel in enumerate(channels, 1):
            channel_id = channel["channel_id"]
            username = channel.get("channel_username", f"ID: {channel_id}")
            
            try:
                chat = await self.get_chat(channel_id)
                channel_text += f"{i}. {chat.title}\n"
                if chat.username:
                    channel_text += f"   @{chat.username}\n\n"
                else:
                    channel_text += f"   ID: {channel_id}\n\n"
            except:
                channel_text += f"{i}. {username}\n\n"
        
        channel_text += f"📊 Total: {len(channels)} channels"
        
        buttons = [
            [InlineKeyboardButton("⬅️ Back", callback_data="force_sub_settings")],
            [InlineKeyboardButton("❌ Close", callback_data="close")]
        ]
        
        keyboard = InlineKeyboardMarkup(buttons)
        
        response = await message.reply(
            channel_text,
            parse_mode=enums.ParseMode.HTML
        )
        
        self.user_last_messages[message.from_user.id] = response.id
    
    async def add_fsub_command(self, message: Message):
        """Handle /add_fsub command"""
        if message.from_user.id != Config.OWNER_ID:
            response = await message.reply("❌ Owner only!")
            self.user_last_messages[message.from_user.id] = response.id
            return
        
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", False):
            await self.delete_previous_message(message.from_user.id)
        
        if len(message.command) < 2:
            response = await message.reply(
                "📢 <b>ADD FORCE SUB</b>\n\n"
                "Usage: <code>/add_fsub @channel</code>\n"
                "or\n"
                "<code>/add_fsub -100123456</code>",
                parse_mode=enums.ParseMode.HTML
            )
            self.user_last_messages[message.from_user.id] = response.id
            return
        
        try:
            channel = message.command[1]
            
            # Try to get chat info
            chat = await self.get_chat(channel)
            
            # Add to database
            await self.db.add_force_sub_channel(chat.id, chat.username)
            
            # Update local list
            self.force_sub_channels = await self.db.get_force_sub_channels()
            
            response = await message.reply(
                f"✅ <b>Channel Added!</b>\n\n"
                f"Channel: {chat.title}\n"
                f"ID: <code>{chat.id}</code>",
                parse_mode=enums.ParseMode.HTML
            )
            
            self.user_last_messages[message.from_user.id] = response.id
            
        except Exception as e:
            logger.error(f"Error adding force sub channel: {e}")
            response = await message.reply("❌ Error adding channel!")
            self.user_last_messages[message.from_user.id] = response.id
    
    async def del_fsub_command(self, message: Message):
        """Handle /del_fsub command"""
        if message.from_user.id != Config.OWNER_ID:
            response = await message.reply("❌ Owner only!")
            self.user_last_messages[message.from_user.id] = response.id
            return
        
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", False):
            await self.delete_previous_message(message.from_user.id)
        
        if len(message.command) < 2:
            response = await message.reply(
                "🗑️ <b>REMOVE FORCE SUB</b>\n\n"
                "Usage: <code>/del_fsub -100123456</code>",
                parse_mode=enums.ParseMode.HTML
            )
            self.user_last_messages[message.from_user.id] = response.id
            return
        
        try:
            channel_id = int(message.command[1])
            
            # Remove from database
            await self.db.remove_force_sub_channel(channel_id)
            
            # Update local list
            self.force_sub_channels = await self.db.get_force_sub_channels()
            
            response = await message.reply(
                f"✅ <b>Channel Removed!</b>\n\n"
                f"Channel ID: <code>{channel_id}</code>",
                parse_mode=enums.ParseMode.HTML
            )
            
            self.user_last_messages[message.from_user.id] = response.id
            
        except ValueError:
            response = await message.reply("❌ Invalid channel ID!")
            self.user_last_messages[message.from_user.id] = response.id
        except Exception as e:
            logger.error(f"Error removing force sub channel: {e}")
            response = await message.reply("❌ Error removing channel!")
            self.user_last_messages[message.from_user.id] = response.id
    
    # ===================================
    # SECTION 10: FILES COMMAND (WITH PHOTO)
    # ===================================
    
    async def files_command(self, message: Message):
        """Handle /files command WITH PHOTO"""
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", False):
            await self.delete_previous_message(message.from_user.id)
        
        # Get current settings
        settings = await self.db.get_settings()
        
        protect_content = settings.get("protect_content", True)
        hide_caption = settings.get("hide_caption", False)
        channel_button = settings.get("channel_button", True)
        files_pics = settings.get("files_pics", Config.FILES_PICS)
        
        # Get random files picture
        files_pic = get_random_pic(files_pics)
        
        # Format exactly like screenshot
        protect_status = "DISABLED" if not protect_content else "ENABLED"
        hide_status = "DISABLED" if not hide_caption else "ENABLED"
        button_status = "ENABLED" if channel_button else "DISABLED"
        
        files_text = (
            "<b>FILES RELATED SETTINGS</b>\n\n"
            f"PROTECT CONTENT: {protect_status}\n"
            f"HIDE CAPTION: {hide_status}\n"
            f"CHANNEL BUTTON: {button_status}\n\n"
            "CLICK BELOW BUTTONS TO CHANGE SETTINGS"
        )
        
        # Create toggle buttons - simple layout like screenshot
        buttons = []
        
        # Protect Content toggle
        if protect_content:
            buttons.append([
                InlineKeyboardButton("🔓 DISABLE PROTECT", callback_data="toggle_protect_content")
            ])
        else:
            buttons.append([
                InlineKeyboardButton("🔒 ENABLE PROTECT", callback_data="toggle_protect_content")
            ])
        
        # Hide Caption toggle
        if hide_caption:
            buttons.append([
                InlineKeyboardButton("👁️ SHOW CAPTION", callback_data="toggle_hide_caption")
            ])
        else:
            buttons.append([
                InlineKeyboardButton("👁️‍🗨️ HIDE CAPTION", callback_data="toggle_hide_caption")
            ])
        
        # Channel Button toggle
        if channel_button:
            buttons.append([
                InlineKeyboardButton("📢 DISABLE BUTTON", callback_data="toggle_channel_button")
            ])
        else:
            buttons.append([
                InlineKeyboardButton("📢 ENABLE BUTTON", callback_data="toggle_channel_button")
            ])
        
        buttons.append([
            InlineKeyboardButton("🔘 CUSTOM BUTTON", callback_data="custom_buttons_menu")
        ])
        
        buttons.append([
            InlineKeyboardButton("⬅️ Back", callback_data="settings_menu"),
            InlineKeyboardButton("❌ Close", callback_data="close")
        ])
        
        keyboard = InlineKeyboardMarkup(buttons)
        
        try:
            # Try to send photo with caption
            response = await message.reply_photo(
                photo=files_pic,
                caption=files_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Error sending files photo: {e}")
            # Fallback to text message
            response = await message.reply(
                files_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
        
        self.user_last_messages[message.from_user.id] = response.id
    
    # ===================================
    # SECTION 11: AUTO DELETE COMMAND (WITH PHOTO)
    # ===================================
    
    async def auto_del_command(self, message: Message):
        """Handle /auto_del command WITH PHOTO"""
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", False):
            await self.delete_previous_message(message.from_user.id)
        
        # Get current settings
        settings = await self.db.get_settings()
        
        auto_delete = settings.get("auto_delete", False)
        auto_delete_time = settings.get("auto_delete_time", 300)
        auto_del_pics = settings.get("auto_del_pics", Config.AUTO_DEL_PICS)
        
        # Get random auto delete picture
        auto_del_pic = get_random_pic(auto_del_pics)
        
        # Format exactly like screenshot
        status = "ENABLED" if auto_delete else "DISABLED"
        time_text = format_time(auto_delete_time)
        
        auto_del_text = (
            "<b>AUTO DELETE SETTINGS</b>\n\n"
            f"AUTO DELETE MODE: {status}\n\n"
            f"DELETE TIMER: {time_text}\n\n"
            "CLICK BELOW BUTTONS TO CHANGE SETTINGS"
        )
        
        buttons = []
        
        # Toggle button
        if auto_delete:
            buttons.append([
                InlineKeyboardButton("❌ DISABLE MODE", callback_data="toggle_auto_delete")
            ])
        else:
            buttons.append([
                InlineKeyboardButton("✅ ENABLE MODE", callback_data="toggle_auto_delete")
            ])
        
        # Time buttons (only show if auto delete is enabled)
        if auto_delete:
            time_buttons = []
            for time_sec in AUTO_DELETE_TIMES:
                time_display = format_time(time_sec)
                time_buttons.append(
                    InlineKeyboardButton(time_display, callback_data=f"autodel_{time_sec}")
                )
            
            # Add time buttons in rows
            buttons.append(time_buttons[:3])  # First 3
            if len(time_buttons) > 3:
                buttons.append(time_buttons[3:])  # Remaining
        
        buttons.append([
            InlineKeyboardButton("🔄 REFRESH", callback_data="refresh_autodel"),
            InlineKeyboardButton("❌ CLOSE", callback_data="close")
        ])
        
        keyboard = InlineKeyboardMarkup(buttons)
        
        try:
            # Try to send photo with caption
            response = await message.reply_photo(
                photo=auto_del_pic,
                caption=auto_del_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Error sending auto delete photo: {e}")
            # Fallback to text message
            response = await message.reply(
                auto_del_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
        
        self.user_last_messages[message.from_user.id] = response.id
    
    # ===================================
    # SECTION 12: OTHER COMMANDS
    # ===================================
    
    async def show_deleted_message(self, message: Message):
        """Show deleted message prompt"""
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
        
        self.user_last_messages[message.from_user.id] = response.id
    
    async def custom_button_menu(self, message: Message):
        """Show custom button menu"""
        button_text = (
            "<b>Custom Button:</b>\n\n"
            "You can add a custom button to your message"
        )
        
        buttons = [
            [
                InlineKeyboardButton("⬅️ back", callback_data="files_settings"),
                InlineKeyboardButton("🗑️ Delete", callback_data="delete_custom_button")
            ]
        ]
        
        keyboard = InlineKeyboardMarkup(buttons)
        
        response = await message.reply(
            button_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
        
        self.user_last_messages[message.from_user.id] = response.id
    
    async def send_file_with_buttons(self, message: Message, file_info: dict):
        """Send file with buttons - MATCHING SCREENSHOT FORMAT"""
        # Example format from screenshot
        file_text = (
            "@Hental_Community\n\n"
            "❤️ Dark Gathering.\n\n"
            "- Season: 1\n"
            "- Episode: 25\n"
            "- Audio track: Hindi | #FanDub\n"
            "- Quality: 720p\n\n"
            "[ ] Anime: @Ongoing_Animes_Hindi 🟺\n\n"
            "[ ] Movie: @Anime_Hindi_dubbed_Series ✔\n\n"
            "Main Channel Join"
        )
        
        buttons = [
            [
                InlineKeyboardButton("Anime", url="https://t.me/Ongoing_Animes_Hindi"),
                InlineKeyboardButton("Movie", url="https://t.me/Anime_Hindi_dubbed_Series")
            ],
            [
                InlineKeyboardButton("Main Channel Join", url=f"https://t.me/{Config.UPDATE_CHANNEL}")
            ]
        ]
        
        keyboard = InlineKeyboardMarkup(buttons)
        
        # This would be called when sending actual files
        # For now, just show the format
        return file_text, keyboard
    
    # ===================================
    # SECTION 13: SETTINGS COMMAND (WITH PHOTO)
    # ===================================
    
    async def settings_command(self, message: Message):
        """Handle /settings command WITH PHOTO"""
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", False):
            await self.delete_previous_message(message.from_user.id)
        
        # Get current settings
        settings = await self.db.get_settings()
        welcome_pics = settings.get("welcome_pics", Config.WELCOME_PICS)
        
        # Get random settings picture
        settings_pic = get_random_pic(welcome_pics)
        
        # Format settings
        settings_text = (
            "⚙️ <b>BOT SETTINGS</b>\n\n"
            f"• 🔒 Protect Content: {'✅' if settings.get('protect_content') else '❌'}\n"
            f"• 🎭 Hide Caption: {'✅' if settings.get('hide_caption') else '❌'}\n"
            f"• 📢 Channel Button: {'✅' if settings.get('channel_button') else '❌'}\n"
            f"• 🗑️ Auto Delete: {'✅' if settings.get('auto_delete') else '❌'}\n"
            f"• 👥 Force Sub: {'✅' if settings.get('request_fsub') else '❌'}\n"
            f"• 🤖 Bot Msg Delete: {'✅' if settings.get('auto_delete_bot_messages') else '❌'}\n\n"
            "Select a category to configure:"
        )
        
        # Create button grid
        buttons = [
            [
                InlineKeyboardButton("📁 Files", callback_data="files_settings"),
                InlineKeyboardButton("🗑️ Auto Delete", callback_data="auto_delete_settings")
            ],
            [
                InlineKeyboardButton("📢 Force Sub", callback_data="force_sub_settings"),
                InlineKeyboardButton("🤖 Bot Messages", callback_data="bot_msg_settings")
            ],
            [
                InlineKeyboardButton("🔘 Buttons", callback_data="custom_buttons_menu"),
                InlineKeyboardButton("📝 Texts", callback_data="custom_texts_menu")
            ],
            [
                InlineKeyboardButton("⬅️ Back", callback_data="admin_panel"),
                InlineKeyboardButton("❌ Close", callback_data="close")
            ]
        ]
        
        keyboard = InlineKeyboardMarkup(buttons)
        
        try:
            # Try to send photo with caption
            response = await message.reply_photo(
                photo=settings_pic,
                caption=settings_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Error sending settings photo: {e}")
            # Fallback to text message
            response = await message.reply(
                settings_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
        
        self.user_last_messages[message.from_user.id] = response.id
    
    # ===================================
    # SECTION 14: BASIC ADMIN COMMANDS
    # ===================================
    
    async def users_command(self, message: Message):
        """Handle /users command"""
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", False):
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
                # Try to send photo with caption
                response = await message.reply_photo(
                    photo=stats_pic,
                    caption=stats_text,
                    reply_markup=keyboard,
                    parse_mode=enums.ParseMode.HTML
                )
            except Exception as e:
                logger.error(f"Error sending stats photo: {e}")
                # Fallback to text message
                response = await message.reply(
                    stats_text,
                    reply_markup=keyboard,
                    parse_mode=enums.ParseMode.HTML
                )
            
            self.user_last_messages[message.from_user.id] = response.id
            
        except Exception as e:
            logger.error(f"Error in users command: {e}")
            response = await message.reply("❌ Error fetching user statistics!")
            self.user_last_messages[message.from_user.id] = response.id
    
    async def stats_command(self, message: Message):
        """Handle /stats command WITH PHOTO"""
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", False):
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
                # Try to send photo with caption
                response = await message.reply_photo(
                    photo=stats_pic,
                    caption=stats_text,
                    reply_markup=keyboard,
                    parse_mode=enums.ParseMode.HTML
                )
            except Exception as e:
                logger.error(f"Error sending stats photo: {e}")
                # Fallback to text message
                response = await message.reply(
                    stats_text,
                    reply_markup=keyboard,
                    parse_mode=enums.ParseMode.HTML
                )
            
            self.user_last_messages[message.from_user.id] = response.id
            
        except Exception as e:
            logger.error(f"Error in stats command: {e}")
            response = await message.reply("❌ Error fetching statistics!")
            self.user_last_messages[message.from_user.id] = response.id
    
    async def cmd_command(self, message: Message):
        """Handle /cmd command WITH PHOTO"""
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", False):
            await self.delete_previous_message(message.from_user.id)
        
        # Check if user is admin
        is_admin = await self.db.is_admin(message.from_user.id)
        
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
            InlineKeyboardButton("⬅️ Back", callback_data="admin_panel"),
            InlineKeyboardButton("❌ Close", callback_data="close")
        ])
        
        keyboard = InlineKeyboardMarkup(buttons)
        
        try:
            # Try to send photo with caption
            response = await message.reply_photo(
                photo=cmd_pic,
                caption=cmd_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Error sending cmd photo: {e}")
            # Fallback to text message
            response = await message.reply(
                cmd_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
        
        self.user_last_messages[message.from_user.id] = response.id
    
    async def broadcast_command(self, message: Message):
        """Handle /broadcast command"""
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", False):
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
            self.user_last_messages[message.from_user.id] = response.id
            return
        
        try:
            # Get all users
            users = await self.db.get_all_users()
            total_users = len(users)
            
            if total_users == 0:
                response = await message.reply("❌ No users to broadcast to!")
                self.user_last_messages[message.from_user.id] = response.id
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
            
            self.user_last_messages[message.from_user.id] = response.id
            
        except Exception as e:
            logger.error(f"Error in broadcast command: {e}")
            response = await message.reply("❌ Error during broadcast!")
            self.user_last_messages[message.from_user.id] = response.id
    
    async def ban_command(self, message: Message):
        """Handle /ban command"""
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", False):
            await self.delete_previous_message(message.from_user.id)
        
        if len(message.command) < 2:
            response = await message.reply(
                "🚫 <b>BAN USER</b>\n\n"
                "Usage: <code>/ban user_id [reason]</code>\n\n"
                "Example: <code>/ban 123456789 Spamming</code>",
                parse_mode=enums.ParseMode.HTML
            )
            self.user_last_messages[message.from_user.id] = response.id
            return
        
        try:
            user_id = int(message.command[1])
            reason = " ".join(message.command[2:]) if len(message.command) > 2 else "No reason provided"
            
            # Check if user exists
            try:
                user = await self.get_users(user_id)
            except:
                response = await message.reply("❌ User not found!")
                self.user_last_messages[message.from_user.id] = response.id
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
            
            self.user_last_messages[message.from_user.id] = response.id
            
        except ValueError:
            response = await message.reply("❌ Invalid user ID!")
            self.user_last_messages[message.from_user.id] = response.id
        except Exception as e:
            logger.error(f"Error banning user: {e}")
            response = await message.reply("❌ Error banning user!")
            self.user_last_messages[message.from_user.id] = response.id
    
    async def unban_command(self, message: Message):
        """Handle /unban command"""
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", False):
            await self.delete_previous_message(message.from_user.id)
        
        if len(message.command) < 2:
            response = await message.reply(
                "✅ <b>UNBAN USER</b>\n\n"
                "Usage: <code>/unban user_id</code>\n\n"
                "Example: <code>/unban 123456789</code>",
                parse_mode=enums.ParseMode.HTML
            )
            self.user_last_messages[message.from_user.id] = response.id
            return
        
        try:
            user_id = int(message.command[1])
            
            # Check if user is banned
            if not await self.db.is_user_banned(user_id):
                response = await message.reply("⚠️ User is not banned!")
                self.user_last_messages[message.from_user.id] = response.id
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
            
            self.user_last_messages[message.from_user.id] = response.id
            
        except ValueError:
            response = await message.reply("❌ Invalid user ID!")
            self.user_last_messages[message.from_user.id] = response.id
        except Exception as e:
            logger.error(f"Error unbanning user: {e}")
            response = await message.reply("❌ Error unbanning user!")
            self.user_last_messages[message.from_user.id] = response.id
    
    async def logs_command(self, message: Message):
        """Handle /logs command"""
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", False):
            await self.delete_previous_message(message.from_user.id)
        
        try:
            # Check if log file exists
            if not os.path.exists('bot.log'):
                response = await message.reply("❌ Log file not found!")
                self.user_last_messages[message.from_user.id] = response.id
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
            self.user_last_messages[message.from_user.id] = response.id
    
    # ===================================
    # SECTION 15: FILE MANAGEMENT COMMANDS
    # ===================================
    
    async def getlink_command(self, message: Message):
        """Handle /getlink command"""
        if not await self.db.is_admin(message.from_user.id):
            response = await message.reply("❌ Admin only!")
            self.user_last_messages[message.from_user.id] = response.id
            return
        
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", False):
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
            
            self.user_last_messages[message.from_user.id] = response.id
    
    async def genlink_command(self, message: Message):
        """Handle /genlink command"""
        if not await self.db.is_admin(message.from_user.id):
            response = await message.reply("❌ Admin only!")
            self.user_last_messages[message.from_user.id] = response.id
            return
        
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", False):
            await self.delete_previous_message(message.from_user.id)
        
        if not message.reply_to_message:
            response = await message.reply(
                "🔗 <b>GENERATE LINK</b>\n\n"
                "Reply to a file with\n"
                "/genlink to create\n"
                "a shareable link",
                parse_mode=enums.ParseMode.HTML
            )
            self.user_last_messages[message.from_user.id] = response.id
            return
        
        if not self.db_channel:
            response = await message.reply("❌ Set database channel first!")
            self.user_last_messages[message.from_user.id] = response.id
            return
        
        try:
            # Forward message to database channel
            forwarded = await message.reply_to_message.forward(self.db_channel)
            
            # Generate link
            base64_id = await encode(f"file_{forwarded.id}")
            bot_username = Config.BOT_USERNAME
            link = f"https://t.me/{bot_username}?start={base64_id}"
            
            # Shorten URL if configured
            if Config.SHORTENER_API and Config.SHORTENER_URL:
                link = await shorten_url(link)
            
            response = await message.reply(
                f"✅ <b>Link Generated!</b>\n\n"
                f"🔗 Link:\n"
                f"<code>{link}</code>\n\n"
                "Share this link with users",
                parse_mode=enums.ParseMode.HTML,
                disable_web_page_preview=True
            )
            
            self.user_last_messages[message.from_user.id] = response.id
            
        except Exception as e:
            logger.error(f"Error generating link: {e}")
            response = await message.reply("❌ Error generating link!")
            self.user_last_messages[message.from_user.id] = response.id
    
    async def batch_command(self, message: Message):
        """Handle /batch command"""
        if not await self.db.is_admin(message.from_user.id):
            response = await message.reply("❌ Admin only!")
            self.user_last_messages[message.from_user.id] = response.id
            return
        
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", False):
            await self.delete_previous_message(message.from_user.id)
        
        if not self.db_channel:
            response = await message.reply("❌ Set database channel first!")
            self.user_last_messages[message.from_user.id] = response.id
            return
        
        user_id = message.from_user.id
        self.batch_state[user_id] = []
        
        response = await message.reply(
            "📦 <b>BATCH UPLOAD</b>\n\n"
            "1. Forward files\n"
            "2. Send /done when done\n"
            "3. Max: 100 files",
            parse_mode=enums.ParseMode.HTML
        )
        
        self.user_last_messages[user_id] = response.id
    
    async def custom_batch_command(self, message: Message):
        """Handle /custom_batch command"""
        if not await self.db.is_admin(message.from_user.id):
            response = await message.reply("❌ Admin only!")
            self.user_last_messages[message.from_user.id] = response.id
            return
        
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", False):
            await self.delete_previous_message(message.from_user.id)
        
        if not self.db_channel:
            response = await message.reply("❌ Set database channel first!")
            self.user_last_messages[message.from_user.id] = response.id
            return
        
        user_id = message.from_user.id
        self.custom_batch_state[user_id] = {"files": [], "message": ""}
        
        response = await message.reply(
            "📝 <b>CUSTOM BATCH</b>\n\n"
            "1. Send custom message\n"
            "2. Forward files\n"
            "3. Send /done when done",
            parse_mode=enums.ParseMode.HTML
        )
        
        self.user_last_messages[user_id] = response.id
    
    async def special_link_command(self, message: Message):
        """Handle /special_link command"""
        if not await self.db.is_admin(message.from_user.id):
            response = await message.reply("❌ Admin only!")
            self.user_last_messages[message.from_user.id] = response.id
            return
        
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", False):
            await self.delete_previous_message(message.from_user.id)
        
        if not self.db_channel:
            response = await message.reply("❌ Set database channel first!")
            self.user_last_messages[message.from_user.id] = response.id
            return
        
        user_id = message.from_user.id
        self.special_link_state[user_id] = {"files": [], "message": ""}
        
        response = await message.reply(
            "🌟 <b>SPECIAL LINK</b>\n\n"
            "1. Send custom message\n"
            "2. Forward files\n"
            "3. Send /done when done",
            parse_mode=enums.ParseMode.HTML
        )
        
        self.user_last_messages[user_id] = response.id
    
    # ===================================
    # SECTION 16: CHANNEL MANAGEMENT COMMANDS
    # ===================================
    
    async def setchannel_command(self, message: Message):
        """Handle /setchannel command"""
        if not await self.db.is_admin(message.from_user.id):
            response = await message.reply("❌ Admin only!")
            self.user_last_messages[message.from_user.id] = response.id
            return
        
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", False):
            await self.delete_previous_message(message.from_user.id)
        
        if len(message.command) < 2:
            response = await message.reply(
                "📺 <b>SET CHANNEL</b>\n\n"
                "Usage: <code>/setchannel @channel</code>\n"
                "or\n"
                "<code>/setchannel -100123456</code>",
                parse_mode=enums.ParseMode.HTML
            )
            self.user_last_messages[message.from_user.id] = response.id
            return
        
        try:
            channel = message.command[1]
            
            # Try to get chat info
            try:
                chat = await self.get_chat(channel)
                
                # Check if bot is admin in channel
                try:
                    member = await self.get_chat_member(chat.id, (await self.get_me()).id)
                    if member.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
                        response = await message.reply("❌ Bot must be admin!")
                        self.user_last_messages[message.from_user.id] = response.id
                        return
                except:
                    response = await message.reply("❌ Bot must be admin!")
                    self.user_last_messages[message.from_user.id] = response.id
                    return
                
                # Set as database channel
                await self.db.set_db_channel(chat.id)
                self.db_channel = chat.id
                
                response = await message.reply(
                    f"✅ <b>Channel Set!</b>\n\n"
                    f"📺 {chat.title}\n"
                    f"🆔 <code>{chat.id}</code>",
                    parse_mode=enums.ParseMode.HTML
                )
                
            except Exception as e:
                logger.error(f"Error setting channel: {e}")
                response = await message.reply("❌ Invalid channel!")
            
            self.user_last_messages[message.from_user.id] = response.id
            
        except Exception as e:
            logger.error(f"Error in setchannel command: {e}")
            response = await message.reply("❌ Error setting channel!")
            self.user_last_messages[message.from_user.id] = response.id
    
    async def checkchannel_command(self, message: Message):
        """Handle /checkchannel command"""
        if not await self.db.is_admin(message.from_user.id):
            response = await message.reply("❌ Admin only!")
            self.user_last_messages[message.from_user.id] = response.id
            return
        
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", False):
            await self.delete_previous_message(message.from_user.id)
        
        db_channel = await self.db.get_db_channel()
        
        if not db_channel:
            response = await message.reply("❌ No channel set!")
            self.user_last_messages[message.from_user.id] = response.id
            return
        
        try:
            chat = await self.get_chat(db_channel)
            
            # Check bot admin status
            try:
                member = await self.get_chat_member(chat.id, (await self.get_me()).id)
                admin_status = "✅ Admin" if member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER] else "❌ Not Admin"
            except:
                admin_status = "❌ Not Admin"
            
            response = await message.reply(
                f"📺 <b>CHANNEL INFO</b>\n\n"
                f"📺 {chat.title}\n"
                f"🆔 <code>{chat.id}</code>\n"
                f"👤 @{chat.username if chat.username else 'Private'}\n"
                f"🤖 {admin_status}",
                parse_mode=enums.ParseMode.HTML
            )
            
            self.user_last_messages[message.from_user.id] = response.id
            
        except Exception as e:
            logger.error(f"Error checking channel: {e}")
            response = await message.reply("❌ Error checking channel!")
            self.user_last_messages[message.from_user.id] = response.id
    
    async def removechannel_command(self, message: Message):
        """Handle /removechannel command"""
        if not await self.db.is_admin(message.from_user.id):
            response = await message.reply("❌ Admin only!")
            self.user_last_messages[message.from_user.id] = response.id
            return
        
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", False):
            await self.delete_previous_message(message.from_user.id)
        
        db_channel = await self.db.get_db_channel()
        
        if not db_channel:
            response = await message.reply("❌ No channel to remove!")
            self.user_last_messages[message.from_user.id] = response.id
            return
        
        try:
            await self.db.remove_db_channel()
            self.db_channel = None
            
            response = await message.reply(
                "✅ <b>Channel Removed!</b>\n\n"
                "You can set a new channel",
                parse_mode=enums.ParseMode.HTML
            )
            
            self.user_last_messages[message.from_user.id] = response.id
            
        except Exception as e:
            logger.error(f"Error removing channel: {e}")
            response = await message.reply("❌ Error removing channel!")
            self.user_last_messages[message.from_user.id] = response.id
    
    # ===================================
    # SECTION 17: UTILITY COMMANDS
    # ===================================
    
    async def shortener_command(self, message: Message):
        """Handle /shortener command"""
        if not await self.db.is_admin(message.from_user.id):
            response = await message.reply("❌ Admin only!")
            self.user_last_messages[message.from_user.id] = response.id
            return
        
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", False):
            await self.delete_previous_message(message.from_user.id)
        
        if len(message.command) < 2:
            # Show current shortener status
            if Config.SHORTENER_API and Config.SHORTENER_URL:
                status_text = (
                    "🔗 <b>URL SHORTENER</b>\n\n"
                    f"Status: ✅ ENABLED\n"
                    f"Domain: {Config.SHORTENER_URL}\n\n"
                    "To disable: <code>/shortener disable</code>"
                )
            else:
                status_text = (
                    "🔗 <b>URL SHORTENER</b>\n\n"
                    f"Status: ❌ DISABLED\n\n"
                    "To enable: <code>/shortener api_url domain</code>"
                )
            
            response = await message.reply(
                status_text,
                parse_mode=enums.ParseMode.HTML,
                disable_web_page_preview=True
            )
            self.user_last_messages[message.from_user.id] = response.id
            return
        
        if message.command[1].lower() == "disable":
            # Disable shortener
            Config.SHORTENER_API = ""
            Config.SHORTENER_URL = ""
            
            response = await message.reply(
                "✅ <b>Shortener Disabled!</b>",
                parse_mode=enums.ParseMode.HTML
            )
        else:
            # Enable shortener
            if len(message.command) < 3:
                response = await message.reply(
                    "❌ <b>Invalid format!</b>\n\n"
                    "Usage: <code>/shortener api_url domain</code>",
                    parse_mode=enums.ParseMode.HTML
                )
                self.user_last_messages[message.from_user.id] = response.id
                return
            
            api_url = message.command[1]
            short_domain = message.command[2]
            
            # Validate URLs
            if not validate_url(api_url) or not validate_url(short_domain):
                response = await message.reply("❌ Invalid URL!")
                self.user_last_messages[message.from_user.id] = response.id
                return
            
            Config.SHORTENER_API = api_url
            Config.SHORTENER_URL = short_domain
            
            response = await message.reply(
                f"✅ <b>Shortener Enabled!</b>\n\n"
                f"Domain: {short_domain}",
                parse_mode=enums.ParseMode.HTML,
                disable_web_page_preview=True
            )
        
        self.user_last_messages[message.from_user.id] = response.id
    
    async def ping_command(self, message: Message):
        """Handle /ping command"""
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", False):
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
        
        self.user_last_messages[message.from_user.id] = response.id
    
    async def refresh_command(self, message: Message):
        """Handle /refresh command"""
        if not await self.db.is_admin(message.from_user.id):
            response = await message.reply("❌ Admin only!")
            self.user_last_messages[message.from_user.id] = response.id
            return
        
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", False):
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
        
        self.user_last_messages[message.from_user.id] = response.id
    
    async def font_command(self, message: Message):
        """Handle /font command WITH PHOTO"""
        # Check if user is admin
        if not await self.db.is_admin(message.from_user.id):
            response = await message.reply("❌ Admin only!")
            settings = await self.db.get_settings()
            if settings.get("auto_delete_bot_messages", False):
                delay = settings.get("auto_delete_time_bot", 30)
                asyncio.create_task(self.auto_delete_message(message.chat.id, response.id, delay))
            return
        
        if len(message.command) < 2:
            # Get font picture
            settings = await self.db.get_settings()
            welcome_pics = settings.get("welcome_pics", Config.WELCOME_PICS)
            font_pic = get_random_pic(welcome_pics)
            
            font_text = (
                "🎨 <b>FONT STYLES</b>\n\n"
                "Usage: <code>/font Your Text</code>\n\n"
                "Example: <code>/font Hello World</code>"
            )
            
            response = await message.reply_photo(
                photo=font_pic,
                caption=font_text,
                parse_mode=enums.ParseMode.HTML
            )
            
            settings = await self.db.get_settings()
            if settings.get("auto_delete_bot_messages", False):
                delay = settings.get("auto_delete_time_bot", 30)
                asyncio.create_task(self.auto_delete_message(message.chat.id, response.id, delay))
            return
        
        text = " ".join(message.command[1:])
        
        # Create font style buttons
        buttons = [
            [
                InlineKeyboardButton('𝚃𝚢𝚙𝚎𝚠𝚛𝚒𝚝𝚎𝚛', callback_data=f'font_typewriter_{text}'),
                InlineKeyboardButton('𝕆𝕦𝕝𝕚𝕟𝕖', callback_data=f'font_outline_{text}')
            ],
            [
                InlineKeyboardButton('𝐒𝐞𝐫𝐢𝐟', callback_data=f'font_serif_{text}'),
                InlineKeyboardButton('𝑺𝒆𝒓𝒊𝒇', callback_data=f'font_bold_cool_{text}')
            ],
            [
                InlineKeyboardButton('𝑆𝑒𝑟𝑖𝑓', callback_data=f'font_cool_{text}'),
                InlineKeyboardButton('Sᴍᴀʟʟ Cᴀᴘs', callback_data=f'font_smallcap_{text}')
            ],
            [
                InlineKeyboardButton('𝓈𝒸𝓇𝒾𝓅𝓉', callback_data=f'font_script_{text}'),
                InlineKeyboardButton('𝓼𝓬𝓻𝓲𝓹𝓽', callback_data=f'font_bold_script_{text}')
            ],
            [
                InlineKeyboardButton('ᵗⁱⁿʸ', callback_data=f'font_tiny_{text}'),
                InlineKeyboardButton('ᑕOᗰIᑕ', callback_data=f'font_comic_{text}')
            ],
            [
                InlineKeyboardButton("⬅️ Back", callback_data="admin_panel"),
                InlineKeyboardButton("❌ Close", callback_data="close")
            ]
        ]
        
        keyboard = InlineKeyboardMarkup(buttons)
        
        response = await message.reply(
            f"<b>Original:</b> <code>{text}</code>\n\n"
            "Select a font style:",
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
        
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", False):
            delay = settings.get("auto_delete_time_bot", 30)
            asyncio.create_task(self.auto_delete_message(message.chat.id, response.id, delay))
    
    # ===================================
    # SECTION 18: DONE COMMAND
    # ===================================
    
    async def done_command(self, message: Message):
        """Handle /done command"""
        if not await self.db.is_admin(message.from_user.id):
            response = await message.reply("❌ Admin only!")
            self.user_last_messages[message.from_user.id] = response.id
            return
        
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", False):
            await self.delete_previous_message(message.from_user.id)
        
        user_id = message.from_user.id
        
        # Check which state the user is in
        if user_id in self.batch_state:
            await self.process_batch(message)
        elif user_id in self.custom_batch_state:
            await self.process_custom_batch(message)
        elif user_id in self.special_link_state:
            await self.process_special_link(message)
        elif user_id in self.button_setting_state:
            await self.process_button_setting(message)
        elif user_id in self.text_setting_state:
            await self.process_text_setting(message)
        else:
            response = await message.reply("❌ No operation in progress!")
            self.user_last_messages[user_id] = response.id
    
    async def process_batch(self, message: Message):
        """Process batch files"""
        user_id = message.from_user.id
        files = self.batch_state[user_id]
        
        if not files:
            response = await message.reply("❌ No files added!")
            self.user_last_messages[user_id] = response.id
            del self.batch_state[user_id]
            return
        
        try:
            # Forward all files to database channel
            file_ids = []
            for file in files[:MAX_BATCH_SIZE]:
                try:
                    forwarded = await file.forward(self.db_channel)
                    file_ids.append(forwarded.id)
                except Exception as e:
                    logger.error(f"Error forwarding file: {e}")
            
            # Generate batch link
            batch_data = f"batch_{','.join(map(str, file_ids))}"
            base64_id = await encode(batch_data)
            bot_username = Config.BOT_USERNAME
            link = f"https://t.me/{bot_username}?start={base64_id}"
            
            # Shorten URL if configured
            if Config.SHORTENER_API and Config.SHORTENER_URL:
                link = await shorten_url(link)
            
            response = await message.reply(
                f"✅ <b>Batch Created!</b>\n\n"
                f"📦 Files: {len(file_ids)}\n"
                f"🔗 Link:\n"
                f"<code>{link}</code>",
                parse_mode=enums.ParseMode.HTML,
                disable_web_page_preview=True
            )
            
            # Clear state
            del self.batch_state[user_id]
            self.user_last_messages[user_id] = response.id
            
        except Exception as e:
            logger.error(f"Error processing batch: {e}")
            response = await message.reply("❌ Error creating batch!")
            self.user_last_messages[user_id] = response.id
            del self.batch_state[user_id]
    
    async def process_custom_batch(self, message: Message):
        """Process custom batch with message"""
        user_id = message.from_user.id
        state = self.custom_batch_state[user_id]
        
        if not state["files"]:
            response = await message.reply("❌ No files added!")
            self.user_last_messages[user_id] = response.id
            del self.custom_batch_state[user_id]
            return
        
        try:
            # Forward all files to database channel
            file_ids = []
            for file in state["files"][:MAX_CUSTOM_BATCH]:
                try:
                    forwarded = await file.forward(self.db_channel)
                    file_ids.append(forwarded.id)
                except Exception as e:
                    logger.error(f"Error forwarding file: {e}")
            
            # Generate batch link
            batch_data = f"batch_{','.join(map(str, file_ids))}"
            base64_id = await encode(batch_data)
            bot_username = Config.BOT_USERNAME
            link = f"https://t.me/{bot_username}?start={base64_id}"
            
            # Shorten URL if configured
            if Config.SHORTENER_API and Config.SHORTENER_URL:
                link = await shorten_url(link)
            
            response = await message.reply(
                f"✅ <b>Custom Batch Created!</b>\n\n"
                f"📝 Message: {state['message'][:50]}...\n"
                f"📦 Files: {len(file_ids)}\n"
                f"🔗 Link:\n"
                f"<code>{link}</code>",
                parse_mode=enums.ParseMode.HTML,
                disable_web_page_preview=True
            )
            
            # Clear state
            del self.custom_batch_state[user_id]
            self.user_last_messages[user_id] = response.id
            
        except Exception as e:
            logger.error(f"Error processing custom batch: {e}")
            response = await message.reply("❌ Error creating custom batch!")
            self.user_last_messages[user_id] = response.id
            del self.custom_batch_state[user_id]
    
    async def process_special_link(self, message: Message):
        """Process special link creation"""
        user_id = message.from_user.id
        state = self.special_link_state[user_id]
        
        if not state["files"]:
            response = await message.reply("❌ No files added!")
            self.user_last_messages[user_id] = response.id
            del self.special_link_state[user_id]
            return
        
        try:
            # Forward all files to database channel
            file_ids = []
            for file in state["files"][:MAX_SPECIAL_FILES]:
                try:
                    forwarded = await file.forward(self.db_channel)
                    file_ids.append(forwarded.id)
                except Exception as e:
                    logger.error(f"Error forwarding file: {e}")
            
            # Generate unique link ID
            link_id = f"special_{int(time.time())}_{random.randint(1000, 9999)}"
            
            # Save to database
            await self.db.save_special_link(link_id, state["message"], file_ids)
            
            # Generate full link
            base64_id = await encode(f"link_{link_id}")
            bot_username = Config.BOT_USERNAME
            link = f"https://t.me/{bot_username}?start={base64_id}"
            
            # Shorten URL if configured
            if Config.SHORTENER_API and Config.SHORTENER_URL:
                link = await shorten_url(link)
            
            response = await message.reply(
                f"✅ <b>Special Link Created!</b>\n\n"
                f"🌟 Link ID: {link_id}\n"
                f"📦 Files: {len(file_ids)}\n"
                f"🔗 Link:\n"
                f"<code>{link}</code>",
                parse_mode=enums.ParseMode.HTML,
                disable_web_page_preview=True
            )
            
            # Clear state
            del self.special_link_state[user_id]
            self.user_last_messages[user_id] = response.id
            
        except Exception as e:
            logger.error(f"Error processing special link: {e}")
            response = await message.reply("❌ Error creating special link!")
            self.user_last_messages[user_id] = response.id
            del self.special_link_state[user_id]
    
    async def process_button_setting(self, message: Message):
        """Process button setting"""
        user_id = message.from_user.id
        
        if not message.text:
            response = await message.reply("❌ Please send button config!")
            self.user_last_messages[user_id] = response.id
            return
        
        if message.text.lower() == "cancel":
            del self.button_setting_state[user_id]
            response = await message.reply("✅ Cancelled!")
            self.user_last_messages[user_id] = response.id
            return
        
        try:
            # Parse and validate button configuration
            buttons = parse_button_string(message.text)
            
            # Save to database
            await self.db.update_setting("custom_button", message.text)
            
            # Update local settings
            self.settings["custom_button"] = message.text
            
            response = await message.reply(
                f"✅ <b>Buttons Saved!</b>\n\n"
                f"Total rows: {len(buttons)}",
                parse_mode=enums.ParseMode.HTML
            )
            
            # Clear state
            del self.button_setting_state[user_id]
            self.user_last_messages[user_id] = response.id
            
        except Exception as e:
            logger.error(f"Error processing button setting: {e}")
            response = await message.reply("❌ Error saving buttons!")
            self.user_last_messages[user_id] = response.id
    
    async def process_text_setting(self, message: Message):
        """Process text setting"""
        user_id = message.from_user.id
        setting_type = self.text_setting_state[user_id]
        
        if not message.text:
            response = await message.reply("❌ Please send text!")
            self.user_last_messages[user_id] = response.id
            return
        
        if message.text.lower() == "cancel":
            del self.text_setting_state[user_id]
            response = await message.reply("✅ Cancelled!")
            self.user_last_messages[user_id] = response.id
            return
        
        try:
            # Save to database
            await self.db.update_setting(setting_type, message.text)
            
            # Update local settings
            self.settings[setting_type] = message.text
            
            response = await message.reply(
                f"✅ <b>Text Saved!</b>",
                parse_mode=enums.ParseMode.HTML
            )
            
            # Clear state
            del self.text_setting_state[user_id]
            self.user_last_messages[user_id] = response.id
            
        except Exception as e:
            logger.error(f"Error processing text setting: {e}")
            response = await message.reply("❌ Error saving text!")
            self.user_last_messages[user_id] = response.id
    
    # ===================================
    # SECTION 19: TEXT MESSAGE HANDLER
    # ===================================
    
    async def text_message_handler(self, message: Message):
        """Handle text messages from admins"""
        user_id = message.from_user.id
        
        # Check if user is in any state
        if user_id in self.batch_state:
            # Add file to batch
            if message.forward_from_chat or message.document or message.video or message.audio or message.photo:
                self.batch_state[user_id].append(message)
                response = await message.reply(f"✅ File added! Total: {len(self.batch_state[user_id])}")
                self.user_last_messages[user_id] = response.id
            else:
                response = await message.reply("❌ Send a file or /done")
                self.user_last_messages[user_id] = response.id
        
        elif user_id in self.custom_batch_state:
            state = self.custom_batch_state[user_id]
            
            if not state["message"]:
                # First message is the custom message
                state["message"] = message.text
                response = await message.reply("✅ Message saved! Now send files.")
                self.user_last_messages[user_id] = response.id
            else:
                # Add files after message is set
                if message.forward_from_chat or message.document or message.video or message.audio or message.photo:
                    state["files"].append(message)
                    response = await message.reply(f"✅ File added! Total: {len(state['files'])}")
                    self.user_last_messages[user_id] = response.id
                else:
                    response = await message.reply("❌ Send a file or /done")
                    self.user_last_messages[user_id] = response.id
        
        elif user_id in self.special_link_state:
            state = self.special_link_state[user_id]
            
            if not state["message"]:
                # First message is the custom message
                state["message"] = message.text
                response = await message.reply("✅ Message saved! Now send files.")
                self.user_last_messages[user_id] = response.id
            else:
                # Add files after message is set
                if message.forward_from_chat or message.document or message.video or message.audio or message.photo:
                    state["files"].append(message)
                    response = await message.reply(f"✅ File added! Total: {len(state['files'])}")
                    self.user_last_messages[user_id] = response.id
                else:
                    response = await message.reply("❌ Send a file or /done")
                    self.user_last_messages[user_id] = response.id
        
        elif user_id in self.button_setting_state:
            # Handle button setting
            await self.process_button_setting(message)
        
        elif user_id in self.text_setting_state:
            # Handle text setting
            await self.process_text_setting(message)
    
    # ===================================
    # SECTION 20: CALLBACK HANDLERS (UPDATED FOR PHOTOS)
    # ===================================
    
    async def handle_callback_query(self, query: CallbackQuery):
        """Handle all callback queries"""
        try:
            data = query.data
            
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
                await self.req_fsub_command(query.message)
            
            elif data == "fsub_channels_menu":
                await query.answer()
                await self.fsub_chnl_command(query.message)
            
            elif data == "bot_msg_settings":
                await query.answer()
                await self.bot_msg_settings_command(query.message)
            
            elif data == "custom_buttons_menu":
                await query.answer()
                await self.custom_button_menu(query.message)
            
            elif data == "custom_texts_menu":
                await query.answer()
                await self.handle_text_setting_callback(query)
            
            elif data == "users_menu":
                await query.answer()
                await self.users_command(query.message)
            
            elif data == "stats_menu":
                await query.answer()
                await self.stats_command(query.message)
            
            elif data == "admin_list_menu":
                await query.answer()
                await self.admin_list_command(query.message)
            
            # Command sending callbacks
            elif data.startswith("send_"):
                command = data.replace("send_", "")
                await query.answer(f"Sending /{command}")
                await query.message.reply(f"/{command}")
            
            # Toggle callbacks
            elif data.startswith("toggle_"):
                await query.answer()
                await self.handle_toggle_callback(query)
            
            # Auto delete time callbacks
            elif data.startswith("autodel_"):
                await query.answer()
                await self.handle_autodel_callback(query)
            
            # Force sub callbacks
            elif data.startswith("reqfsub_"):
                await query.answer()
                await self.handle_reqfsub_callback(query)
            
            # Font callbacks
            elif data.startswith("font_"):
                await query.answer()
                await self.handle_font_callback(query)
            
            # Text setting callbacks
            elif data.startswith("settext_"):
                await query.answer()
                await self.handle_settext_callback(query)
            
            # Refresh callbacks
            elif data.startswith("refresh_"):
                await query.answer("Refreshing...")
                await self.refresh_callback(query)
            
            # Delete custom button
            elif data == "delete_custom_button":
                await query.answer()
                await self.delete_custom_button(query)
            
            # Resend files callback
            elif data == "resend_files":
                await query.answer("Sending files...")
                await self.resend_files_callback(query)
            
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
            await self.bot_msg_settings_command(query.message)
    
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
    
    async def handle_font_callback(self, query: CallbackQuery):
        """Handle font style callback"""
        try:
            # Extract font style and text
            parts = query.data.split('_', 2)
            if len(parts) < 3:
                await query.answer("Invalid font data!", show_alert=True)
                return
            
            font_style = parts[1]
            original_text = parts[2]
            
            # Apply font style (simplified for now)
            styled_text = original_text  # In real implementation, use font library
            
            await query.answer("Font applied!")
            await query.message.edit_text(
                f"<b>Original:</b> <code>{original_text}</code>\n\n"
                f"<b>Styled:</b> <code>{styled_text}</code>\n\n"
                "You can copy the styled text.",
                parse_mode=enums.ParseMode.HTML
            )
            
        except Exception as e:
            logger.error(f"Error applying font: {e}")
            await query.answer("Error applying font!", show_alert=True)
    
    async def handle_settext_callback(self, query: CallbackQuery):
        """Handle text setting callback"""
        setting_type = query.data.replace("settext_", "")
        user_id = query.from_user.id
        
        # Set state for text setting
        self.text_setting_state[user_id] = setting_type
        
        # Get current text
        settings = await self.db.get_settings()
        current_text = settings.get(setting_type, "")
        
        setting_names = {
            "welcome_text": "Welcome Text",
            "help_text": "Help Text", 
            "about_text": "About Text"
        }
        
        await query.message.edit_text(
            f"📝 <b>SET {setting_names.get(setting_type, setting_type).upper()}</b>\n\n"
            f"Current text:\n<code>{current_text[:100]}...</code>\n\n"
            "Send me the new text, or send 'cancel' to cancel.",
            parse_mode=enums.ParseMode.HTML
        )
    
    async def handle_text_setting_callback(self, query: CallbackQuery):
        """Handle text setting callback"""
        user_id = query.from_user.id
        
        # Show options for text settings
        buttons = [
            [
                InlineKeyboardButton("👋 Welcome Text", callback_data="settext_welcome_text"),
                InlineKeyboardButton("📚 Help Text", callback_data="settext_help_text")
            ],
            [
                InlineKeyboardButton("ℹ️ About Text", callback_data="settext_about_text")
            ],
            [
                InlineKeyboardButton("⬅️ Back", callback_data="settings_menu"),
                InlineKeyboardButton("❌ Close", callback_data="close")
            ]
        ]
        
        keyboard = InlineKeyboardMarkup(buttons)
        
        await query.message.edit_text(
            "📝 <b>CUSTOM TEXTS</b>\n\n"
            "Select which text to customize:\n\n"
            "• 👋 Welcome - Shown when users start bot\n"
            "• 📚 Help - Shown when users use /help\n"
            "• ℹ️ About - Shown when users use /about",
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
    
    async def refresh_callback(self, query: CallbackQuery):
        """Handle refresh callback"""
        await query.answer("Refreshing...")
        
        # Delete previous bot message if auto-delete is enabled
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", False):
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
    
    async def delete_custom_button(self, query: CallbackQuery):
        """Delete custom button configuration"""
        await query.answer("Deleting custom button...")
        
        # Delete custom button from settings
        await self.db.update_setting("custom_button", "")
        self.settings["custom_button"] = ""
        
        await query.message.edit_text(
            "✅ <b>Custom button deleted!</b>",
            parse_mode=enums.ParseMode.HTML
        )
    
    async def resend_files_callback(self, query: CallbackQuery):
        """Resend files after deletion"""
        await query.answer("Files will be sent...")
        
        # This would need to track which files were previously sent
        # For now, just show a message
        await query.message.edit_text(
            "📦 <b>Resending files...</b>\n\n"
            "Please use the original link to access files again.",
            parse_mode=enums.ParseMode.HTML
        )
    
    async def bot_msg_settings_command(self, message: Message):
        """Handle bot message settings WITH PHOTO"""
        if not await self.db.is_admin(message.from_user.id):
            response = await message.reply("❌ Admin only!")
            self.user_last_messages[message.from_user.id] = response.id
            return
        
        # Delete previous bot message if auto-delete is enabled
        settings = await self.db.get_settings()
        if settings.get("auto_delete_bot_messages", False):
            await self.delete_previous_message(message.from_user.id)
        
        # Get current settings
        settings = await self.db.get_settings()
        auto_del_pics = settings.get("auto_del_pics", Config.AUTO_DEL_PICS)
        
        # Get random bot message picture
        bot_msg_pic = get_random_pic(auto_del_pics)
        
        auto_delete_bot = settings.get("auto_delete_bot_messages", False)
        auto_delete_time = settings.get("auto_delete_time_bot", 30)
        
        status = "ENABLED" if auto_delete_bot else "DISABLED"
        
        settings_text = (
            "🤖 <b>BOT MESSAGE SETTINGS</b>\n\n"
            f"🗑️ Auto Delete: {status}\n"
            f"⏱️ Delete After: {auto_delete_time}s\n\n"
            "Auto-delete bot's previous messages"
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
        time_options = [10, 30, 60, 120, 300]  # 10s, 30s, 1min, 2min, 5min
        
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
            # Try to send photo with caption
            response = await message.reply_photo(
                photo=bot_msg_pic,
                caption=settings_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Error sending bot message settings photo: {e}")
            # Fallback to text message
            response = await message.reply(
                settings_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
        
        self.user_last_messages[message.from_user.id] = response.id
    
    # ===================================
    # SECTION 21: JOIN REQUEST HANDLER
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
                    
                    # Log the approval
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
# SECTION 22: WEB SERVER (UNCHANGED)
# ===================================

async def start_web_server():
    """Start aiohttp web server for Render deployment"""
    app = web.Application()
    
    async def handle_root(request):
        return web.Response(
            text="🤖 Telegram Bot is Online!\n\n"
                 "This is a file sharing bot running on Render.\n"
                 "Bot is active and ready to serve files.",
            content_type="text/plain"
        )
    
    async def handle_health(request):
        return web.Response(
            text="✅ Bot is running!",
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
        await asyncio.sleep(3600)  # Sleep for 1 hour


# ===================================
# SECTION 23: MAIN FUNCTION (UPDATED)
# ===================================

async def main():
    """Main function to start the bot"""
    print(BANNER)
    logger.info("🚀 Starting File Sharing Bot with Photos in All Panels...")
    
    # Validate configuration
    if not Config.validate():
        logger.error("Configuration validation failed. Exiting.")
        return
    
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
        
        logger.info("✅ Bot is now running with Photos in All Panels!")
        logger.info("✅ Welcome message has photo from welcome pics")
        logger.info("✅ Force sub message has photo from force sub pics")
        logger.info("✅ Help message has photo from help pics")
        logger.info("✅ Files settings has photo from files pics")
        logger.info("✅ Auto delete settings has photo from auto del pics")
        logger.info("✅ All other panels have photos")
        
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
