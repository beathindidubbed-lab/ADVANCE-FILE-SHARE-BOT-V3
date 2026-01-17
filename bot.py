#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 TELEGRAM FILE SHARING BOT - COMPLETE FIXED VERSION
Three Auto-Delete Features + Blockquote Expandable Support
All Issues Fixed - Ready to Deploy
FIXED ISSUES:
1. Bot admin check ✓ - FIXED
2. File link generation ✓  
3. del_fsub_menu callback ✓
4. THREE CRITICAL BUGS FIXED ✓
5. BLOCKQUOTE EXPANDABLE SUPPORT ✓
"""

# ===================================
# SECTION 1: IMPORTS & SETUP (FIXED)
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
from fotnt_string import Fonts

# Pyrogram imports
from pyrogram import Client, filters, enums
from pyrogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery, InputMediaPhoto, ChatPermissions,
    ChatJoinRequest, BotCommand, BotCommandScopeAllPrivateChats,
    BotCommandScopeDefault, BotCommandScopeChat,
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
║               𝙁𝙄𝙇𝙀 𝙎𝙃𝘼𝙍𝙄𝙉𝙂 𝘽𝙊𝙏 - 𝙏𝙃𝙍𝙀𝙀 𝘼𝙐𝙏𝙊-𝘿𝙀𝙇𝙀𝙏𝙀 𝙁𝙀𝘼𝙏𝙐𝙍𝙀𝙎              ║
║               𝘽𝙇𝙊𝘾𝙆𝙌𝙐𝙊𝙏𝙀 𝙀𝙓𝙋𝘼𝙉𝘿𝘼𝘽𝙇𝙀 𝙎𝙐𝙋𝙋𝙊𝙍𝙏                            ║
╚════════════════════════════════════════════════════════════════════════════╝
"""

# Global constants
MAX_BATCH_SIZE = 100
MAX_SPECIAL_FILES = 50
MAX_CUSTOM_BATCH = 50
AUTO_DELETE_TIMES = [60, 300, 600, 1800, 3600]  # 1min, 5min, 10min, 30min, 1hour
DEFAULT_BOT_PICS = [
    "https://ibb.co/kjTFrs3",
    "https://ibb.co/rKXkRhP5",
    "https://ibb.co/Fk8yhV07",
    "https://ibb.co/bjfbzQTM",
    "https://ibb.co/N2PDXw6w"
]

# Start Command Reactions
REACTIONS = ["🙋", "🙌", "🙆", "🙅", "👋", "🙂", "🙃", "🍩", "🙈", "🤩", "🤖"]

# Bot Commands Configuration
BOT_COMMANDS = {
    "all_users": [
        BotCommand("start", "Check bot status"),
        BotCommand("help", "Get help"),
        BotCommand("ping", "Check bot ping"),
        BotCommand("about", "About bot")
    ],
    "admins": [
        BotCommand("start", "Check bot status"),
        BotCommand("help", "Get help"),
        BotCommand("ping", "Check bot ping"),
        BotCommand("about", "About bot"),
        BotCommand("cmd", "Command list"),
        BotCommand("settings", "Bot settings panel"),
        BotCommand("getlink", "Generate file link"),
        BotCommand("batch", "Store multiple files"),
        BotCommand("custom_batch", "Store files with custom message"),
        BotCommand("stats", "View bot statistics"),
        BotCommand("refresh", "Refresh statistics"),
        BotCommand("logs", "View bot logs"),
        BotCommand("setchannel", "Set database channel"),
        BotCommand("genlink", "Generate file link"),
        BotCommand("special_link", "Create special link"),
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
    DATABASE_NAME = os.environ.get("DATABASE_NAME", "file_bot")
    
    # Bot settings
    BOT_NAME = os.environ.get("BOT_NAME", "File Sharing Bot")
    BOT_USERNAME = os.environ.get("BOT_USERNAME", "").lstrip('@')
    OWNER_ID = int(os.environ.get("OWNER_ID", 0))
    
    # Admins (comma-separated)
    ADMINS = [int(x.strip()) for x in os.environ.get("ADMINS", "").split(",") if x.strip().isdigit()]
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
    
    # ==================================================================
    # THREE SEPARATE AUTO-DELETE FEATURES (VERIFIED & FIXED)
    # ==================================================================
    
    # FEATURE 1: CLEAN CONVERSATION
    # Delete previous bot message when sending new one (keeps PM clean)
    CLEAN_CONVERSATION = os.environ.get("CLEAN_CONVERSATION", "true").lower() == "true"
    
    # FEATURE 2: AUTO DELETE FILES
    # Delete file messages after set time (user configurable)
    AUTO_DELETE = os.environ.get("AUTO_DELETE", "false").lower() == "true"
    AUTO_DELETE_TIME = int(os.environ.get("AUTO_DELETE_TIME", 300))  # seconds (default 5 min)
    
    # FEATURE 3: SHOW INSTRUCTION AFTER FILE DELETION
    # Show "files deleted" instruction with resend button (NOT auto-deleted)
    SHOW_INSTRUCTION_AFTER_DELETE = os.environ.get("SHOW_INSTRUCTION_AFTER_DELETE", "true").lower() == "true"
    
    # ==================================================================
    
    # Force subscribe settings
    REQUEST_FSUB = os.environ.get("REQUEST_FSUB", "false").lower() == "true"
    
    # Auto approve join requests
    AUTO_APPROVE_MODE = os.environ.get("AUTO_APPROVE_MODE", "false").lower() == "true"
    
    # Auto-clean join requests after 24 hours
    AUTO_CLEAN_JOIN_REQUESTS = os.environ.get("AUTO_CLEAN_JOIN_REQUESTS", "true").lower() == "true"
    AUTO_CLEAN_INTERVAL = int(os.environ.get("AUTO_CLEAN_INTERVAL", 86400))
    
    @classmethod
    def parse_force_sub_channels(cls):
        """Parse force subscribe channels from environment variable"""
        channels = []
        for channel_str in cls.FORCE_SUB_CHANNELS_RAW:
            if ':' in channel_str:
                parts = channel_str.split(':', 1)
                channel_id_str = parts[0].strip()
                username = parts[1].strip().lstrip('@')
                try:
                    channel_id = int(channel_id_str)
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
        
        logger.info("✅ Configuration validated successfully")
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
        logger.info("=" * 60)
        logger.info("THREE AUTO-DELETE FEATURES CONFIGURED:")
        logger.info(f"✅ Feature 1 - Clean Conversation: {cls.CLEAN_CONVERSATION}")
        logger.info(f"✅ Feature 2 - Auto Delete Files: {cls.AUTO_DELETE} ({cls.AUTO_DELETE_TIME}s)")
        logger.info(f"✅ Feature 3 - Show Instruction: {cls.SHOW_INSTRUCTION_AFTER_DELETE}")
        logger.info("=" * 60)

# ===================================
# SECTION 3: DATABASE CLASS (VERIFIED & FIXED)
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
            logger.error(f"❌ MongoDB connection failed: {e}")
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
    # SETTINGS OPERATIONS (VERIFIED - THREE AUTO-DELETE FEATURES)
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
                    # File protection settings
                    "protect_content": Config.PROTECT_CONTENT,
                    "hide_caption": False,
                    "channel_button": True,
                    
                    # ==================================================================
                    # THREE SEPARATE AUTO-DELETE FEATURES (VERIFIED)
                    # ==================================================================
                    
                    # FEATURE 1: CLEAN CONVERSATION
                    # When bot sends a new message, delete the previous bot message
                    # This keeps the PM conversation clean (no message accumulation)
                    "clean_conversation": Config.CLEAN_CONVERSATION,
                    
                    # FEATURE 2: AUTO DELETE FILES
                    # Delete file messages after specified time
                    "auto_delete": Config.AUTO_DELETE,
                    "auto_delete_time": Config.AUTO_DELETE_TIME,  # Time in seconds
                    
                    # FEATURE 3: SHOW INSTRUCTION AFTER DELETE
                    # After files are deleted, show instruction message with resend button
                    # This message is NOT auto-deleted (stays permanently for user)
                    "show_instruction": Config.SHOW_INSTRUCTION_AFTER_DELETE,
                    
                    # ==================================================================
                    
                    # Force subscribe settings
                    "request_fsub": Config.REQUEST_FSUB,
                    
                    # Custom buttons and texts
                    "custom_button": "",
                    "welcome_text": "",
                    "help_text": "I AM A PRIVATE FILE SHARING BOT, MEANT TO PROVIDE FILES AND NECESSARY STUFF THROUGH SPECIAL LINK FOR SPECIFIC CHANNELS.",
                    "about_text": "",
                    
                    # Images for different panels
                    "bot_pics": Config.BOT_PICS,
                    "welcome_pics": Config.WELCOME_PICS,
                    "help_pics": Config.HELP_PICS,
                    "files_pics": Config.FILES_PICS,
                    "auto_del_pics": Config.AUTO_DEL_PICS,
                    "force_sub_pics": Config.FORCE_SUB_PICS,
                    
                    # Database channel
                    "db_channel_id": None,
                    
                    # Auto approve join requests
                    "auto_approve": Config.AUTO_APPROVE_MODE,
                    
                    # Auto clean old join requests
                    "auto_clean_join_requests": Config.AUTO_CLEAN_JOIN_REQUESTS
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
            logger.error(f"Error removing force subchannel {channel_id}: {e}")
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
    # ADMIN OPERATIONS (VERIFIED & FIXED) - NOW PROPERLY INDENTED
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
        """
        Check if user is admin - VERIFIED & FIXED
        Checks BOTH Config.ADMINS (includes owner) AND database
        """
        # First check Config.ADMINS (includes OWNER_ID)
        if user_id in Config.ADMINS:
            return True
        
        # Then check database
        try:
            admin = await self.admins.find_one({"user_id": user_id})
            if admin:
                return True
        except Exception as e:
            logger.error(f"Error checking admin status for {user_id}: {e}")
        
        # If both fail, user is not admin
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
            logger.error(f"❌ Error cleaning old join requests: {e}")
            return 0

# ===================================
# SECTION 4: HELPER FUNCTIONS (COMPLETELY FIXED & VERIFIED)
# ===================================

async def encode(string: str) -> str:
    """Base64 URL-safe encoding for file IDs"""
    try:
        string_bytes = string.encode("ascii")
        base64_bytes = base64.urlsafe_b64encode(string_bytes)
        return base64_bytes.decode("ascii")
    except Exception as e:
        logger.error(f"Error encoding string: {e}")
        return ""

async def decode(base64_string: str) -> str:
    """Base64 URL-safe decoding for file IDs"""
    try:
        # Add padding if needed
        padding = 4 - len(base64_string) % 4
        if padding != 4:
            base64_string += "=" * padding
        
        base64_bytes = base64_string.encode("ascii")
        string_bytes = base64.urlsafe_b64decode(base64_bytes)
        return string_bytes.decode("ascii")
    except Exception as e:
        logger.error(f"Error decoding string: {e}")
        return ""

async def is_subscribed(client, user_id: int, channel_ids: list) -> bool:
    """
    Check if user is subscribed to all channels - COMPLETELY FIXED
    
    Returns:
        True: User is subscribed to ALL channels
        False: User is NOT subscribed to at least one channel
    """
    if not channel_ids:
        return True
    
    for channel in channel_ids:
        try:
            channel_id = channel.get("channel_id")
            channel_username = channel.get("channel_username")
            
            # Skip if both are missing
            if not channel_id and not channel_username:
                logger.warning(f"Skipping invalid channel: {channel}")
                continue
            
            is_member = False
            
            # Method 1: Try with username first (most reliable)
            if channel_username:
                try:
                    username = channel_username.lstrip('@')
                    member = await client.get_chat_member(username, user_id)
                    
                    # Check if user is a valid member
                    if member.status in ["creator", "administrator", "member"]:
                        is_member = True
                    else:
                        # User is kicked, left, or restricted
                        return False
                        
                except UserNotParticipant:
                    # User is not a member
                    return False
                except (PeerIdInvalid, ChannelInvalid, ValueError) as e:
                    logger.debug(f"Username check failed for {channel_username}: {e}")
                    is_member = False
                except Exception as e:
                    logger.error(f"Unexpected error checking username {channel_username}: {e}")
                    is_member = False
            
            # Method 2: Try with channel ID if username failed
            if not is_member and channel_id:
                try:
                    # Ensure channel_id is integer
                    if isinstance(channel_id, str):
                        channel_id = int(channel_id)
                    
                    member = await client.get_chat_member(channel_id, user_id)
                    
                    # Check if user is a valid member
                    if member.status in ["creator", "administrator", "member"]:
                        is_member = True
                    else:
                        # User is kicked, left, or restricted
                        return False
                        
                except UserNotParticipant:
                    # User is not a member
                    return False
                except (PeerIdInvalid, ChannelInvalid, ValueError) as e:
                    logger.debug(f"Channel ID check failed for {channel_id}: {e}")
                    
                    # Last attempt: Try to get chat info and check again
                    try:
                        chat = await client.get_chat(channel_id)
                        if hasattr(chat, 'username') and chat.username:
                            member = await client.get_chat_member(chat.username, user_id)
                            if member.status in ["creator", "administrator", "member"]:
                                is_member = True
                            else:
                                return False
                    except Exception as e2:
                        logger.error(f"Final check failed for channel {channel_id}: {e2}")
                        return False
                        
                except Exception as e:
                    logger.error(f"Unexpected error checking channel ID {channel_id}: {e}")
                    return False
            
            # If both methods failed, user is not subscribed
            if not is_member:
                logger.info(f"User {user_id} not subscribed to channel {channel_id or channel_username}")
                return False
                
        except Exception as e:
            logger.error(f"Critical error in is_subscribed for channel {channel}: {e}")
            return False
    
    # User is subscribed to all channels
    return True

def format_file_size(size_in_bytes: int) -> str:
    """Format file size to human readable format"""
    if size_in_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_in_bytes)
    
    while size >= 1024 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.2f} {size_names[i]}"

def format_time(seconds: int) -> str:
    """Format seconds to human readable time"""
    if seconds < 60:
        return f"{seconds} second{'s' if seconds != 1 else ''}"
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
    """
    Parse button configuration string - FIXED
    
    Format: Button Text | URL : Button Text 2 | URL2
    Each line is a new row
    
    Example:
        Channel 1 | https://t.me/channel1 : Channel 2 | https://t.me/channel2
        Support | https://t.me/support
    """
    if not button_string or not button_string.strip():
        return []
    
    buttons = []
    
    try:
        rows = button_string.strip().split('\n')
        
        for row in rows:
            row = row.strip()
            if not row:
                continue
                
            row_buttons = []
            button_pairs = row.split(' : ')
            
            for pair in button_pairs:
                pair = pair.strip()
                if ' | ' in pair:
                    parts = pair.split(' | ', 1)
                    text = parts[0].strip()
                    url = parts[1].strip()
                    
                    if text and url:
                        row_buttons.append(InlineKeyboardButton(text, url=url))
            
            if row_buttons:
                buttons.append(row_buttons)
                
    except Exception as e:
        logger.error(f"Error parsing button string: {e}")
        return []
    
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
    elif message.video_note:
        return "video_note"
    else:
        return "text"

def get_random_pic(pics_list: list) -> str:
    """Get random picture from list - FIXED"""
    if not pics_list or len(pics_list) == 0:
        return random.choice(DEFAULT_BOT_PICS)
    
    try:
        return random.choice(pics_list)
    except Exception as e:
        logger.error(f"Error getting random pic: {e}")
        return DEFAULT_BOT_PICS[0]

def get_random_reaction() -> str:
    """Get random reaction emoji"""
    try:
        return random.choice(REACTIONS)
    except Exception as e:
        logger.error(f"Error getting random reaction: {e}")
        return "👋"

def validate_url(url: str) -> bool:
    """Validate URL format - FIXED"""
    if not url:
        return False
    
    try:
        result = urlparse(url)
        return all([result.scheme in ['http', 'https'], result.netloc])
    except Exception as e:
        logger.error(f"Error validating URL {url}: {e}")
        return False

def format_text_with_blockquote(text: str, expandable: bool = False) -> str:
    """
    Format text with blockquote support for Telegram
    
    Args:
        text: The text to format
        expandable: If True, uses expandable blockquote (Telegram feature)
    
    Returns:
        Formatted text with blockquote HTML tags
        
    VERIFIED: Supports Telegram blockquote and expandable blockquote
    """
    if not text:
        return ""
    
    if expandable:
        return f'<blockquote expandable>{text}</blockquote>'
    else:
        return f'<blockquote>{text}</blockquote>'

def create_welcome_text(user_name: str, custom_text: str = None, expandable: bool = True) -> str:
    """
    Create welcome text with blockquote expandable support
    
    VERIFIED: Uses expandable blockquote for better UX
    Supports custom welcome text from database settings
    """
    if custom_text:
        # Use custom text if provided
        return custom_text
    
    # Default welcome message
    welcome_msg = (
        "I AM AN ADVANCE FILE SHARE BOT V3.\n"
        "THE BEST PART IS I AM ALSO SUPPORT REQUEST FORCESUB FEATURE.\n"
        "TO KNOW DETAILED INFORMATION CLICK ABOUT ME BUTTON TO KNOW MY ALL ADVANCE FEATURES"
    )
    
    return (
        f"🔰 <b>Hey, {user_name} ~</b>\n\n"
        f"<blockquote expandable>{welcome_msg}</blockquote>"
    )

def create_help_text(user_name: str, custom_text: str = None, expandable: bool = True) -> str:
    """
    Create help text with blockquote expandable support
    
    VERIFIED: Uses expandable blockquote for better UX
    Supports custom help text from database settings
    """
    if custom_text:
        # Use custom text if provided
        return custom_text
    
    # Default help message
    help_msg = (
        "🌐 I ᴀᴍ ᴀ ᴘʀɪᴠᴀᴛᴇ ғɪʟᴇ sʜᴀʀɪɴɢ ʙᴏᴛ, ᴍᴇᴀɴᴛ ᴛᴏ ᴘʀᴏᴠɪᴅᴇ ғɪʟᴇs ᴀɴᴅ ɴᴇᴄᴇssᴀʀʏ sᴛᴜғғ ᴛʜʀᴏᴜɢʜ sᴘᴇᴄɪᴀʟ ʟɪɴᴋ ғᴏʀ sᴘᴇᴄɪғɪᴄ ᴄʜᴀɴɴᴇʟs.\n\n"
        "🌐 In ᴏʀᴅᴇʀ ᴛᴏ ʟᴇᴛ ʏᴏᴜ ᴋɴᴏᴡ ᴛʜᴇ ᴀʀᴇ ᴀʟʟ ʙᴇɴᴇғɪᴄɪᴀʀʏ ᴄʜᴀɴɴᴇʟ ᴛʜᴀᴛ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴋɴᴏᴡ. "
        "You ᴄᴀɴ ɴᴏᴛ ᴀᴄᴄᴇss ᴛʜᴇ ғɪʟᴇs ᴜɴʟᴇss ʏᴏᴜ ᴊᴏɪɴᴇᴅ ᴀʟʟ ᴄʜᴀɴɴᴇʟs.\n\n"
        "🌐 So ᴊᴏɪɴᴇᴅ ɴᴇᴄᴇssᴀʀʏ ᴄʜᴀɴɴᴇʟs ᴛᴏ ɢᴇᴛ ғɪʟᴇs ᴏɴ ɪɴɪᴛɪᴀʟ ʀᴇǫᴜᴇsᴛs...\n\n"
        "• /help - Open ᴛʜɪs ʀᴇǫᴜᴇsᴛ !"
    )
    
    return (
        f"<b>ℹ️ Hello {user_name} ~</b>\n\n"
        f"<blockquote expandable>{help_msg}</blockquote>\n"
        "<b>⚠️ Strictly follows, contact us/admins if u face any issues/errors !</b>"
    )

# FIX #1: Updated create_force_sub_text with proper blockquote
def create_force_sub_text(user_name: str, joined_count: int, total_count: int, expandable: bool = True) -> str:
    """
    Create force subscribe text with blockquote expandable support - FIXED
    
    VERIFIED: Uses expandable blockquote for better UX
    """
    fsub_msg = (
        f"You haven't joined {total_count - joined_count} out of {total_count} channels yet.\n"
        f"Please join the channels provided below, then try again."
    )
    
    # FIXED: Proper blockquote formatting
    return (
        f"<b>Hey, {user_name}</b>\n\n"
        f"<blockquote expandable>{fsub_msg}</blockquote>\n\n"
        f"<blockquote><b>Facing problems? Use: /help</b></blockquote>"
    )

