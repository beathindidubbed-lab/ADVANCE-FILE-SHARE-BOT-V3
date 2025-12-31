#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 TELEGRAM FILE SHARING BOT - ALL FEATURES IN ONE FILE
Complete implementation based on specification
File: bot.py (~3000 lines)
Author: Auto-generated from specification
Date: 2024
"""

# ===================================
# SECTION 1: IMPORTS & SETUP (Lines 1-100)
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
from typing import List, Dict, Tuple, Optional, Union
from urllib.parse import urlparse

# Pyrogram imports
from pyrogram import Client, filters, enums
from pyrogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery, InputMediaPhoto, ChatPermissions
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
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
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
║               𝙁𝙄𝙇𝙀 𝙎𝙃𝘼𝙍𝙄𝙉𝙂 𝘽𝙊𝙏 - 𝙎𝙄𝙉𝙂𝙇𝙀 𝙁𝙄𝙇𝙀 𝙑𝙀𝙍𝙎𝙄𝙊𝙉                      ║
║                       ~ 𝘾𝙊𝙈𝙋𝙇𝙀𝙏𝙀 𝙁𝙀𝘼𝙏𝙐𝙍𝙀𝙎 ~                              ║
╚════════════════════════════════════════════════════════════════════════════╝
"""

# Global constants
MAX_BATCH_SIZE = 100
MAX_SPECIAL_FILES = 50
MAX_CUSTOM_BATCH = 50
AUTO_DELETE_TIMES = [60, 300, 600, 1800, 3600]  # 1min, 5min, 10min, 30min, 1hour
DEFAULT_BOT_PICS = [
    "https://telegra.ph/file/1c2c2c2c2c2c2c2c2c2c2.jpg",
    "https://telegra.ph/file/2d2d2d2d2d2d2d2d2d2d.jpg",
    "https://telegra.ph/file/3e3e3e3e3e3e3e3e3e3e.jpg"
]


# ===================================
# SECTION 2: CONFIGURATION CLASS (Lines 101-200)
# ===================================

class Config:
    """Configuration class for environment variables"""
    
    # Telegram API
    API_ID = int(os.environ.get("API_ID", 0))
    API_HASH = os.environ.get("API_HASH", "")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
    
    # Database
    DATABASE_URL = os.environ.get("DATABASE_URL", "")
    DATABASE_NAME = os.environ.get("DATABASE_NAME", "AdvanceAutoFilterBot")
    
    # Bot settings
    BOT_NAME = os.environ.get("BOT_NAME", "File Share Bot")
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
        logger.info(f"Web Server: {cls.WEB_SERVER}")
        logger.info(f"Port: {cls.PORT}")


# ===================================
# SECTION 3: DATABASE CLASS (Lines 201-400)
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
            
            # Create indexes
            await self.users.create_index("user_id", unique=True)
            await self.banned.create_index("user_id", unique=True)
            await self.settings.create_index("key", unique=True)
            await self.special_links.create_index("link_id", unique=True)
            await self.channels.create_index("channel_id", unique=True)
            await self.force_sub.create_index("channel_id", unique=True)
            
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
            "joined_date": datetime.datetime.utcnow(),
            "last_active": datetime.datetime.utcnow()
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
            {"$set": {"last_active": datetime.datetime.utcnow()}}
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
            "banned_date": datetime.datetime.utcnow()
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
                "help_text": "➪ I ᴀᴍ ᴀ ᴘʀɪᴠᴀᴛᴇ ғɪʟᴇ sʜᴀʀɪɴɢ ʙᴏᴛ, ᴍᴇᴀɴᴛ ᴛᴏ ᴘʀᴏᴠɪᴅᴇ ғɪʟᴇs ᴀɴᴅ ɴᴇᴄᴇssᴀʀʏ sᴛᴜғғ ᴛʜʀᴏᴜɢʜ sᴘᴇᴄɪᴀʟ ʟɪɴᴋ ғᴏʀ sᴘᴇᴄɪғɪᴄ ᴄʜᴀɴɴᴇʟs.",
                "about_text": "",
                "db_channel_id": None
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
            "created_date": datetime.datetime.utcnow()
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
            "added_date": datetime.datetime.utcnow()
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


# ===================================
# SECTION 4: HELPER FUNCTIONS (Lines 401-600)
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

async def is_subscribed(client: Client, user_id: int, channel_ids: list) -> bool:
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

async def get_messages(client: Client, chat_id: int, message_ids: list):
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


# ===================================
# SECTION 5: BOT CLASS (Lines 601-800)
# ===================================

class Bot(Client):
    """Main Bot Class"""
    
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
        
        # Register all handlers
        self.register_all_handlers()
        
        # Print bot info
        me = await self.get_me()
        Config.BOT_USERNAME = me.username
        logger.info(f"✓ Bot started as @{me.username}")
        logger.info(f"✓ Bot ID: {me.id}")
        
        return True
    
    async def stop(self, *args):
        """Stop the bot"""
        await self.db.close()
        await super().stop()
        logger.info("✓ Bot stopped")
    
    def register_all_handlers(self):
        """Register ALL handlers in one place"""
        
        # === START COMMAND ===
        @self.on_message(filters.command("start") & filters.private)
        async def start_handler(client, message):
            await start_command(self, message)
        
        # === HELP COMMAND ===
        @self.on_message(filters.command("help") & filters.private)
        async def help_handler(client, message):
            await help_command(self, message)
        
        # === ABOUT COMMAND ===
        @self.on_message(filters.command("about") & filters.private)
        async def about_handler(client, message):
            await about_command(self, message)
        
        # === ADMIN COMMANDS ===
        
        # Users command
        @self.on_message(filters.command("users") & filters.private & filters.user(Config.ADMINS))
        async def users_handler(client, message):
            await users_command(self, message)
        
        # Broadcast command
        @self.on_message(filters.command("broadcast") & filters.private & filters.user(Config.ADMINS))
        async def broadcast_handler(client, message):
            await broadcast_command(self, message)
        
        # Ban command
        @self.on_message(filters.command("ban") & filters.private & filters.user(Config.ADMINS))
        async def ban_handler(client, message):
            await ban_command(self, message)
        
        # Unban command
        @self.on_message(filters.command("unban") & filters.private & filters.user(Config.ADMINS))
        async def unban_handler(client, message):
            await unban_command(self, message)
        
        # Stats command
        @self.on_message(filters.command("stats") & filters.private & filters.user(Config.ADMINS))
        async def stats_handler(client, message):
            await stats_command(self, message)
        
        # File Management Commands
        @self.on_message(filters.command("genlink") & filters.private & filters.user(Config.ADMINS))
        async def genlink_handler(client, message):
            await genlink_command(self, message)
        
        @self.on_message(filters.command("batch") & filters.private & filters.user(Config.ADMINS))
        async def batch_handler(client, message):
            await batch_command(self, message)
        
        @self.on_message(filters.command("custom_batch") & filters.private & filters.user(Config.ADMINS))
        async def custom_batch_handler(client, message):
            await custom_batch_command(self, message)
        
        @self.on_message(filters.command("special_link") & filters.private & filters.user(Config.ADMINS))
        async def special_link_handler(client, message):
            await special_link_command(self, message)
        
        # Channel Management Commands
        @self.on_message(filters.command("setchannel") & filters.private & filters.user(Config.ADMINS))
        async def setchannel_handler(client, message):
            await setchannel_command(self, message)
        
        @self.on_message(filters.command("checkchannel") & filters.private & filters.user(Config.ADMINS))
        async def checkchannel_handler(client, message):
            await checkchannel_command(self, message)
        
        @self.on_message(filters.command("removechannel") & filters.private & filters.user(Config.ADMINS))
        async def removechannel_handler(client, message):
            await removechannel_command(self, message)
        
        # Settings Commands
        @self.on_message(filters.command("settings") & filters.private & filters.user(Config.ADMINS))
        async def settings_handler(client, message):
            await settings_command(self, message)
        
        @self.on_message(filters.command("files") & filters.private & filters.user(Config.ADMINS))
        async def files_handler(client, message):
            await files_command(self, message)
        
        @self.on_message(filters.command("auto_del") & filters.private & filters.user(Config.ADMINS))
        async def auto_del_handler(client, message):
            await auto_del_command(self, message)
        
        @self.on_message(filters.command("forcesub") & filters.private & filters.user(Config.ADMINS))
        async def forcesub_handler(client, message):
            await forcesub_command(self, message)
        
        @self.on_message(filters.command("req_fsub") & filters.private & filters.user(Config.ADMINS))
        async def req_fsub_handler(client, message):
            await req_fsub_command(self, message)
        
        @self.on_message(filters.command("botsettings") & filters.private & filters.user(Config.ADMINS))
        async def botsettings_handler(client, message):
            await botsettings_command(self, message)
        
        # Utility Commands
        @self.on_message(filters.command("shortener") & filters.private & filters.user(Config.ADMINS))
        async def shortener_handler(client, message):
            await shortener_command(self, message)
        
        @self.on_message(filters.command("ping") & filters.private)
        async def ping_handler(client, message):
            await ping_command(self, message)
        
        # Force Subscribe Commands (for admins)
        @self.on_message(filters.command("fsub_chnl") & filters.private & filters.user(Config.ADMINS))
        async def fsub_chnl_handler(client, message):
            await fsub_chnl_command(self, message)
        
        @self.on_message(filters.command("add_fsub") & filters.private & filters.user([Config.OWNER_ID]))
        async def add_fsub_handler(client, message):
            await add_fsub_command(self, message)
        
        @self.on_message(filters.command("del_fsub") & filters.private & filters.user([Config.OWNER_ID]))
        async def del_fsub_handler(client, message):
            await del_fsub_command(self, message)
        
        # Done command (for batch operations)
        @self.on_message(filters.command("done") & filters.private & filters.user(Config.ADMINS))
        async def done_handler(client, message):
            await done_command(self, message)
        
        # Text message handlers for interactive commands
        @self.on_message(filters.private & filters.user(Config.ADMINS))
        async def text_handler(client, message):
            await text_message_handler(self, message)
        
        logger.info("✓ All handlers registered")
    
    async def setup_callbacks(self):
        """Setup callback query handlers"""
        # This method will be called after bot starts
        
        @self.on_callback_query()
        async def callback_handler(client, query):
            await handle_callback_query(self, query)


# ===================================
# SECTION 6: START COMMAND (Lines 801-1100)
# ===================================

