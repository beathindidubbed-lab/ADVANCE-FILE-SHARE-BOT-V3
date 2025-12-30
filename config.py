"""
Configuration File - Advanced Auto Filter Bot V3
All settings and environment variables
"""

import os
from os import environ

# ============ BOT CREDENTIALS ============
API_ID = int(environ.get("API_ID", "0"))
API_HASH = environ.get("API_HASH", "")
BOT_TOKEN = environ.get("BOT_TOKEN", "")

# ============ DATABASE ============
DATABASE_URI = environ.get("DATABASE_URI", "")
DATABASE_NAME = environ.get("DATABASE_NAME", "AdvanceAutoFilterBot")

# ============ CHANNELS ============
# FIXED: Allow 0 or empty to skip channel requirement
try:
    channels_str = environ.get("CHANNELS", "0")
    if channels_str and channels_str != "0":
        CHANNELS = [int(ch) if ch.startswith("-") else int(ch) for ch in channels_str.split()]
    else:
        CHANNELS = [0]
except:
    CHANNELS = [0]

LOG_CHANNEL = int(environ.get("LOG_CHANNEL", "0")) if environ.get("LOG_CHANNEL") else None

# ============ ADMINS ============
ADMINS = [int(admin) for admin in environ.get("ADMINS", "").split() if admin]
AUTH_USERS = [int(user) for user in environ.get("AUTH_USERS", "").split() if user]

# ============ FORCE SUBSCRIBE ============
FORCE_SUB_CHANNELS = [int(ch) for ch in environ.get("FORCE_SUB_CHANNELS", "0").split() if ch and ch != "0"]
REQUEST_FSUB = bool(environ.get("REQUEST_FSUB", "False") == "True")

# ============ BOT SETTINGS ============
WORKERS = int(environ.get("WORKERS", "4"))
PORT = int(environ.get("PORT", "8080"))

# ============ PICS ============
BOT_PICS = environ.get("BOT_PICS", "https://telegra.ph/file/d8d2e9cc6d60741c7e77d.jpg").split()

# ============ TEXT MESSAGES ============
WELCOME_TEXT = environ.get("WELCOME_TEXT", """
⚡ Hey, {mention}!

I am an advance file share bot 🤖
The best part is I am also support request forcesub feature.

To know detailed information click about me button below.

Made with ❤️
""")

HELP_TEXT = environ.get("HELP_TEXT", """
📚 <b>HELP MENU</b>

<b>→ I am a private file sharing bot, meant to provide files through special links for specific channels.</b>

<b>◈ Still have doubts, contact below persons / group as per your need!</b>
""")

ABOUT_TEXT = environ.get("ABOUT_TEXT", """
ℹ️ <b>ABOUT BOT</b>

<b>◈ Bot Name:</b> {bot_name}
<b>◈ Username:</b> @{username}
<b>◈ Framework:</b> Pyrogram
<b>◈ Language:</b> Python 3
<b>◈ Version:</b> V3.0

<b>◈ Made with ❤️</b>
""")

FORCE_SUB_TEXT = environ.get("FORCE_SUB_TEXT", """
⚠️ <b>JOIN OUR CHANNEL</b>

Dear {mention},

You need to join our channel to use this bot!

Please join the channel(s) and /start again.
""")

# ============ FILE SETTINGS ============
PROTECT_CONTENT = bool(environ.get("PROTECT_CONTENT", "True") == "True")
HIDE_CAPTION = bool(environ.get("HIDE_CAPTION", "False") == "True")
CUSTOM_CAPTION = environ.get("CUSTOM_CAPTION", "")

# Blockquote/Spoiler settings
USE_BLOCKQUOTE = bool(environ.get("USE_BLOCKQUOTE", "False") == "True")
BLOCKQUOTE_COLLAPSED = bool(environ.get("BLOCKQUOTE_COLLAPSED", "True") == "True")

# ============ AUTO DELETE ============
AUTO_DELETE_TIME = int(environ.get("AUTO_DELETE_TIME", "0"))
AUTO_DELETE_MSG = environ.get("AUTO_DELETE_MSG", """
⚠️ <b>AUTO DELETE ENABLED!</b>

This file will be deleted in <code>{time}</code> seconds.
Please save/forward it before deletion!
""")

AUTO_DEL_SUCCESS_MSG = environ.get("AUTO_DEL_SUCCESS_MSG", """
✅ <b>File Deleted Successfully!</b>

Click the link again to get the file.
""")

# ============ BUTTONS ============
CHANNEL_BUTTON = environ.get("CHANNEL_BUTTON", "")  # Format: Text | URL
CUSTOM_BUTTONS = environ.get("CUSTOM_BUTTONS", "")  # Format: Text1 | URL1 : Text2 | URL2

# ============ SUPPORT ============
SUPPORT_CHAT = environ.get("SUPPORT_CHAT", "")
UPDATES_CHANNEL = environ.get("UPDATES_CHANNEL", "")

# ============ ADVANCED ============
MAX_BTN = int(environ.get("MAX_BTN", "10"))
SINGLE_BUTTON = bool(environ.get("SINGLE_BUTTON", "False") == "True")