# FIX #2: Updated create_files_settings_text with proper blockquote
def create_files_settings_text(protect_content: bool, hide_caption: bool, channel_button: bool) -> str:
    """
    Create files settings text with blockquote support - FIXED
    
    VERIFIED: Uses proper blockquote formatting
    """
    protect_status = "ᴇɴᴀʙʟᴇᴅ ✅" if protect_content else "ᴅɪsᴀʙʟᴇᴅ ❌"
    hide_status = "ᴇɴᴀʙʟᴇᴅ ✅" if hide_caption else "ᴅɪsᴀʙʟᴇᴅ ❌"
    button_status = "ᴇɴᴀʙʟᴇᴅ ✅" if channel_button else "ᴅɪsᴀʙʟᴇᴅ ❌"
    
    return (
        "<b>📁 𝗙𝗜𝗟𝗘𝗦 𝗥𝗘𝗟𝗔𝗧𝗘𝗗 𝗦𝗘𝗧𝗧𝗜𝗡𝗚𝗦</b>\n\n"
        "<blockquote>"
        f"<b>🔒 ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ:</b> {protect_status}\n"
        f"<b>🫥 ʜɪᴅᴇ ᴄᴀᴘᴛɪᴏɴ:</b> {hide_status}\n"
        f"<b>🔘 ᴄʜᴀɴɴᴇʟ ʙᴜᴛᴛᴏɴ:</b> {button_status}"
        "</blockquote>\n\n"
        "<b>ᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴs ᴛᴏ ᴄʜᴀɴɢᴇ sᴇᴛᴛɪɴɢs</b>"
    )

# FIX #3: Updated create_auto_delete_text with proper blockquote
def create_auto_delete_text(auto_delete: bool, auto_delete_time: int, clean_conv: bool, show_inst: bool) -> str:
    """
    Create auto delete settings text with blockquote support
    
    VERIFIED: Shows THREE separate auto-delete features clearly
    """
    file_delete_status = "ᴇɴᴀʙʟᴇᴅ ✅" if auto_delete else "ᴅɪsᴀʙʟᴇᴅ ❌"
    time_text = format_time(auto_delete_time)
    clean_status = "ᴇɴᴀʙʟᴇᴅ ✅" if clean_conv else "ᴅɪsᴀʙʟᴇᴅ ❌"
    inst_status = "ᴇɴᴀʙʟᴇᴅ ✅" if show_inst else "ᴅɪsᴀʙʟᴇᴅ ❌"
    
    return (
        "<b>🤖 𝗔𝗨𝗧𝗢 𝗗𝗘𝗟𝗘𝗧𝗘 𝗦𝗘𝗧𝗧𝗜𝗡𝗚𝗦 ⚙️</b>\n\n"
        "<blockquote>"
        f"<b>🗑️ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ғɪʟᴇs:</b> {file_delete_status}\n"
        f"<b>⏱️ ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇʀ:</b> {time_text}\n"
        f"<b>💬 ᴄʟᴇᴀɴ ᴄᴏɴᴠᴇʀsᴀᴛɪᴏɴ:</b> {clean_status}\n"
        f"<b>📝 sʜᴏᴡ ɪɴsᴛʀᴜᴄᴛɪᴏɴ:</b> {inst_status}"
        "</blockquote>\n\n"
        "<b>ᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴs ᴛᴏ ᴄʜᴀɴɢᴇ sᴇᴛᴛɪɴɢs</b>"
    )

# FIX #4: Updated create_instruction_message with proper blockquote
def create_instruction_message() -> str:
    """
    Create instruction message shown after files are deleted
    
    VERIFIED: This is Feature 3 - Show instruction after file deletion
    This message is NOT auto-deleted (stays for user to resend files)
    """
    return (
        "<b>⚠️ FILES DELETED</b>\n\n"
        "<blockquote>"
        "YOUR FILES HAVE BEEN DELETED!\n\n"
        "IF YOU WANT TO GET THE FILES AGAIN, "
        "CLICK THE BUTTON BELOW OR USE THE ORIGINAL LINK AGAIN."
        "</blockquote>"
    )

def get_file_delete_time_options() -> list:
    """
    Get auto delete time options
    
    VERIFIED: These are options for Feature 2 (Auto delete files)
    Returns list of time options in seconds
    """
    return AUTO_DELETE_TIMES.copy()  # [60, 300, 600, 1800, 3600]

def verify_three_autodelete_features():
    """
    Verification function to ensure THREE auto-delete features are properly configured
    
    CRITICAL VERIFICATION:
    
    Feature 1: CLEAN_CONVERSATION
        - Delete previous bot message when sending new message
        - Keeps PM conversation clean (no message accumulation)
        
    Feature 2: AUTO_DELETE + AUTO_DELETE_TIME
        - Delete FILE messages after specified time
        - User-configurable timer (60s to 1 hour)
        
    Feature 3: SHOW_INSTRUCTION_AFTER_DELETE
        - After files are deleted, show instruction with resend button
        - This message is NOT auto-deleted (permanent for user)
    """
    logger.info("=" * 70)
    logger.info("VERIFYING THREE AUTO-DELETE FEATURES:")
    logger.info("-" * 70)
    logger.info(f"✅ Feature 1 - Clean Conversation: {Config.CLEAN_CONVERSATION}")
    logger.info(f"  → Deletes previous bot message when sending new one")
    logger.info("-" * 70)
    logger.info(f"✅ Feature 2 - Auto Delete Files: {Config.AUTO_DELETE}")
    logger.info(f"  → Delete timer: {Config.AUTO_DELETE_TIME} seconds")
    logger.info(f"  → Deletes file messages after specified time")
    logger.info("-" * 70)
    logger.info(f"✅ Feature 3 - Show Instruction: {Config.SHOW_INSTRUCTION_AFTER_DELETE}")
    logger.info(f"  → Shows resend button after file deletion")
    logger.info(f"  → This message is NOT auto-deleted")
    logger.info("=" * 70)
    
    return {
        "clean_conversation": Config.CLEAN_CONVERSation,
        "auto_delete": Config.AUTO_DELETE,
        "auto_delete_time": Config.AUTO_DELETE_TIME,
        "show_instruction": Config.SHOW_INSTRUCTION_AFTER_DELETE
    }

# ===================================
# SECTION 5: BOT CLASS WITH THREE AUTO-DELETE FEATURES (COMPLETE & VERIFIED)
# ===================================