async def start_command(client: Bot, message: Message):
    """Handle /start command"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    # Check if user is banned
    if await client.db.is_user_banned(user_id):
        await message.reply("🚫 <b>You are banned from using this bot!</b>", parse_mode=enums.ParseMode.HTML)
        return
    
    # Add user to database
    await client.db.add_user(
        user_id=user_id,
        first_name=message.from_user.first_name,
        username=message.from_user.username
    )
    
    # Update activity
    await client.db.update_user_activity(user_id)
    
    # Check for start arguments
    if len(message.command) > 1:
        start_arg = message.command[1]
        await handle_start_argument(client, message, start_arg)
        return
    
    # Check force subscribe
    if client.force_sub_channels:
        is_subscribed = await is_subscribed(client, user_id, client.force_sub_channels)
        if not is_subscribed:
            await show_force_subscribe(client, message)
            return
    
    # Show welcome message
    await show_welcome_message(client, message)

async def handle_start_argument(client: Bot, message: Message, start_arg: str):
    """Handle start arguments (file links)"""
    user_id = message.from_user.id
    
    try:
        # Decode the argument
        decoded = await decode(start_arg)
        
        # Check force subscribe
        if client.force_sub_channels:
            is_subscribed = await is_subscribed(client, user_id, client.force_sub_channels)
            if not is_subscribed:
                await show_force_subscribe(client, message)
                return
        
        # Check if it's a special link
        if decoded.startswith("special_"):
            await handle_special_link(client, message, decoded)
            return
        
        # Check if it's a custom batch
        if decoded.startswith("custombatch_"):
            await handle_custom_batch(client, message, decoded)
            return
        
        # Handle regular file or batch
        if decoded.startswith("get-"):
            parts = decoded.split("-")[1:]
            
            if len(parts) == 1:
                # Single file
                await send_single_file(client, message, decoded)
            elif len(parts) == 2:
                # Batch files
                await send_batch_files(client, message, decoded)
            else:
                # Multiple custom files
                await send_multiple_files(client, message, decoded)
        
    except Exception as e:
        logger.error(f"Error handling start argument: {e}")
        await message.reply(
            "❌ <b>Invalid link or error processing request!</b>\n\n"
            "The link may be expired or invalid. Please contact admin.",
            parse_mode=enums.ParseMode.HTML
        )

async def show_welcome_message(client: Bot, message: Message):
    """Show welcome message with image"""
    user = message.from_user
    
    # Get settings
    settings = await client.db.get_settings()
    welcome_text = settings.get("welcome_text", "")
    bot_pics = settings.get("bot_pics", Config.BOT_PICS)
    
    # Default welcome text if not set
    if not welcome_text:
        welcome_text = (
            f"⚡ Hey, {user.first_name}!\n\n"
            "I am an advance file share bot 🤖\n"
            "The best part is I also support\n"
            "request forcesub feature.\n\n"
            "To know detailed information click\n"
            "about me button below.\n\n"
            "Made with ❤️"
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
    
    # Create buttons
    buttons = []
    
    # Row 1: Help and About
    buttons.append([
        InlineKeyboardButton("📚 Help", callback_data="help"),
        InlineKeyboardButton("ℹ️ About", callback_data="about")
    ])
    
    # Row 2: Updates Channel (if configured)
    if Config.UPDATE_CHANNEL:
        buttons.append([
            InlineKeyboardButton("📢 Updates Channel", url=f"https://t.me/{Config.UPDATE_CHANNEL}")
        ])
    
    # Row 3: Support Chat (if configured)
    if Config.SUPPORT_CHAT:
        buttons.append([
            InlineKeyboardButton("💬 Support Chat", url=f"https://t.me/{Config.SUPPORT_CHAT}")
        ])
    
    # Add custom buttons from settings
    custom_button_str = settings.get("custom_button", "")
    if custom_button_str:
        custom_buttons = parse_button_string(custom_button_str)
        buttons.extend(custom_buttons)
    
    # Last row: Close button
    buttons.append([
        InlineKeyboardButton("🔒 Close", callback_data="close")
    ])
    
    keyboard = InlineKeyboardMarkup(buttons)
    
    # Try to send with image
    try:
        # Get random image
        random_pic = get_random_pic(bot_pics)
        
        # Send photo with caption
        await message.reply_photo(
            photo=random_pic,
            caption=welcome_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"Error sending welcome image: {e}")
        # Fallback to text only
        await message.reply(
            welcome_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True
        )

async def show_force_subscribe(client: Bot, message: Message):
    """Show force subscribe message"""
    user = message.from_user
    
    # Create buttons for each channel
    buttons = []
    for channel in client.force_sub_channels:
        channel_id = channel.get("channel_id")
        username = channel.get("channel_username")
        
        if username:
            button_text = f"📢 Join {username}"
            button_url = f"https://t.me/{username}"
        else:
            # Try to get channel info
            try:
                chat = await client.get_chat(channel_id)
                button_text = f"📢 Join {chat.title}"
                button_url = f"https://t.me/{chat.username}" if chat.username else f"t.me/c/{str(channel_id)[4:]}"
            except:
                button_text = f"📢 Join Channel"
                button_url = f"t.me/c/{str(channel_id)[4:]}"
        
        buttons.append([InlineKeyboardButton(button_text, url=button_url)])
    
    # Add try again button
    if Config.REQUEST_FSUB:
        buttons.append([
            InlineKeyboardButton("📢 Request to Join Channel", callback_data="request_join")
        ])
    else:
        buttons.append([
            InlineKeyboardButton("🔄 Try Again", callback_data="start")
        ])
    
    keyboard = InlineKeyboardMarkup(buttons)
    
    message_text = (
        f"⚠️ <b>JOIN OUR CHANNEL</b>\n\n"
        f"Dear {user.first_name},\n\n"
        "You need to join our channel to use this bot!\n\n"
        "Please join the channel(s) and click Try Again."
    )
    
    await message.reply(
        message_text,
        reply_markup=keyboard,
        parse_mode=enums.ParseMode.HTML
    )

async def send_single_file(client: Bot, message: Message, encoded: str):
    """Send single file to user"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    try:
        # Decode the link
        decoded = await decode(encoded)
        file_id = int(decoded.split("-")[1])
        
        # Get database channel
        db_channel = await client.db.get_db_channel()
        if not db_channel:
            await message.reply("❌ Database channel not configured!")
            return
        
        # Calculate original message ID
        channel_id = abs(db_channel)
        msg_id = file_id // channel_id
        
        # Get the file message
        try:
            file_msg = await client.get_messages(db_channel, msg_id)
            if not file_msg:
                raise Exception("Message not found")
        except Exception as e:
            await message.reply("❌ File not found or deleted!")
            return
        
        # Get settings
        settings = await client.db.get_settings()
        
        # Prepare caption
        caption = file_msg.caption or ""
        if settings.get("hide_caption"):
            caption = ""
        elif settings.get("custom_caption"):
            # Apply custom caption template
            file_info = await get_file_info(file_msg)
            caption = settings["custom_caption"].format(
                filename=file_info["file_name"],
                filesize=format_file_size(file_info["file_size"]),
                previouscaption=caption
            )
        
        # Prepare buttons
        buttons = []
        custom_button_str = settings.get("custom_button", "")
        if custom_button_str and settings.get("channel_button", True):
            custom_buttons = parse_button_string(custom_button_str)
            buttons.extend(custom_buttons)
        
        keyboard = InlineKeyboardMarkup(buttons) if buttons else None
        
        # Send the file with protection settings
        protect_content = settings.get("protect_content", True)
        
        # Determine message type and send accordingly
        if file_msg.photo:
            sent_msg = await client.send_photo(
                chat_id=chat_id,
                photo=file_msg.photo.file_id,
                caption=caption,
                reply_markup=keyboard,
                protect_content=protect_content,
                parse_mode=enums.ParseMode.HTML
            )
        elif file_msg.video:
            sent_msg = await client.send_video(
                chat_id=chat_id,
                video=file_msg.video.file_id,
                caption=caption,
                reply_markup=keyboard,
                protect_content=protect_content,
                parse_mode=enums.ParseMode.HTML
            )
        elif file_msg.document:
            sent_msg = await client.send_document(
                chat_id=chat_id,
                document=file_msg.document.file_id,
                caption=caption,
                reply_markup=keyboard,
                protect_content=protect_content,
                parse_mode=enums.ParseMode.HTML
            )
        elif file_msg.audio:
            sent_msg = await client.send_audio(
                chat_id=chat_id,
                audio=file_msg.audio.file_id,
                caption=caption,
                reply_markup=keyboard,
                protect_content=protect_content,
                parse_mode=enums.ParseMode.HTML
            )
        else:
            await message.reply("❌ Unsupported file type!")
            return
        
        # Handle auto-delete if enabled
        if settings.get("auto_delete", False):
            delete_time = settings.get("auto_delete_time", 300)
            await schedule_auto_delete(client, sent_msg, delete_time, encoded)
        
        # Update user activity
        await client.db.update_user_activity(user_id)
        
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await send_single_file(client, message, encoded)
    except Exception as e:
        logger.error(f"Error sending single file: {e}")
        await message.reply("❌ Error sending file!")

async def send_batch_files(client: Bot, message: Message, encoded: str):
    """Send batch files to user"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    try:
        # Decode the link
        decoded = await decode(encoded)
        parts = decoded.split("-")[1:]
        
        if len(parts) != 2:
            await message.reply("❌ Invalid batch link!")
            return
        
        start_id = int(parts[0])
        end_id = int(parts[1])
        
        # Get database channel
        db_channel = await client.db.get_db_channel()
        if not db_channel:
            await message.reply("❌ Database channel not configured!")
            return
        
        # Calculate message IDs
        channel_id = abs(db_channel)
        start_msg_id = start_id // channel_id
        end_msg_id = end_id // channel_id
        
        # Validate range
        if start_msg_id > end_msg_id:
            await message.reply("❌ Invalid range!")
            return
        
        total_files = end_msg_id - start_msg_id + 1
        
        if total_files > MAX_BATCH_SIZE:
            await message.reply(f"❌ Batch too large! Maximum {MAX_BATCH_SIZE} files allowed.")
            return
        
        # Send progress message
        progress_msg = await message.reply(
            f"📦 <b>Sending {total_files} files...</b>\n\n"
            f"Progress: {generate_progress_bar(0)}",
            parse_mode=enums.ParseMode.HTML
        )
        
        # Get settings
        settings = await client.db.get_settings()
        
        # Send files
        sent_count = 0
        for msg_id in range(start_msg_id, end_msg_id + 1):
            try:
                file_msg = await client.get_messages(db_channel, msg_id)
                if not file_msg:
                    continue
                
                # Prepare caption
                caption = file_msg.caption or ""
                if settings.get("hide_caption"):
                    caption = ""
                
                # Prepare buttons
                buttons = []
                custom_button_str = settings.get("custom_button", "")
                if custom_button_str and settings.get("channel_button", True):
                    custom_buttons = parse_button_string(custom_button_str)
                    buttons.extend(custom_buttons)
                
                keyboard = InlineKeyboardMarkup(buttons) if buttons else None
                
                # Send file based on type
                protect_content = settings.get("protect_content", True)
                
                if file_msg.photo:
                    await client.send_photo(
                        chat_id=chat_id,
                        photo=file_msg.photo.file_id,
                        caption=caption,
                        reply_markup=keyboard,
                        protect_content=protect_content,
                        parse_mode=enums.ParseMode.HTML
                    )
                elif file_msg.video:
                    await client.send_video(
                        chat_id=chat_id,
                        video=file_msg.video.file_id,
                        caption=caption,
                        reply_markup=keyboard,
                        protect_content=protect_content,
                        parse_mode=enums.ParseMode.HTML
                    )
                elif file_msg.document:
                    await client.send_document(
                        chat_id=chat_id,
                        document=file_msg.document.file_id,
                        caption=caption,
                        reply_markup=keyboard,
                        protect_content=protect_content,
                        parse_mode=enums.ParseMode.HTML
                    )
                
                sent_count += 1
                
                # Update progress every 5 files
                if sent_count % 5 == 0 or sent_count == total_files:
                    progress = (sent_count / total_files) * 100
                    try:
                        await progress_msg.edit_text(
                            f"📦 <b>Sending {total_files} files...</b>\n\n"
                            f"Progress: {generate_progress_bar(progress)}\n"
                            f"Sent: {sent_count}/{total_files}",
                            parse_mode=enums.ParseMode.HTML
                        )
                    except:
                        pass
                
                # Small delay to avoid flood
                await asyncio.sleep(0.5)
                
            except FloodWait as e:
                await asyncio.sleep(e.value)
                continue
            except Exception as e:
                logger.error(f"Error sending file {msg_id}: {e}")
                continue
        
        # Delete progress message
        try:
            await progress_msg.delete()
        except:
            pass
        
        # Send completion message
        await message.reply(
            f"✅ <b>Batch completed!</b>\n\n"
            f"Successfully sent {sent_count} files.",
            parse_mode=enums.ParseMode.HTML
        )
        
        # Update user activity
        await client.db.update_user_activity(user_id)
        
    except Exception as e:
        logger.error(f"Error sending batch files: {e}")
        await message.reply("❌ Error sending batch files!")

async def send_multiple_files(client: Bot, message: Message, encoded: str):
    """Send multiple custom files"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    try:
        # Decode the link
        decoded = await decode(encoded)
        
        if decoded.startswith("custombatch_"):
            # Custom batch format: custombatch_id1-id2-id3
            file_ids = [int(x) for x in decoded.split("_")[1].split("-")]
        else:
            # Old format: get-id1-id2-id3
            file_ids = [int(x) for x in decoded.split("-")[1:]]
        
        # Get database channel
        db_channel = await client.db.get_db_channel()
        if not db_channel:
            await message.reply("❌ Database channel not configured!")
            return
        
        # Calculate message IDs
        channel_id = abs(db_channel)
        msg_ids = [fid // channel_id for fid in file_ids]
        
        total_files = len(msg_ids)
        
        # Send progress message
        progress_msg = await message.reply(
            f"📦 <b>Sending {total_files} files...</b>\n\n"
            f"Progress: {generate_progress_bar(0)}",
            parse_mode=enums.ParseMode.HTML
        )
        
        # Get settings
        settings = await client.db.get_settings()
        
        # Send files
        sent_count = 0
        for msg_id in msg_ids:
            try:
                file_msg = await client.get_messages(db_channel, msg_id)
                if not file_msg:
                    continue
                
                # Prepare caption
                caption = file_msg.caption or ""
                if settings.get("hide_caption"):
                    caption = ""
                
                # Prepare buttons
                buttons = []
                custom_button_str = settings.get("custom_button", "")
                if custom_button_str and settings.get("channel_button", True):
                    custom_buttons = parse_button_string(custom_button_str)
                    buttons.extend(custom_buttons)
                
                keyboard = InlineKeyboardMarkup(buttons) if buttons else None
                
                # Send file based on type
                protect_content = settings.get("protect_content", True)
                
                if file_msg.photo:
                    await client.send_photo(
                        chat_id=chat_id,
                        photo=file_msg.photo.file_id,
                        caption=caption,
                        reply_markup=keyboard,
                        protect_content=protect_content,
                        parse_mode=enums.ParseMode.HTML
                    )
                elif file_msg.video:
                    await client.send_video(
                        chat_id=chat_id,
                        video=file_msg.video.file_id,
                        caption=caption,
                        reply_markup=keyboard,
                        protect_content=protect_content,
                        parse_mode=enums.ParseMode.HTML
                    )
                elif file_msg.document:
                    await client.send_document(
                        chat_id=chat_id,
                        document=file_msg.document.file_id,
                        caption=caption,
                        reply_markup=keyboard,
                        protect_content=protect_content,
                        parse_mode=enums.ParseMode.HTML
                    )
                
                sent_count += 1
                
                # Update progress
                if sent_count % 5 == 0 or sent_count == total_files:
                    progress = (sent_count / total_files) * 100
                    try:
                        await progress_msg.edit_text(
                            f"📦 <b>Sending {total_files} files...</b>\n\n"
                            f"Progress: {generate_progress_bar(progress)}\n"
                            f"Sent: {sent_count}/{total_files}",
                            parse_mode=enums.ParseMode.HTML
                        )
                    except:
                        pass
                
                # Small delay
                await asyncio.sleep(0.5)
                
            except FloodWait as e:
                await asyncio.sleep(e.value)
                continue
            except Exception as e:
                logger.error(f"Error sending file {msg_id}: {e}")
                continue
        
        # Delete progress message
        try:
            await progress_msg.delete()
        except:
            pass
        
        # Send completion message
        await message.reply(
            f"✅ <b>Files sent!</b>\n\n"
            f"Successfully sent {sent_count} files.",
            parse_mode=enums.ParseMode.HTML
        )
        
        # Update user activity
        await client.db.update_user_activity(user_id)
        
    except Exception as e:
        logger.error(f"Error sending multiple files: {e}")
        await message.reply("❌ Error sending files!")

async def handle_special_link(client: Bot, message: Message, decoded: str):
    """Handle special link with custom message"""
    user_id = message.from_user.id
    
    try:
        # Get special link data
        special_link = await client.db.get_special_link(decoded)
        if not special_link:
            await message.reply("❌ Special link not found or expired!")
            return
        
        # Show custom message first
        custom_message = special_link.get("message", "")
        files = special_link.get("files", [])
        
        if custom_message:
            await message.reply(
                custom_message,
                parse_mode=enums.ParseMode.HTML,
                disable_web_page_preview=True
            )
            await asyncio.sleep(1)  # Small delay
        
        # Send files if any
        if files:
            # Create encoded string for the files
            encoded_files = await encode(f"custombatch_{'-'.join(map(str, files))}")
            await send_multiple_files(client, message, encoded_files)
        
    except Exception as e:
        logger.error(f"Error handling special link: {e}")
        await message.reply("❌ Error processing special link!")

async def handle_custom_batch(client: Bot, message: Message, decoded: str):
    """Handle custom batch link"""
    # Remove the prefix and send as multiple files
    encoded = await encode(decoded.replace("custombatch_", "get-"))
    await send_multiple_files(client, message, encoded)

async def schedule_auto_delete(client: Bot, message: Message, delete_time: int, encoded_link: str):
    """Schedule auto-delete for a message"""
    try:
        await asyncio.sleep(delete_time)
        
        # Try to delete the message
        try:
            await message.delete()
        except MessageDeleteForbidden:
            # Can't delete, edit instead
            buttons = [
                [InlineKeyboardButton("🔗 Click Here", url=f"https://t.me/{Config.BOT_USERNAME}?start={encoded_link}")]
            ]
            
            await message.edit(
                "✅ <b>File Deleted Successfully!</b>\n\n"
                "Click the link below to get the file again.\n"
                "The link will expire in 24 hours.",
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=enums.ParseMode.HTML
            )
        
    except Exception as e:
        logger.error(f"Error in auto-delete: {e}")


# ===================================
# SECTION 7: HELP & ABOUT (Lines 1101-1400)
# ===================================

async def help_command(client: Bot, message: Message):
    """Handle /help command"""
    user_id = message.from_user.id
    
    # Check if user is admin
    if user_id in Config.ADMINS:
        await show_admin_help(client, message)
    else:
        await show_user_help(client, message)

async def show_user_help(client: Bot, message: Message):
    """Show help for regular users"""
    # Get settings
    settings = await client.db.get_settings()
    help_text = settings.get("help_text", "➪ I ᴀᴍ ᴀ ᴘʀɪᴠᴀᴛᴇ ғɪʟᴇ sʜᴀʀɪɴɢ ʙᴏᴛ, ᴍᴇᴀɴᴛ ᴛᴏ ᴘʀᴏᴠɪᴅᴇ ғɪʟᴇs ᴀɴᴅ ɴᴇᴄᴇssᴀʀʏ sᴛᴜғғ ᴛʜʀᴏᴜɢʜ sᴘᴇᴄɪᴀʟ ʟɪɴᴋ ғᴏʀ sᴘᴇᴄɪғɪᴄ ᴄʜᴀɴɴᴇʟs.")
    
    # Create buttons
    buttons = []
    
    # Support chat button
    if Config.SUPPORT_CHAT:
        buttons.append([
            InlineKeyboardButton("🗨 Support Chat Group", url=f"https://t.me/{Config.SUPPORT_CHAT}")
        ])
    
    # Owner and Developer buttons
    buttons.append([
        InlineKeyboardButton("📥 Owner", url=f"tg://user?id={Config.OWNER_ID}"),
        InlineKeyboardButton("💫 Developer", url=f"tg://user?id={Config.OWNER_ID}")
    ])
    
    # Close button
    buttons.append([
        InlineKeyboardButton("🔐 Close", callback_data="close")
    ])
    
    keyboard = InlineKeyboardMarkup(buttons)
    
    # Try to send with image
    try:
        await message.reply_photo(
            photo="https://telegra.ph/file/help_image.jpg",  # Replace with actual help image
            caption=help_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
    except:
        # Fallback to text
        await message.reply(
            help_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True
        )

async def show_admin_help(client: Bot, message: Message):
    """Show help for admins"""
    help_text = (
        "👑 <b>ADMIN COMMANDS PANEL</b>\n\n"
        "Hello Admin! You have full admin access.\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "<b>📁 FILE MANAGEMENT:</b>\n"
        "• /genlink - Generate single file link\n"
        "• /batch - Create batch link (sequential)\n"
        "• /custom_batch - Create custom batch link\n"
        "• /special_link - Link with custom message\n\n"
        "<b>⚙️ CHANNEL SETTINGS:</b>\n"
        "• /setchannel - Configure database channel\n"
        "• /checkchannel - Check channel status\n"
        "• /removechannel - Remove channel\n\n"
        "<b>👥 USER MANAGEMENT:</b>\n"
        "• /users - View user statistics\n"
        "• /ban - Ban a user\n"
        "• /unban - Unban a user\n"
        "• /broadcast - Broadcast message\n\n"
        "<b>📊 BOT SETTINGS:</b>\n"
        "• /settings - Main settings panel\n"
        "• /botsettings - Configure bot appearance\n"
        "• /files - File protection settings\n"
        "• /forcesub - Force subscribe settings\n"
        "• /auto_del - Auto-delete settings\n\n"
        "<b>📈 STATISTICS:</b>\n"
        "• /stats - Complete bot statistics\n\n"
        "<b>🔗 UTILITIES:</b>\n"
        "• /shortener - Shorten any URL\n"
        "• /ping - Check bot status\n"
        "• /test - Test bot functionality\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "💡 <i>Click any command below to execute it!</i>"
    )
    
    # Create buttons grid
    buttons = [
        [
            InlineKeyboardButton("📝 Generate Link", callback_data="help_genlink"),
            InlineKeyboardButton("📦 Batch Link", callback_data="help_batch")
        ],
        [
            InlineKeyboardButton("🎯 Custom Batch", callback_data="help_custom_batch"),
            InlineKeyboardButton("⭐ Special Link", callback_data="help_special_link")
        ],
        [
            InlineKeyboardButton("📺 Set Channel", callback_data="help_setchannel"),
            InlineKeyboardButton("✅ Check Channel", callback_data="help_checkchannel")
        ],
        [
            InlineKeyboardButton("👥 Users Stats", callback_data="help_users"),
            InlineKeyboardButton("📊 Bot Stats", callback_data="help_stats")
        ],
        [
            InlineKeyboardButton("⚙️ Settings", callback_data="help_settings"),
            InlineKeyboardButton("🎨 Bot Settings", callback_data="help_botsettings")
        ],
        [
            InlineKeyboardButton("📁 Files Settings", callback_data="help_files"),
            InlineKeyboardButton("📢 Force Sub", callback_data="help_forcesub")
        ],
        [
            InlineKeyboardButton("🔗 URL Shortener", callback_data="help_shortener"),
            InlineKeyboardButton("🏓 Ping", callback_data="help_ping")
        ],
        [
            InlineKeyboardButton("🔐 Close", callback_data="close")
        ]
    ]
    
    keyboard = InlineKeyboardMarkup(buttons)
    
    await message.reply(
        help_text,
        reply_markup=keyboard,
        parse_mode=enums.ParseMode.HTML
    )

async def about_command(client: Bot, message: Message):
    """Handle /about command"""
    # Get settings
    settings = await client.db.get_settings()
    about_text = settings.get("about_text", "")
    
    # Default about text if not set
    if not about_text:
        about_text = (
            "ℹ️ <b>ABOUT BOT</b>\n\n"
            "◈ Bot Name: {bot_name}\n"
            "◈ Username: @{username}\n"
            "◈ Framework: Pyrogram\n"
            "◈ Language: Python 3\n"
            "◈ Version: V3.0\n\n"
            "◈ Made with ❤️"
        )
    
    # Replace variables
    about_text = about_text.format(
        bot_name=Config.BOT_NAME,
        username=Config.BOT_USERNAME
    )
    
    # Create buttons
    buttons = []
    
    if Config.SUPPORT_CHAT:
        buttons.append([
            InlineKeyboardButton("💬 Support", url=f"https://t.me/{Config.SUPPORT_CHAT}")
        ])
    
    if Config.UPDATE_CHANNEL:
        buttons.append([
            InlineKeyboardButton("📢 Updates", url=f"https://t.me/{Config.UPDATE_CHANNEL}")
        ])
    
    buttons.append([
        InlineKeyboardButton("🏠 Home", callback_data="start"),
        InlineKeyboardButton("🔐 Close", callback_data="close")
    ])
    
    keyboard = InlineKeyboardMarkup(buttons)
    
    await message.reply(
        about_text,
        reply_markup=keyboard,
        parse_mode=enums.ParseMode.HTML
    )


# ===================================
# SECTION 8: ADMIN COMMANDS (Lines 1401-1800)
# ===================================

async def users_command(client: Bot, message: Message):
    """Handle /users command - show user statistics"""
    try:
        # Get counts
        total_users = await client.db.total_users_count()
        banned_users = await client.db.get_banned_count()
        active_users = total_users - banned_users
        
        # Format message
        stats_text = (
            "👥 <b>USER STATISTICS</b>\n\n"
            f"📊 Total Users: {total_users:,}\n"
            f"🚫 Banned Users: {banned_users:,}\n"
            f"✅ Active Users: {active_users:,}\n\n"
            f"<i>Last updated: Just now</i>"
        )
        
        # Create buttons
        buttons = [
            [
                InlineKeyboardButton("🔄 Refresh", callback_data="refresh"),
                InlineKeyboardButton("🔒 Close", callback_data="close")
            ]
        ]
        
        keyboard = InlineKeyboardMarkup(buttons)
        
        await message.reply(
            stats_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
        
    except Exception as e:
        logger.error(f"Error in users command: {e}")
        await message.reply("❌ Error fetching user statistics!")

async def broadcast_command(client: Bot, message: Message):
    """Handle /broadcast command"""
    # Check if replying to a message
    if not message.reply_to_message:
        await message.reply(
            "📢 <b>BROADCAST USAGE</b>\n\n"
            "Reply to any message with /broadcast\n"
            "to send it to all users.",
            parse_mode=enums.ParseMode.HTML
        )
        return
    
    # Confirm broadcast
    buttons = [
        [
            InlineKeyboardButton("✅ Yes, Broadcast", callback_data="broadcast_confirm"),
            InlineKeyboardButton("❌ Cancel", callback_data="close")
        ]
    ]
    
    keyboard = InlineKeyboardMarkup(buttons)
    
    await message.reply(
        "⚠️ <b>CONFIRM BROADCAST</b>\n\n"
        "Are you sure you want to broadcast this message to ALL users?\n\n"
        "This action cannot be undone!",
        reply_markup=keyboard,
        parse_mode=enums.ParseMode.HTML
    )

async def ban_command(client: Bot, message: Message):
    """Handle /ban command"""
    if len(message.command) < 2:
        await message.reply(
            "🚫 <b>BAN USER</b>\n\n"
            "Usage: <code>/ban user_id [reason]</code>\n\n"
            "Example:\n"
            "<code>/ban 123456789 Spamming</code>",
            parse_mode=enums.ParseMode.HTML
        )
        return
    
    try:
        user_id = int(message.command[1])
        reason = " ".join(message.command[2:]) if len(message.command) > 2 else "No reason provided"
        
        # Check if user exists
        if not await client.db.is_user_exist(user_id):
            await message.reply("❌ User not found in database!")
            return
        
        # Ban the user
        await client.db.ban_user(user_id, reason)
        
        # Try to notify the user
        try:
            await client.send_message(
                user_id,
                f"🚫 <b>You have been banned from using this bot!</b>\n\n"
                f"Reason: {reason}\n"
                f"If you think this is a mistake, contact admin.",
                parse_mode=enums.ParseMode.HTML
            )
        except:
            pass
        
        await message.reply(
            f"✅ <b>User Banned Successfully!</b>\n\n"
            f"User ID: <code>{user_id}</code>\n"
            f"Reason: {reason}",
            parse_mode=enums.ParseMode.HTML
        )
        
    except ValueError:
        await message.reply("❌ Invalid user ID! User ID must be a number.")
    except Exception as e:
        logger.error(f"Error banning user: {e}")
        await message.reply("❌ Error banning user!")

async def unban_command(client: Bot, message: Message):
    """Handle /unban command"""
    if len(message.command) < 2:
        await message.reply(
            "✅ <b>UNBAN USER</b>\n\n"
            "Usage: <code>/unban user_id</code>\n\n"
            "Example:\n"
            "<code>/unban 123456789</code>",
            parse_mode=enums.ParseMode.HTML
        )
        return
    
    try:
        user_id = int(message.command[1])
        
        # Check if user is banned
        if not await client.db.is_user_banned(user_id):
            await message.reply("❌ User is not banned!")
            return
        
        # Unban the user
        await client.db.unban_user(user_id)
        
        # Try to notify the user
        try:
            await client.send_message(
                user_id,
                "✅ <b>You have been unbanned from the bot!</b>\n\n"
                "You can now use the bot again.",
                parse_mode=enums.ParseMode.HTML
            )
        except:
            pass
        
        await message.reply(
            f"✅ <b>User Unbanned Successfully!</b>\n\n"
            f"User ID: <code>{user_id}</code>",
            parse_mode=enums.ParseMode.HTML
        )
        
    except ValueError:
        await message.reply("❌ Invalid user ID! User ID must be a number.")
    except Exception as e:
        logger.error(f"Error unbanning user: {e}")
        await message.reply("❌ Error unbanning user!")

async def stats_command(client: Bot, message: Message):
    """Handle /stats command - show bot statistics"""
    try:
        # Get counts
        total_users = await client.db.total_users_count()
        banned_users = await client.db.get_banned_count()
        active_users = total_users - banned_users
        
        # Get bot info
        bot = await client.get_me()
        
        # Get database channel info
        db_channel = await client.db.get_db_channel()
        channel_info = "Not configured"
        if db_channel:
            try:
                chat = await client.get_chat(db_channel)
                channel_info = f"{chat.title} (ID: {db_channel})"
            except:
                channel_info = f"ID: {db_channel}"
        
        # Format message
        stats_text = (
            "📊 <b>BOT STATISTICS</b>\n\n"
            "<b>🤖 Bot Info:</b>\n"
            f"• Name: {bot.first_name}\n"
            f"• Username: @{bot.username}\n"
            f"• ID: <code>{bot.id}</code>\n\n"
            f"<b>👥 Users:</b>\n"
            f"• Total: {total_users:,}\n"
            f"• Banned: {banned_users:,}\n"
            f"• Active: {active_users:,}\n\n"
            f"<b>⚙️ System:</b>\n"
            f"• Database: ✅ Connected\n"
            f"• Channels: {'✅ Configured' if db_channel else '❌ Not configured'}\n"
            f"• File Channel: {channel_info}\n\n"
            f"<i>Last updated: Just now</i>"
        )
        
        # Create buttons
        buttons = [
            [
                InlineKeyboardButton("🔄 Refresh", callback_data="refresh"),
                InlineKeyboardButton("🔒 Close", callback_data="close")
            ]
        ]
        
        keyboard = InlineKeyboardMarkup(buttons)
        
        await message.reply(
            stats_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
        
    except Exception as e:
        logger.error(f"Error in stats command: {e}")
        await message.reply("❌ Error fetching bot statistics!")


# ===================================
# SECTION 9: FILE MANAGEMENT (Lines 1801-2200)
# ===================================

async def genlink_command(client: Bot, message: Message):
    """Handle /genlink command - generate single file link"""
    # Check if replying to a message
    if not message.reply_to_message:
        await message.reply(
            "📝 <b>GENERATE SINGLE FILE LINK</b>\n\n"
            "Forward a file from your database channel\n"
            "and reply with /genlink to create a shareable link.",
            parse_mode=enums.ParseMode.HTML
        )
        return
    
    # Check database channel
    db_channel = await client.db.get_db_channel()
    if not db_channel:
        await message.reply(
            "❌ <b>Database channel not configured!</b>\n\n"
            "Use /setchannel to configure your database channel first.",
            parse_mode=enums.ParseMode.HTML
        )
        return
    
    try:
        # Forward the message to database channel
        forwarded_msg = await message.reply_to_message.forward(db_channel)
        
        # Calculate unique ID
        channel_id = abs(db_channel)
        message_id = forwarded_msg.id
        converted_id = message_id * channel_id
        
        # Create link string
        link_string = f"get-{converted_id}"
        
        # Encode the link
        encoded = await encode(link_string)
        
        # Generate bot link
        bot_username = Config.BOT_USERNAME or (await client.get_me()).username
        link = f"https://t.me/{bot_username}?start={encoded}"
        
        # Get file info
        file_info = await get_file_info(message.reply_to_message)
        
        # Create response message
        response_text = (
            "✅ <b>File Uploaded Successfully!</b>\n\n"
            f"📁 File Name: {file_info['file_name']}\n"
            f"📊 Size: {format_file_size(file_info['file_size'])}\n"
            f"💾 Message ID: {message_id}\n\n"
            f"🔗 <b>Shareable Link:</b>\n"
            f"<code>{link}</code>\n\n"
            f"💡 <i>Tip: Share this link with users!</i>"
        )
        
        # Create copy button
        buttons = [[InlineKeyboardButton("📋 Copy Link", url=link)]]
        keyboard = InlineKeyboardMarkup(buttons)
        
        await message.reply(
            response_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
        
    except Exception as e:
        logger.error(f"Error generating link: {e}")
        await message.reply("❌ Error generating link!")

async def batch_command(client: Bot, message: Message):
    """Handle /batch command - generate sequential batch link"""
    # Check database channel
    db_channel = await client.db.get_db_channel()
    if not db_channel:
        await message.reply(
            "❌ <b>Database channel not configured!</b>\n\n"
            "Use /setchannel to configure your database channel first.",
            parse_mode=enums.ParseMode.HTML
        )
        return
    
    # Start batch process
    user_id = message.from_user.id
    client.batch_state[user_id] = {"step": 1}
    
    await message.reply(
        "📦 <b>BATCH LINK GENERATION</b>\n\n"
        "Forward the <b>FIRST</b> message from your database channel.\n"
        "This should be the starting message of your batch.",
        parse_mode=enums.ParseMode.HTML
    )

async def custom_batch_command(client: Bot, message: Message):
    """Handle /custom_batch command - generate custom batch link"""
    # Check database channel
    db_channel = await client.db.get_db_channel()
    if not db_channel:
        await message.reply(
            "❌ <b>Database channel not configured!</b>\n\n"
            "Use /setchannel to configure your database channel first.",
            parse_mode=enums.ParseMode.HTML
        )
        return
    
    # Start custom batch process
    user_id = message.from_user.id
    client.custom_batch_state[user_id] = {
        "step": 1,
        "message_ids": []
    }
    
    await message.reply(
        "🎯 <b>CUSTOM BATCH GENERATION</b>\n\n"
        "Forward messages from your database channel.\n"
        "I'll add them to the batch.\n"
        "Send /done when you're finished.\n\n"
        "Currently: 0 files added",
        parse_mode=enums.ParseMode.HTML
    )

async def special_link_command(client: Bot, message: Message):
    """Handle /special_link command - generate link with custom message"""
    # Check database channel
    db_channel = await client.db.get_db_channel()
    if not db_channel:
        await message.reply(
            "❌ <b>Database channel not configured!</b>\n\n"
            "Use /setchannel to configure your database channel first.",
            parse_mode=enums.ParseMode.HTML
        )
        return
    
    # Start special link process
    user_id = message.from_user.id
    client.special_link_state[user_id] = {
        "step": 1,
        "files": []
    }
    
    await message.reply(
        "⭐ <b>SPECIAL LINK GENERATION</b>\n\n"
        "Forward files from your database channel.\n"
        "These will be included in the special link.\n"
        "Send /done when you're finished with files.\n\n"
        "Currently: 0 files added",
        parse_mode=enums.ParseMode.HTML
    )

async def done_command(client: Bot, message: Message):
    """Handle /done command for batch operations"""
    user_id = message.from_user.id
    
    # Check if user is in batch state
    if user_id in client.batch_state:
        await handle_batch_done(client, message)
    elif user_id in client.custom_batch_state:
        await handle_custom_batch_done(client, message)
    elif user_id in client.special_link_state:
        await handle_special_link_done(client, message)
    else:
        await message.reply("❌ No active batch operation!")

async def handle_batch_done(client: Bot, message: Message):
    """Handle batch completion"""
    user_id = message.from_user.id
    state = client.batch_state.get(user_id, {})
    
    if state.get("step") != 2:
        await message.reply("❌ Please forward the LAST message first!")
        return
    
    try:
        db_channel = await client.db.get_db_channel()
        if not db_channel:
            await message.reply("❌ Database channel not configured!")
            return
        
        # Get first and last message IDs
        first_msg = state.get("first_message")
        last_msg = state.get("last_message")
        
        if not first_msg or not last_msg:
            await message.reply("❌ Missing messages!")
            return
        
        # Calculate IDs
        channel_id = abs(db_channel)
        first_id = first_msg.id * channel_id
        last_id = last_msg.id * channel_id
        
        # Create link string
        link_string = f"get-{first_id}-{last_id}"
        
        # Encode the link
        encoded = await encode(link_string)
        
        # Generate bot link
        bot_username = Config.BOT_USERNAME or (await client.get_me()).username
        link = f"https://t.me/{bot_username}?start={encoded}"
        
        # Calculate total files
        total_files = last_msg.id - first_msg.id + 1
        
        # Create response message
        response_text = (
            "✅ <b>Batch Link Generated!</b>\n\n"
            f"📦 First Message ID: {first_msg.id}\n"
            f"📦 Last Message ID: {last_msg.id}\n"
            f"📊 Total Files: {total_files}\n\n"
            f"🔗 <b>Batch Link:</b>\n"
            f"<code>{link}</code>\n\n"
            f"💡 <i>Tip: Share this link to send all {total_files} files at once!</i>"
        )
        
        # Create copy button
        buttons = [[InlineKeyboardButton("📋 Copy Link", url=link)]]
        keyboard = InlineKeyboardMarkup(buttons)
        
        await message.reply(
            response_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
        
        # Clean up state
        if user_id in client.batch_state:
            del client.batch_state[user_id]
        
    except Exception as e:
        logger.error(f"Error completing batch: {e}")
        await message.reply("❌ Error generating batch link!")
        if user_id in client.batch_state:
            del client.batch_state[user_id]

async def handle_custom_batch_done(client: Bot, message: Message):
    """Handle custom batch completion"""
    user_id = message.from_user.id
    state = client.custom_batch_state.get(user_id, {})
    
    message_ids = state.get("message_ids", [])
    
    if not message_ids:
        await message.reply("❌ No files added to batch!")
        if user_id in client.custom_batch_state:
            del client.custom_batch_state[user_id]
        return
    
    try:
        db_channel = await client.db.get_db_channel()
        if not db_channel:
            await message.reply("❌ Database channel not configured!")
            return
        
        # Calculate IDs
        channel_id = abs(db_channel)
        converted_ids = [msg_id * channel_id for msg_id in message_ids]
        
        # Create link string
        link_string = f"custombatch_{'-'.join(map(str, converted_ids))}"
        
        # Encode the link
        encoded = await encode(link_string)
        
        # Generate bot link
        bot_username = Config.BOT_USERNAME or (await client.get_me()).username
        link = f"https://t.me/{bot_username}?start={encoded}"
        
        # Create response message
        response_text = (
            "✅ <b>Custom Batch Link Generated!</b>\n\n"
            f"📊 Total Files: {len(message_ids)}\n"
            f"📦 Message IDs: {', '.join(map(str, message_ids[:5]))}"
            f"{'...' if len(message_ids) > 5 else ''}\n\n"
            f"🔗 <b>Batch Link:</b>\n"
            f"<code>{link}</code>\n\n"
            f"💡 <i>Tip: Share this link to send all files at once!</i>"
        )
        
        # Create copy button
        buttons = [[InlineKeyboardButton("📋 Copy Link", url=link)]]
        keyboard = InlineKeyboardMarkup(buttons)
        
        await message.reply(
            response_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
        
        # Clean up state
        if user_id in client.custom_batch_state:
            del client.custom_batch_state[user_id]
        
    except Exception as e:
        logger.error(f"Error completing custom batch: {e}")
        await message.reply("❌ Error generating custom batch link!")
        if user_id in client.custom_batch_state:
            del client.custom_batch_state[user_id]

async def handle_special_link_done(client: Bot, message: Message):
    """Handle special link file collection completion"""
    user_id = message.from_user.id
    state = client.special_link_state.get(user_id, {})
    
    if state.get("step") != 1:
        await message.reply("❌ Unexpected state!")
        return
    
    # Move to step 2: get custom message
    client.special_link_state[user_id]["step"] = 2
    
    await message.reply(
        "⭐ <b>SPECIAL LINK - CUSTOM MESSAGE</b>\n\n"
        "Now send the custom message that users will see\n"
        "when they click the special link.\n\n"
        "You can use HTML formatting.\n"
        "Send /cancel to cancel."
    )

async def text_message_handler(client: Bot, message: Message):
    """Handle text messages for interactive commands"""
    user_id = message.from_user.id
    
    # Check batch state
    if user_id in client.batch_state:
        await handle_batch_text(client, message)
    
    # Check custom batch state
    elif user_id in client.custom_batch_state:
        await handle_custom_batch_text(client, message)
    
    # Check special link state
    elif user_id in client.special_link_state:
        await handle_special_link_text(client, message)
    
    # Check button setting state
    elif user_id in client.button_setting_state:
        await handle_button_setting_text(client, message)
    
    # Check text setting state
    elif user_id in client.text_setting_state:
        await handle_text_setting_text(client, message)

async def handle_batch_text(client: Bot, message: Message):
    """Handle text messages during batch process"""
    user_id = message.from_user.id
    state = client.batch_state.get(user_id, {})
    
    # Check if it's a forwarded message
    if not message.forward_date:
        await message.reply("❌ Please forward a message from your database channel!")
        return
    
    if state.get("step") == 1:
        # First message
        client.batch_state[user_id] = {
            "step": 2,
            "first_message": message
        }
        
        await message.reply(
            "✅ <b>First message received!</b>\n\n"
            "Now forward the <b>LAST</b> message from your database channel.\n"
            "This should be the ending message of your batch.",
            parse_mode=enums.ParseMode.HTML
        )
    
    elif state.get("step") == 2:
        # Last message
        client.batch_state[user_id]["last_message"] = message
        client.batch_state[user_id]["step"] = 3
        
        await message.reply(
            "✅ <b>Last message received!</b>\n\n"
            "Send /done to generate the batch link.",
            parse_mode=enums.ParseMode.HTML
        )

async def handle_custom_batch_text(client: Bot, message: Message):
    """Handle text messages during custom batch process"""
    user_id = message.from_user.id
    state = client.custom_batch_state.get(user_id, {})
    
    # Check if it's a forwarded message
    if not message.forward_date:
        await message.reply("❌ Please forward a message from your database channel!")
        return
    
    # Add message ID to list
    if "message_ids" not in state:
        state["message_ids"] = []
    
    state["message_ids"].append(message.id)
    
    # Update count
    count = len(state["message_ids"])
    
    await message.reply(
        f"✅ <b>Added!</b> Total: {count}\n\n"
        "Forward more messages or send /done when finished.",
        parse_mode=enums.ParseMode.HTML
    )

async def handle_special_link_text(client: Bot, message: Message):
    """Handle text messages during special link process"""
    user_id = message.from_user.id
    state = client.special_link_state.get(user_id, {})
    
    if state.get("step") == 1:
        # Still collecting files (should be forwarded messages)
        if not message.forward_date:
            await message.reply("❌ Please forward a message from your database channel!")
            return
        
        # Add file to list
        if "files" not in state:
            state["files"] = []
        
        state["files"].append(message.id)
        
        # Update count
        count = len(state["files"])
        
        await message.reply(
            f"✅ <b>Added!</b> Total: {count}\n\n"
            "Forward more files or send /done when finished.",
            parse_mode=enums.ParseMode.HTML
        )
    
    elif state.get("step") == 2:
        # Getting custom message
        custom_message = message.text
        
        try:
            db_channel = await client.db.get_db_channel()
            if not db_channel:
                await message.reply("❌ Database channel not configured!")
                return
            
            # Calculate file IDs
            channel_id = abs(db_channel)
            file_ids = [msg_id * channel_id for msg_id in state.get("files", [])]
            
            # Create unique link ID
            link_id = f"special_{random.randint(100000, 999999)}"
            
            # Save special link to database
            await client.db.save_special_link(link_id, custom_message, file_ids)
            
            # Create link string
            link_string = f"get-{'-'.join(map(str, file_ids))}"
            encoded = await encode(link_string)
            
            # Generate bot link
            bot_username = Config.BOT_USERNAME or (await client.get_me()).username
            link = f"https://t.me/{bot_username}?start={encoded}"
            
            # Create response message
            response_text = (
                "✅ <b>Special Link Generated!</b>\n\n"
                f"📊 Total Files: {len(file_ids)}\n"
                f"💬 Custom Message: {custom_message[:50]}...\n\n"
                f"🔗 <b>Special Link:</b>\n"
                f"<code>{link}</code>\n\n"
                f"💡 <i>Users will see your custom message first!</i>"
            )
            
            # Create copy button
            buttons = [[InlineKeyboardButton("📋 Copy Link", url=link)]]
            keyboard = InlineKeyboardMarkup(buttons)
            
            await message.reply(
                response_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
            
            # Clean up state
            if user_id in client.special_link_state:
                del client.special_link_state[user_id]
            
        except Exception as e:
            logger.error(f"Error creating special link: {e}")
            await message.reply("❌ Error creating special link!")
            if user_id in client.special_link_state:
                del client.special_link_state[user_id]


# ===================================
# SECTION 10: CHANNEL MANAGEMENT (Lines 2201-2400)
# ===================================

async def setchannel_command(client: Bot, message: Message):
    """Handle /setchannel command - configure database channel"""
    if len(message.command) < 2 and not message.reply_to_message:
        await message.reply(
            "📺 <b>SET DATABASE CHANNEL</b>\n\n"
            "Usage:\n"
            "1. Forward a message from the channel\n"
            "2. Send channel username (with @)\n"
            "3. Send channel ID\n\n"
            "Example:\n"
            "<code>/setchannel @my_channel</code>\n"
            "<code>/setchannel -1001234567890</code>",
            parse_mode=enums.ParseMode.HTML
        )
        return
    
    try:
        channel_input = None
        
        if message.reply_to_message and message.reply_to_message.forward_from_chat:
            # Forwarded from channel
            channel = message.reply_to_message.forward_from_chat
            channel_input = channel.id
        
        elif len(message.command) >= 2:
            # Command argument
            arg = message.command[1]
            
            if arg.startswith("@"):
                # Username
                try:
                    channel = await client.get_chat(arg)
                    channel_input = channel.id
                except Exception as e:
                    await message.reply(f"❌ Cannot get channel {arg}: {e}")
                    return
            
            else:
                # Try as ID
                try:
                    channel_id = int(arg)
                    channel_input = channel_id
                except ValueError:
                    await message.reply("❌ Invalid channel ID or username!")
                    return
        
        if not channel_input:
            await message.reply("❌ Could not identify channel!")
            return
        
        # Verify the channel
        try:
            channel = await client.get_chat(channel_input)
            
            # Check if bot is admin in the channel
            try:
                member = await client.get_chat_member(channel.id, (await client.get_me()).id)
                if member.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
                    await message.reply(
                        "❌ <b>Bot is not admin in the channel!</b>\n\n"
                        "Make sure the bot has admin permissions in the channel.",
                        parse_mode=enums.ParseMode.HTML
                    )
                    return
            except:
                await message.reply(
                    "❌ <b>Bot is not in the channel!</b>\n\n"
                    "Add the bot to the channel first and make it admin.",
                    parse_mode=enums.ParseMode.HTML
                )
                return
            
            # Save channel to database
            await client.db.set_db_channel(channel.id)
            client.db_channel = channel.id
            
            await message.reply(
                f"✅ <b>Database channel set successfully!</b>\n\n"
                f"Channel: {channel.title}\n"
                f"ID: <code>{channel.id}</code>\n"
                f"Username: @{channel.username if channel.username else 'None'}",
                parse_mode=enums.ParseMode.HTML
            )
            
        except Exception as e:
            await message.reply(f"❌ Error setting channel: {e}")
    
    except Exception as e:
        logger.error(f"Error in setchannel command: {e}")
        await message.reply("❌ Error setting channel!")

async def checkchannel_command(client: Bot, message: Message):
    """Handle /checkchannel command - check channel status"""
    db_channel = await client.db.get_db_channel()
    
    if not db_channel:
        await message.reply(
            "❌ <b>No database channel configured!</b>\n\n"
            "Use /setchannel to configure a channel.",
            parse_mode=enums.ParseMode.HTML
        )
        return
    
    try:
        # Get channel info
        channel = await client.get_chat(db_channel)
        
        # Check bot permissions
        try:
            member = await client.get_chat_member(channel.id, (await client.get_me()).id)
            bot_is_admin = member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]
        except:
            bot_is_admin = False
        
        # Create status message
        status_text = (
            "✅ <b>DATABASE CHANNEL STATUS</b>\n\n"
            f"📺 Channel: {channel.title}\n"
            f"🔗 ID: <code>{channel.id}</code>\n"
            f"👤 Username: @{channel.username if channel.username else 'None'}\n"
            f"🤖 Bot Admin: {'✅ Yes' if bot_is_admin else '❌ No'}\n\n"
        )
        
        if bot_is_admin:
            status_text += "✅ <i>Channel is properly configured!</i>"
        else:
            status_text += (
                "⚠️ <i>Bot needs admin permissions!</i>\n\n"
                "Make sure the bot has:\n"
                "• Post messages permission\n"
                "• Edit messages permission\n"
                "• Delete messages permission"
            )
        
        await message.reply(
            status_text,
            parse_mode=enums.ParseMode.HTML
        )
    
    except Exception as e:
        logger.error(f"Error checking channel: {e}")
        await message.reply(
            f"❌ <b>Error accessing channel!</b>\n\n"
            f"Error: {str(e)}",
            parse_mode=enums.ParseMode.HTML
        )

async def removechannel_command(client: Bot, message: Message):
    """Handle /removechannel command - remove database channel"""
    # Confirm removal
    buttons = [
        [
            InlineKeyboardButton("✅ Yes, Remove", callback_data="removechannel_confirm"),
            InlineKeyboardButton("❌ Cancel", callback_data="close")
        ]
    ]
    
    keyboard = InlineKeyboardMarkup(buttons)
    
    await message.reply(
        "⚠️ <b>CONFIRM CHANNEL REMOVAL</b>\n\n"
        "Are you sure you want to remove the database channel?\n\n"
        "This will disable file sharing until a new channel is set!",
        reply_markup=keyboard,
        parse_mode=enums.ParseMode.HTML
    )


# ===================================
# SECTION 11: SETTINGS COMMANDS (Lines 2401-2800)
# ===================================

async def settings_command(client: Bot, message: Message):
    """Handle /settings command - main settings panel"""
    settings_text = (
        "⚙️ <b>SETTINGS PANEL</b>\n\n"
        "Configure your bot settings below:\n\n"
        "🔒 Protection Settings\n"
        "📁 File Settings\n"
        "🗑️ Auto Delete Settings\n"
        "📢 Force Subscribe Settings\n\n"
        "<i>Click a button to configure</i>"
    )
    
    buttons = [
        [
            InlineKeyboardButton("🔒 Protection", callback_data="settings_protection"),
            InlineKeyboardButton("📁 Files", callback_data="settings_files")
        ],
        [
            InlineKeyboardButton("🗑️ Auto Del", callback_data="settings_autodel"),
            InlineKeyboardButton("📢 Force Sub", callback_data="settings_forcesub")
        ],
        [
            InlineKeyboardButton("⚙️ Request FSub", callback_data="settings_reqfsub")
        ],
        [
            InlineKeyboardButton("🔒 Close", callback_data="close")
        ]
    ]
    
    keyboard = InlineKeyboardMarkup(buttons)
    
    await message.reply(
        settings_text,
        reply_markup=keyboard,
        parse_mode=enums.ParseMode.HTML
    )

async def files_command(client: Bot, message: Message):
    """Handle /files command - file settings"""
    # Get current settings
    settings = await client.db.get_settings()
    
    protect_content = settings.get("protect_content", True)
    hide_caption = settings.get("hide_caption", False)
    channel_button = settings.get("channel_button", True)
    
    # Create status emojis
    protect_emoji = "✅" if protect_content else "❌"
    hide_emoji = "✅" if hide_caption else "❌"
    button_emoji = "✅" if channel_button else "❌"
    
    settings_text = (
        "📁 <b>FILES RELATED SETTINGS</b>\n\n"
        f"🔒 PROTECT CONTENT: {protect_emoji}\n"
        f"🎭 HIDE CAPTION: {hide_emoji}\n"
        f"📢 CHANNEL BUTTON: {button_emoji}\n\n"
        "<i>CLICK BELOW BUTTONS TO CHANGE SETTINGS</i>"
    )
    
    buttons = [
        [
            InlineKeyboardButton(f"PROTECT CONTENT: {protect_emoji}", callback_data="toggle_protect_content")
        ],
        [
            InlineKeyboardButton(f"HIDE CAPTION: {hide_emoji}", callback_data="toggle_hide_caption")
        ],
        [
            InlineKeyboardButton(f"CHANNEL BUTTON: {button_emoji}", callback_data="toggle_channel_button")
        ],
        [
            InlineKeyboardButton("◈ SET BUTTON ◈", callback_data="set_button")
        ],
        [
            InlineKeyboardButton("🔄 Refresh", callback_data="refresh"),
            InlineKeyboardButton("🔒 Close", callback_data="close")
        ]
    ]
    
    keyboard = InlineKeyboardMarkup(buttons)
    
    await message.reply(
        settings_text,
        reply_markup=keyboard,
        parse_mode=enums.ParseMode.HTML
    )

async def auto_del_command(client: Bot, message: Message):
    """Handle /auto_del command - auto delete settings"""
    # Get current settings
    settings = await client.db.get_settings()
    
    auto_delete = settings.get("auto_delete", False)
    auto_delete_time = settings.get("auto_delete_time", 300)
    
    # Create status
    status_emoji = "✅" if auto_delete else "❌"
    time_text = format_time(auto_delete_time)
    
    settings_text = (
        "🗑️ <b>AUTO DELETE SETTINGS</b>\n\n"
        f"🔔 AUTO DELETE MODE: {status_emoji}\n"
        f"⏱️ DELETE TIMER: {time_text}\n\n"
        "<i>CLICK BELOW BUTTONS TO CHANGE SETTINGS</i>"
    )
    
    buttons = []
    
    # Toggle button
    if auto_delete:
        buttons.append([
            InlineKeyboardButton("DISABLE MODE ❌", callback_data="toggle_auto_delete")
        ])
    else:
        buttons.append([
            InlineKeyboardButton("ENABLE MODE ✅", callback_data="toggle_auto_delete")
        ])
    
    # Time buttons
    time_buttons = []
    for time_sec in AUTO_DELETE_TIMES:
        time_display = format_time(time_sec)
        time_buttons.append(
            InlineKeyboardButton(time_display, callback_data=f"autodel_{time_sec}")
        )
    
    # Split into rows of 2
    for i in range(0, len(time_buttons), 2):
        row = time_buttons[i:i+2]
        buttons.append(row)
    
    # Refresh and Close
    buttons.append([
        InlineKeyboardButton("🔄 Refresh", callback_data="refresh"),
        InlineKeyboardButton("🔒 Close", callback_data="close")
    ])
    
    keyboard = InlineKeyboardMarkup(buttons)
    
    await message.reply(
        settings_text,
        reply_markup=keyboard,
        parse_mode=enums.ParseMode.HTML
    )

async def forcesub_command(client: Bot, message: Message):
    """Handle /forcesub command - force subscribe settings"""
    # Get current channels
    channels = await client.db.get_force_sub_channels()
    
    if not channels:
        status_text = "❌ DISABLED"
        channels_text = "No channels configured"
    else:
        status_text = "✅ ENABLED"
        channels_text = ""
        for i, channel in enumerate(channels, 1):
            username = channel.get("channel_username", f"ID: {channel['channel_id']}")
            channels_text += f"{i}. {username}\n"
    
    settings_text = (
        "👥 <b>FORCE SUB COMMANDS</b>\n\n"
        f"Current Status: {status_text}\n\n"
        f"{channels_text}\n"
        "<b>Available Commands:</b>\n\n"
        "<code>/fsub_chnl</code> - Check current force-sub channels (Admins)\n\n"
        "<code>/add_fsub</code> - Add one or multiple force sub channels (Owner)\n\n"
        "<code>/del_fsub</code> - Delete one or multiple force sub channels (Owner)"
    )
    
    buttons = [[InlineKeyboardButton("🔒 Close", callback_data="close")]]
    
    keyboard = InlineKeyboardMarkup(buttons)
    
    await message.reply(
        settings_text,
        reply_markup=keyboard,
        parse_mode=enums.ParseMode.HTML
    )

async def req_fsub_command(client: Bot, message: Message):
    """Handle /req_fsub command - request force subscribe settings"""
    # Get current settings
    settings = await client.db.get_settings()
    request_fsub = settings.get("request_fsub", False)
    
    status_emoji = "✅" if request_fsub else "❌"
    
    settings_text = (
        "👥 <b>REQUEST FSUB SETTINGS</b>\n\n"
        f"🔔 REQUEST FSUB MODE: {status_emoji}\n\n"
        "<i>CLICK BELOW BUTTONS TO CHANGE SETTINGS</i>"
    )
    
    buttons = [
        [
            InlineKeyboardButton("🟢 ON", callback_data="reqfsub_on"),
            InlineKeyboardButton("OFF", callback_data="reqfsub_off")
        ],
        [
            InlineKeyboardButton("⚙️ MORE SETTINGS ⚙️", callback_data="settings_forcesub")
        ],
        [
            InlineKeyboardButton("🔒 Close", callback_data="close")
        ]
    ]
    
    keyboard = InlineKeyboardMarkup(buttons)
    
    await message.reply(
        settings_text,
        reply_markup=keyboard,
        parse_mode=enums.ParseMode.HTML
    )

async def botsettings_command(client: Bot, message: Message):
    """Handle /botsettings command - bot appearance settings"""
    settings_text = (
        "⚙️ <b>BOT SETTINGS</b>\n\n"
        "Configure your bot appearance and behavior:\n\n"
        "📸 Welcome Images - Set bot pics\n"
        "💬 Welcome Message - Customize start message\n"
        "📚 Help Message - Edit help text\n"
        "ℹ️ About Message - Edit about text\n"
        "🔘 Custom Buttons - Add channel/support buttons\n\n"
        "<i>Click a button below to configure</i>"
    )
    
    buttons = [
        [
            InlineKeyboardButton("📸 Images", callback_data="botsettings_images"),
            InlineKeyboardButton("💬 Welcome", callback_data="botsettings_welcome")
        ],
        [
            InlineKeyboardButton("📚 Help", callback_data="botsettings_help"),
            InlineKeyboardButton("ℹ️ About", callback_data="botsettings_about")
        ],
        [
            InlineKeyboardButton("🔘 Buttons", callback_data="botsettings_buttons")
        ],
        [
            InlineKeyboardButton("👀 Preview", callback_data="botsettings_preview"),
            InlineKeyboardButton("🔒 Close", callback_data="close")
        ]
    ]
    
    keyboard = InlineKeyboardMarkup(buttons)
    
    await message.reply(
        settings_text,
        reply_markup=keyboard,
        parse_mode=enums.ParseMode.HTML
    )

async def fsub_chnl_command(client: Bot, message: Message):
    """Handle /fsub_chnl command - list force subscribe channels"""
    channels = await client.db.get_force_sub_channels()
    
    if not channels:
        await message.reply(
            "📢 <b>FORCE SUBSCRIBE CHANNELS</b>\n\n"
            "No force subscribe channels configured.",
            parse_mode=enums.ParseMode.HTML
        )
        return
    
    response_text = "📢 <b>FORCE SUBSCRIBE CHANNELS</b>\n\n"
    
    for i, channel in enumerate(channels, 1):
        channel_id = channel.get("channel_id")
        username = channel.get("channel_username", f"ID: {channel_id}")
        
        response_text += f"{i}. {username}\n"
        response_text += f"   ID: <code>{channel_id}</code>\n\n"
    
    await message.reply(
        response_text,
        parse_mode=enums.ParseMode.HTML
    )

async def add_fsub_command(client: Bot, message: Message):
    """Handle /add_fsub command - add force subscribe channel"""
    if len(message.command) < 2:
        await message.reply(
            "📢 <b>ADD FORCE SUB CHANNEL</b>\n\n"
            "Usage: <code>/add_fsub channel_username_or_id</code>\n\n"
            "Examples:\n"
            "<code>/add_fsub @my_channel</code>\n"
            "<code>/add_fsub -1001234567890</code>\n\n"
            "To add multiple channels, separate with commas:\n"
            "<code>/add_fsub @channel1,@channel2,@channel3</code>",
            parse_mode=enums.ParseMode.HTML
        )
        return
    
    try:
        args = message.command[1].split(",")
        added_channels = []
        
        for arg in args:
            arg = arg.strip()
            
            try:
                # Try to get chat
                chat = await client.get_chat(arg)
                
                # Check if bot is admin in the channel
                try:
                    member = await client.get_chat_member(chat.id, (await client.get_me()).id)
                    if member.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
                        await message.reply(f"❌ Bot is not admin in {arg}")
                        continue
                except:
                    await message.reply(f"❌ Bot is not in {arg}")
                    continue
                
                # Add to database
                await client.db.add_force_sub_channel(
                    chat.id,
                    chat.username if chat.username else None
                )
                
                added_channels.append(f"@{chat.username}" if chat.username else f"ID: {chat.id}")
                
            except Exception as e:
                await message.reply(f"❌ Error adding {arg}: {str(e)}")
                continue
        
        if added_channels:
            # Refresh force sub channels
            client.force_sub_channels = await client.db.get_force_sub_channels()
            
            await message.reply(
                f"✅ <b>Channels added successfully!</b>\n\n"
                f"Added {len(added_channels)} channel(s):\n"
                + "\n".join(f"• {channel}" for channel in added_channels),
                parse_mode=enums.ParseMode.HTML
            )
        else:
            await message.reply("❌ No channels were added!")
    
    except Exception as e:
        logger.error(f"Error adding force sub channels: {e}")
        await message.reply("❌ Error adding channels!")

async def del_fsub_command(client: Bot, message: Message):
    """Handle /del_fsub command - delete force subscribe channel"""
    if len(message.command) < 2:
        await message.reply(
            "🗑️ <b>DELETE FORCE SUB CHANNEL</b>\n\n"
            "Usage: <code>/del_fsub channel_username_or_id</code>\n\n"
            "Examples:\n"
            "<code>/del_fsub @my_channel</code>\n"
            "<code>/del_fsub -1001234567890</code>\n\n"
            "To delete all channels:\n"
            "<code>/del_fsub all</code>",
            parse_mode=enums.ParseMode.HTML
        )
        return
    
    try:
        arg = message.command[1].strip().lower()
        
        if arg == "all":
            # Delete all channels
            await client.db.clear_force_sub_channels()
            client.force_sub_channels = []
            
            await message.reply(
                "✅ <b>All force subscribe channels deleted!</b>",
                parse_mode=enums.ParseMode.HTML
            )
            return
        
        # Try to get the channel
        try:
            chat = await client.get_chat(arg)
            channel_id = chat.id
        except:
            # Try as ID
            try:
                channel_id = int(arg)
            except ValueError:
                await message.reply("❌ Invalid channel identifier!")
                return
        
        # Remove from database
        await client.db.remove_force_sub_channel(channel_id)
        
        # Refresh force sub channels
        client.force_sub_channels = await client.db.get_force_sub_channels()
        
        await message.reply(
            f"✅ <b>Channel removed successfully!</b>\n\n"
            f"Channel ID: <code>{channel_id}</code>",
            parse_mode=enums.ParseMode.HTML
        )
    
    except Exception as e:
        logger.error(f"Error deleting force sub channel: {e}")
        await message.reply("❌ Error deleting channel!")

async def shortener_command(client: Bot, message: Message):
    """Handle /shortener command - shorten URLs"""
    if len(message.command) < 2:
        await message.reply(
            "🔗 <b>URL SHORTENER</b>\n\n"
            "Usage: <code>/shortener URL</code>\n\n"
            "Example:\n"
            "<code>/shortener https://example.com/very-long-url-path</code>",
            parse_mode=enums.ParseMode.HTML
        )
        return
    
    url = message.command[1]
    
    # Validate URL
    if not validate_url(url):
        await message.reply("❌ Invalid URL format!")
        return
    
    try:
        # Shorten URL
        short_url = await shorten_url(url)
        
        if short_url == url:
            # Shortener not configured or failed
            await message.reply(
                "⚠️ <b>URL Shortener not configured!</b>\n\n"
                f"Original URL: <code>{url}</code>\n\n"
                "Configure SHORTENER_API and SHORTENER_URL in environment variables.",
                parse_mode=enums.ParseMode.HTML
            )
        else:
            await message.reply(
                f"✅ <b>URL Shortened Successfully!</b>\n\n"
                f"Original: <code>{url}</code>\n\n"
                f"Shortened: <code>{short_url}</code>",
                parse_mode=enums.ParseMode.HTML
            )
    
    except Exception as e:
        logger.error(f"Error shortening URL: {e}")
        await message.reply("❌ Error shortening URL!")

async def ping_command(client: Bot, message: Message):
    """Handle /ping command - check bot status"""
    start_time = time.time()
    msg = await message.reply("🏓 <b>Pinging...</b>", parse_mode=enums.ParseMode.HTML)
    end_time = time.time()
    
    ping_time = round((end_time - start_time) * 1000, 2)
    
    # Get bot info
    bot = await client.get_me()
    
    await msg.edit_text(
        f"🏓 <b>Pong!</b>\n\n"
        f"🤖 Bot: @{bot.username}\n"
        f"⏱️ Ping: {ping_time}ms\n"
        f"✅ Status: Online",
        parse_mode=enums.ParseMode.HTML
    )


# ===================================
# SECTION 12: CALLBACK HANDLERS (Lines 2801-3200)
# ===================================

async def handle_callback_query(client: Bot, query: CallbackQuery):
    """Handle all callback queries"""
    try:
        data = query.data
        
        if data == "help":
            await query.answer()
            await show_user_help(client, query.message)
        
        elif data == "about":
            await query.answer()
            await about_command(client, query.message)
        
        elif data == "start":
            await query.answer()
            await show_welcome_message(client, query.message)
        
        elif data == "close":
            await query.answer("Closed!")
            await query.message.delete()
        
        elif data == "refresh":
            await query.answer("Refreshing...")
            await refresh_callback(client, query)
        
        elif data.startswith("help_"):
            await query.answer()
            await handle_help_callback(client, query)
        
        elif data.startswith("toggle_"):
            await query.answer()
            await handle_toggle_callback(client, query)
        
        elif data.startswith("autodel_"):
            await query.answer()
            await handle_autodel_callback(client, query)
        
        elif data.startswith("reqfsub_"):
            await query.answer()
            await handle_reqfsub_callback(client, query)
        
        elif data.startswith("botsettings_"):
            await query.answer()
            await handle_botsettings_callback(client, query)
        
        elif data.startswith("settings_"):
            await query.answer()
            await handle_settings_callback(client, query)
        
        elif data == "set_button":
            await query.answer()
            await handle_button_setting_callback(client, query)
        
        elif data == "broadcast_confirm":
            await query.answer()
            await handle_broadcast_confirm(client, query)
        
        elif data == "removechannel_confirm":
            await query.answer()
            await handle_removechannel_confirm(client, query)
        
        else:
            await query.answer("Button not configured!", show_alert=True)
    
    except Exception as e:
        logger.error(f"Error handling callback: {e}")
        await query.answer("Error processing request!", show_alert=True)

async def handle_help_callback(client: Bot, query: CallbackQuery):
    """Handle help command callbacks"""
    data = query.data
    
    if data == "help_genlink":
        await query.message.edit_text(
            "📝 <b>Generate Single File Link</b>\n\n"
            "Usage: Reply to a file with /genlink\n\n"
            "This command will generate a shareable link for a single file.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="help")]
            ])
        )
    elif data == "help_batch":
        await query.message.edit_text(
            "📦 <b>Create Batch Link</b>\n\n"
            "Usage: /batch (then follow instructions)\n\n"
            "This command creates a batch link for sequential files.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="help")]
            ])
        )
    elif data == "help_custom_batch":
        await query.message.edit_text(
            "🎯 <b>Create Custom Batch Link</b>\n\n"
            "Usage: /custom_batch (then follow instructions)\n\n"
            "This command creates a batch link for specific files.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="help")]
            ])
        )
    elif data == "help_special_link":
        await query.message.edit_text(
            "⭐ <b>Create Special Link</b>\n\n"
            "Usage: /special_link (then follow instructions)\n\n"
            "This command creates a link with custom message.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="help")]
            ])
        )
    elif data == "help_setchannel":
        await query.message.edit_text(
            "📺 <b>Set Database Channel</b>\n\n"
            "Usage: /setchannel @channel_username or channel_id\n\n"
            "This command sets the database channel for storing files.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="help")]
            ])
        )
    elif data == "help_checkchannel":
        await query.message.edit_text(
            "✅ <b>Check Channel Status</b>\n\n"
            "Usage: /checkchannel\n\n"
            "This command checks the database channel status.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="help")]
            ])
        )
    elif data == "help_users":
        await query.message.edit_text(
            "👥 <b>User Statistics</b>\n\n"
            "Usage: /users\n\n"
            "This command shows user statistics.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="help")]
            ])
        )
    elif data == "help_stats":
        await query.message.edit_text(
            "📊 <b>Bot Statistics</b>\n\n"
            "Usage: /stats\n\n"
            "This command shows complete bot statistics.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="help")]
            ])
        )
    elif data == "help_settings":
        await query.message.edit_text(
            "⚙️ <b>Main Settings</b>\n\n"
            "Usage: /settings\n\n"
            "This command opens the main settings panel.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="help")]
            ])
        )
    elif data == "help_botsettings":
        await query.message.edit_text(
            "🎨 <b>Bot Settings</b>\n\n"
            "Usage: /botsettings\n\n"
            "This command configures bot appearance.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="help")]
            ])
        )
    elif data == "help_files":
        await query.message.edit_text(
            "📁 <b>File Settings</b>\n\n"
            "Usage: /files\n\n"
            "This command configures file protection settings.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="help")]
            ])
        )
    elif data == "help_forcesub":
        await query.message.edit_text(
            "📢 <b>Force Subscribe Settings</b>\n\n"
            "Usage: /forcesub\n\n"
            "This command configures force subscribe settings.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="help")]
            ])
        )
    elif data == "help_shortener":
        await query.message.edit_text(
            "🔗 <b>URL Shortener</b>\n\n"
            "Usage: /shortener URL\n\n"
            "This command shortens URLs.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="help")]
            ])
        )
    elif data == "help_ping":
        await query.message.edit_text(
            "🏓 <b>Ping Command</b>\n\n"
            "Usage: /ping\n\n"
            "This command checks bot status and ping.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="help")]
            ])
        )