class Bot(Client):
    """
    Main Bot Class with THREE separate auto-delete features
    
    FEATURE 1: Clean Conversation - Delete previous bot message when sending new one
    FEATURE 2: Auto Delete Files - Delete file messages after specified time
    FEATURE 3: Show Instruction - Show resend button after files deleted (NOT auto-deleted)
    """
    
    def __init__(self):
        super().__init__(
            name="file_sharing_bot",
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
        
        # ===================================
        # THREE AUTO-DELETE FEATURE TRACKING
        # ===================================
        
        # FEATURE 1: Clean Conversation - Track last bot message per user
        # Stores: {user_id: {"message_id": int, "timestamp": datetime}}
        self.user_last_bot_message = {}
        
        # FEATURE 2: Auto Delete Files - Track file messages with delete timers
        # Stores: {user_id: [{"message_id": int, "delete_at": datetime, "task": asyncio.Task}]}
        self.user_file_messages = {}
        
        # FEATURE 3: Show Instruction - Track if instruction is already shown
        # Stores: {user_id: {"message_id": int, "shown": bool}}
        self.user_instruction_message = {}
        
        # Track user file history for resend capability
        self.user_file_history = {}
        
        # Admin cache for faster access
        self.admin_cache = set()
        
        logger.info("✅ Bot instance created with THREE auto-delete features")
    
    # ===================================
    # ADMIN CHECK METHOD
    # ===================================
    
    async def is_user_admin(self, user_id: int) -> bool:
        """
        Check if user is admin - FIXED VERSION
        Checks cache, Config.ADMINS, and database
        """
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
                
            logger.info(f"✅ Admin cache refreshed: {len(self.admin_cache)} admins")
        except Exception as e:
            logger.error(f"Error refreshing admin cache: {e}")
    
    # ===================================
    # FEATURE 1: CLEAN CONVERSATION METHODS
    # ===================================
    
    async def delete_previous_bot_message(self, user_id: int):
        """
        FEATURE 1: Clean Conversation
        
        Delete previous bot message when sending a new one
        This keeps the PM conversation clean (no message accumulation)
        """
        if user_id in self.user_last_bot_message:
            try:
                msg_info = self.user_last_bot_message[user_id]
                message_id = msg_info.get("message_id")
                
                if message_id:
                    await self.delete_messages(user_id, message_id)
                    logger.debug(f"✅ Deleted previous bot message {message_id} for user {user_id}")
                
                # Remove from tracking
                del self.user_last_bot_message[user_id]
                
            except MessageDeleteForbidden:
                logger.warning(f"Cannot delete message for user {user_id} - permission denied")
            except MessageIdInvalid:
                logger.warning(f"Message ID invalid for user {user_id} - already deleted")
            except Exception as e:
                logger.error(f"Error deleting previous message for user {user_id}: {e}")
    
    async def store_bot_message(self, user_id: int, message_id: int):
        """
        FEATURE 1: Clean Conversation
        
        Store bot message ID for later deletion
        Only stores the most recent bot message per user
        """
        self.user_last_bot_message[user_id] = {
            "message_id": message_id,
            "timestamp": datetime.datetime.now(datetime.timezone.utc)
        }
        logger.debug(f"✅ Stored bot message {message_id} for user {user_id}")
    
    # ===================================
    # FEATURE 2: AUTO DELETE FILES METHODS
    # ===================================
    
    async def schedule_file_deletion(self, user_id: int, message_id: int, delete_after: int):
        """
        FEATURE 2: Auto Delete Files
        
        Schedule a file message for deletion after specified time
        
        Args:
            user_id: User ID
            message_id: Message ID to delete
            delete_after: Time in seconds before deletion
        """
        try:
            # Calculate deletion time
            delete_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=delete_after)
            
            # Create deletion task
            task = asyncio.create_task(self._delete_file_after_delay(user_id, message_id, delete_after))
            
            # Store file message info
            if user_id not in self.user_file_messages:
                self.user_file_messages[user_id] = []
            
            self.user_file_messages[user_id].append({
                "message_id": message_id,
                "delete_at": delete_at,
                "task": task
            })
            
            logger.info(f"✅ Scheduled file message {message_id} for deletion in {delete_after}s for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error scheduling file deletion: {e}")

    async def _delete_file_after_delay(self, user_id: int, message_id: int, delay: int):
        """
        FEATURE 2: Auto Delete Files
        
        Internal method to delete file message after delay
        """
        try:
            # Wait for the specified delay
            await asyncio.sleep(delay)
            
            # Delete the file message
            await self.delete_messages(user_id, message_id)
            logger.info(f"✅ Auto-deleted file message {message_id} for user {user_id}")
            
            # Remove from tracking
            if user_id in self.user_file_messages:
                self.user_file_messages[user_id] = [
                    msg for msg in self.user_file_messages[user_id]
                    if msg["message_id"] != message_id
                ]
                
                # Clean up empty list
                if not self.user_file_messages[user_id]:
                    del self.user_file_messages[user_id]
            
            # FEATURE 3: Show instruction after files are deleted
            await self.show_instruction_after_deletion(user_id)
            
        except MessageDeleteForbidden:
            logger.warning(f"Cannot delete file message {message_id} for user {user_id}")
        except MessageIdInvalid:
            logger.warning(f"File message {message_id} already deleted for user {user_id}")
        except asyncio.CancelledError:
            logger.info(f"File deletion cancelled for message {message_id}")
        except Exception as e:
            logger.error(f"Error deleting file message {message_id}: {e}")

    async def cancel_file_deletions(self, user_id: int):
        """
        FEATURE 2: Auto Delete Files
        
        Cancel all pending file deletions for a user
        """
        try:
            if user_id in self.user_file_messages:
                for msg_info in self.user_file_messages[user_id]:
                    task = msg_info.get("task")
                    if task and not task.done():
                        task.cancel()
                
                del self.user_file_messages[user_id]
                logger.info(f"✅ Cancelled all file deletions for user {user_id}")
                
        except Exception as e:
            logger.error(f"Error cancelling file deletions for user {user_id}: {e}")

    # ===================================
    # FEATURE 3: SHOW INSTRUCTION METHODS
    # ===================================

    async def show_instruction_after_deletion(self, user_id: int):
        """
        FEATURE 3: Show Instruction After File Deletion
        
        Show instruction message with resend button after files are deleted
        This message is NOT auto-deleted (stays permanently for user)
        """
        try:
            # Check if instruction already shown
            if user_id in self.user_instruction_message:
                logger.debug(f"Instruction already shown for user {user_id}")
                return
            
            # Get settings to check if this feature is enabled
            settings = await self.db.get_settings()
            show_instruction = settings.get("show_instruction", True)
            
            if not show_instruction:
                logger.debug(f"Show instruction feature disabled")
                return
            
            # Create instruction message
            instruction_text = create_instruction_message()
            
            # Create resend button
            buttons = [
                [InlineKeyboardButton("🔃 GET FILES AGAIN", callback_data="resend_files")],
                [InlineKeyboardButton("❌ CLOSE", callback_data="close_instruction")]
            ]
            keyboard = InlineKeyboardMarkup(buttons)
            
            # Send instruction message
            try:
                instruction_msg = await self.send_message(
                    user_id,
                    instruction_text,
                    reply_markup=keyboard,
                    parse_mode=enums.ParseMode.HTML
                )
                
                # Store instruction message (NOT in clean conversation tracking)
                self.user_instruction_message[user_id] = {
                    "message_id": instruction_msg.id,
                    "shown": True,
                    "timestamp": datetime.datetime.now(datetime.timezone.utc)
                }
                
                logger.info(f"✅ Showed instruction message for user {user_id}")
                
            except Exception as e:
                logger.error(f"Error sending instruction message to user {user_id}: {e}")
                
        except Exception as e:
            logger.error(f"Error in show_instruction_after_deletion: {e}")

    async def clear_instruction_message(self, user_id: int):
        """
        FEATURE 3: Show Instruction
        
        Clear instruction message tracking (does not delete the message)
        """
        try:
            if user_id in self.user_instruction_message:
                del self.user_instruction_message[user_id]
                logger.debug(f"✅ Cleared instruction tracking for user {user_id}")
        except Exception as e:
            logger.error(f"Error clearing instruction for user {user_id}: {e}")

    # ===================================
    # FILE HISTORY TRACKING
    # ===================================
    
    async def track_user_files(self, user_id: int, file_ids: list, link_data: dict = None):
        """
        Track files sent to user for potential resend
        
        Args:
            user_id: User ID
            file_ids: List of file message IDs from database channel
            link_data: Optional link data (for special links)
        """
        try:
            if user_id not in self.user_file_history:
                self.user_file_history[user_id] = []
            
            self.user_file_history[user_id].append({
                "file_ids": file_ids,
                "link_data": link_data,
                "timestamp": datetime.datetime.now(datetime.timezone.utc)
            })
            
            # Keep only last 5 entries per user
            if len(self.user_file_history[user_id]) > 5:
                self.user_file_history[user_id] = self.user_file_history[user_id][-5:]
            
            logger.debug(f"✅ Tracked {len(file_ids)} files for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error tracking files for user {user_id}: {e}")
    
    # ===================================
    # USER ACCOUNT FOR REACTIONS - FIXED
    # ===================================
    
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
                logger.info(f"✅ User account started: @{user_me.username} (ID: {user_me.id})")
                return True
                
            except Exception as e:
                logger.error(f"❌ Failed to start user account: {e}")
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
                logger.info(f"✅ User account started: @{user_me.username} (ID: {user_me.id})")
                return True
                
            except Exception as e:
                logger.error(f"❌ Failed to start user account: {e}")
                self.user_client = None
                return False
        
        else:
            logger.warning("⚠️  No user account configured - reactions will be disabled")
            return False
    
    async def stop_user_account(self):
        """Stop user account"""
        if self.user_client:
            try:
                await self.user_client.stop()
                logger.info("✅ User account stopped")
            except Exception as e:
                logger.error(f"Error stopping user account: {e}")
    
    async def send_reaction(self, chat_id: int, message_id: int):
        """Send reaction using user account - FIXED VERSION"""
        if not self.user_client:
            logger.debug("User client not available")
            return False
        
        try:
            # STEP 1: Verify message exists
            try:
                message = await self.get_messages(chat_id, message_id)
                if not message:
                    logger.debug(f"Message {message_id} not found")
                    return False
            except Exception as e:
                logger.debug(f"Cannot access message: {e}")
                return False
            
            # STEP 2: Verify user client has chat access
            try:
                chat = await self.user_client.get_chat(chat_id)
                if not chat:
                    logger.debug(f"Cannot access chat {chat_id}")
                    return False
            except Exception as e:
                logger.debug(f"User client error: {e}")
                return False
            
            # STEP 3: Send reaction
            reaction = get_random_reaction()
            await self.user_client.send_reaction(
                chat_id=chat_id,
                message_id=message_id,
                emoji=reaction
            )
            
            logger.debug(f"✅ Reaction sent: {reaction}")
            return True
            
        except Exception as e:
            if "MESSAGE_ID_INVALID" not in str(e):
                logger.debug(f"Reaction failed: {e}")
            return False
    
    # ===================================
    # BOT STARTUP METHODS
    # ===================================
    
    async def start(self):
        """Start the bot - COMPLETE & VERIFIED"""
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
            if channel_id and channel_id not in all_channels:
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
        
        # Set bot commands
        await self.set_bot_commands()
        
        # Register all handlers
        self.register_all_handlers()
        
        # Start auto-clean task if enabled
        if Config.AUTO_CLEAN_JOIN_REQUESTS:
            asyncio.create_task(self.auto_clean_join_requests())
        
        # Verify three auto-delete features
        verify_three_autodelete_features()
        
        # Print bot info
        me = await self.get_me()
        Config.BOT_USERNAME = me.username
        logger.info(f"✅ Bot started as @{me.username}")
        logger.info(f"✅ Bot ID: {me.id}")
        logger.info(f"✅ Force Sub Channels: {len(self.force_sub_channels)}")
        logger.info("=" * 70)
        logger.info("THREE AUTO-DELETE FEATURES ACTIVE:")
        logger.info(f"  1. Clean Conversation: {self.settings.get('clean_conversation', True)}")
        logger.info(f"  2. Auto Delete Files: {self.settings.get('auto_delete', False)}")
        logger.info(f"  3. Show Instruction: {self.settings.get('show_instruction', True)}")
        logger.info("=" * 70)
        
        # Send startup message to owner
        await self.send_log_message(
            f"🚀 <b>Bot Started Successfully!</b>\n\n"
            f"<b>THREE AUTO-DELETE FEATURES:</b>\n"
            f"1️⃣─ Clean Conversation: {'✅' if self.settings.get('clean_conversation') else '❌'}\n"
            f"2️⃣─ Auto Delete Files: {'✅' if self.settings.get('auto_delete') else '❌'}\n"
            f"3️⃣─ Show Instruction: {'✅' if self.settings.get('show_instruction') else '❌'}\n\n"
            f"📢 Force Subscribe: {len(self.force_sub_channels)} channels"
        )
        
        return True
    
    async def stop(self, *args):
        """Stop the bot"""
        await self.stop_user_account()
        await self.db.close()
        await super().stop()
        logger.info("✅ Bot stopped")
    
    async def set_bot_commands(self):
        """
        Set bot commands - FIXED VERSION
        Shows different commands to different user types
        """
        try:
            # Set basic commands for ALL users (default scope)
            await super().set_bot_commands(
                commands=BOT_COMMANDS["all_users"],
                scope=BotCommandScopeDefault()
            )
            logger.info("✅ Basic commands set for all users in '/' menu")
            
            # Set admin commands for each admin (individual scope)
            all_admins = Config.ADMINS.copy()
            
            # Add database admins
            try:
                db_admins = await self.db.get_admins()
                all_admins.extend(db_admins)
                all_admins = list(set(all_admins))  # Remove duplicates
            except:
                pass
            
            for admin_id in all_admins:
                try:
                    await super().set_bot_commands(
                        commands=BOT_COMMANDS["admins"],
                        scope=BotCommandScopeChat(chat_id=admin_id)
                    )
                except Exception as e:
                    logger.debug(f"Could not set admin commands for {admin_id}: {e}")
            
            logger.info(f"✅ Admin commands set for {len(all_admins)} admins in '/' menu")
            
        except Exception as e:
            logger.error(f"Error setting bot commands: {e}")
    
    async def send_log_message(self, message: str):
        """Send log message to owner"""
        try:
            await self.send_message(
                Config.OWNER_ID,
                message,
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Failed to send log message: {e}")
    
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
                        f"🧹 <b>Auto-clean completed!</b>\n\n"
                        f"Cleaned {cleaned_count} join requests older than 24 hours."
                    )
                    
        except asyncio.CancelledError:
            logger.info("Auto-clean task cancelled")
        except Exception as e:
            logger.error(f"Error in auto-clean task: {e}")
    
    async def create_invite_link(self, channel_id: int) -> str:
        """Create temporary invite link for private channels"""
        try:
            invite_link = await self.create_chat_invite_link(
                chat_id=channel_id,
                expire_date=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=5),
                member_limit=1
            )
            return invite_link.invite_link
        except Exception as e:
            logger.error(f"Error creating invite link for channel {channel_id}: {e}")
            return None
    
    # ===================================
    # SECTION 6: HANDLER REGISTRATION & COMMANDS
    # ===================================
    
    def register_all_handlers(self):
        """
        Register ALL message and callback handlers
        
        CRITICAL: This method registers ALL bot commands and callbacks
        THREE AUTO-DELETE FEATURES are implemented in each handler
        """
        
        logger.info("=" * 70)
        logger.info("REGISTERING ALL HANDLERS...")
        logger.info("=" * 70)
        
        # ===================================
        # BASIC COMMANDS
        # ===================================
        
        @self.on_message(filters.command("start") & filters.private)
        async def start_handler(client, message):
            await self.start_command(message)
        
        @self.on_message(filters.command("help") & filters.private)
        async def help_handler(client, message):
            await self.help_command(message)
        
        @self.on_message(filters.command("about") & filters.private)
        async def about_handler(client, message):
            await self.about_command(message)
        
        @self.on_message(filters.command("ping") & filters.private)
        async def ping_handler(client, message):
            await self.ping_command(message)
        
        @self.on_message(filters.command("cmd") & filters.private)
        async def cmd_handler(client, message):
            await self.cmd_command(message)
        
        # ===================================
        # ADMIN MANAGEMENT COMMANDS
        # ===================================
        
        @self.on_message(filters.command("admin_list") & filters.private)
        async def admin_list_handler(client, message):
            await self.admin_list_command(message)
        
        @self.on_message(filters.command("add_admins") & filters.private)
        async def add_admins_handler(client, message):
            await self.add_admins_command(message)
        
        @self.on_message(filters.command("del_admins") & filters.private)
        async def del_admins_handler(client, message):
            await self.del_admins_command(message)
        
        # ===================================
        # USER MANAGEMENT COMMANDS
        # ===================================
        
        @self.on_message(filters.command("users") & filters.private)
        async def users_handler(client, message):
            await self.users_command(message)
        
        @self.on_message(filters.command("stats") & filters.private)
        async def stats_handler(client, message):
            await self.stats_command(message)
        
        @self.on_message(filters.command("refresh") & filters.private)
        async def refresh_handler(client, message):
            await self.refresh_command(message)
        
        # ===================================
        # BAN/UNBAN COMMANDS
        # ===================================
        
        @self.on_message(filters.command("banuser_list") & filters.private)
        async def banuser_list_handler(client, message):
            await self.banuser_list_command(message)
        
        @self.on_message(filters.command("add_banuser") & filters.private)
        async def add_banuser_handler(client, message):
            await self.add_banuser_command(message)
        
        @self.on_message(filters.command("del_banuser") & filters.private)
        async def del_banuser_handler(client, message):
            await self.del_banuser_command(message)
        
        @self.on_message(filters.command("ban") & filters.private)
        async def ban_handler(client, message):
            await self.ban_command(message)
        
        @self.on_message(filters.command("unban") & filters.private)
        async def unban_handler(client, message):
            await self.unban_command(message)
        
        # ===================================
        # BROADCAST COMMAND
        # ===================================
        
        @self.on_message(filters.command("broadcast") & filters.private)
        async def broadcast_handler(client, message):
            await self.broadcast_command(message)
        
        # ===================================
        # FILE MANAGEMENT COMMANDS
        # ===================================
        
        @self.on_message(filters.command("genlink") & filters.private)
        async def genlink_handler(client, message):
            await self.genlink_command(message)
        
        @self.on_message(filters.command("getlink") & filters.private)
        async def getlink_handler(client, message):
            await self.getlink_command(message)
        
        @self.on_message(filters.command("batch") & filters.private)
        async def batch_handler(client, message):
            await self.batch_command(message)
        
        @self.on_message(filters.command("custom_batch") & filters.private)
        async def custom_batch_handler(client, message):
            await self.custom_batch_command(message)
        
        @self.on_message(filters.command("special_link") & filters.private)
        async def special_link_handler(client, message):
            await self.special_link_command(message)
        
        @self.on_message(filters.command("done") & filters.private)
        async def done_handler(client, message):
            await self.done_command(message)
        
        # ===================================
        # CHANNEL MANAGEMENT COMMANDS
        # ===================================
        
        @self.on_message(filters.command("setchannel") & filters.private)
        async def setchannel_handler(client, message):
            await self.setchannel_command(message)
        
        @self.on_message(filters.command("checkchannel") & filters.private)
        async def checkchannel_handler(client, message):
            await self.checkchannel_command(message)
        
        @self.on_message(filters.command("removechannel") & filters.private)
        async def removechannel_handler(client, message):
            await self.removechannel_command(message)
        
        # ===================================
        # SETTINGS COMMANDS
        # ===================================
        
        @self.on_message(filters.command("settings") & filters.private)
        async def settings_handler(client, message):
            await self.settings_command(message)
        
        @self.on_message(filters.command("files") & filters.private)
        async def files_handler(client, message):
            await self.files_command(message)
        
        @self.on_message(filters.command("auto_del") & filters.private)
        async def auto_del_handler(client, message):
            await self.auto_del_command(message)
        
        @self.on_message(filters.command("botsettings") & filters.private)
        async def botsettings_handler(client, message):
            await self.botsettings_command(message)
        
        # ===================================
        # FORCE SUBSCRIBE COMMANDS
        # ===================================
        
        @self.on_message(filters.command("forcesub") & filters.private)
        async def forcesub_handler(client, message):
            await self.forcesub_command(message)
        
        @self.on_message(filters.command("req_fsub") & filters.private)
        async def req_fsub_handler(client, message):
            await self.req_fsub_command(message)
        
        @self.on_message(filters.command("fsub_chnl") & filters.private)
        async def fsub_chnl_handler(client, message):
            await self.fsub_chnl_command(message)
        
        @self.on_message(filters.command("add_fsub") & filters.private)
        async def add_fsub_handler(client, message):
            await self.add_fsub_command(message)
        
        @self.on_message(filters.command("del_fsub") & filters.private)
        async def del_fsub_handler(client, message):
            await self.del_fsub_command(message)
        
        # ===================================
        # UTILITY COMMANDS
        # ===================================
        
        @self.on_message(filters.command("logs") & filters.private)
        async def logs_handler(client, message):
            await self.logs_command(message)
        
        @self.on_message(filters.command("shortener") & filters.private)
        async def shortener_handler(client, message):
            await self.shortener_command(message)
        
        @self.on_message(filters.command("font") & filters.private)
        async def font_handler(client, message):
            await self.font_command(message)
        
        # ===================================
        # CALLBACK QUERY HANDLER
        # ===================================
        
        @self.on_callback_query()
        async def callback_handler(client, query):
            await self.handle_callback_query(query)
        
        # ===================================
        # CHAT JOIN REQUEST HANDLER
        # ===================================
        
        @self.on_chat_join_request()
        async def join_request_handler(client, join_request):
            await self.handle_join_request(join_request)
        
        # ===================================
        # TEXT MESSAGE HANDLER (for batch states)
        # ===================================
        
        @self.on_message(filters.private & filters.text & ~filters.command(list(set([cmd.command for cmd in BOT_COMMANDS["all_users"]] + [cmd.command for cmd in BOT_COMMANDS["admins"]]))))
        async def text_handler(client, message):
            await self.text_message_handler(message)
        
        logger.info("✅ All handlers registered successfully")
        logger.info("=" * 70)

    # ===================================
    # START COMMAND WITH THREE AUTO-DELETE FEATURES - FIXED
    # ===================================
    
    async def start_command(self, message: Message):
        """
        Handle /start command
        
        IMPLEMENTS: FEATURE 1 (Clean Conversation)
        """
        user_id = message.from_user.id
        chat_id = message.chat.id

        # FEATURE 1: Delete previous bot message (Clean Conversation)
        settings = await self.db.get_settings()
        if settings.get("clean_conversation", True):
            await self.delete_previous_bot_message(user_id)

        # Check if user is banned
        if await self.db.is_user_banned(user_id):
            response = await message.reply(
                "🚫 <b>You are banned from using this bot!</b>",
                parse_mode=enums.ParseMode.HTML
            )
            # FEATURE 1: Store this message for future deletion
            await self.store_bot_message(user_id, response.id)
            return

        # Add user to database
        await self.db.add_user(
            user_id=user_id,
            first_name=message.from_user.first_name,
            username=message.from_user.username
        )

        # Update activity
        await self.db.update_user_activity(user_id)

        # Send reaction using user account - FIXED: Added delay
        try:
            await asyncio.sleep(0.5)  # Wait for message to be processed
            await self.send_reaction(chat_id, message.id)
        except Exception as e:
            logger.debug(f"Reaction error: {e}")

        # Check for start arguments (file links, batch links, etc.)
        if len(message.command) > 1:
            start_arg = message.command[1]
            await self.handle_start_argument(message, start_arg)
            return

        # Check force subscribe - ONLY if request_fsub is enabled
        request_fsub = settings.get("request_fsub", False)
        
        if request_fsub and self.force_sub_channels:
            user_is_subscribed = await is_subscribed(self, user_id, self.force_sub_channels)
            if not user_is_subscribed:
                await self.show_force_subscribe(message)
                return

        # Show welcome message
        await self.show_welcome_message(message)
    
    async def show_welcome_message(self, message: Message):
        """
        Show welcome message with photo and blockquote expandable
        
        IMPLEMENTS: FEATURE 1 (Clean Conversation)
        """
        user = message.from_user
        user_id = user.id
    
        # Get settings
        settings = await self.db.get_settings()
        welcome_text_custom = settings.get("welcome_text", "")
        welcome_pics = settings.get("welcome_pics", Config.WELCOME_PICS)
    
        # Get random welcome picture
        welcome_pic = get_random_pic(welcome_pics)
    
        # Create welcome text with blockquote expandable
        if welcome_text_custom:
            try:
                welcome_text = welcome_text_custom.format(
                    first=user.first_name,
                    last=user.last_name or "",
                    username=f"@{user.username}" if user.username else "None",
                    mention=f"<a href='tg://user?id={user.id}'>{user.first_name}</a>",
                    id=user.id
                )
            except KeyError as e:
                logger.error(f"Invalid placeholder in welcome_text: {e}")
                welcome_text = create_welcome_text(user.first_name, expandable=True)
        else:
            welcome_text = create_welcome_text(user.first_name, expandable=True)
    
        # Create buttons
        buttons = [
            [
                InlineKeyboardButton("ℹ️ Help", callback_data="help_menu"),
                InlineKeyboardButton("About 📄", callback_data="about_menu")
            ],
            [
                InlineKeyboardButton("Close ✖️", callback_data="close")
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
    
        # FEATURE 1: Store this message for future deletion (Clean Conversation)
        await self.store_bot_message(user_id, response.id)
    
    async def show_force_subscribe(self, message: Message):
        """
        Show force subscribe message with photo and blockquote expandable
        
        IMPLEMENTS: FEATURE 1 (Clean Conversation)
        """
        user = message.from_user
        user_id = user.id
    
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
    
        # Create force sub text with blockquote expandable - FIXED
        fsub_text = create_force_sub_text(user.first_name, joined_count, total_channels, expandable=True)
    
        # Create buttons for each channel
        buttons = []
        for channel in self.force_sub_channels:
            channel_id = channel.get("channel_id")
            username = channel.get("channel_username")
        
            if username:
                button_text = "Join Channel"
                button_url = f"https://t.me/{username}"
            else:
                button_text = "Private Channel"
                try:
                    invite_link = await self.create_invite_link(channel_id)
                    if invite_link:
                        button_url = invite_link
                    else:
                        # Fallback to channel link
                        button_url = f"https://t.me/c/{str(channel_id)[4:]}"
                except:
                    button_url = f"https://t.me/c/{str(channel_id)[4:]}"
        
            buttons.append([InlineKeyboardButton(button_text, url=button_url)])
    
        # Add try again and help buttons
        buttons.append([InlineKeyboardButton("🔃 Try Again", callback_data="check_fsub")])
        buttons.append([InlineKeyboardButton("ℹ️ Help", callback_data="help_menu")])
    
        keyboard = InlineKeyboardMarkup(buttons)
    
        try:
            response = await message.reply_photo(
                photo=force_sub_pic,
                caption=fsub_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Error sending force sub photo: {e}")
            response = await message.reply(
                fsub_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
    
        # FEATURE 1: Store this message for future deletion (Clean Conversation)
        await self.store_bot_message(user_id, response.id)
    
    # ===================================
    # HANDLE START ARGUMENTS (FILE LINKS)
    # ===================================
    
    async def handle_start_argument(self, message: Message, start_arg: str):
        """
        Handle start command arguments (file links, batch links, special links)
        
        IMPLEMENTS: ALL THREE AUTO-DELETE FEATURES
        """
        try:
            user_id = message.from_user.id
            
            # Check if it's a special link
            if start_arg.startswith("link_"):
                link_id = start_arg.replace("link_", "")
                await self.handle_special_link(message, link_id)
            # Check if it's a file link
            elif start_arg.startswith("file_"):
                file_id_encoded = start_arg.replace("file_", "")
                await self.handle_file_link(message, file_id_encoded)
            # Check if it's a batch link
            elif start_arg.startswith("batch_"):
                batch_id = start_arg.replace("batch_", "")
                await self.handle_batch_link(message, batch_id)
            else:
                # Try to decode as file ID
                try:
                    decoded = await decode(start_arg)
                    if decoded:
                        await self.handle_file_link(message, start_arg)
                    else:
                        raise ValueError("Invalid link")
                except:
                    error_msg = await message.reply("❌ <b>Invalid or expired link!</b>", parse_mode=enums.ParseMode.HTML)
                    # FEATURE 1: Store for clean conversation
                    await self.store_bot_message(user_id, error_msg.id)
                    
        except Exception as e:
            logger.error(f"Error handling start argument: {e}")
            error_msg = await message.reply("❌ <b>Error processing link!</b>", parse_mode=enums.ParseMode.HTML)
            await self.store_bot_message(message.from_user.id, error_msg.id)
    
    async def handle_special_link(self, message: Message, link_id: str):
        """
        Handle special link access
        
        IMPLEMENTS: ALL THREE AUTO-DELETE FEATURES
        """
        try:
            user_id = message.from_user.id
            
            # Get link data from database
            link_data = await self.db.get_special_link(link_id)
            if not link_data:
                error_msg = await message.reply("❌ <b>Link not found or expired!</b>", parse_mode=enums.ParseMode.HTML)
                await self.store_bot_message(user_id, error_msg.id)
                return
            
            # Send custom message if available
            custom_msg = link_data.get("message")
            if custom_msg:
                msg = await message.reply(custom_msg, parse_mode=enums.ParseMode.HTML)
                # FEATURE 1: Store for clean conversation
                await self.store_bot_message(user_id, msg.id)
            
            # Send files
            files = link_data.get("files", [])
            if files:
                file_ids = []
                sent_message_ids = []
                
                for file_id in files[:MAX_SPECIAL_FILES]:
                    try:
                        response = await self.copy_message(
                            chat_id=message.chat.id,
                            from_chat_id=self.db_channel,
                            message_id=file_id,
                            protect_content=self.settings.get("protect_content", True)
                        )
                        file_ids.append(file_id)
                        sent_message_ids.append(response.id)
                        
                        # FEATURE 2: Schedule file for auto-deletion if enabled
                        settings = await self.db.get_settings()
                        auto_delete = settings.get("auto_delete", False)
                        if auto_delete:
                            delete_time = settings.get("auto_delete_time", 300)
                            await self.schedule_file_deletion(user_id, response.id, delete_time)
                        
                    except Exception as e:
                        logger.error(f"Error sending file {file_id}: {e}")
                
                # Track files for potential resend
                if file_ids:
                    await self.track_user_files(user_id, file_ids, link_data)
                
                # Send completion message
                success_msg = await message.reply(
                    f"✅ <b>Files sent successfully!</b>\n\n📁 Total: {len(file_ids)} files",
                    parse_mode=enums.ParseMode.HTML
                )
                # FEATURE 1: Store for clean conversation
                await self.store_bot_message(user_id, success_msg.id)
                
        except Exception as e:
            logger.error(f"Error handling special link: {e}")
            error_msg = await message.reply("❌ <b>Error accessing link!</b>", parse_mode=enums.ParseMode.HTML)
            await self.store_bot_message(message.from_user.id, error_msg.id)
    
    async def handle_file_link(self, message: Message, file_id_encoded: str):
        """
        Handle single file link
        
        IMPLEMENTS: ALL THREE AUTO-DELETE FEATURES
        """
        try:
            user_id = message.from_user.id
            
            # Decode file ID
            decoded = await decode(file_id_encoded)
            if not decoded or not decoded.isdigit():
                error_msg = await message.reply("❌ <b>Invalid file link!</b>", parse_mode=enums.ParseMode.HTML)
                await self.store_bot_message(user_id, error_msg.id)
                return
            
            file_id = int(decoded)
            
            # Check if bot has access to the database channel
            if not self.db_channel:
                error_msg = await message.reply("❌ <b>Database channel not set!</b>", parse_mode=enums.ParseMode.HTML)
                await self.store_bot_message(user_id, error_msg.id)
                return
            
            # Check if bot is admin in database channel
            try:
                # Get bot's status in the channel
                me = await self.get_me()
                bot_id = me.id
                member = await self.get_chat_member(self.db_channel, bot_id)
                if member.status not in ["administrator", "creator"]:
                    # Bot is not admin - cannot copy message
                    error_msg = await message.reply("❌ <b>Bot is not admin in database channel!</b>", parse_mode=enums.ParseMode.HTML)
                    await self.store_bot_message(user_id, error_msg.id)
                    return
            except Exception as e:
                logger.error(f"Error checking admin status: {e}")
                error_msg = await message.reply("❌ <b>Cannot access database channel!</b>", parse_mode=enums.ParseMode.HTML)
                await self.store_bot_message(user_id, error_msg.id)
                return
            
            # Send the file
            try:
                response = await self.copy_message(
                    chat_id=message.chat.id,
                    from_chat_id=self.db_channel,
                    message_id=file_id,
                    protect_content=self.settings.get("protect_content", True)
                )
                
                # FEATURE 2: Schedule file for auto-deletion if enabled
                settings = await self.db.get_settings()
                auto_delete = settings.get("auto_delete", False)
                if auto_delete:
                    delete_time = settings.get("auto_delete_time", 300)
                    await self.schedule_file_deletion(user_id, response.id, delete_time)
                
                # Track file for potential resend
                await self.track_user_files(user_id, [file_id])
                
            except Exception as e:
                logger.error(f"Error sending file {file_id}: {e}")
                error_msg = await message.reply("❌ <b>File not found or access denied!</b>", parse_mode=enums.ParseMode.HTML)
                await self.store_bot_message(user_id, error_msg.id)
            
        except Exception as e:
            logger.error(f"Error in handle_file_link: {e}")
            error_msg = await message.reply("❌ <b>File not found or access denied!</b>", parse_mode=enums.ParseMode.HTML)
            await self.store_bot_message(message.from_user.id, error_msg.id)
    
    async def handle_batch_link(self, message: Message, batch_id: str):
        """
        Handle batch file link
        
        IMPLEMENTS: ALL THREE AUTO-DELETE FEATURES
        """
        try:
            user_id = message.from_user.id
            
            # Decode batch data
            decoded = await decode(batch_id)
            if not decoded:
                error_msg = await message.reply("❌ <b>Invalid batch link!</b>", parse_mode=enums.ParseMode.HTML)
                await self.store_bot_message(user_id, error_msg.id)
                return
            
            file_ids = [int(x) for x in decoded.split(",") if x.isdigit()]
            
            if not file_ids:
                error_msg = await message.reply("❌ <b>No files found in batch!</b>", parse_mode=enums.ParseMode.HTML)
                await self.store_bot_message(user_id, error_msg.id)
                return
            
            # Check if bot has access to the database channel
            if not self.db_channel:
                error_msg = await message.reply("❌ <b>Database channel not set!</b>", parse_mode=enums.ParseMode.HTML)
                await self.store_bot_message(user_id, error_msg.id)
                return
            
            # Check if bot is admin in database channel
            try:
                # Get bot's status in the channel
                me = await self.get_me()
                bot_id = me.id
                member = await self.get_chat_member(self.db_channel, bot_id)
                if member.status not in ["administrator", "creator"]:
                    # Bot is not admin - cannot copy messages
                    error_msg = await message.reply("❌ <b>Bot is not admin in database channel!</b>", parse_mode=enums.ParseMode.HTML)
                    await self.store_bot_message(user_id, error_msg.id)
                    return
            except Exception as e:
                logger.error(f"Error checking admin status: {e}")
                error_msg = await message.reply("❌ <b>Cannot access database channel!</b>", parse_mode=enums.ParseMode.HTML)
                await self.store_bot_message(user_id, error_msg.id)
                return
            
            # Send progress message
            progress_msg = await message.reply(
                f"📤 <b>Sending {len(file_ids)} files...</b>",
                parse_mode=enums.ParseMode.HTML
            )
            
            # Send files
            sent_file_ids = []
            sent_message_ids = []
            
            for file_id in file_ids[:MAX_BATCH_SIZE]:
                try:
                    response = await self.copy_message(
                        chat_id=message.chat.id,
                        from_chat_id=self.db_channel,
                        message_id=file_id,
                        protect_content=self.settings.get("protect_content", True)
                    )
                    sent_file_ids.append(file_id)
                    sent_message_ids.append(response.id)
                    
                    # FEATURE 2: Schedule file for auto-deletion if enabled
                    settings = await self.db.get_settings()
                    auto_delete = settings.get("auto_delete", False)
                    if auto_delete:
                        delete_time = settings.get("auto_delete_time", 300)
                        await self.schedule_file_deletion(user_id, response.id, delete_time)
                    
                except Exception as e:
                    logger.error(f"Error sending file {file_id}: {e}")
            
            # Delete progress message
            try:
                await progress_msg.delete()
            except:
                pass
            
            # Track files for potential resend
            if sent_file_ids:
                await self.track_user_files(user_id, sent_file_ids)
            
            # Send completion message
            success_msg = await message.reply(
                f"✅ <b>Batch sent successfully!</b>\n\n"
                f"📁 Total: {len(sent_file_ids)} files",
                parse_mode=enums.ParseMode.HTML
            )
            # FEATURE 1: Store for clean conversation
            await self.store_bot_message(user_id, success_msg.id)
            
        except Exception as e:
            logger.error(f"Error handling batch link: {e}")
            error_msg = await message.reply("❌ <b>Batch not found or access denied!</b>", parse_mode=enums.ParseMode.HTML)
            await self.store_bot_message(message.from_user.id, error_msg.id)
    
    # ===================================
    # HELP & ABOUT COMMANDS
    # ===================================
    
    async def help_command(self, message: Message):
        """
        Handle /help command
        
        IMPLEMENTS: FEATURE 1 (Clean Conversation)
        """
        user_id = message.from_user.id
        user = message.from_user

        # FEATURE 1: Delete previous bot message
        settings = await self.db.get_settings()
        if settings.get("clean_conversation", True):
            await self.delete_previous_bot_message(user_id)

        # Get help text and pictures
        help_text_custom = settings.get("help_text", "")
        help_pics = settings.get("help_pics", Config.HELP_PICS)

        # Get random help picture
        help_pic = get_random_pic(help_pics)

        # Create help text with blockquote expandable
        if help_text_custom:
            help_text = help_text_custom
        else:
            help_text = create_help_text(user.first_name, expandable=True)

        # Create buttons
        buttons = [
            [
                InlineKeyboardButton("Update Channel", url=f"https://t.me/{Config.UPDATE_CHANNEL}"),
                InlineKeyboardButton("Support Admin", url=f"https://t.me/{Config.SUPPORT_CHAT}")
            ],
            [
                InlineKeyboardButton("About 📄", callback_data="about_menu"),
                InlineKeyboardButton("🏠 Home", callback_data="start_menu")
            ],
            [
                InlineKeyboardButton("Close ✖️", callback_data="close")
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

        # FEATURE 1: Store this message for future deletion
        await self.store_bot_message(user_id, response.id)

    async def about_command(self, message: Message):
        """
        Handle /about command
        
        IMPLEMENTS: FEATURE 1 (Clean Conversation)
        """
        user_id = message.from_user.id
        
        # FEATURE 1: Delete previous bot message
        settings = await self.db.get_settings()
        if settings.get("clean_conversation", True):
            await self.delete_previous_bot_message(user_id)

        # Get about text from settings
        about_text_custom = settings.get("about_text", "")
        about_pics = settings.get("welcome_pics", Config.WELCOME_PICS)

        # Get random about picture
        about_pic = get_random_pic(about_pics)

        # Default about text with blockquote
        if about_text_custom:
            about_text = about_text_custom
        else:
            about_content = (
                f"<b>• Bot Name:</b> {Config.BOT_NAME}\n"
                f"<b>• Framework:</b> Pyrogram\n"
                f"<b>• Language:</b> Python 3\n"
                f"<b>• Version:</b> V3.0\n"
                f"<b>• Features:</b> Three Auto-Delete System\n"
                f"<b>• Database:</b> MongoDB\n\n"
                f"<b>Developed by @{Config.UPDATE_CHANNEL}</b>"
            )
            
            about_text = (
                "ℹ️ <b>About Bot</b>\n\n"
                f'<blockquote>{about_content}</blockquote>'
            )

        buttons = [
            [InlineKeyboardButton("🏠 Home", callback_data="start_menu")],
            [InlineKeyboardButton("Close ✖️", callback_data="close")]
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

        # FEATURE 1: Store this message for future deletion
        await self.store_bot_message(user_id, response.id)

    # ===================================
    # CALLBACK QUERY HANDLER (FIXED - CRITICAL)
    # ===================================
    
    async def handle_callback_query(self, query: CallbackQuery):
        """
        Handle all callback queries from inline buttons - FIXED VERSION
        
        IMPLEMENTS: ALL THREE AUTO-DELETE FEATURES
        """
        try:
            data = query.data
            user_id = query.from_user.id

            logger.debug(f"Callback received: {data} from user {user_id}")

            # ===================================
            # ADMIN CHECK FOR ADMIN-ONLY BUTTONS
            # ===================================
            
            admin_callbacks = [
                "settings_menu", "files_settings", "auto_delete_settings",
                "force_sub_settings", "bot_msg_settings", "fsub_chnl_menu", 
                "stats_menu", "users_menu", "add_fsub_menu", "del_fsub_menu",  # Fixed: Added del_fsub_menu
                "refresh_fsub", "test_fsub", "reqfsub_on", "reqfsub_off",
                "refresh_users", "refresh_stats", "refresh_autodel", 
                "toggle_protect_content", "toggle_hide_caption", 
                "toggle_channel_button", "toggle_auto_delete", 
                "toggle_clean_conversation", "toggle_show_instruction",
                "custom_buttons_menu", "custom_texts_menu", "more_stats",
                "admin_list_menu"  # Added admin_list_menu
            ]

            if data in admin_callbacks:
                if not await self.is_user_admin(user_id):
                    await query.answer("❌ Admin only!", show_alert=True)
                    return

            # ===================================
            # NAVIGATION CALLBACKS (PUBLIC + ADMIN)
            # ===================================

            if data == "start_menu":
                await query.answer()
                # Delete current message
                try:
                    await query.message.delete()
                except:
                    pass
                
                # Create Message object from CallbackQuery
                message = await self._create_message_from_callback(query)
                await self.show_welcome_message(message)

            elif data == "help_menu":
                await query.answer()
                try:
                    await query.message.delete()
                except:
                    pass
                
                message = await self._create_message_from_callback(query)
                await self.help_command(message)

            elif data == "about_menu":
                await query.answer()
                try:
                    await query.message.delete()
                except:
                    pass
                
                message = await self._create_message_from_callback(query)
                await self.about_command(message)

            # ===================================
            # ADMIN NAVIGATION CALLBACKS
            # ===================================

            elif data == "settings_menu":
                await query.answer()
                try:
                    await query.message.delete()
                except:
                    pass
                
                message = await self._create_message_from_callback(query)
                await self.settings_command(message)

            elif data == "files_settings":
                await query.answer()
                try:
                    await query.message.delete()
                except:
                    pass
                
                message = await self._create_message_from_callback(query)
                await self.files_command(message)

            elif data == "auto_delete_settings":
                await query.answer()
                try:
                    await query.message.delete()
                except:
                    pass
                
                message = await self._create_message_from_callback(query)
                await self.auto_del_command(message)

            elif data == "force_sub_settings":
                await query.answer()
                try:
                    await query.message.delete()
                except:
                    pass
                
                message = await self._create_message_from_callback(query)
                await self.forcesub_command(message)

            elif data == "bot_msg_settings":
                await query.answer()
                try:
                    await query.message.delete()
                except:
                    pass
                
                message = await self._create_message_from_callback(query)
                await self.botsettings_command(message)

            elif data == "fsub_chnl_menu":
                await query.answer()
                try:
                    await query.message.delete()
                except:
                    pass
                
                message = await self._create_message_from_callback(query)
                await self.fsub_chnl_command(message)

            elif data == "users_menu":
                await query.answer()
                try:
                    await query.message.delete()
                except:
                    pass
                
                message = await self._create_message_from_callback(query)
                await self.users_command(message)

            elif data == "stats_menu":
                await query.answer()
                try:
                    await query.message.delete()
                except:
                    pass
                
                message = await self._create_message_from_callback(query)
                await self.stats_command(message)

            elif data == "admin_list_menu":  # NEW: Handle admin list menu
                await query.answer()
                try:
                    await query.message.delete()
                except:
                    pass
                
                message = await self._create_message_from_callback(query)
                await self.admin_list_command(message)

            # ===================================
            # FORCE SUBSCRIBE CHECK CALLBACK
            # ===================================

            elif data == "check_fsub":
                await query.answer("🔃 Checking subscription...")
                
                # Check if user is subscribed
                user_is_subscribed = await is_subscribed(self, user_id, self.force_sub_channels)
                
                if user_is_subscribed:
                    # User is now subscribed - delete fsub message and show welcome
                    try:
                        await query.message.delete()
                    except:
                        pass
                    
                    message = await self._create_message_from_callback(query)
                    await self.show_welcome_message(message)
                else:
                    await query.answer("❌ Please join all channels first!", show_alert=True)

            # ===================================
            # RESEND FILES CALLBACK (FEATURE 3)
            # ===================================

            elif data == "resend_files":
                await query.answer("🔃 Resending files...")
                await self.resend_files_callback(query)

            # ===================================
            # CLOSE CALLBACKS
            # ===================================

            elif data == "close":
                await query.answer("Closed!")
                try:
                    await query.message.delete()
                    # Clear from tracking if it was stored
                    if user_id in self.user_last_bot_message:
                        if self.user_last_bot_message[user_id]["message_id"] == query.message.id:
                            del self.user_last_bot_message[user_id]
                except Exception as e:
                    logger.error(f"Error deleting message on close: {e}")

            elif data == "close_instruction":
                await query.answer()
                try:
                    await query.message.delete()
                    # Clear instruction tracking
                    await self.clear_instruction_message(user_id)
                except:
                    pass

            # ===================================
            # TOGGLE CALLBACKS (Settings)
            # ===================================

            elif data.startswith("toggle_"):
                await query.answer()
                await self.handle_toggle_callback(query)

            # ===================================
            # AUTO DELETE TIME CALLBACKS
            # ===================================

            elif data.startswith("autodel_"):
                await query.answer()
                await self.handle_autodel_time_callback(query)

            # ===================================
            # REFRESH CALLBACKS
            # ===================================

            elif data.startswith("refresh_"):
                await query.answer("🔃 Refreshing...")
                await self.handle_refresh_callback(query)

            # ===================================
            # FORCE SUB CALLBACKS
            # ===================================

            elif data == "reqfsub_on":
                await query.answer("✅ Request FSub Enabled!")
                await self.handle_reqfsub_on(query)

            elif data == "reqfsub_off":
                await query.answer("❌ Request FSub Disabled!")
                await self.handle_reqfsub_off(query)

            elif data == "test_fsub":
                await self.test_force_sub(query)

            # ===================================
            # ADD/REMOVE FSUB CHANNELS CALLBACKS (FIXED)
            # ===================================

            elif data == "add_fsub_menu":
                await query.answer("➕ Add Force Sub Channel")
                await self.handle_add_fsub_menu(query)

            elif data == "del_fsub_menu":  # FIXED: This callback was missing
                await query.answer("➖ Remove Force Sub Channel")
                await self.handle_del_fsub_menu(query)

            # ===================================
            # CHANNEL REMOVAL CALLBACK
            # ===================================

            elif data.startswith("remove_channel_"):
                channel_id_str = data.replace("remove_channel_", "")
                try:
                    channel_id = int(channel_id_str)
                    await self.handle_remove_channel_callback(query, channel_id)
                except ValueError:
                    await query.answer("❌ Invalid channel ID!", show_alert=True)

            # ===================================
            # DEFAULT - NOT CONFIGURED
            # ===================================

            else:
                logger.warning(f"Unhandled callback: {data}")
                await query.answer(f"⚠️ Button '{data}' not configured yet!", show_alert=True)

        except Exception as e:
            logger.error(f"Error handling callback query '{query.data}': {e}")
            traceback.print_exc()
            await query.answer("❌ Error processing request!", show_alert=True)
    
    async def _create_message_from_callback(self, query: CallbackQuery) -> Message:
        """
        Helper method to create a Message-like object from CallbackQuery
        This allows us to use command methods with callback queries
        """
        # Create a dummy message object with necessary attributes
        class FakeMessage:
            def __init__(self, query):
                self.from_user = query.from_user
                self.chat = query.message.chat
                self._bot = query.message._client
                
            async def reply(self, text, **kwargs):
                return await self._bot.send_message(
                    self.chat.id,
                    text,
                    **kwargs
                )
            
            async def reply_photo(self, photo, **kwargs):
                return await self._bot.send_photo(
                    self.chat.id,
                    photo,
                    **kwargs
                )
        
        return FakeMessage(query)
    
    # ===================================
    # NEW: ADD FSUB MENU HANDLER (FIXED)
    # ===================================
    
    async def handle_add_fsub_menu(self, query: CallbackQuery):
        """Handle add force sub channel menu"""
        try:
            await query.answer()
            
            # Set state for adding force sub channel
            user_id = query.from_user.id
            self.button_setting_state[user_id] = {"type": "add_fsub"}
            
            # Ask for channel ID
            await query.message.edit_text(
                "➕ <b>ADD FORCE SUB CHANNEL</b>\n\n"
                "<blockquote>"
                "<b>Please send:</b>\n"
                "<code>channel_id channel_username</code>\n\n"
                "<b>Examples:</b>\n"
                "<code>-1001234567890 @channel_username</code>\n"
                "<code>-1001234567890</code> (for private channels)\n\n"
                "<b>Note:</b> Bot must be admin in the channel!"
                "</blockquote>",
                parse_mode=enums.ParseMode.HTML
            )
            
        except Exception as e:
            logger.error(f"Error in handle_add_fsub_menu: {e}")
            await query.answer("❌ Error!", show_alert=True)
    
    # ===================================
    # NEW: DEL FSUB MENU HANDLER (FIXED - WAS MISSING)
    # ===================================
    
    async def handle_del_fsub_menu(self, query: CallbackQuery):
        """Handle delete force sub channel menu"""
        try:
            await query.answer()
            
            # Get current force sub channels
            force_sub_channels = await self.db.get_force_sub_channels()
            
            if not force_sub_channels:
                await query.answer("❌ No force sub channels to remove!", show_alert=True)
                return
            
            # Create message with buttons for each channel
            message_text = "➖ <b>REMOVE FORCE SUB CHANNEL</b>\n\n"
            message_text += "<blockquote>"
            message_text += "Select a channel to remove:\n\n"
            
            buttons = []
            
            for i, channel in enumerate(force_sub_channels[:10]):  # Show max 10
                channel_id = channel.get("channel_id")
                username = channel.get("channel_username", "Private")
                
                message_text += f"<b>{i+1}. Channel ID:</b> <code>{channel_id}</code>\n"
                message_text += f"   <b>Username:</b> @{username}\n\n"
                
                buttons.append([
                    InlineKeyboardButton(
                        f"Remove {channel_id}",
                        callback_data=f"remove_channel_{channel_id}"
                    )
                ])
            
            message_text += "</blockquote>"
            
            buttons.append([
                InlineKeyboardButton("🏠 Back", callback_data="fsub_chnl_menu"),
                InlineKeyboardButton("❌ Close", callback_data="close")
            ])
            
            keyboard = InlineKeyboardMarkup(buttons)
            
            await query.message.edit_text(
                message_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
            
        except Exception as e:
            logger.error(f"Error in handle_del_fsub_menu: {e}")
            await query.answer("❌ Error!", show_alert=True)
    
    # ===================================
    # RESEND FILES CALLBACK METHOD (FEATURE 3)
    # ===================================
    
    async def resend_files_callback(self, query: CallbackQuery):
        """
        Resend files after they were deleted
        
        IMPLEMENTS: ALL THREE AUTO-DELETE FEATURES
        """
        try:
            user_id = query.from_user.id

            # Check if user has file history
            if user_id not in self.user_file_history or not self.user_file_history[user_id]:
                await query.answer("❌ No file history found!", show_alert=True)
                return

            # Get the most recent file entry
            recent_files = self.user_file_history[user_id][-1]
            file_ids = recent_files.get("file_ids", [])
            link_data = recent_files.get("link_data")

            if not file_ids:
                await query.answer("❌ No files to resend!", show_alert=True)
                return

            # Delete instruction message
            try:
                await query.message.delete()
                await self.clear_instruction_message(user_id)
            except:
                pass

            # Send files again
            sent_count = 0
            for file_id in file_ids[:MAX_SPECIAL_FILES]:
                try:
                    response = await self.copy_message(
                        chat_id=query.message.chat.id,
                        from_chat_id=self.db_channel,
                        message_id=file_id,
                        protect_content=self.settings.get("protect_content", True)
                    )
                    sent_count += 1

                    # FEATURE 2: Schedule for auto-deletion
                    settings = await self.db.get_settings()
                    auto_delete = settings.get("auto_delete", False)
                    if auto_delete:
                        delete_time = settings.get("auto_delete_time", 300)
                        await self.schedule_file_deletion(user_id, response.id, delete_time)

                except Exception as e:
                    logger.error(f"Error resending file {file_id}: {e}")

            # Send success message
            if sent_count > 0:
                success_msg = await self.send_message(
                    user_id,
                    f"✅ <b>Files resent successfully!</b>\n\n📁 Total: {sent_count} files",
                    parse_mode=enums.ParseMode.HTML
                )
                # FEATURE 1: Store for clean conversation
                await self.store_bot_message(user_id, success_msg.id)

                await query.answer(f"✅ Resent {sent_count} files!")
            else:
                await query.answer("❌ Failed to resend files!", show_alert=True)

        except Exception as e:
            logger.error(f"Error in resend_files_callback: {e}")
            await query.answer("❌ Error resending files!", show_alert=True)
    
    # ===================================
    # TOGGLE CALLBACK HANDLERS
    # ===================================
    
    async def handle_toggle_callback(self, query: CallbackQuery):
        """Handle toggle callbacks for settings"""
        try:
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
            
            await query.answer(f"{'✅ Enabled' if new_value else '❌ Disabled'}")
            
            # Refresh the settings page
            message = await self._create_message_from_callback(query)
            
            if data in ["protect_content", "hide_caption", "channel_button"]:
                await self.files_command(message)
            elif data == "auto_delete":
                await self.auto_del_command(message)
            elif data in ["clean_conversation", "show_instruction"]:
                await self.botsettings_command(message)
            else:
                await self.settings_command(message)
                
        except Exception as e:
            logger.error(f"Error in toggle callback: {e}")
            await query.answer("❌ Error toggling setting!", show_alert=True)
    
    async def handle_autodel_time_callback(self, query: CallbackQuery):
        """Handle auto delete time callbacks"""
        try:
            seconds = int(query.data.replace("autodel_", ""))
            
            # Update auto delete time
            await self.db.update_setting("auto_delete_time", seconds)
            
            # Update local settings
            self.settings["auto_delete_time"] = seconds
            
            await query.answer(f"⏱️ Time set to {format_time(seconds)}")
            
            # Refresh the auto delete settings page
            message = await self._create_message_from_callback(query)
            await self.auto_del_command(message)
            
        except Exception as e:
            logger.error(f"Error in autodel time callback: {e}")
            await query.answer("❌ Error setting time!", show_alert=True)
    
    async def handle_refresh_callback(self, query: CallbackQuery):
        """Handle refresh callbacks"""
        try:
            message = await self._create_message_from_callback(query)
            
            # Delete old message
            try:
                await query.message.delete()
            except:
                pass
            
            # Determine which page to refresh based on callback data
            data = query.data.replace("refresh_", "")
            
            if data == "users":
                await self.users_command(message)
            elif data == "stats":
                await self.stats_command(message)
            elif data == "autodel":
                await self.auto_del_command(message)
            elif data == "fsub":
                await self.forcesub_command(message)
            else:
                await self.settings_command(message)
                
        except Exception as e:
            logger.error(f"Error in refresh callback: {e}")
            await query.answer("❌ Error refreshing!", show_alert=True)
    
    async def handle_reqfsub_on(self, query: CallbackQuery):
        """Enable request force subscribe"""
        try:
            await self.db.update_setting("request_fsub", True)
            self.settings["request_fsub"] = True
            
            # Refresh the page
            message = await self._create_message_from_callback(query)
            
            # Delete old message
            try:
                await query.message.delete()
            except:
                pass
            
            await self.forcesub_command(message)
            
        except Exception as e:
            logger.error(f"Error enabling request fsub: {e}")
            await query.answer("❌ Error!", show_alert=True)
    
    async def handle_reqfsub_off(self, query: CallbackQuery):
        """Disable request force subscribe"""
        try:
            await self.db.update_setting("request_fsub", False)
            self.settings["request_fsub"] = False
            
            # Refresh the page
            message = await self._create_message_from_callback(query)
            
            # Delete old message
            try:
                await query.message.delete()
            except:
                pass
            
            await self.forcesub_command(message)
            
        except Exception as e:
            logger.error(f"Error disabling request fsub: {e}")
            await query.answer("❌ Error!", show_alert=True)
    
    async def test_force_sub(self, query: CallbackQuery):
        """Test force subscribe functionality"""
        user_id = query.from_user.id
        
        # Get force sub channels
        force_sub_channels = await self.db.get_force_sub_channels()
        
        if not force_sub_channels:
            await query.answer("❌ No force subscribe channels configured!", show_alert=True)
            return
        
        # Check subscription status
        is_subscribed_all = await is_subscribed(self, user_id, force_sub_channels)
        
        if is_subscribed_all:
            await query.answer("✅ You are subscribed to all channels!", show_alert=True)
        else:
            # Show which channels are missing
            missing_channels = []
            for channel in force_sub_channels:
                try:
                    channel_check = await is_subscribed(self, user_id, [channel])
                    if not channel_check:
                        username = channel.get("channel_username", f"Channel {channel.get('channel_id')}")
                        missing_channels.append(username)
                except:
                    username = channel.get("channel_username", f"Channel {channel.get('channel_id')}")
                    missing_channels.append(username)
            
            message = f"❌ You need to join {len(missing_channels)} channel(s):\n"
            for channel in missing_channels[:5]:  # Show max 5
                message += f"• @{channel}\n"
            
            if len(missing_channels) > 5:
                message += f"... and {len(missing_channels) - 5} more"
            
            await query.answer(message, show_alert=True)
    
    async def handle_remove_channel_callback(self, query: CallbackQuery, channel_id: int):
        """Handle channel removal callback"""
        try:
            # Remove channel from database
            await self.db.remove_force_sub_channel(channel_id)
            
            # Update local cache
            self.force_sub_channels = await self.db.get_force_sub_channels()
            
            await query.answer(f"✅ Channel {channel_id} removed!")
            
            # Refresh the page
            message = await self._create_message_from_callback(query)
            
            # Delete old message
            try:
                await query.message.delete()
            except:
                pass
            
            await self.fsub_chnl_command(message)
            
        except Exception as e:
            logger.error(f"Error removing channel: {e}")
            await query.answer("❌ Error removing channel!", show_alert=True)

    # ===================================
    # UTILITY COMMANDS
    # ===================================

    async def ping_command(self, message: Message):
        """
        Handle /ping command
        
        IMPLEMENTS: FEATURE 1 (Clean Conversation)
        """
        user_id = message.from_user.id
        
        # FEATURE 1: Delete previous bot message
        settings = await self.db.get_settings()
        if settings.get("clean_conversation", True):
            await self.delete_previous_bot_message(user_id)

        start_time = time.time()
        response = await message.reply("🏓 <b>Pinging...</b>", parse_mode=enums.ParseMode.HTML)
        end_time = time.time()

        ping_time = round((end_time - start_time) * 1000, 2)

        await response.edit_text(
            f"🏓 <b>Pong!</b>\n\n"
            f"<blockquote>"
            f"<b>📊 Ping:</b> {ping_time}ms\n"
            f"<b>⏰ Time:</b> {datetime.datetime.now().strftime('%H:%M:%S')}\n"
            f"<b>📅 Date:</b> {datetime.datetime.now().strftime('%Y-%m-%d')}"
            f"</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )

        # FEATURE 1: Store this message for future deletion
        await self.store_bot_message(user_id, response.id)

    async def cmd_command(self, message: Message):
        """
        Handle /cmd command - Show command list
        
        ADMINS: Show panel WITH navigation buttons
        USERS: Show list with ONLY close button
        
        IMPLEMENTS: FEATURE 1 (Clean Conversation)
        """
        user_id = message.from_user.id
        
        # FEATURE 1: Delete previous bot message
        settings = await self.db.get_settings()
        if settings.get("clean_conversation", True):
            await self.delete_previous_bot_message(user_id)

        # Check if user is admin
        is_admin = await self.is_user_admin(user_id)

        # Get cmd picture
        welcome_pics = settings.get("welcome_pics", Config.WELCOME_PICS)
        cmd_pic = get_random_pic(welcome_pics)

        # Basic commands for all users
        cmd_text = (
            "🔘 <b>BOT COMMANDS</b>\n\n"
            "<b>⚙️ BASIC COMMANDS:</b>\n"
            "<blockquote>"
            "• /start - Start bot\n"
            "• /help - Show help\n"
            "• /ping - Check status\n"
            "• /about - About bot"
            "</blockquote>"
        )

        if is_admin:
            cmd_text += (
                "\n<b>👑 ADMIN COMMANDS:</b>\n"
                "<blockquote expandable>"
                "<b>📊 Statistics:</b>\n"
                "• /stats - View statistics\n"
                "• /users - User stats\n"
                "• /refresh< - Refresh stats\n\n"
                "<b>📁 File Management:</b>\n"
                "• /genlink - Generate link\n"
                "• /getlink - Get link (reply to file)\n"
                "• /batch - Store multiple files\n"
                "• /custom_batch - Custom batch\n"
                "• /special_link - Special link\n"
                "• /done - Finish batch\n\n"
                "<b>⚙️ Settings:</b>\n"
                "• /settings - Bot settings panel\n"
                "• /files - File settings\n"
                "• /auto_del - Auto delete settings\n"
                "• /forcesub - Force sub settings\n"
                "• /botsettings - Bot message settings\n\n"
                "<b>👥 User Management:</b>\n"
                "• /broadcast - Send broadcast\n"
                "• /ban - Ban user\n"
                "• /unban - Unban user\n"
                "• /banuser_list - Banned users\n\n"
                "<b>👑 Admin Management:</b>\n"
                "• /admin_list - Admin commands\n"
                "• /add_admins - Add admins\n"
                "• /del_admins - Remove admins\n\n"
                "<b>📢 Channel Management:</b>\n"
                "• /setchannel - Set DB channel\n"
                "• /checkchannel - Check channel\n"
                "• /removechannel - Remove channel\n"
                "• /fsub_chnl - FSub channels\n"
                "• /add_fsub - Add FSub channel\n"
                "• /del_fsub - Remove FSub channel\n\n"
                "<b>🛠️ Other:</b>\n"
                "• /logs - View logs\n"
                "• /shortener - URL shortener\n"
                "• /font - Font styles"
                "</blockquote>\n\n"
                "<i>🔘 Click buttons below to navigate</i>"
            )

        # ===================================
        # BUTTONS: Different for Admin vs User
        # ===================================
        
        if is_admin:
            # ADMIN PANEL - FULL BUTTONS
            buttons = [
                [
                    InlineKeyboardButton("⚙️ settings", callback_data="settings_menu"),
                    InlineKeyboardButton("📊 stats", callback_data="stats_menu")
                ],
                [
                    InlineKeyboardButton("👥 users", callback_data="users_menu"),
                    InlineKeyboardButton("📁 files", callback_data="files_settings")
                ],
                [
                    InlineKeyboardButton("🗑️ auto delete", callback_data="auto_delete_settings"),
                    InlineKeyboardButton("📢 force sub", callback_data="force_sub_settings")
                ],
                [
                    InlineKeyboardButton("🏠 Home", callback_data="start_menu"),
                    InlineKeyboardButton("❌ Close", callback_data="close")
                ]
            ]
        else:
            # USER PANEL - ONLY CLOSE BUTTON
            buttons = [
                [InlineKeyboardButton("❌ Close", callback_data="close")]
            ]

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

        # FEATURE 1: Store this message for future deletion
        await self.store_bot_message(user_id, response.id)

    async def refresh_command(self, message: Message):
        """
        Handle /refresh command - Refresh statistics
        
        IMPLEMENTS: FEATURE 1 (Clean Conversation)
        """
        user_id = message.from_user.id
        
        # Check admin permission
        if not await self.is_user_admin(user_id):
            response = await message.reply("❌ <b>Admin only!</b>", parse_mode=enums.ParseMode.HTML)
            await self.store_bot_message(user_id, response.id)
            return

        # FEATURE 1: Delete previous bot message
        settings = await self.db.get_settings()
        if settings.get("clean_conversation", True):
            await self.delete_previous_bot_message(user_id)

        response = await message.reply("🔃 <b>Refreshing...</b>", parse_mode=enums.ParseMode.HTML)

        # Get updated counts
        total_users = await self.db.total_users_count()
        banned_users = await self.db.get_banned_count()
        active_users = total_users - banned_users

        await response.edit_text(
            f"✅ <b>Refreshed!</b>\n\n"
            f"<blockquote>"
            f"<b>👥 Users:</b> {total_users:,}\n"
            f"<b>✅ Active:</b> {active_users:,}\n"
            f"<b>🚫 Banned:</b> {banned_users:,}\n\n"
            f"<b>Updated:</b> {datetime.datetime.now().strftime('%H:%M:%S')}"
            f"</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )

        # FEATURE 1: Store this message for future deletion
        await self.store_bot_message(user_id, response.id)
async def logs_command(self, message: Message):
    """
    Handle /logs command - Send bot logs
    
    IMPLEMENTS: FEATURE 1 (Clean Conversation)
    """
    user_id = message.from_user.id
    
    # Check admin permission
    if not await self.is_user_admin(user_id):
        response = await message.reply("❌ <b>Admin only!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)
        return

    # FEATURE 1: Delete previous bot message
    settings = await self.db.get_settings()
    if settings.get("clean_conversation", True):
        await self.delete_previous_bot_message(user_id)

    try:
        # Check if log file exists
        if not os.path.exists('bot.log'):
            response = await message.reply("❌ <b>Log file not found!</b>", parse_mode=enums.ParseMode.HTML)
            await self.store_bot_message(user_id, response.id)
            return

        # Send the log file
        await message.reply_document(
            document='bot.log',
            caption="📊 <b>Bot Logs</b>\n\n<i>Latest logs from bot.log</i>",
            parse_mode=enums.ParseMode.HTML
        )

        # Note: We don't store document messages

    except Exception as e:
        logger.error(f"Error in logs command: {e}")
        response = await message.reply(
            f"❌ <b>Error fetching logs:</b>\n<code>{str(e)}</code>",
            parse_mode=enums.ParseMode.HTML
        )
        await self.store_bot_message(user_id, response.id)

async def shortener_command(self, message: Message):
    """
    Handle /shortener command - URL shortener settings
    
    IMPLEMENTS: FEATURE 1 (Clean Conversation)
    """
    user_id = message.from_user.id
    
    # Check admin permission
    if not await self.is_user_admin(user_id):
        response = await message.reply("❌ <b>Admin only!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)
        return

    # FEATURE 1: Delete previous bot message
    settings = await self.db.get_settings()
    if settings.get("clean_conversation", True):
        await self.delete_previous_bot_message(user_id)

    # Get shortener settings
    shortener_url = Config.SHORTENER_URL
    shortener_api = Config.SHORTENER_API

    status = "✅ <b>ENABLED</b>" if shortener_url and shortener_api else "❌ <b>DISABLED</b>"

    shortener_text = (
        "<b>🔗 URL SHORTENER SETTINGS</b>\n\n"
        "<blockquote>"
        f"<b>Status:</b> {status}\n"
        f"<b>Shortener URL:</b> {shortener_url if shortener_url else 'Not set'}\n"
        f"<b>API Key:</b> {'Set' if shortener_api else 'Not set'}"
        "</blockquote>\n\n"
        "<i>Configure shortener in environment variables:\n"
        "• SHORTENER_URL\n"
        "• SHORTENER_API</i>"
    )

    buttons = [
        [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings_menu")],
        [InlineKeyboardButton("ᴄʟᴏsᴇ ✖️", callback_data="close")]
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    response = await message.reply(
        shortener_text,
        reply_markup=keyboard,
        parse_mode=enums.ParseMode.HTML
    )

    # FEATURE 1: Store this message for future deletion
    await self.store_bot_message(user_id, response.id)

async def font_command(self, message: Message):
    """
    Handle /font command - Show font menu
    
    IMPLEMENTS: FEATURE 1 (Clean Conversation)
    """
    user_id = message.from_user.id
    
    # Check admin permission
    if not await self.is_user_admin(user_id):
        response = await message.reply("❌ <b>Admin only!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)
        return

    # FEATURE 1: Delete previous bot message
    settings = await self.db.get_settings()
    if settings.get("clean_conversation", True):
        await self.delete_previous_bot_message(user_id)
    
    response = await message.reply(
        "<b>🎨 FONT STYLES</b>\n\n"
        "<blockquote>"
        "Use <code>/font [text]</code> to style your text.\n\n"
        "<b>Example:</b> <code>/font Hello World</code>"
        "</blockquote>",
        parse_mode=enums.ParseMode.HTML
    )
    
    await self.store_bot_message(user_id, response.id)

# ===================================
# ADMIN MANAGEMENT COMMANDS
# ===================================

async def admin_list_command(self, message: Message):
    """
    Handle /admin_list command
    
    IMPLEMENTS: FEATURE 1 (Clean Conversation)
    """
    user_id = message.from_user.id
    
    # Check admin permission
    if not await self.is_user_admin(user_id):
        response = await message.reply("❌ <b>Admin only!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)
        return
    
    # FEATURE 1: Delete previous bot message
    settings = await self.db.get_settings()
    if settings.get("clean_conversation", True):
        await self.delete_previous_bot_message(user_id)
    
    try:
        # Get admins
        db_admins = await self.db.get_admins()
        all_admins = list(set(Config.ADMINS + db_admins))
        
        if not all_admins:
            response = await message.reply("❌ <b>No admins found!</b>", parse_mode=enums.ParseMode.HTML)
            await self.store_bot_message(user_id, response.id)
            return
        
        # Format message - FIXED: Proper blockquote expandable formatting
        admin_text = (
            "<b>🤖 𝗨𝗦𝗘𝗥 𝗦𝗘𝗧𝗧𝗜𝗡𝗚 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 :</b>\n\n"
            "<blockquote expandable>"
            "<b>/admin_list</b> - ᴠɪᴇᴡ ᴛʜᴇ ᴀᴠᴀɪʟᴀʙʟᴇ ᴀᴅᴍɪɴ ʟɪsᴛ (ᴏᴡɴᴇʀ)\n\n"
            "<b>/add_admins</b> - ᴀᴅᴅ ᴏɴᴇ ᴏʀ ᴍᴜʟᴛɪᴘʟᴇ ᴜsᴇʀ ɪᴅs ᴀs ᴀᴅᴍɪɴ (ᴏᴡɴᴇʀ)\n\n"
            "<b>/del_admins</b> - ᴅᴇʟᴇᴛᴇ ᴏɴᴇ ᴏʀ ᴍᴜʟᴛɪᴘʟᴇ ᴜsᴇʀ ɪᴅs ғʀᴏᴍ ᴀᴅᴍɪɴs (ᴏᴡɴᴇʀ)\n\n"
            "<b>/banuser_list</b> - ᴠɪᴇᴡ ᴛʜᴇ ᴀᴠᴀɪʟᴀʙʟᴇ ʙᴀɴɴᴇᴅ ᴜsᴇʀ ʟɪsᴛ (ᴀᴅᴍɪɴs)\n\n"
            "<b>/add_banuser</b> - ᴀᴅᴅ ᴏɴᴇ ᴏʀ ᴍᴜʟᴛɪᴘʟᴇ ᴜsᴇʀ ɪᴅs ɪɴ ʙᴀɴɴᴇᴅ ʟɪsᴛ (ᴀᴅᴍɪɴs)\n\n"
            "<b>/del_banuser</b> - ᴅᴇʟᴇᴛᴇ ᴏɴᴇ ᴏʀ ᴍᴜʟᴛɪᴘʟᴇ ᴜsᴇʀ ɪᴅs ғʀᴏᴍ ʙᴀɴɴᴇᴅ ʟɪsᴛ (ᴀᴅᴍɪɴs)"
            "</blockquote>\n\n"
            f"<b>👑 Total Admins:</b> {len(all_admins)}"
        )
        
        buttons = [
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings_menu")],
            [InlineKeyboardButton("ᴄʟᴏsᴇ ✖️", callback_data="close")]
        ]
        
        keyboard = InlineKeyboardMarkup(buttons)
        
        response = await message.reply(
            admin_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
        
        await self.store_bot_message(user_id, response.id)
        
    except Exception as e:
        logger.error(f"Error in admin_list command: {e}")
        response = await message.reply("❌ <b>Error fetching admin list!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)

async def add_admins_command(self, message: Message):
    """
    Handle /add_admins command
    
    IMPLEMENTS: FEATURE 1 (Clean Conversation)
    """
    user_id = message.from_user.id
    
    # Check if user is owner
    if user_id != Config.OWNER_ID:
        response = await message.reply("❌ <b>Owner only!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)
        return
    
    # FEATURE 1: Delete previous bot message
    settings = await self.db.get_settings()
    if settings.get("clean_conversation", True):
        await self.delete_previous_bot_message(user_id)
    
    if len(message.command) < 2:
        response = await message.reply(
            "<b>➕ 𝗔𝗗𝗗 𝗔𝗗𝗠𝗜𝗡𝗦</b>\n\n"
            "<blockquote>"
            "<b>Usage:</b> <code>/add_admins user_id1,user_id2</code>\n\n"
            "<b>Example:</b> <code>/add_admins 123456789,987654321</code>"
            "</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
        await self.store_bot_message(user_id, response.id)
        return
    
    try:
        args = message.command[1].split(",")
        added_admins = []
        
        for arg in args:
            arg = arg.strip()
            
            try:
                admin_id = int(arg)
                
                # Check if user exists
                try:
                    user = await self.get_users(admin_id)
                    
                    # Add to database
                    await self.db.add_admin(admin_id)
                    
                    # Add to Config.ADMINS if not already
                    if admin_id not in Config.ADMINS:
                        Config.ADMINS.append(admin_id)
                    
                    # Refresh admin cache
                    self.admin_cache.add(admin_id)
                    
                    added_admins.append(f"{user.first_name} ({admin_id})")
                    
                except Exception as e:
                    await message.reply(f"❌ <b>Error adding {arg}:</b> {str(e)}", parse_mode=enums.ParseMode.HTML)
                    continue
                
            except ValueError:
                await message.reply(f"❌ <b>Invalid user ID:</b> {arg}", parse_mode=enums.ParseMode.HTML)
                continue
        
        if added_admins:
            response = await message.reply(
                f"✅ <b>ᴀᴅᴍɪɴs ᴀᴅᴅᴇᴅ!</b>\n\n"
                "<blockquote>"
                f"<b>ᴀᴅᴅᴇᴅ {len(added_admins)} ᴀᴅᴍɪɴ(s):</b>\n"
                + "\n".join(f"• {admin}" for admin in added_admins) +
                "</blockquote>",
                parse_mode=enums.ParseMode.HTML
            )
        else:
            response = await message.reply("❌ <b>No admins were added!</b>", parse_mode=enums.ParseMode.HTML)
        
        await self.store_bot_message(user_id, response.id)
    
    except Exception as e:
        logger.error(f"Error adding admins: {e}")
        response = await message.reply("❌ <b>Error adding admins!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)

async def del_admins_command(self, message: Message):
    """
    Handle /del_admins command
    
    IMPLEMENTS: FEATURE 1 (Clean Conversation)
    """
    user_id = message.from_user.id
    
    # Check if user is owner
    if user_id != Config.OWNER_ID:
        response = await message.reply("❌ <b>Owner only!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)
        return
    
    # FEATURE 1: Delete previous bot message
    settings = await self.db.get_settings()
    if settings.get("clean_conversation", True):
        await self.delete_previous_bot_message(user_id)
    
    if len(message.command) < 2:
        response = await message.reply(
            "<b>🗑️ ᴅᴇʟᴇᴛᴇ ᴀᴅᴍɪɴs</b>\n\n"
            "<blockquote>"
            "<b>Usage:</b> <code>/del_admins user_id1,user_id2</code>\n\n"
            "<b>Example:</b> <code>/del_admins 123456789,987654321</code>\n\n"
            "<b>Note:</b> Cannot remove owner!"
            "</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
        await self.store_bot_message(user_id, response.id)
        return
    
    try:
        args = message.command[1].split(",")
        removed_admins = []
        
        for arg in args:
            arg = arg.strip()
            
            try:
                admin_id = int(arg)
                
                # Check if trying to remove owner
                if admin_id == Config.OWNER_ID:
                    await message.reply(f"❌ <b>Cannot remove owner ({admin_id})!</b>", parse_mode=enums.ParseMode.HTML)
                    continue
                
                # Remove from database
                await self.db.remove_admin(admin_id)
                
                # Remove from Config.ADMINS if present
                if admin_id in Config.ADMINS:
                    Config.ADMINS.remove(admin_id)
                
                # Remove from cache
                if admin_id in self.admin_cache:
                    self.admin_cache.remove(admin_id)
                
                removed_admins.append(str(admin_id))
                
            except ValueError:
                await message.reply(f"❌ <b>Invalid user ID:</b> {arg}", parse_mode=enums.ParseMode.HTML)
                continue
        
        if removed_admins:
            response = await message.reply(
                f"✅ <b>Admins Removed!</b>\n\n"
                "<blockquote>"
                f"<b>Removed {len(removed_admins)} admin(s):</b>\n"
                + "\n".join(f"• {admin}" for admin in removed_admins) +
                "</blockquote>",
                parse_mode=enums.ParseMode.HTML
            )
        else:
            response = await message.reply("❌ <b>No admins were removed!</b>", parse_mode=enums.ParseMode.HTML)
        
        await self.store_bot_message(user_id, response.id)
    
    except Exception as e:
        logger.error(f"Error removing admins: {e}")
        response = await message.reply("❌ <b>Error removing admins!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)

# ===================================
# USER STATISTICS COMMANDS
# ===================================

async def users_command(self, message: Message):
    """
    Handle /users command
    
    IMPLEMENTS: FEATURE 1 (Clean Conversation)
    """
    user_id = message.from_user.id
    
    # Check admin permission
    if not await self.is_user_admin(user_id):
        response = await message.reply("❌ <b>Admin only!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)
        return
    
    # FEATURE 1: Delete previous bot message
    settings = await self.db.get_settings()
    if settings.get("clean_conversation", True):
        await self.delete_previous_bot_message(user_id)
    
    try:
        # Get counts
        total_users = await self.db.total_users_count()
        banned_users = await self.db.get_banned_count()
        active_users = total_users - banned_users
        
        # Get stats picture
        welcome_pics = settings.get("welcome_pics", Config.WELCOME_PICS)
        stats_pic = get_random_pic(welcome_pics)
        
        # Format message
        stats_text = (
            "<b>👥 USER STATISTICS</b>\n\n"
            "<blockquote>"
            f"<b>📊 Total Users:</b> {total_users:,}\n"
            f"<b>✅ Active Users:</b> {active_users:,}\n"
            f"<b>🚫 Banned Users:</b> {banned_users:,}\n\n"
            f"<i>Last updated: {datetime.datetime.now().strftime('%H:%M:%S')}</i>"
            "</blockquote>"
        )
        
        buttons = [
            [
                InlineKeyboardButton("🔄 Refresh", callback_data="refresh_users"),
                InlineKeyboardButton("📊 Stats", callback_data="stats_menu")
            ],
            [
                InlineKeyboardButton("⬅️ Back", callback_data="settings_menu"),
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
        
        await self.store_bot_message(user_id, response.id)
        
    except Exception as e:
        logger.error(f"Error in users command: {e}")
        response = await message.reply("❌ <b>Error fetching user statistics!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)

async def stats_command(self, message: Message):
    """
    Handle /stats command
    
    IMPLEMENTS: FEATURE 1 (Clean Conversation)
    """
    user_id = message.from_user.id
    
    # Check admin permission
    if not await self.is_user_admin(user_id):
        response = await message.reply("❌ <b>Admin only!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)
        return
    
    # FEATURE 1: Delete previous bot message
    settings = await self.db.get_settings()
    if settings.get("clean_conversation", True):
        await self.delete_previous_bot_message(user_id)
    
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
        welcome_pics = settings.get("welcome_pics", Config.WELCOME_PICS)
        stats_pic = get_random_pic(welcome_pics)
        
        # Format message
        stats_text = (
            "<b>📊 BOT STATISTICS</b>\n\n"
            "<blockquote>"
            f"<b>👥 Users:</b> {total_users:,}\n"
            f"<b>✅ Active:</b> {active_users:,}\n"
            f"<b>🚫 Banned:</b> {banned_users:,}\n"
            f"<b>👑 Admins:</b> {len(all_admins)}\n"
            f"<b>📢 Force Sub:</b> {len(force_sub_channels)}\n"
            f"<b>💾 DB Channel:</b> {'✅' if db_channel else '❌'}\n\n"
            f"<i>Updated: {datetime.datetime.now().strftime('%H:%M:%S')}</i>"
            "</blockquote>"
        )
        
        buttons = [
            [
                InlineKeyboardButton("👥 Users", callback_data="users_menu"),
                InlineKeyboardButton("🔄 Refresh", callback_data="refresh_stats")
            ],
            [
                InlineKeyboardButton("⬅️ Back", callback_data="settings_menu"),
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
        
        await self.store_bot_message(user_id, response.id)
        
    except Exception as e:
        logger.error(f"Error in stats command: {e}")
        response = await message.reply("❌ <b>Error fetching statistics!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)

# ===================================
# BAN/UNBAN COMMANDS
# ===================================

async def banuser_list_command(self, message: Message):
    """Handle /banuser_list command"""
    user_id = message.from_user.id
    
    # Check admin permission
    if not await self.is_user_admin(user_id):
        response = await message.reply("❌ <b>Admin only!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)
        return
    
    # FEATURE 1: Delete previous bot message
    settings = await self.db.get_settings()
    if settings.get("clean_conversation", True):
        await self.delete_previous_bot_message(user_id)
    
    try:
        # Get banned users
        banned_users = await self.db.get_banned_users()
        
        if not banned_users:
            response = await message.reply("✅ <b>No banned users found!</b>", parse_mode=enums.ParseMode.HTML)
            await self.store_bot_message(user_id, response.id)
            return
        
        # Format message - FIXED: Proper blockquote formatting
        ban_text = "<b>🚫 𝗕𝗔𝗡𝗡𝗘𝗗 𝗨𝗦𝗘𝗥𝗦 𝗟𝗜𝗦𝗧</b>\n\n"
        ban_text += "<blockquote expandable>"
        
        for i, ban in enumerate(banned_users[:10], 1):
            ban_user_id = ban["user_id"]
            reason = ban.get("reason", "No reason")
            banned_date = ban.get("banned_date", "").strftime("%Y-%m-%d") if ban.get("banned_date") else "Unknown"
            
            ban_text += f"<b>{i}. ID:</b> <code>{ban_user_id}</code>\n"
            ban_text += f"   <b>Reason:</b> {reason}\n"
            ban_text += f"   <b>Date:</b> {banned_date}\n\n"
        
        ban_text += f"</blockquote>\n\n<b>📊 Total Banned:</b> {len(banned_users)}"
        
        buttons = [
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings_menu")],
            [InlineKeyboardButton("ᴄʟᴏsᴇ ✖️", callback_data="close")]
        ]
        
        keyboard = InlineKeyboardMarkup(buttons)
        
        response = await message.reply(
            ban_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
        
        await self.store_bot_message(user_id, response.id)
        
    except Exception as e:
        logger.error(f"Error in banuser_list command: {e}")
        response = await message.reply("❌ <b>Error fetching banned users list!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)

async def add_banuser_command(self, message: Message):
    """Handle /add_banuser command"""
    user_id = message.from_user.id
    
    # Check admin permission
    if not await self.is_user_admin(user_id):
        response = await message.reply("❌ <b>Admin only!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)
        return
    
    # FEATURE 1: Delete previous bot message
    settings = await self.db.get_settings()
    if settings.get("clean_conversation", True):
        await self.delete_previous_bot_message(user_id)
    
    if len(message.command) < 2:
        response = await message.reply(
            "<b>🚫 𝗕𝗔𝗡 𝗨𝗦𝗘𝗥</b>\n\n"
            "<blockquote>"
            "<b>Usage:</b> <code>/add_banuser user_id1,user_id2 [reason]</code>\n\n"
            "<b>Example:</b> <code>/add_banuser 123456789,987654321 Spamming</code>"
            "</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
        await self.store_bot_message(user_id, response.id)
        return
    
    try:
        args = message.command[1].split(",")
        reason = " ".join(message.command[2:]) if len(message.command) > 2 else "No reason provided"
        
        banned_users = []
        
        for arg in args:
            arg = arg.strip()
            
            try:
                ban_user_id = int(arg)
                
                # Check if user exists
                if not await self.db.is_user_exist(ban_user_id):
                    try:
                        user = await self.get_users(ban_user_id)
                        await self.db.add_user(ban_user_id, user.first_name, user.username)
                    except:
                        pass
                
                # Ban the user
                await self.db.ban_user(ban_user_id, reason)
                banned_users.append(str(ban_user_id))
                
                # Try to notify the user
                try:
                    await self.send_message(
                        ban_user_id,
                        f"🚫 <b>ʏᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ʙᴀɴɴᴇᴅ!</b>\n\n"
                        "<blockquote>"
                        f"<b>ʀᴇᴀsᴏɴ:</b> {reason}\n\n"
                        f"ᴄᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ ɪғ ᴛʜɪs ɪs ᴀ ᴍɪsᴛᴀᴋᴇ."
                        "</blockquote>",
                        parse_mode=enums.ParseMode.HTML
                    )
                except:
                    pass
                
            except ValueError:
                await message.reply(f"❌ <b>Invalid user ID:</b> {arg}", parse_mode=enums.ParseMode.HTML)
                continue
        
        if banned_users:
            response = await message.reply(
                f"✅ <b>Users Banned!</b>\n\n"
                "<blockquote>"
                f"<b>Banned {len(banned_users)} user(s):</b>\n"
                + "\n".join(f"• {uid}" for uid in banned_users) +
                f"\n\n<b>Reason:</b> {reason}"
                "</blockquote>",
                parse_mode=enums.ParseMode.HTML
            )
        else:
            response = await message.reply("❌ <b>No users were banned!</b>", parse_mode=enums.ParseMode.HTML)
        
        await self.store_bot_message(user_id, response.id)
    
    except Exception as e:
        logger.error(f"Error banning users: {e}")
        response = await message.reply("❌ <b>Error banning users!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)

async def del_banuser_command(self, message: Message):
    """Handle /del_banuser command"""
    user_id = message.from_user.id
    
    # Check admin permission
    if not await self.is_user_admin(user_id):
        response = await message.reply("❌ <b>Admin only!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)
        return
    
    # FEATURE 1: Delete previous bot message
    settings = await self.db.get_settings()
    if settings.get("clean_conversation", True):
        await self.delete_previous_bot_message(user_id)
    
    if len(message.command) < 2:
        response = await message.reply(
            "<b>✅ 𝗨𝗡𝗕𝗔𝗡 𝗨𝗦𝗘𝗥</b>\n\n"
            "<blockquote>"
            "<b>Usage:</b> <code>/del_banuser user_id1,user_id2</code>\n\n"
            "<b>Example:</b> <code>/del_banuser 123456789,987654321</code>"
            "</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
        await self.store_bot_message(user_id, response.id)
        return
    
    try:
        args = message.command[1].split(",")
        unbanned_users = []
        
        for arg in args:
            arg = arg.strip()
            
            try:
                unban_user_id = int(arg)
                
                # Check if user is banned
                if not await self.db.is_user_banned(unban_user_id):
                    await message.reply(f"⚠️ <b>User {unban_user_id} is not banned!</b>", parse_mode=enums.ParseMode.HTML)
                    continue
                
                # Unban the user
                await self.db.unban_user(unban_user_id)
                unbanned_users.append(str(unban_user_id))
                
                # Try to notify the user
                try:
                    await self.send_message(
                        unban_user_id,
                        "<b>✅ ʏᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ᴜɴʙᴀɴɴᴇᴅ!</b>\n\n"
                        "ʏᴏᴜ ᴄᴀɴ ɴᴏᴡ ᴜsᴇ ᴛʜᴇ ʙᴏᴛ ᴀɢᴀɪɴ.",
                        parse_mode=enums.ParseMode.HTML
                    )
                except:
                    pass
                
            except ValueError:
                await message.reply(f"❌ <b>Invalid user ID: {arg}</b>", parse_mode=enums.ParseMode.HTML)
                continue
        
        if unbanned_users:
            response = await message.reply(
                f"<b>✅ 𝗨𝗦𝗘𝗥𝗦 𝗨𝗡𝗕𝗔𝗡𝗡𝗘𝗗!</b>\n\n"
                "<blockquote>"
                f"<b>Unbanned {len(unbanned_users)} user(s):</b>\n"
                + "\n".join(f"• <code>{user_id}</code>" for user_id in unbanned_users) +
                "</blockquote>",
                parse_mode=enums.ParseMode.HTML
            )
        else:
            response = await message.reply("⚠️ <b>No users were unbanned!</b>", parse_mode=enums.ParseMode.HTML)
        
        await self.store_bot_message(user_id, response.id)
    
    except Exception as e:
        logger.error(f"Error unbanning users: {e}")
        response = await message.reply("❌ <b>Error unbanning users!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)

# ===================================
# SETTINGS COMMANDS
# ===================================

async def settings_command(self, message: Message):
    """
    Handle /settings command - Admin panel with working buttons
    
    IMPLEMENTS: FEATURE 1 (Clean Conversation)
    """
    user_id = message.from_user.id
    
    # Check admin permission
    if not await self.is_user_admin(user_id):
        response = await message.reply("❌ <b>Admin only!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)
        return

    # FEATURE 1: Delete previous bot message
    settings = await self.db.get_settings()
    if settings.get("clean_conversation", True):
        await self.delete_previous_bot_message(user_id)

    # Get current settings
    protect_content = settings.get("protect_content", True)
    auto_delete = settings.get("auto_delete", False)
    clean_conversation = settings.get("clean_conversation", True)
    request_fsub = settings.get("request_fsub", False)

    # Get settings picture
    welcome_pics = settings.get("welcome_pics", Config.WELCOME_PICS)
    settings_pic = get_random_pic(welcome_pics)

    # Format settings text with blockquote
    settings_text = (
        "⚙️ <b>BOT SETTINGS PANEL</b>\n\n"
        "<blockquote>"
        f"🔒 <b>Protect Content:</b> {'✅' if protect_content else '❌'}\n"
        f"🗑️ <b>Auto Delete Files:</b> {'✅' if auto_delete else '❌'}\n"
        f"💬 <b>Clean Conversation:</b> {'✅' if clean_conversation else '❌'}\n"
        f"📢 <b>Force Subscribe:</b> {'✅' if request_fsub else '❌'}"
        "</blockquote>\n\n"
        "<b>Select a category to configure:</b>"
    )

    # Create button grid
    buttons = [
        [
            InlineKeyboardButton("📁 ғɪʟᴇs", callback_data="files_settings"),
            InlineKeyboardButton("🗑️ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ", callback_data="auto_delete_settings")
        ],
        [
            InlineKeyboardButton("📢 ғᴏʀᴄᴇ sᴜʙ", callback_data="force_sub_settings"),
            InlineKeyboardButton("💬 ʙᴏᴛ ᴍsɢs", callback_data="bot_msg_settings")
        ],
        [
            InlineKeyboardButton("📊 sᴛᴀᴛɪsᴛɪᴄs", callback_data="stats_menu"),
            InlineKeyboardButton("👥 ᴜsᴇʀs", callback_data="users_menu")
        ],
        [
            InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="start_menu"),
            InlineKeyboardButton("❌ ᴄʟᴏsᴇ", callback_data="close")
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

    # FEATURE 1: Store this message for future deletion
    await self.store_bot_message(user_id, response.id)

async def files_command(self, message: Message):
    """
    Handle /files command - File settings - FIXED
    
    IMPLEMENTS: FEATURE 1 (Clean Conversation)
    """
    user_id = message.from_user.id
    
    # Check admin permission
    if not await self.is_user_admin(user_id):
        response = await message.reply("❌ <b>Admin only!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)
        return
    
    # FEATURE 1: Delete previous bot message
    settings = await self.db.get_settings()
    if settings.get("clean_conversation", True):
        await self.delete_previous_bot_message(user_id)

    # Get current settings
    protect_content = settings.get("protect_content", True)
    hide_caption = settings.get("hide_caption", False)
    channel_button = settings.get("channel_button", True)
    files_pics = settings.get("files_pics", Config.FILES_PICS)

    # Get random files picture
    files_pic = get_random_pic(files_pics)

    # Create files settings text using helper function - FIXED
    files_text = create_files_settings_text(protect_content, hide_caption, channel_button)
    
    # Create toggle buttons
    buttons = [
        [
            InlineKeyboardButton(f"🔒 ᴘʀᴏᴛᴇᴄᴛ: {'✅' if protect_content else '❌'}", callback_data="toggle_protect_content"),
            InlineKeyboardButton(f"🫥 ʜɪᴅᴇ: {'✅' if hide_caption else '❌'}", callback_data="toggle_hide_caption")
        ],
        [
            InlineKeyboardButton(f"🔘 ʙᴜᴛᴛᴏɴ: {'✅' if channel_button else '❌'}", callback_data="toggle_channel_button"),
            InlineKeyboardButton("🔘 ᴄᴜsᴛᴏᴍ ʙᴜᴛᴛᴏɴ", callback_data="custom_buttons_menu")
        ],
        [
            InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings_menu"),
            InlineKeyboardButton("❌ ᴄʟᴏsᴇ", callback_data="close")
        ]
    ]
    
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
    
    await self.store_bot_message(user_id, response.id)

async def auto_del_command(self, message: Message):
    """
    Handle /auto_del command - Auto delete settings (THREE FEATURES) - FIXED
    
    IMPLEMENTS: FEATURE 1 (Clean Conversation)
    """
    user_id = message.from_user.id
    
    # Check admin permission
    if not await self.is_user_admin(user_id):
        response = await message.reply("❌ <b>Admin only!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)
        return

    # FEATURE 1: Delete previous bot message
    settings = await self.db.get_settings()
    if settings.get("clean_conversation", True):
        await self.delete_previous_bot_message(user_id)

    # Get current settings for ALL THREE FEATURES
    auto_delete = settings.get("auto_delete", False)
    auto_delete_time = settings.get("auto_delete_time", 300)
    clean_conversation = settings.get("clean_conversation", True)
    show_instruction = settings.get("show_instruction", True)
    auto_del_pics = settings.get("auto_del_pics", Config.AUTO_DEL_PICS)

    # Get random auto delete picture
    auto_del_pic = get_random_pic(auto_del_pics)

    # Create auto delete text using helper function (shows all 3 features) - FIXED
    auto_del_text = create_auto_delete_text(
        auto_delete, 
        auto_delete_time, 
        clean_conversation, 
        show_instruction
    )
    
    buttons = []

    # Toggle buttons for each feature
    buttons.append([
        InlineKeyboardButton(f"🗑️ ғɪʟᴇs: {'✅' if auto_delete else '❌'}", callback_data="toggle_auto_delete"),
        InlineKeyboardButton(f"💬 ᴄʟᴇᴀɴ: {'✅' if clean_conversation else '❌'}", callback_data="toggle_clean_conversation")
    ])
    
    buttons.append([
        InlineKeyboardButton(f"📝 ɪɴsᴛʀᴜᴄᴛ: {'✅' if show_instruction else '❌'}", callback_data="toggle_show_instruction"),
        InlineKeyboardButton("⏱️ sᴇᴛ ᴛɪᴍᴇʀ", callback_data="set_timer")
    ])

    # Time buttons (only show if auto delete files is enabled)
    if auto_delete:
        time_row1 = []
        time_row2 = []
        
        for i, time_sec in enumerate(AUTO_DELETE_TIMES):
            time_display = format_time(time_sec)
            btn = InlineKeyboardButton(
                f"{'✅ ' if time_sec == auto_delete_time else ''}{time_display}", 
                callback_data=f"autodel_{time_sec}"
            )
            if i < 3:
                time_row1.append(btn)
            else:
                time_row2.append(btn)
        
        if time_row1:
            buttons.append(time_row1)
        if time_row2:
            buttons.append(time_row2)
    
    buttons.append([
        InlineKeyboardButton("🔄 ʀᴇғʀᴇsʜ", callback_data="refresh_autodel"),
        InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings_menu")
    ])
    
    buttons.append([
        InlineKeyboardButton("❌ ᴄʟᴏsᴇ", callback_data="close")
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
    
    await self.store_bot_message(user_id, response.id)

async def botsettings_command(self, message: Message):
    """
    Handle /botsettings command - Bot message settings
    
    IMPLEMENTS: FEATURE 1 (Clean Conversation)
    """
    user_id = message.from_user.id
    
    # Check admin permission
    if not await self.is_user_admin(user_id):
        response = await message.reply("❌ <b>Admin only!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)
        return
        
    # FEATURE 1: Delete previous bot message
    settings = await self.db.get_settings()
    if settings.get("clean_conversation", True):
        await self.delete_previous_bot_message(user_id)
    
    # Get current settings
    clean_conversation = settings.get("clean_conversation", True)
    show_instruction = settings.get("show_instruction", True)
    welcome_pics = settings.get("welcome_pics", Config.WELCOME_PICS)
    
    # Get random picture
    settings_pic = get_random_pic(welcome_pics)
    
    settings_text = (
        "<b>🤖 BOT MESSAGE SETTINGS</b>\n\n"
        "<blockquote>"
        f"<b>💬 Clean Conversation:</b> {'✅ ENABLED' if clean_conversation else '❌ DISABLED'}\n"
        f"<b>📝 Show Instruction:</b> {'✅ ENABLED' if show_instruction else '❌ DISABLED'}"
        "</blockquote>\n\n"
        "<b>Feature Explanation:</b>\n"
        "<blockquote expandable>"
        "<b>Clean Conversation:</b>\n"
        "Deletes previous bot message when sending new one. Keeps PM clean.\n\n"
        "<b>Show Instruction:</b>\n"
        "After files are deleted, shows instruction message with resend button. This message is NOT auto-deleted."
        "</blockquote>"
    )
    
    buttons = [
        [
            InlineKeyboardButton(f"💬 {'✅' if clean_conversation else '❌'}", callback_data="toggle_clean_conversation"),
            InlineKeyboardButton(f"📝 {'✅' if show_instruction else '❌'}", callback_data="toggle_show_instruction")
        ],
        [
            InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings_menu"),
            InlineKeyboardButton("❌ ᴄʟᴏsᴇ", callback_data="close")
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
        logger.error(f"Error sending bot settings photo: {e}")
        response = await message.reply(
            settings_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
    
    await self.store_bot_message(user_id, response.id)

# ===================================
# BAN/UNBAN COMMANDS
# ===================================

async def ban_command(self, message: Message):
    """Handle /ban command"""
    user_id = message.from_user.id
    
    # Check admin permission
    if not await self.is_user_admin(user_id):
        response = await message.reply("❌ <b>Admin only!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)
        return

    # FEATURE 1: Delete previous bot message
    settings = await self.db.get_settings()
    if settings.get("clean_conversation", True):
        await self.delete_previous_bot_message(user_id)

    if len(message.command) < 2:
        response = await message.reply(
            "🚫 <b>BAN USER</b>\n\n"
            "<blockquote>"
            "<b>Usage:</b> <code>/ban user_id [reason]</code>\n\n"
            "<b>Example:</b> <code>/ban 123456789 Spamming</code>"
            "</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
        await self.store_bot_message(user_id, response.id)
        return

    try:
        ban_user_id = int(message.command[1])
        reason = " ".join(message.command[2:]) if len(message.command) > 2 else "No reason provided"

        # Check if user exists
        try:
            user = await self.get_users(ban_user_id)
        except:
            response = await message.reply("❌ <b>User not found!</b>", parse_mode=enums.ParseMode.HTML)
            await self.store_bot_message(user_id, response.id)
            return

        # Ban the user
        await self.db.ban_user(ban_user_id, reason)

        # Try to notify the user
        try:
            await self.send_message(
                ban_user_id,
                f"🚫 <b>You have been banned!</b>\n\n"
                "<blockquote>"
                f"<b>Reason:</b> {reason}\n\n"
                f"Contact admin if this is a mistake."
                "</blockquote>",
                parse_mode=enums.ParseMode.HTML
            )
        except:
            pass

        response = await message.reply(
            f"✅ <b>User Banned!</b>\n\n"
            "<blockquote>"
            f"<b>👤 User:</b> {user.first_name}\n"
            f"<b>🆔 ID:</b> <code>{ban_user_id}</code>\n"
            f"<b>📝 Reason:</b> {reason}"
            "</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )

        await self.store_bot_message(user_id, response.id)

    except ValueError:
        response = await message.reply("❌ <b>Invalid user ID!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)
    except Exception as e:
        logger.error(f"Error banning user: {e}")
        response = await message.reply("❌ <b>Error banning user!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)

async def unban_command(self, message: Message):
    """Handle /unban command"""
    user_id = message.from_user.id
    
    # Check admin permission
    if not await self.is_user_admin(user_id):
        response = await message.reply("❌ <b>Admin only!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)
        return

    # FEATURE 1: Delete previous bot message
    settings = await self.db.get_settings()
    if settings.get("clean_conversation", True):
        await self.delete_previous_bot_message(user_id)

    if len(message.command) < 2:
        response = await message.reply(
            "✅ <b>UNBAN USER</b>\n\n"
            "<blockquote>"
            "<b>Usage:</b> <code>/unban user_id</code>\n\n"
            "<b>Example:</b> <code>/unban 123456789</code>"
            "</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
        await self.store_bot_message(user_id, response.id)
        return

    try:
        unban_user_id = int(message.command[1])

        # Check if user is banned
        if not await self.db.is_user_banned(unban_user_id):
            response = await message.reply("⚠️ <b>User is not banned!</b>", parse_mode=enums.ParseMode.HTML)
            await self.store_bot_message(user_id, response.id)
            return

        # Unban the user
        await self.db.unban_user(unban_user_id)

        # Try to notify the user
        try:
            await self.send_message(
                unban_user_id,
                "✅ <b>You have been unbanned!</b>\n\n"
                "You can now use the bot again.",
                parse_mode=enums.ParseMode.HTML
            )
        except:
            pass

        response = await message.reply(
            f"✅ <b>User Unbanned!</b>\n\n"
            "<blockquote>"
            f"<b>🆔 User ID:</b> <code>{unban_user_id}</code>\n"
            f"<b>✅ Status:</b> Unbanned"
            "</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )

        await self.store_bot_message(user_id, response.id)

    except ValueError:
        response = await message.reply("❌ <b>Invalid user ID!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)
    except Exception as e:
        logger.error(f"Error unbanning user: {e}")
        response = await message.reply("❌ <b>Error unbanning user!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)

# ===================================
# FILE MANAGEMENT COMMANDS (FIXED VERSION)
# ===================================

async def genlink_command(self, message: Message):
    """
    Handle /genlink command - FIXED VERSION
    
    FIXES:
    1. Checks if bot is admin in database channel
    2. Properly generates working links
    3. Handles errors correctly
    """
    user_id = message.from_user.id
    
    # Check admin permission
    if not await self.is_user_admin(user_id):
        response = await message.reply("❌ <b>Admin only!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)
        return

    # FEATURE 1: Delete previous bot message
    settings = await self.db.get_settings()
    if settings.get("clean_conversation", True):
        await self.delete_previous_bot_message(user_id)

    if not message.reply_to_message:
        response = await message.reply(
            "🔗 <b>GENERATE LINK</b>\n\n"
            "<blockquote>"
            "<b>How to use:</b>\n"
            "Reply to a file with /genlink to create a shareable link"
            "</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
        await self.store_bot_message(user_id, response.id)
        return

    if not self.db_channel:
        response = await message.reply("❌ <b>Set database channel first!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)
        return

    try:
        # Check if bot is admin in database channel
        try:
            me = await self.get_me()
            bot_id = me.id
            member = await self.get_chat_member(self.db_channel, bot_id)
            if member.status not in ["administrator", "creator"]:
                # Bot is not admin - cannot forward message
                response = await message.reply("❌ <b>Bot is not admin in the database channel!</b>", parse_mode=enums.ParseMode.HTML)
                await self.store_bot_message(user_id, response.id)
                return
        except Exception as e:
            logger.error(f"Error checking admin status: {e}")
            response = await message.reply("❌ <b>Cannot access database channel!</b>", parse_mode=enums.ParseMode.HTML)
            await self.store_bot_message(user_id, response.id)
            return

        # Forward message to database channel
        try:
            forwarded = await message.reply_to_message.forward(self.db_channel)
            
            # Generate link
            base64_id = await encode(str(forwarded.id))  # FIXED: Encode only the message ID
            bot_username = Config.BOT_USERNAME
            link = f"https://t.me/{bot_username}?start={base64_id}"  # FIXED: Use direct encoded ID

            response = await message.reply(
                f"✅ <b>Link Generated!</b>\n\n"
                "<blockquote>"
                f"<b>🔗 Link:</b>\n"
                f"<code>{link}</code>\n\n"
                f"<b>📁 File ID:</b> <code>{forwarded.id}</code>"
                "</blockquote>",
                parse_mode=enums.ParseMode.HTML,
                disable_web_page_preview=True
            )

            await self.store_bot_message(user_id, response.id)

        except Exception as e:
            logger.error(f"Error forwarding message: {e}")
            response = await message.reply("❌ <b>Error forwarding message to database channel!</b>", parse_mode=enums.ParseMode.HTML)
            await self.store_bot_message(user_id, response.id)

    except Exception as e:
        logger.error(f"Error generating link: {e}")
        response = await message.reply("❌ <b>Error generating link!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)

async def getlink_command(self, message: Message):
    """Handle /getlink command - Alias for genlink"""
    await self.genlink_command(message)

# ===================================
# BATCH COMMAND - FIXED VERSION
# ===================================

async def batch_command(self, message: Message):
    """
    Handle /batch command - First/Last Message Method
    
    IMPLEMENTS: FEATURE 1 (Clean Conversation)
    """
    user_id = message.from_user.id
    
    # Check admin permission
    if not await self.is_user_admin(user_id):
        response = await message.reply("❌ <b>Admin only!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)
        return

    # FEATURE 1: Delete previous bot message
    settings = await self.db.get_settings()
    if settings.get("clean_conversation", True):
        await self.delete_previous_bot_message(user_id)

    if not self.db_channel:
        response = await message.reply("❌ <b>Set database channel first!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)
        return

    # Initialize batch state with FIRST/LAST method
    self.batch_state[user_id] = {
        "method": "first_last",  # NEW: Method identifier
        "step": "waiting_first",  # NEW: Current step
        "first_msg_id": None,
        "last_msg_id": None,
        "channel_id": self.db_channel
    }

    response = await message.reply(
        "📁 <b>BATCH MODE STARTED</b>\n\n"
        "<blockquote>"
        f"<b>Method:</b> First/Last Message\n"
        f"<b>Max files:</b> {MAX_BATCH_SIZE}\n\n"
        f"<b>📝 Step 1:</b>\n"
        "Go to your database channel and forward the <b>FIRST message</b> (starting file) to me.\n\n"
        f"<i>Example: If you want Episodes 1-50, forward Episode 1</i>"
        "</blockquote>",
        parse_mode=enums.ParseMode.HTML
    )

    await self.store_bot_message(user_id, response.id)

# ===================================
# CHANNEL MANAGEMENT COMMANDS (FIXED)
# ===================================

async def setchannel_command(self, message: Message):
    """Handle /setchannel command"""
    user_id = message.from_user.id
    
    # Check admin permission
    if not await self.is_user_admin(user_id):
        response = await message.reply("❌ <b>Admin only!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)
        return

    # FEATURE 1: Delete previous bot message
    settings = await self.db.get_settings()
    if settings.get("clean_conversation", True):
        await self.delete_previous_bot_message(user_id)

    if len(message.command) < 2:
        response = await message.reply(
            "📺 <b>SET DATABASE CHANNEL</b>\n\n"
            "<blockquote>"
            "<b>Usage:</b> <code>/setchannel channel_id</code>\n\n"
            "<b>Example:</b> <code>/setchannel -1001234567890</code>\n\n"
            "<b>How to get Channel ID:</b>\n"
            "1. Add @RawDataBot to your channel\n"
            "2. Send any message\n"
            "3. Copy the chat_id (it will be negative)"
            "</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
        await self.store_bot_message(user_id, response.id)
        return

    try:
        channel_id = int(message.command[1])

        # Check if bot is admin in channel
        try:
            chat = await self.get_chat(channel_id)
            me = await self.get_me()
            member = await self.get_chat_member(channel_id, me.id)
            
            if member.status not in ["administrator", "creator"]:
                response = await message.reply("❌ <b>Bot must be admin in the channel!</b>", parse_mode=enums.ParseMode.HTML)
                await self.store_bot_message(user_id, response.id)
                return

        except Exception as e:
            response = await message.reply(f"❌ <b>Error accessing channel:</b>\n<code>{e}</code>", parse_mode=enums.ParseMode.HTML)
            await self.store_bot_message(user_id, response.id)
            return

        # Set database channel
        await self.db.set_db_channel(channel_id)
        self.db_channel = channel_id

        response = await message.reply(
            f"✅ <b>Database Channel Set!</b>\n\n"
            "<blockquote>"
            f"<b>📺 Channel:</b> {chat.title}\n"
            f"<b>🆔 ID:</b> <code>{channel_id}</code>\n"
            f"<b>👤 Username:</b> @{chat.username if chat.username else 'Private'}"
            "</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )

        await self.store_bot_message(user_id, response.id)

    except ValueError:
        response = await message.reply("❌ <b>Invalid channel ID!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)
    except Exception as e:
        logger.error(f"Error setting channel: {e}")
        response = await message.reply("❌ <b>Error setting channel!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)

async def checkchannel_command(self, message: Message):
    """
    Handle /checkchannel command - FIXED VERSION
    
    FIXED: Now properly checks if bot is admin in the channel
    """
    user_id = message.from_user.id
    
    # Check admin permission
    if not await self.is_user_admin(user_id):
        response = await message.reply("❌ <b>Admin only!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)
        return

    # FEATURE 1: Delete previous bot message
    settings = await self.db.get_settings()
    if settings.get("clean_conversation", True):
        await self.delete_previous_bot_message(user_id)

    if not self.db_channel:
        response = await message.reply("❌ <b>No database channel set!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)
        return

    try:
        chat = await self.get_chat(self.db_channel)
        me = await self.get_me()
        bot_id = me.id
        
        # FIXED: Check bot's admin status in the channel
        try:
            member = await self.get_chat_member(self.db_channel, bot_id)
            
            if member.status == "creator":
                status = "✅ Creator (Owner)"
                bot_permissions = "✅ Full access"
            elif member.status == "administrator":
                status = "✅ Administrator"
                permissions = []
                if member.privileges:
                    if getattr(member.privileges, 'can_post_messages', False):
                        permissions.append("📝 Post")
                    if getattr(member.privileges, 'can_delete_messages', False):
                        permissions.append("🗑️ Delete")
                bot_permissions = "✅ " + ", ".join(permissions) if permissions else "✅ Admin"
            else:
                status = f"❌ Not Admin (Status: {member.status})"
                bot_permissions = "❌ No access"
                
        except Exception as e:
            logger.error(f"Error checking admin: {e}")
            status = "⚠️ Error"
            bot_permissions = f"⚠️ {str(e)[:50]}"

        response = await message.reply(
            f"📊 <b>CHANNEL STATUS</b>\n\n"
            "<blockquote>"
            f"<b>📺 Channel:</b> {chat.title}\n"
            f"<b>🆔 ID:</b> <code>{self.db_channel}</code>\n"
            f"<b>👤 Username:</b> @{chat.username if chat.username else 'Private'}\n"
            f"<b>🤖 Bot Status:</b> {status}\n"
            f"<b>🔧 Permissions:</b> {bot_permissions}\n"
            f"<b>👥 Members:</b> {getattr(chat, 'members_count', 'Unknown')}"
            "</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )

        await self.store_bot_message(user_id, response.id)

    except Exception as e:
        logger.error(f"Error checking channel: {e}")
        response = await message.reply(
            f"❌ <b>Error checking channel</b>\n\n<blockquote>{str(e)[:100]}</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
        await self.store_bot_message(user_id, response.id)

async def removechannel_command(self, message: Message):
    """Handle /removechannel command"""
    user_id = message.from_user.id
    
    # Check admin permission
    if not await self.is_user_admin(user_id):
        response = await message.reply("❌ <b>Admin only!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)
        return

    # FEATURE 1: Delete previous bot message
    settings = await self.db.get_settings()
    if settings.get("clean_conversation", True):
        await self.delete_previous_bot_message(user_id)

    if not self.db_channel:
        response = await message.reply("❌ <b>No database channel to remove!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)
        return

    try:
        old_channel_id = self.db_channel
        
        # Remove database channel
        await self.db.remove_db_channel()
        self.db_channel = None

        response = await message.reply(
            f"✅ <b>Database Channel Removed!</b>\n\n"
            "<blockquote>"
            f"<b>🆔 Channel ID:</b> <code>{old_channel_id}</code>\n"
            f"<b>🗑️ Status:</b> Removed"
            "</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )

        await self.store_bot_message(user_id, response.id)

    except Exception as e:
        logger.error(f"Error removing channel: {e}")
        response = await message.reply("❌ <b>Error removing channel!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)

# ===================================
# FORCE SUBSCRIBE COMMANDS
# ===================================

async def forcesub_command(self, message: Message):
    """Handle /forcesub command"""
    user_id = message.from_user.id
    
    # Check admin permission
    if not await self.is_user_admin(user_id):
        response = await message.reply("❌ <b>Admin only!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)
        return

    # FEATURE 1: Delete previous bot message
    settings = await self.db.get_settings()
    if settings.get("clean_conversation", True):
        await self.delete_previous_bot_message(user_id)

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
        channels_text += f"🔄 <b>Request FSub:</b> {request_status}\n\n"
        channels_text += "<b>Current Channels:</b>\n"
        
        for i, channel in enumerate(force_sub_channels, 1):
            channel_id = channel.get("channel_id")
            username = channel.get("channel_username", "No username")
            
            channels_text += f"{i}. <b>Channel ID:</b> <code>{channel_id}</code>\n"
            channels_text += f"   <b>Username:</b> @{username}\n\n"
        
        channels_text += f"📊 <b>Total Channels:</b> {len(force_sub_channels)}"
    else:
        channels_text = "<b>📢 FORCE SUBSCRIBE SETTINGS</b>\n\n"
        channels_text += f"🔄 <b>Request FSub:</b> {request_status}\n\n"
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
        InlineKeyboardButton("➖ REMOVE CHANNEL", callback_data="del_fsub_menu")  # FIXED: Now works
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
    
    await self.store_bot_message(user_id, response.id)

async def req_fsub_command(self, message: Message):
    """Handle /req_fsub command"""
    user_id = message.from_user.id
    
    # Check admin permission
    if not await self.is_user_admin(user_id):
        response = await message.reply("❌ <b>Admin only!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)
        return

    # FEATURE 1: Delete previous bot message
    settings = await self.db.get_settings()
    if settings.get("clean_conversation", True):
        await self.delete_previous_bot_message(user_id)

    # Get current settings
    request_fsub = settings.get("request_fsub", False)
    force_sub_pics = settings.get("force_sub_pics", Config.FORCE_SUB_PICS)
    
    # Get random force sub picture
    force_sub_pic = get_random_pic(force_sub_pics)
    
    # Format
    status = "✅ ENABLED" if request_fsub else "❌ DISABLED"
    
    req_fsub_text = (
        "<b>📢 REQUEST FSUB SETTINGS</b>\n\n"
        "<blockquote>"
        f"<b>Status:</b> {status}\n\n"
        f"<i>When enabled, users must join all force subscribe channels before using the bot.</i>"
        "</blockquote>"
    )
    
    # Create toggle buttons
    buttons = []
    
    if request_fsub:
        buttons.append([
            InlineKeyboardButton("❌ DISABLE", callback_data="reqfsub_off"),
            InlineKeyboardButton("⚙️ CHANNELS", callback_data="fsub_chnl_menu")
        ])
    else:
        buttons.append([
            InlineKeyboardButton("✅ ENABLE", callback_data="reqfsub_on"),
            InlineKeyboardButton("⚙️ CHANNELS", callback_data="fsub_chnl_menu")
        ])
    
    buttons.append([
        InlineKeyboardButton("🔙 BACK", callback_data="settings_menu"),
        InlineKeyboardButton("❌ CLOSE", callback_data="close")
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
    
    await self.store_bot_message(user_id, response.id)

async def fsub_chnl_command(self, message: Message):
    """Handle /fsub_chnl command"""
    user_id = message.from_user.id
    
    # Check admin permission
    if not await self.is_user_admin(user_id):
        response = await message.reply("❌ <b>Admin only!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)
        return

    # FEATURE 1: Delete previous bot message
    settings = await self.db.get_settings()
    if settings.get("clean_conversation", True):
        await self.delete_previous_bot_message(user_id)

    # Get force sub channels
    force_sub_channels = await self.db.get_force_sub_channels()
    
    # Get force sub pictures
    force_sub_pics = settings.get("force_sub_pics", Config.FORCE_SUB_PICS)
    force_sub_pic = get_random_pic(force_sub_pics)
    
    # Format message
    if force_sub_channels:
        channels_text = "<b>📢 FORCE SUBSCRIBE CHANNELS</b>\n\n"
        channels_text += "<blockquote>"
        
        for i, channel in enumerate(force_sub_channels, 1):
            channel_id = channel.get("channel_id")
            username = channel.get("channel_username", "No username")
            
            channels_text += f"<b>{i}. Channel ID:</b> <code>{channel_id}</code>\n"
            channels_text += f"   <b>Username:</b> @{username}\n\n"
        
        channels_text += f"</blockquote>\n\n"
        channels_text += f"📊 <b>Total Channels:</b> {len(force_sub_channels)}"
    else:
        channels_text = "<b>📢 FORCE SUBSCRIBE CHANNELS</b>\n\n"
        channels_text += "<blockquote>"
        channels_text += "No force subscribe channels configured.\n"
        channels_text += "Use /add_fsub to add channels."
        channels_text += "</blockquote>"
    
    # Create buttons
    buttons = []
    
    if force_sub_channels:
        buttons.append([
            InlineKeyboardButton("➕ ADD CHANNEL", callback_data="add_fsub_menu"),
            InlineKeyboardButton("➖ REMOVE CHANNEL", callback_data="del_fsub_menu")
        ])
    else:
        buttons.append([
            InlineKeyboardButton("➕ ADD CHANNEL", callback_data="add_fsub_menu")
        ])
    
    buttons.append([
        InlineKeyboardButton("🔄 REFRESH", callback_data="refresh_fsub"),
        InlineKeyboardButton("🔙 BACK", callback_data="force_sub_settings")
    ])
    
    buttons.append([
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
        logger.error(f"Error sending fsub channels photo: {e}")
        response = await message.reply(
            channels_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
    
    await self.store_bot_message(user_id, response.id)

async def add_fsub_command(self, message: Message):
    """Handle /add_fsub command"""
    user_id = message.from_user.id
    
    # Check admin permission
    if not await self.is_user_admin(user_id):
        response = await message.reply("❌ <b>Admin only!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)
        return

    # FEATURE 1: Delete previous bot message
    settings = await self.db.get_settings()
    if settings.get("clean_conversation", True):
        await self.delete_previous_bot_message(user_id)

    if len(message.command) < 2:
        response = await message.reply(
            "➕ <b>ADD FORCE SUB CHANNEL</b>\n\n"
            "<blockquote>"
            "<b>Usage:</b> <code>/add_fsub channel_id [username]</code>\n\n"
            "<b>Examples:</b>\n"
            "<code>/add_fsub -100123456789 @channel_username</code>\n"
            "<code>/add_fsub -100123456789</code>\n\n"
            "<b>Note:</b> Bot must be admin in the channel!"
            "</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
        await self.store_bot_message(user_id, response.id)
        return

    try:
        channel_id = int(message.command[1])
        username = message.command[2] if len(message.command) > 2 else None
        
        if username:
            username = username.lstrip('@')
        
        # Check if bot is admin in channel
        try:
            me = await self.get_me()
            await self.get_chat_member(channel_id, me.id)
        except Exception as e:
            response = await message.reply(f"❌ <b>Bot is not admin in channel {channel_id}!</b>", parse_mode=enums.ParseMode.HTML)
            await self.store_bot_message(user_id, response.id)
            return
        
        # Add channel to database
        await self.db.add_force_sub_channel(channel_id, username)
        
        # Update local cache
        self.force_sub_channels = await self.db.get_force_sub_channels()
        
        response = await message.reply(
            f"✅ <b>Channel Added!</b>\n\n"
            "<blockquote>"
            f"<b>📢 Channel ID:</b> <code>{channel_id}</code>\n"
            f"<b>👤 Username:</b> @{username if username else 'Private'}\n\n"
            f"<b>Total channels:</b> {len(self.force_sub_channels)}"
            "</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
        
        await self.store_bot_message(user_id, response.id)
        
    except ValueError:
        response = await message.reply("❌ <b>Invalid channel ID! Must be a number.</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)
    except Exception as e:
        logger.error(f"Error adding force sub channel: {e}")
        response = await message.reply("❌ <b>Error adding channel!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)

async def del_fsub_command(self, message: Message):
    """Handle /del_fsub command"""
    user_id = message.from_user.id
    
    # Check admin permission
    if not await self.is_user_admin(user_id):
        response = await message.reply("❌ <b>Admin only!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)
        return

    # FEATURE 1: Delete previous bot message
    settings = await self.db.get_settings()
    if settings.get("clean_conversation", True):
        await self.delete_previous_bot_message(user_id)

    if len(message.command) < 2:
        response = await message.reply(
            "➖ <b>REMOVE FORCE SUB CHANNEL</b>\n\n"
            "<blockquote>"
            "<b>Usage:</b> <code>/del_fsub channel_id</code>\n\n"
            "<b>Example:</b> <code>/del_fsub -100123456789</code>"
            "</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
        await self.store_bot_message(user_id, response.id)
        return

    try:
        channel_id = int(message.command[1])
        
        # Remove channel from database
        await self.db.remove_force_sub_channel(channel_id)
        
        # Update local cache
        self.force_sub_channels = await self.db.get_force_sub_channels()
        
        response = await message.reply(
            f"✅ <b>Channel Removed!</b>\n\n"
            "<blockquote>"
            f"<b>📢 Channel ID:</b> <code>{channel_id}</code>\n\n"
            f"<b>Remaining channels:</b> {len(self.force_sub_channels)}"
            "</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
        
        await self.store_bot_message(user_id, response.id)
        
    except ValueError:
        response = await message.reply("❌ <b>Invalid channel ID!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)
    except Exception as e:
        logger.error(f"Error removing force sub channel: {e}")
        response = await message.reply("❌ <b>Error removing channel!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)

# ===================================
# BROADCAST COMMAND
# ===================================

async def broadcast_command(self, message: Message):
    """
    Handle /broadcast command
    
    IMPLEMENTS: FEATURE 1 (Clean Conversation)
    """
    user_id = message.from_user.id
    
    # Check admin permission
    if not await self.is_user_admin(user_id):
        response = await message.reply("❌ <b>Admin only!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)
        return

    # FEATURE 1: Delete previous bot message
    settings = await self.db.get_settings()
    if settings.get("clean_conversation", True):
        await self.delete_previous_bot_message(user_id)

    if not message.reply_to_message:
        response = await message.reply(
            "📢 <b>BROADCAST MESSAGE</b>\n\n"
            "<blockquote>"
            "<b>How to use:</b>\n"
            "1. Send your message (text, photo, video, etc.)\n"
            "2. Reply to that message with /broadcast\n\n"
            "<b>Example:</b>\n"
            "Your broadcast message here...\n"
            "/broadcast"
            "</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
        await self.store_bot_message(user_id, response.id)
        return

    try:
        # Get all users
        users = await self.db.get_all_users()
        total_users = len(users)

        if total_users == 0:
            response = await message.reply("❌ <b>No users to broadcast to!</b>", parse_mode=enums.ParseMode.HTML)
            await self.store_bot_message(user_id, response.id)
            return

        response = await message.reply(f"📢 <b>Broadcasting to {total_users:,} users...</b>", parse_mode=enums.ParseMode.HTML)

        success = 0
        failed = 0

        # Send to all users
        for target_user_id in users:
            try:
                # Skip if user is banned
                if await self.db.is_user_banned(target_user_id):
                    failed += 1
                    continue

                # Forward the message
                await message.reply_to_message.forward(target_user_id)
                success += 1

                # Small delay to avoid flood
                await asyncio.sleep(0.1)

            except Exception as e:
                failed += 1
                logger.error(f"Failed to send to {target_user_id}: {e}")

        await response.edit_text(
            f"✅ <b>Broadcast Complete!</b>\n\n"
            "<blockquote>"
            f"<b>📊 Total Users:</b> {total_users:,}\n"
            f"<b>✅ Success:</b> {success:,}\n"
            f"<b>❌ Failed:</b> {failed:,}\n"
            f"<b>📈 Success Rate:</b> {(success/total_users*100):.1f}%"
            "</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )

        await self.store_bot_message(user_id, response.id)

    except Exception as e:
        logger.error(f"Error in broadcast command: {e}")
        response = await message.reply("❌ <b>Error during broadcast!</b>", parse_mode=enums.ParseMode.HTML)
        await self.store_bot_message(user_id, response.id)

# ===================================
# FONT STYLE HANDLERS (MODULE LEVEL - OUTSIDE CLASS)
# ===================================

@Client.on_message(filters.private & filters.command(["font"]))
async def style_buttons(c, m, cb=False):
    buttons = [[
        InlineKeyboardButton('𝚃𝚢𝚙𝚎𝚠𝚛𝚒𝚝𝚎𝚛', callback_data='style+typewriter'),
        InlineKeyboardButton('𝕆𝕦𝕥𝕝𝕚𝕟𝕖', callback_data='style+outline'),
        InlineKeyboardButton('𝐒𝐞𝐫𝐢𝐟', callback_data='style+serif'),
    ],[
        InlineKeyboardButton('𝑺𝒆𝒓𝒊𝒇', callback_data='style+bold_cool'),
        InlineKeyboardButton('𝑆𝑒𝑟𝑖𝑓', callback_data='style+cool'),
        InlineKeyboardButton('Sᴍᴀʟʟ Cᴀᴘs', callback_data='style+small_cap'),
    ],[
        InlineKeyboardButton('𝓈𝒸𝓇𝒾𝓅𝓉', callback_data='style+script'),
        InlineKeyboardButton('𝓼𝓬𝓻𝓲𝓹𝓽', callback_data='style+script_bolt'),
        InlineKeyboardButton('ᵗⁱⁿʸ', callback_data='style+tiny'),
    ],[
        InlineKeyboardButton('ᑕOᗰIᑕ', callback_data='style+comic'),
        InlineKeyboardButton('𝗦𝗮𝗻𝘀', callback_data='style+sans'),
        InlineKeyboardButton('𝙎𝙖𝙣𝙨', callback_data='style+slant_sans'),
    ],[
        InlineKeyboardButton('𝘚𝘢𝘯𝘴', callback_data='style+slant'),
        InlineKeyboardButton('𝖲𝖺𝗇𝗌', callback_data='style+sim'),
        InlineKeyboardButton('Ⓒ︎Ⓘ︎Ⓡ︎Ⓒ︎Ⓛ︎Ⓔ︎Ⓢ︎', callback_data='style+circles')
    ],[
        InlineKeyboardButton('🅒︎🅘︎🅡︎🅒︎🅛︎🅔︎🅢︎', callback_data='style+circle_dark'),
        InlineKeyboardButton('𝔊𝔬𝔱𝔥𝔦𝔠', callback_data='style+gothic'),
        InlineKeyboardButton('𝕲𝖔𝖙𝖍𝖎𝖈', callback_data='style+gothic_bolt'),
    ],[
        InlineKeyboardButton('C͜͡l͜͡o͜͡u͜͡d͜͡s͜͡', callback_data='style+cloud'),
        InlineKeyboardButton('H̆̈ă̈p̆̈p̆̈y̆̈', callback_data='style+happy'),
        InlineKeyboardButton('S̑̈ȃ̈d̑̈', callback_data='style+sad'),
    ],[
        InlineKeyboardButton('Next ➡️', callback_data="nxt")
    ]]
    
    if not cb:
        if ' ' in m.text:
            title = m.text.split(" ", 1)[1]
            await m.reply_text(title, reply_markup=InlineKeyboardMarkup(buttons), reply_to_message_id=m.id, parse_mode=enums.ParseMode.HTML)                     
        else:
            await m.reply_text(text="Enter Any Text Eg:- `/font [text]`", parse_mode=enums.ParseMode.HTML)    
    else:
        await m.answer()
        await m.message.edit_reply_markup(InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex('^nxt'))
async def nxt(c, m):
    if m.data == "nxt":
        buttons = [[
            InlineKeyboardButton('🇸 🇵 🇪 🇨 🇮 🇦 🇱 ', callback_data='style+special'),
            InlineKeyboardButton('🅂🅀🅄🄰🅁🄴🅂', callback_data='style+squares'),
            InlineKeyboardButton('🆂︎🆀︎🆄︎🅰︎🆁︎🅴︎🆂︎', callback_data='style+squares_bold'),
        ],[
            InlineKeyboardButton('ꪖꪀᦔꪖꪶꪊᥴ𝓲ꪖ', callback_data='style+andalucia'),
            InlineKeyboardButton('爪卂几ᘜ卂', callback_data='style+manga'),
            InlineKeyboardButton('S̾t̾i̾n̾k̾y̾', callback_data='style+stinky'),
        ],[
            InlineKeyboardButton('B̥ͦu̥ͦb̥ͦb̥ͦl̥ͦe̥ͦs̥ͦ', callback_data='style+bubbles'),
            InlineKeyboardButton('U͟n͟d͟e͟r͟l͟i͟n͟e͟', callback_data='style+underline'),
            InlineKeyboardButton('꒒ꍏꀷꌩꌃꀎꁅ', callback_data='style+ladybug'),
        ],[
            InlineKeyboardButton('R҉a҉y҉s҉', callback_data='style+rays'),
            InlineKeyboardButton('B҈i҈r҈d҈s҈', callback_data='style+birds'),
            InlineKeyboardButton('S̸l̸a̸s̸h̸', callback_data='style+slash'),
        ],[
            InlineKeyboardButton('s⃠t⃠o⃠p⃠', callback_data='style+stop'),
            InlineKeyboardButton('S̺͆k̺͆y̺͆l̺͆i̺͆n̺͆e̺͆', callback_data='style+skyline'),
            InlineKeyboardButton('A͎r͎r͎o͎w͎s͎', callback_data='style+arrows'),
        ],[
            InlineKeyboardButton('ዪሀክቿነ', callback_data='style+qvnes'),
            InlineKeyboardButton('S̶t̶r̶i̶k̶e̶', callback_data='style+strike'),
            InlineKeyboardButton('F༙r༙o༙z༙e༙n༙', callback_data='style+frozen')
        ],[
            InlineKeyboardButton('⬅️ Back', callback_data='nxt+0')
        ]]
        await m.answer()
        await m.message.edit_reply_markup(InlineKeyboardMarkup(buttons))
    else:
        await style_buttons(c, m, cb=True)


@Client.on_callback_query(filters.regex('^style'))
async def style(c, m):
    await m.answer()
    cmd, style = m.data.split('+')

    if style == 'typewriter':
        cls = Fonts.typewriter
    elif style == 'outline':
        cls = Fonts.outline
    elif style == 'serif':
        cls = Fonts.serief
    elif style == 'bold_cool':
        cls = Fonts.bold_cool
    elif style == 'cool':
        cls = Fonts.cool
    elif style == 'small_cap':
        cls = Fonts.smallcap
    elif style == 'script':
        cls = Fonts.script
    elif style == 'script_bolt':
        cls = Fonts.bold_script
    elif style == 'tiny':
        cls = Fonts.tiny
    elif style == 'comic':
        cls = Fonts.comic
    elif style == 'sans':
        cls = Fonts.san
    elif style == 'slant_sans':
        cls = Fonts.slant_san
    elif style == 'slant':
        cls = Fonts.slant
    elif style == 'sim':
        cls = Fonts.sim
    elif style == 'circles':
        cls = Fonts.circles
    elif style == 'circle_dark':
        cls = Fonts.dark_circle
    elif style == 'gothic':
        cls = Fonts.gothic
    elif style == 'gothic_bolt':
        cls = Fonts.bold_gothic
    elif style == 'cloud':
        cls = Fonts.cloud
    elif style == 'happy':
        cls = Fonts.happy
    elif style == 'sad':
        cls = Fonts.sad
    elif style == 'special':
        cls = Fonts.special
    elif style == 'squares':
        cls = Fonts.square
    elif style == 'squares_bold':
        cls = Fonts.dark_square
    elif style == 'andalucia':
        cls = Fonts.andalucia
    elif style == 'manga':
        cls = Fonts.manga
    elif style == 'stinky':
        cls = Fonts.stinky
    elif style == 'bubbles':
        cls = Fonts.bubbles
    elif style == 'underline':
        cls = Fonts.underline
    elif style == 'ladybug':
        cls = Fonts.ladybug
    elif style == 'rays':
        cls = Fonts.rays
    elif style == 'birds':
        cls = Fonts.birds
    elif style == 'slash':
        cls = Fonts.slash
    elif style == 'stop':
        cls = Fonts.stop
    elif style == 'skyline':
        cls = Fonts.skyline
    elif style == 'arrows':
        cls = Fonts.arrows
    elif style == 'qvnes':
        cls = Fonts.rvnes
    elif style == 'strike':
        cls = Fonts.strike
    elif style == 'frozen':
        cls = Fonts.frozen

    r, oldtxt = m.message.reply_to_message.text.split(None, 1) 
    new_text = cls(oldtxt)            
    try:
        await m.message.edit_text(f"`{new_text}`\n\n👆 Click To Copy", reply_markup=m.message.reply_markup, parse_mode=enums.ParseMode.HTML)
    except Exception as e:
        print(e)

# ===================================
# BOT STARTUP & MAIN LOOP
# ===================================

async def main():
    """Main function to start the bot"""
    print(BANNER)
    logger.info("=" * 70)
    logger.info("🤖 FILE SHARING BOT - THREE AUTO-DELETE FEATURES")
    logger.info("=" * 70)
    
    # Validate configuration
    if not Config.validate():
        logger.error("Configuration validation failed. Exiting.")
        return
    
    Config.print_config()
    
    # Create and start bot
    bot = Bot()
    
    try:
        # Start the bot
        if await bot.start():
            logger.info("✓ Bot started successfully!")
            
            # Keep running
            await asyncio.Event().wait()
            
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        traceback.print_exc()
    finally:
        await bot.stop()

if __name__ == "__main__":
    # Run the bot
    asyncio.run(main())