async def handle_toggle_callback(client: Bot, query: CallbackQuery):
    """Handle toggle callbacks"""
    data = query.data.replace("toggle_", "")
    
    # Get current settings
    settings = await client.db.get_settings()
    current_value = settings.get(data, False)
    
    # Toggle the value
    new_value = not current_value
    
    # Update in database
    await client.db.update_setting(data, new_value)
    
    # Update local settings
    client.settings[data] = new_value
    
    await query.answer(f"Setting updated: {new_value}")
    
    # Refresh the settings page
    if data in ["protect_content", "hide_caption", "channel_button"]:
        await files_command(client, query.message)
    elif data == "auto_delete":
        await auto_del_command(client, query.message)

async def handle_autodel_callback(client: Bot, query: CallbackQuery):
    """Handle auto delete time callbacks"""
    try:
        seconds = int(query.data.replace("autodel_", ""))
        
        # Update auto delete time
        await client.db.update_setting("auto_delete_time", seconds)
        
        # Update local settings
        client.settings["auto_delete_time"] = seconds
        
        await query.answer(f"Auto delete time set to {format_time(seconds)}")
        
        # Refresh the auto delete settings page
        await auto_del_command(client, query.message)
    
    except Exception as e:
        logger.error(f"Error in autodel callback: {e}")
        await query.answer("Error setting time!")

async def handle_reqfsub_callback(client: Bot, query: CallbackQuery):
    """Handle request FSub callbacks"""
    action = query.data.replace("reqfsub_", "")
    new_value = (action == "on")
    
    # Update setting
    await client.db.update_setting("request_fsub", new_value)
    client.settings["request_fsub"] = new_value
    
    await query.answer(f"Request FSub {'enabled' if new_value else 'disabled'}")
    
    # Refresh the settings page
    await req_fsub_command(client, query.message)

async def handle_botsettings_callback(client: Bot, query: CallbackQuery):
    """Handle bot settings callbacks"""
    data = query.data.replace("botsettings_", "")
    
    if data == "images":
        await handle_images_callback(client, query)
    elif data == "welcome":
        await handle_welcome_callback(client, query)
    elif data == "help":
        await handle_help_text_callback(client, query)
    elif data == "about":
        await handle_about_callback(client, query)
    elif data == "buttons":
        await handle_buttons_callback(client, query)
    elif data == "preview":
        await query.answer("Showing preview...")
        await show_welcome_message(client, query.message)

async def handle_images_callback(client: Bot, query: CallbackQuery):
    """Handle images callback"""
    settings = await client.db.get_settings()
    bot_pics = settings.get("bot_pics", Config.BOT_PICS)
    
    text = (
        "📸 <b>Welcome Images Settings</b>\n\n"
        f"Current number of images: {len(bot_pics)}\n\n"
        "To change images, add BOT_PICS to environment variables:\n"
        "BOT_PICS=url1,url2,url3\n\n"
        "Or use the bot settings command."
    )
    
    buttons = [
        [InlineKeyboardButton("🔙 Back", callback_data="botsettings")],
        [InlineKeyboardButton("🔒 Close", callback_data="close")]
    ]
    
    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )

async def handle_welcome_callback(client: Bot, query: CallbackQuery):
    """Handle welcome text callback"""
    settings = await client.db.get_settings()
    welcome_text = settings.get("welcome_text", "")
    
    text = (
        "💬 <b>Welcome Message Settings</b>\n\n"
        f"Current welcome message:\n<code>{welcome_text[:200] or 'Not set'}</code>\n\n"
        "To change, use environment variable:\n"
        "WELCOME_TEXT=Your welcome message\n\n"
        "Or edit in the database directly."
    )
    
    buttons = [
        [InlineKeyboardButton("🔙 Back", callback_data="botsettings")],
        [InlineKeyboardButton("🔒 Close", callback_data="close")]
    ]
    
    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )

async def handle_help_text_callback(client: Bot, query: CallbackQuery):
    """Handle help text callback"""
    settings = await client.db.get_settings()
    help_text = settings.get("help_text", "➪ I ᴀᴍ ᴀ ᴘʀɪᴠᴀᴛᴇ ғɪʟᴇ sʜᴀʀɪɴɢ ʙᴏᴛ, ᴍᴇᴀɴᴛ ᴛᴏ ᴘʀᴏᴠɪᴅᴇ ғɪʟᴇs ᴀɴᴅ ɴᴇᴄᴇssᴀʀʏ sᴛᴜғғ ᴛʜʀᴏᴜɢʜ sᴘᴇᴄɪᴀʟ ʟɪɴᴋ ғᴏʀ sᴘᴇᴄɪғɪᴄ ᴄʜᴀɴɴᴇʟs.")
    
    text = (
        "📚 <b>Help Message Settings</b>\n\n"
        f"Current help message:\n<code>{help_text[:200]}</code>\n\n"
        "This is the help message users see when they use /help command."
    )
    
    buttons = [
        [InlineKeyboardButton("🔙 Back", callback_data="botsettings")],
        [InlineKeyboardButton("🔒 Close", callback_data="close")]
    ]
    
    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )

async def handle_about_callback(client: Bot, query: CallbackQuery):
    """Handle about text callback"""
    settings = await client.db.get_settings()
    about_text = settings.get("about_text", "")
    
    text = (
        "ℹ️ <b>About Message Settings</b>\n\n"
        f"Current about message:\n<code>{about_text[:200] or 'Not set'}</code>\n\n"
        "To change, use environment variable:\n"
        "ABOUT_TEXT=Your about message\n\n"
        "Or edit in the database directly."
    )
    
    buttons = [
        [InlineKeyboardButton("🔙 Back", callback_data="botsettings")],
        [InlineKeyboardButton("🔒 Close", callback_data="close")]
    ]
    
    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )

async def handle_buttons_callback(client: Bot, query: CallbackQuery):
    """Handle buttons callback"""
    settings = await client.db.get_settings()
    button_string = settings.get("custom_button", "")
    
    text = (
        "🔘 <b>Custom Buttons Settings</b>\n\n"
        f"Current button configuration:\n<code>{button_string or 'Not set'}</code>\n\n"
        "Format: Button Text | URL (one per line)\n"
        "For multiple buttons in same row:\n"
        "Button1 | url1 : Button2 | url2"
    )
    
    buttons = [
        [InlineKeyboardButton("🔙 Back", callback_data="botsettings")],
        [InlineKeyboardButton("🔒 Close", callback_data="close")]
    ]
    
    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )

async def handle_settings_callback(client: Bot, query: CallbackQuery):
    """Handle settings callbacks"""
    data = query.data.replace("settings_", "")
    
    if data == "protection":
        await query.answer("Protection settings")
        # This would show protection settings
        await files_command(client, query.message)
    
    elif data == "files":
        await query.answer("File settings")
        await files_command(client, query.message)
    
    elif data == "autodel":
        await query.answer("Auto delete settings")
        await auto_del_command(client, query.message)
    
    elif data == "forcesub":
        await query.answer("Force subscribe settings")
        await forcesub_command(client, query.message)
    
    elif data == "reqfsub":
        await query.answer("Request FSub settings")
        await req_fsub_command(client, query.message)

async def handle_button_setting_callback(client: Bot, query: CallbackQuery):
    """Handle button setting callback"""
    user_id = query.from_user.id
    client.button_setting_state[user_id] = True
    
    await query.message.edit_text(
        "🔘 <b>SET CUSTOM BUTTON</b>\n\n"
        "Send me the button in this format:\n\n"
        "<code>Button Text | URL</code>\n\n"
        "Example:\n"
        "<code>Join Channel | https://t.me/example</code>\n\n"
        "For multiple buttons in same row:\n"
        "<code>Button1 | url1 : Button2 | url2</code>\n\n"
        "Send <code>cancel</code> to cancel.",
        parse_mode=enums.ParseMode.HTML
    )

async def handle_broadcast_confirm(client: Bot, query: CallbackQuery):
    """Handle broadcast confirmation"""
    await query.answer("Starting broadcast...")
    
    try:
        # Get the message to broadcast
        original_message = query.message.reply_to_message
        
        if not original_message:
            await query.message.edit_text("❌ No message to broadcast!")
            return
        
        # Get all users
        all_users = await client.db.get_all_users()
        total_users = len(all_users)
        
        if total_users == 0:
            await query.message.edit_text("❌ No users to broadcast to!")
            return
        
        # Update message
        await query.message.edit_text(
            f"📢 <b>BROADCAST STARTED</b>\n\n"
            f"Total users: {total_users}\n"
            f"Sent: 0/{total_users}\n"
            f"Failed: 0",
            parse_mode=enums.ParseMode.HTML
        )
        
        # Broadcast to users
        success = 0
        failed = 0
        
        for user_id in all_users:
            try:
                # Skip if user is banned
                if await client.db.is_user_banned(user_id):
                    failed += 1
                    continue
                
                # Forward the message
                await original_message.copy(user_id)
                success += 1
                
                # Update progress every 10 users
                if (success + failed) % 10 == 0:
                    try:
                        await query.message.edit_text(
                            f"📢 <b>BROADCAST IN PROGRESS</b>\n\n"
                            f"Total users: {total_users}\n"
                            f"Sent: {success}/{total_users}\n"
                            f"Failed: {failed}",
                            parse_mode=enums.ParseMode.HTML
                        )
                    except:
                        pass
                
                # Small delay to avoid flood
                await asyncio.sleep(0.1)
                
            except Exception as e:
                failed += 1
                logger.error(f"Error broadcasting to {user_id}: {e}")
        
        # Final update
        await query.message.edit_text(
            f"✅ <b>BROADCAST COMPLETED</b>\n\n"
            f"Total users: {total_users}\n"
            f"Successfully sent: {success}\n"
            f"Failed: {failed}\n\n"
            f"<i>Broadcast completed successfully!</i>",
            parse_mode=enums.ParseMode.HTML
        )
    
    except Exception as e:
        logger.error(f"Error in broadcast: {e}")
        await query.message.edit_text(
            f"❌ <b>BROADCAST FAILED</b>\n\n"
            f"Error: {str(e)}",
            parse_mode=enums.ParseMode.HTML
        )

async def handle_removechannel_confirm(client: Bot, query: CallbackQuery):
    """Handle remove channel confirmation"""
    await query.answer("Removing channel...")
    
    try:
        # Remove channel from database
        await client.db.remove_db_channel()
        client.db_channel = None
        
        await query.message.edit_text(
            "✅ <b>Database channel removed successfully!</b>\n\n"
            "You need to set a new channel using /setchannel\n"
            "to enable file sharing again.",
            parse_mode=enums.ParseMode.HTML
        )
    
    except Exception as e:
        logger.error(f"Error removing channel: {e}")
        await query.message.edit_text(
            f"❌ <b>Error removing channel!</b>\n\n"
            f"Error: {str(e)}",
            parse_mode=enums.ParseMode.HTML
        )

async def refresh_callback(client: Bot, query: CallbackQuery):
    """Handle refresh callback"""
    await query.answer("Refreshing...")
    
    # Check what type of page we're on
    message_text = query.message.text or ""
    
    if "USER STATISTICS" in message_text:
        await users_command(client, query.message)
    elif "BOT STATISTICS" in message_text:
        await stats_command(client, query.message)
    elif "FILES RELATED SETTINGS" in message_text:
        await files_command(client, query.message)
    elif "AUTO DELETE SETTINGS" in message_text:
        await auto_del_command(client, query.message)
    elif "REQUEST FSUB SETTINGS" in message_text:
        await req_fsub_command(client, query.message)
    elif "SETTINGS PANEL" in message_text:
        await settings_command(client, query.message)
    elif "ADMIN COMMANDS PANEL" in message_text:
        await show_admin_help(client, query.message)
    else:
        # Default: just show start
        await show_welcome_message(client, query.message)


# ===================================
# SECTION 13: WEB SERVER (Lines 3201-3300)
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
# SECTION 14: MAIN FUNCTION (Lines 3301-3400)
# ===================================

async def main():
    """Main function to start the bot"""
    print(BANNER)
    logger.info("🚀 Starting Advanced File Sharing Bot...")
    
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
        
        logger.info("✅ Bot is now running!")
        
        # Start web server if enabled
        if Config.WEB_SERVER:
            web_server_task = asyncio.create_task(start_web_server())
        
        # Keep the bot running
        await asyncio.Event().wait()
        
    except KeyboardInterrupt:
        logger.info("👋 Received stop signal, shutting down...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        # Stop the bot
        await bot.stop()
        
        if Config.WEB_SERVER and 'web_server_task' in locals():
            web_server_task.cancel()
        
        logger.info("👋 Bot stopped successfully.")

if __name__ == "__main__":
    # Run the bot
    asyncio.run(main())
