"""
Advanced Auto Filter Bot V3 - Unified Version
All features in one file - No plugin system
"""

import sys
import logging
import asyncio
import os
import random
import aiohttp
from aiohttp import web
from pyrogram import Client, filters, idle
from pyrogram.enums import ParseMode
from pyrogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, 
    InlineKeyboardButton
)
from pyrogram.errors import (
    FloodWait, UserIsBlocked, InputUserDeactivated,
    UserNotParticipant
)

try:
    from pyromod import listen
except ImportError:
    print("ERROR: pyromod not installed!")
    sys.exit(1)

# ============================================================================
# 🛠 CONFIGURATION SECTION (THE BRAIN)
# ============================================================================
try:
    import config
    from config import (
        API_ID, API_HASH, BOT_TOKEN, ADMINS, CHANNELS, 
        UPDATES_CHANNEL, SUPPORT_CHAT, FORCE_SUB_CHANNELS, 
        AUTO_DELETE_TIME, CUSTOM_CAPTION, PROTECT_CONTENT, 
        REQUEST_FSUB, BOT_PICS, WELCOME_TEXT, FORCE_SUB_TEXT, 
        CUSTOM_BUTTONS, HIDE_CAPTION
    )
    # Essential Defaults
    CHANNEL_BUTTON = getattr(config, 'CHANNEL_BUTTON', True)
except ImportError:
    print("CRITICAL: config.py missing!")
    sys.exit(1)

# Global Filters
ADMIN_FILTER = filters.user(ADMINS)

# Logging Setup
logging.basicConfig(level=logging.INFO, format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s")
LOGGER = logging.getLogger(__name__)

# ============================================================================
# BOT CLASS
# ============================================================================

class Bot(Client):
    def __init__(self):
        from config import API_ID, API_HASH, BOT_TOKEN, WORKERS
        
        super().__init__(
            name="AdvanceAutoFilterBot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=WORKERS,
            parse_mode=ParseMode.HTML
        )
        self.LOGGER = LOGGER
        self.db_channel = None
        self.db_channel_id = None

    async def start(self):
        await super().start()
        
        me = await self.get_me()
        self.username = me.username
        self.id = me.id
        self.mention = me.mention
        self.first_name = me.first_name
        
        LOGGER.info(f"✅ Bot Started: @{me.username}")
        
        # Connect database
        try:
            from database.database import Database
            self.db = Database()
            await self.db.connect()
            LOGGER.info("✅ Database Connected")
        except Exception as e:
            LOGGER.warning(f"⚠️ Database: {e}")
            self.db = None
        
        LOGGER.info("")
        LOGGER.info("=" * 70)
        LOGGER.info("🎉 BOT IS READY!")
        LOGGER.info(f"   Bot: @{self.username}")
        LOGGER.info(f"   ID: {self.id}")
        LOGGER.info("=" * 70)
        LOGGER.info("")

    async def stop(self, *args):
        await super().stop()
        LOGGER.info("❌ Bot Stopped")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

# Encoding/Decoding functions
async def encode(string: str) -> str:
    """Encode string to base64-like format"""
    import base64
    string_bytes = string.encode("ascii")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    return base64_bytes.decode("ascii").rstrip("=")

async def decode(base64_string: str) -> str:
    """Decode base64-like format to string"""
    import base64
    base64_string += "=" * (-len(base64_string) % 4)
    base64_bytes = base64_string.encode("ascii")
    string_bytes = base64.urlsafe_b64decode(base64_bytes)
    return string_bytes.decode("ascii")

async def is_subscribed(client: Client, user_id: int, channels: list) -> bool:
    """Check if user is subscribed to all channels"""
    for channel_id in channels:
        if channel_id == 0:
            continue
        try:
            member = await client.get_chat_member(channel_id, user_id)
            if member.status not in ["administrator", "creator", "member"]:
                return False
        except UserNotParticipant:
            return False
        except:
            return False
    return True

async def delete_files(messages: list, client: Client, notification: Message, link: str):
    """Auto-delete files after specified time"""
    from config import AUTO_DELETE_TIME
    await asyncio.sleep(AUTO_DELETE_TIME)
    
    for msg in messages:
        try:
            await msg.delete()
        except:
            pass
    
    try:
        await notification.edit_text(
            f"⏱️ <b>Files Deleted!</b>\n\n"
            f"Click below to get files again:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔗 Get Files Again", url=link)]
            ])
        )
    except:
        pass

def parse_custom_buttons(button_string: str) -> list:
    """Parse custom button string to button list"""
    if not button_string:
        return []
    
    buttons = []
    lines = button_string.strip().split('\n')
    
    for line in lines:
        if ':' in line:
            button_row = []
            pairs = line.split(':')
            for pair in pairs:
                if '|' in pair:
                    parts = pair.split('|', 1)
                    if len(parts) == 2:
                        text = parts[0].strip()
                        url = parts[1].strip()
                        button_row.append(InlineKeyboardButton(text, url=url))
            if button_row:
                buttons.append(button_row)
        elif '|' in line:
            parts = line.split('|', 1)
            if len(parts) == 2:
                text = parts[0].strip()
                url = parts[1].strip()
                buttons.append([InlineKeyboardButton(text, url=url)])
    
    return buttons

"""
============================================================================
Start Command - Welcome users and handle file links
Complete file sharing functionality
============================================================================
"""


@Client.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    """Handle /start command"""
    
    user_id = message.from_user.id
    
    # Add user to database
    if hasattr(client, "db") and client.db:
        if not await client.db.is_user_exist(user_id):
            await client.db.add_user(user_id)
        
        # Check if banned
        if await client.db.is_user_banned(user_id):
            await message.reply_text(
                "🚫 <b>You are banned!</b>\n\nContact support for help.",
                quote=True
            )
            return
    
    # Check for file parameter
    if len(message.command) > 1:
        file_param = message.command[1]
        await handle_file_request(client, message, file_param)
        return
    
    # Show welcome message
    await show_welcome(client, message)


async def show_welcome(client: Client, message: Message):
    """Show welcome screen"""
    
    # Get random welcome image
    pic = random.choice(BOT_PICS) if BOT_PICS else None
    
    # Format welcome text
    welcome_text = WELCOME_TEXT.format(
        first=message.from_user.first_name,
        last=message.from_user.last_name or "",
        username=f"@{message.from_user.username}" if message.from_user.username else "None",
        mention=message.from_user.mention,
        id=message.from_user.id
    )
    
    # Create buttons
    buttons = [
        [
            InlineKeyboardButton("📚 Help", callback_data="help"),
            InlineKeyboardButton("ℹ️ About", callback_data="about")
        ]
    ]
    
    # Add channel/support buttons
    if UPDATES_CHANNEL:
        buttons.append([
            InlineKeyboardButton("📢 Updates Channel", url=f"https://t.me/{UPDATES_CHANNEL.replace('@', '')}")
        ])
    
    if SUPPORT_CHAT:
        buttons.append([
            InlineKeyboardButton("💬 Support Chat", url=f"https://t.me/{SUPPORT_CHAT.replace('@', '')}")
        ])
    
    # Parse custom buttons
    if CUSTOM_BUTTONS:
        custom_btns = parse_custom_buttons(CUSTOM_BUTTONS)
        buttons.extend(custom_btns)
    
    buttons.append([
        InlineKeyboardButton("🔐 Close", callback_data="close")
    ])
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    # Send with image
    if pic:
        try:
            await message.reply_photo(
                photo=pic,
                caption=welcome_text,
                reply_markup=reply_markup,
                quote=True
            )
            return
        except:
            pass
    
    # Fallback to text
    await message.reply_text(
        text=welcome_text,
        reply_markup=reply_markup,
        quote=True
    )


async def handle_file_request(client: Client, message: Message, file_param: str):
    """Handle file sharing requests"""
    
    user_id = message.from_user.id
    
    # Check force subscribe
    if FORCE_SUB_CHANNELS:
        is_joined = await is_subscribed(client, user_id, FORCE_SUB_CHANNELS)
        
        if not is_joined:
            # Show force subscribe message
            buttons = []
            
            for channel_id in FORCE_SUB_CHANNELS:
                if channel_id == 0:
                    continue
                
                try:
                    chat = await client.get_chat(channel_id)
                    
                    # Generate invite link
                    if REQUEST_FSUB:
                        # Request join mode
                        try:
                            invite_link = await client.create_chat_invite_link(
                                channel_id,
                                creates_join_request=True
                            )
                            buttons.append([
                                InlineKeyboardButton(
                                    f"📢 Request to Join {chat.title}",
                                    url=invite_link.invite_link
                                )
                            ])
                        except:
                            buttons.append([
                                InlineKeyboardButton(
                                    f"📢 Join {chat.title}",
                                    url=f"https://t.me/{chat.username}" if chat.username else f"https://t.me/c/{str(channel_id)[4:]}"
                                )
                            ])
                    else:
                        # Direct join mode
                        if chat.username:
                            buttons.append([
                                InlineKeyboardButton(
                                    f"📢 Join {chat.title}",
                                    url=f"https://t.me/{chat.username}"
                                )
                            ])
                        else:
                            try:
                                invite_link = await client.create_chat_invite_link(channel_id)
                                buttons.append([
                                    InlineKeyboardButton(
                                        f"📢 Join {chat.title}",
                                        url=invite_link.invite_link
                                    )
                                ])
                            except:
                                pass
                except:
                    pass
            
            buttons.append([
                InlineKeyboardButton("🔄 Try Again", url=f"https://t.me/{client.username}?start={file_param}")
            ])
            
            # Format force sub text
            force_text = FORCE_SUB_TEXT.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name or "",
                username=f"@{message.from_user.username}" if message.from_user.username else "None",
                mention=message.from_user.mention,
                id=message.from_user.id
            )
            
            await message.reply_text(
                force_text,
                reply_markup=InlineKeyboardMarkup(buttons),
                quote=True
            )
            return
    
    # Decode file parameter
    try:
        decoded = await decode(file_param)
    except:
        await message.reply_text("❌ <b>Invalid link!</b>", quote=True)
        return
    
    # Handle different link types
    if decoded.startswith("get-"):
        # Single file
        await send_single_file(client, message, decoded)
    elif decoded.startswith("custombatch-"):
        # Custom batch
        await send_custom_batch(client, message, decoded)
    else:
        await message.reply_text("❌ <b>Unknown link type!</b>", quote=True)


async def send_single_file(client: Client, message: Message, decoded: str):
    """Send single file"""
    
    if not hasattr(client, 'db_channel') or not client.db_channel:
        await message.reply_text("❌ <b>Bot not configured properly!</b>", quote=True)
        return
    
    try:
        # Extract message ID
        file_id = int(decoded.split("-")[1])
        channel_id = abs(client.db_channel.id)
        msg_id = file_id // channel_id
        
        # Fetch message
        file_msg = await client.get_messages(client.db_channel.id, msg_id)
        
        if not file_msg:
            await message.reply_text("❌ <b>File not found!</b>", quote=True)
            return
        
        # Prepare caption
        caption = file_msg.caption or ""
        
        if CUSTOM_CAPTION:
            # Get file info
            file_name = "Unknown"
            file_size = "Unknown"
            
            if file_msg.document:
                file_name = file_msg.document.file_name
                file_size = f"{file_msg.document.file_size / (1024*1024):.2f} MB"
            elif file_msg.video:
                file_name = file_msg.video.file_name or "video.mp4"
                file_size = f"{file_msg.video.file_size / (1024*1024):.2f} MB"
            elif file_msg.audio:
                file_name = file_msg.audio.file_name or "audio.mp3"
                file_size = f"{file_msg.audio.file_size / (1024*1024):.2f} MB"
            
            # Format custom caption
            caption = CUSTOM_CAPTION.format(
                filename=file_name,
                filesize=file_size,
                previouscaption=caption if not HIDE_CAPTION else ""
            )
        elif HIDE_CAPTION:
            caption = ""
        
        # Add custom button
        reply_markup = None
        if CHANNEL_BUTTON and CUSTOM_BUTTONS:
            custom_btns = parse_custom_buttons(CUSTOM_BUTTONS)
            if custom_btns:
                reply_markup = InlineKeyboardMarkup(custom_btns)
        
        # Copy message
        sent_msg = await file_msg.copy(
            chat_id=message.chat.id,
            caption=caption,
            reply_markup=reply_markup,
            protect_content=PROTECT_CONTENT
        )
        
        # Auto delete if enabled
        if AUTO_DELETE_TIME > 0:
            # Send notification
            link = f"https://t.me/{client.username}?start={await encode(decoded)}"
            
            notification = await message.reply_text(
                f"⏱️ <b>Auto-Delete Enabled!</b>\n\n"
                f"This file will be deleted in <code>{AUTO_DELETE_TIME // 60}</code> minutes.\n\n"
                f"Click below to get the file again after deletion:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔗 Click Here", url=link)],
                    [InlineKeyboardButton("🔒 Close", callback_data="close")]
                ]),
                quote=True
            )
            
            # Schedule deletion
            await delete_files([sent_msg], client, notification, link)
    
    except Exception as e:
        await message.reply_text(f"❌ <b>Error:</b> <code>{str(e)}</code>", quote=True)


async def send_custom_batch(client: Client, message: Message, decoded: str):
    """Send custom batch files"""
    
    if not hasattr(client, 'db_channel') or not client.db_channel:
        await message.reply_text("❌ <b>Bot not configured properly!</b>", quote=True)
        return
    
    try:
        # Extract message IDs
        parts = decoded.split("-")[1:]  # Skip "custombatch"
        channel_id = abs(client.db_channel.id)
        msg_ids = [int(part) // channel_id for part in parts]
        
        # Send files
        status_msg = await message.reply_text(
            f"📦 <b>Sending {len(msg_ids)} files...</b>",
            quote=True
        )
        
        sent_messages = []
        
        for msg_id in msg_ids:
            try:
                file_msg = await client.get_messages(client.db_channel.id, msg_id)
                
                if file_msg:
                    # Prepare caption
                    caption = file_msg.caption or ""
                    
                    if CUSTOM_CAPTION:
                        file_name = "Unknown"
                        file_size = "Unknown"
                        
                        if file_msg.document:
                            file_name = file_msg.document.file_name
                            file_size = f"{file_msg.document.file_size / (1024*1024):.2f} MB"
                        
                        caption = CUSTOM_CAPTION.format(
                            filename=file_name,
                            filesize=file_size,
                            previouscaption=caption if not HIDE_CAPTION else ""
                        )
                    elif HIDE_CAPTION:
                        caption = ""
                    
                    # Copy message
                    sent = await file_msg.copy(
                        chat_id=message.chat.id,
                        caption=caption,
                        protect_content=PROTECT_CONTENT
                    )
                    sent_messages.append(sent)
            except:
                pass
        
        await status_msg.edit_text(f"✅ <b>Sent {len(sent_messages)} files!</b>")
        
        # Auto delete if enabled
        if AUTO_DELETE_TIME > 0 and sent_messages:
            link = f"https://t.me/{client.username}?start={await encode(decoded)}"
            
            notification = await message.reply_text(
                f"⏱️ <b>Auto-Delete Enabled!</b>\n\n"
                f"These files will be deleted in <code>{AUTO_DELETE_TIME // 60}</code> minutes.\n\n"
                f"Click below to get files again after deletion:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔗 Click Here", url=link)],
                    [InlineKeyboardButton("🔒 Close", callback_data="close")]
                ]),
                quote=True
            )
            
            await delete_files(sent_messages, client, notification, link)
    
    except Exception as e:
        await message.reply_text(f"❌ <b>Error:</b> <code>{str(e)}</code>", quote=True)


"""
============================================================================
MAXIMUM VERBOSITY - Logs EVERYTHING
============================================================================
"""

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@Client.on_message()
async def log_all_messages(client: Client, message: Message):
    """Logs EVERY single message received"""
    
    logger.info("=" * 80)
    logger.info("MESSAGE RECEIVED!")
    logger.info(f"Chat ID: {message.chat.id}")
    logger.info(f"Chat Type: {message.chat.type}")
    logger.info(f"From User: {message.from_user.first_name if message.from_user else 'None'}")
    logger.info(f"User ID: {message.from_user.id if message.from_user else 'None'}")
    logger.info(f"Text: {message.text}")
    logger.info(f"Message ID: {message.id}")
    logger.info("=" * 80)
    
    # Also print to console
    print("=" * 80)
    print("🔔 MESSAGE RECEIVED!")
    print(f"From: {message.from_user.first_name if message.from_user else 'Unknown'}")
    print(f"User ID: {message.from_user.id if message.from_user else 'Unknown'}")
    print(f"Text: {message.text}")
    print(f"Chat Type: {message.chat.type}")
    print("=" * 80)
    
    # Try to respond
    try:
        await message.reply_text(
            f"✅ <b>MESSAGE RECEIVED!</b>\n\n"
            f"<b>Your message:</b> {message.text}\n"
            f"<b>Your ID:</b> <code>{message.from_user.id}</code>\n"
            f"<b>Chat Type:</b> {message.chat.type}\n\n"
            f"<b>Bot is definitely working!</b>",
            quote=True
        )
        print("✅ Response sent successfully!")
    except Exception as e:
        print(f"❌ Failed to respond: {e}")
        logger.error(f"Failed to respond: {e}")

@Client.on_callback_query()
async def log_callbacks(client: Client, query: CallbackQuery):
    """Logs all callback queries"""
    print(f"🔘 CALLBACK: {query.data} from {query.from_user.id}")



"""
============================================================================
Special Link Command - Create Links with Custom Start Message
Get an editable link with custom message (moderators only)
============================================================================
"""

# Store special links in database
special_links = {}

@Client.on_message(filters.private & filters.user(ADMINS) & filters.command("special_link"))
async def special_link_command(client: Client, message: Message):
    """Generate special link with custom message"""
    
    if not hasattr(client, "db_channel"):
        await message.reply_text(
            "❌ <b>Database Channel Not Configured!</b>",
            quote=True
        )
        return
    
    await message.reply_text(
        "🌟 <b>SPECIAL LINK GENERATOR</b>\n\n"
        "<b>Step 1:</b> Forward message(s) from database channel\n"
        "Send /done when finished\n\n"
        "⏱️ <b>Waiting for messages...</b>",
        quote=True
    )
    
    message_ids = []
    
    # Collect messages
    while True:
        try:
            user_msg = await client.listen(message.chat.id, timeout=300)
            
            if user_msg.text and user_msg.text.lower() == '/done':
                break
            
            if user_msg.forward_from_chat and user_msg.forward_from_chat.id == client.db_channel.id:
                msg_id = user_msg.forward_from_message_id
                message_ids.append(msg_id)
                await user_msg.reply_text(
                    f"✅ Added! Total: {len(message_ids)}\n\nSend more or /done",
                    quote=True
                )
            else:
                await user_msg.reply_text("❌ Forward from database channel!", quote=True)
        
        except:
            await message.reply_text("❌ Timeout!", quote=True)
            return
    
    if not message_ids:
        await message.reply_text("❌ No messages added!", quote=True)
        return
    
    # Ask for custom message
    await message.reply_text(
        "🌟 <b>Step 2:</b> Send custom start message\n\n"
        "This message will appear when users click the link.\n\n"
        "<b>Example:</b>\n"
        "🎬 Welcome! Here are your movies!\n"
        "Enjoy watching! 🍿\n\n"
        "⏱️ <b>Waiting for message...</b>",
        quote=True
    )
    
    try:
        custom_msg = await client.listen(message.chat.id, timeout=300)
        custom_text = custom_msg.text or custom_msg.caption or "Here are your files!"
    except:
        await message.reply_text("❌ Timeout!", quote=True)
        return
    
    # Generate special link
    try:
        channel_id = abs(client.db_channel.id)
        
        # Encode message IDs
        if len(message_ids) == 1:
            converted = message_ids[0] * channel_id
            link_string = f"get-{converted}"
        else:
            converted_ids = [str(msg_id * channel_id) for msg_id in message_ids]
            link_string = f"custombatch-{'-'.join(converted_ids)}"
        
        encoded = await encode(link_string)
        
        # Store custom message
        if hasattr(client, "db") and client.db:
            await client.db.settings.update_one(
                {"_id": f"special_{encoded}"},
                {"$set": {"message": custom_text}},
                upsert=True
            )
        
        link = f"https://t.me/{client.username}?start={encoded}"
        
        # Create reply
        reply_text = f"""
✅ <b>Special Link Generated!</b>

<b>📊 Total Files:</b> <code>{len(message_ids)}</code>

<b>💬 Custom Message:</b>
{custom_text}

<b>🔗 Special Link:</b>
<code>{link}</code>

<b>🌟 When users click this link, they'll see your custom message first, then get the files!</b>
"""
        
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 Copy Link", url=link)]
        ])
        
        await message.reply_text(
            reply_text,
            quote=True,
            reply_markup=buttons,
            disable_web_page_preview=True
        )
    
    except Exception as e:
        await message.reply_text(
            f"❌ <b>Error!</b>\n\n<code>{str(e)}</code>",
            quote=True
        )


# Add handler to show custom message when special link is clicked
async def handle_special_link(client: Client, message: Message, file_param: str):
    """Show custom message for special links"""
    
    # Check if special link exists
    if hasattr(client, "db") and client.db:
        special_data = await client.db.settings.find_one({"_id": f"special_{file_param}"})
        
        if special_data and 'message' in special_data:
            # Show custom message first
            await message.reply_text(
                special_data['message'],
                quote=True
            )
    
    # Continue with normal file sending
    # (This is called from start.py's file handling)

"""
============================================================================
Shortener Command - Shorten Any Shareable Links
Uses URL shortener API (moderators only)
============================================================================
"""

# Popular URL shortener APIs (choose one or add your own)
SHORTENER_API = "https://ulvis.net/api.php"  # Free, no API key needed

@Client.on_message(filters.private & filters.user(ADMINS) & filters.command("shortener"))
async def shortener_command(client: Client, message: Message):
    """Shorten any URL"""
    
    # Check if URL provided
    if len(message.command) < 2:
        await message.reply_text(
            "🔗 <b>URL SHORTENER</b>\n\n"
            "<b>Usage:</b> <code>/shortener [URL]</code>\n\n"
            "<b>Example:</b>\n"
            "<code>/shortener https://t.me/YourBot?start=ABC123XYZ</code>\n\n"
            "Or reply to a message containing a URL with /shortener",
            quote=True
        )
        return
    
    # Get URL
    if len(message.command) >= 2:
        url = message.command[1]
    elif message.reply_to_message and message.reply_to_message.text:
        url = message.reply_to_message.text.strip()
    else:
        await message.reply_text("❌ Please provide a URL!", quote=True)
        return
    
    # Validate URL
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Show loading
    status_msg = await message.reply_text("⏳ <b>Shortening URL...</b>", quote=True)
    
    # Shorten URL
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{SHORTENER_API}?url={url}") as response:
                if response.status == 200:
                    short_url = await response.text()
                    short_url = short_url.strip()
                    
                    # Create reply
                    reply_text = f"""
✅ <b>URL Shortened Successfully!</b>

<b>🔗 Original URL:</b>
<code>{url}</code>

<b>✂️ Short URL:</b>
<code>{short_url}</code>

<b>💡 Share the short URL with users!</b>
"""
                    
                    await status_msg.edit_text(reply_text)
                else:
                    await status_msg.edit_text(
                        f"❌ <b>Error!</b> Status: {response.status}\n\n"
                        "Try another URL shortener or check your link."
                    )
    
    except Exception as e:
        await status_msg.edit_text(
            f"❌ <b>Error Shortening URL!</b>\n\n<code>{str(e)}</code>\n\n"
            "Try again or use a different URL shortener."
        )


@Client.on_message(filters.private & filters.user(ADMINS) & filters.command("shortener_settings"))
async def shortener_settings(client: Client, message: Message):
    """Configure URL shortener"""
    
    await message.reply_text(
        "⚙️ <b>SHORTENER SETTINGS</b>\n\n"
        "<b>Current Shortener:</b> ulvis.net\n\n"
        "<b>Available Shorteners:</b>\n"
        "• ulvis.net (current)\n"
        "• tinyurl.com\n"
        "• is.gd\n"
        "• v.gd\n\n"
        "<b>To change:</b> Edit <code>plugins/shortener.py</code>\n"
        "Update SHORTENER_API variable\n\n"
        "<b>Custom API:</b> You can add your own API like:\n"
        "• bit.ly (needs API key)\n"
        "• short.io (needs API key)\n"
        "• rebrandly.com (needs API key)",
        quote=True
    )


"""
============================================================================
Settings Command - Beautiful Interactive UI with Toggles
EXACTLY like EvaMaria screenshots - /forcesub, /files, /auto_del, /req_fsub
============================================================================
"""

# ========== MAIN SETTINGS COMMAND ==========

@Client.on_message(filters.private & filters.user(ADMINS) & filters.command("settings"))
async def settings_command(client: Client, message: Message):
    """Main settings menu"""
    
    text = """
⚙️ <b>SETTINGS PANEL</b>

<b>Configure your bot settings below:</b>

🔒 <b>Protection Settings</b>
📁 <b>File Settings</b>
🗑️ <b>Auto Delete Settings</b>
📢 <b>Force Subscribe Settings</b>

<i>Click a button to configure</i>
"""
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔒 Protection", callback_data="setting_protection"),
            InlineKeyboardButton("📁 Files", callback_data="setting_files")
        ],
        [
            InlineKeyboardButton("🗑️ Auto Delete", callback_data="setting_auto_delete"),
            InlineKeyboardButton("📢 Force Sub", callback_data="setting_force_sub")
        ],
        [
            InlineKeyboardButton("⚙️ Request FSub", callback_data="setting_req_fsub")
        ],
        [
            InlineKeyboardButton("🔒 Close", callback_data="close")
        ]
    ])
    
    await message.reply_text(text, reply_markup=buttons, quote=True)


# ========== FORCE SUBSCRIBE SETTINGS (/forcesub command) ==========

@Client.on_message(filters.private & filters.user(ADMINS) & filters.command("forcesub"))
async def forcesub_command(client: Client, message: Message):
    """Force subscribe settings - Detailed Channel Management"""
    
    from config import FORCE_SUB_CHANNELS
    
    # Get current status
    is_enabled = len(FORCE_SUB_CHANNELS) > 0 and FORCE_SUB_CHANNELS[0] != 0
    status_icon = "✅" if is_enabled else "❌"
    status_text = "ENABLED" if is_enabled else "DISABLED"
    
    text = f"""
👥 <b>FORCE SUB COMMANDS</b>

<b>Current Status:</b> {status_icon} <b>{status_text}</b>

<b>Available Commands:</b>

<b>/fsub_chnl</b> - Check current force-sub channels (Admins)

<b>/add_fsub</b> - Add one or multiple force sub channels (Owner)

<b>/del_fsub</b> - Delete one or multiple force sub channels (Owner)
"""
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔒 Close", callback_data="close")]
    ])
    
    await message.reply_text(text, reply_markup=buttons, quote=True)


@Client.on_callback_query(filters.regex("^setting_force_sub$"))
async def force_sub_callback(client: Client, query: CallbackQuery):
    """Force subscribe settings panel with back button"""
    
    from config import FORCE_SUB_CHANNELS
    
    is_enabled = len(FORCE_SUB_CHANNELS) > 0 and FORCE_SUB_CHANNELS[0] != 0
    status_icon = "✅" if is_enabled else "❌"
    
    text = f"""
📢 <b>FORCE SUBSCRIBE SETTINGS</b>

<b>Status:</b> {status_icon} <b>{'ENABLED' if is_enabled else 'DISABLED'}</b>

<b>Description:</b>
Force users to join your channel(s) before accessing files.

<b>Commands:</b>
• <code>/forcesub</code> - View commands
• <code>/fsub_chnl</code> - Check channels
• <code>/add_fsub</code> - Add channel
• <code>/del_fsub</code> - Remove channel
"""
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="settings_main")],
        [InlineKeyboardButton("🔒 Close", callback_data="close")]
    ])
    
    await query.message.edit_text(text, reply_markup=buttons)


# ========== REQUEST FORCE SUBSCRIBE (/req_fsub command) ==========

@Client.on_message(filters.private & filters.user(ADMINS) & filters.command("req_fsub"))
async def req_fsub_command(client: Client, message: Message):
    """Request force subscribe settings - Handle Join Requests"""
    
    # Get current status from database
    if hasattr(client, "db") and client.db:
        req_fsub_enabled = await client.db.get_setting("request_fsub")
    else:
        req_fsub_enabled = REQUEST_FSUB
    
    status_icon = "✅" if req_fsub_enabled else "❌"
    on_btn = "🟢 ON" if req_fsub_enabled else "ON"
    off_btn = "OFF" if req_fsub_enabled else "🔴 OFF"
    
    text = f"""
👥 <b>REQUEST FSUB SETTINGS</b>

🔔 <b>REQUEST FSUB MODE:</b> {status_icon}

<b>CLICK BELOW BUTTONS TO CHANGE SETTINGS</b>
"""
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(on_btn, callback_data="req_fsub_on"),
            InlineKeyboardButton(off_btn, callback_data="req_fsub_off")
        ],
        [
            InlineKeyboardButton("⚙️ MORE SETTINGS ⚙️", callback_data="req_fsub_more")
        ],
        [
            InlineKeyboardButton("🔒 Close", callback_data="close")
        ]
    ])
    
    await message.reply_text(text, reply_markup=buttons, quote=True)


@Client.on_callback_query(filters.regex("^req_fsub_(on|off)$"))
async def req_fsub_toggle(client: Client, query: CallbackQuery):
    """Interactive toggle for request force subscribe"""
    
    if query.from_user.id not in ADMINS:
        await query.answer("❌ You're not authorized!", show_alert=True)
        return
    
    action = query.data.split("_")[2]
    new_value = True if action == "on" else False
    
    # Update in database
    if hasattr(client, "db") and client.db:
        await client.db.update_setting("request_fsub", new_value)
    
    # Update config
    import config
    config.REQUEST_FSUB = new_value
    
    await query.answer(f"✅ Request FSub {'Enabled' if new_value else 'Disabled'}!")
    
    # Refresh display with updated status
    status_icon = "✅" if new_value else "❌"
    on_btn = "🟢 ON" if new_value else "ON"
    off_btn = "OFF" if new_value else "🔴 OFF"
    
    text = f"""
👥 <b>REQUEST FSUB SETTINGS</b>

🔔 <b>REQUEST FSUB MODE:</b> {status_icon}

<b>CLICK BELOW BUTTONS TO CHANGE SETTINGS</b>
"""
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(on_btn, callback_data="req_fsub_on"),
            InlineKeyboardButton(off_btn, callback_data="req_fsub_off")
        ],
        [
            InlineKeyboardButton("⚙️ MORE SETTINGS ⚙️", callback_data="req_fsub_more")
        ],
        [
            InlineKeyboardButton("🔒 Close", callback_data="close")
        ]
    ])
    
    await query.message.edit_text(text, reply_markup=buttons)


# ========== FILES SETTINGS (/files command) ==========

@Client.on_message(filters.private & filters.user(ADMINS) & filters.command("files"))
async def files_command(client: Client, message: Message):
    """File settings panel for protection and captions"""
    
    # Get current settings
    if hasattr(client, "db") and client.db:
        protect = await client.db.get_setting("protect_content")
        hide_caption = await client.db.get_setting("hide_caption")
        channel_btn = await client.db.get_setting("channel_button")
    else:
        # Fallback to config
        from config import PROTECT_CONTENT, HIDE_CAPTION
        protect = PROTECT_CONTENT
        hide_caption = HIDE_CAPTION
        channel_btn = True
        
    protect_icon = "❌" if protect else "✅"
    hide_icon = "❌" if hide_caption else "✅"
    channel_icon = "✅" if channel_btn else "❌"
    
    text = f"""
📁 <b>FILES RELATED SETTINGS</b>

🔒 <b>PROTECT CONTENT:</b> {'DISABLED' if not protect else 'ENABLED'} {protect_icon}

🎭 <b>HIDE CAPTION:</b> {'DISABLED' if not hide_caption else 'ENABLED'} {hide_icon}

📢 <b>CHANNEL BUTTON:</b> {'ENABLED' if channel_btn else 'DISABLED'} {channel_icon}

<b>CLICK BELOW BUTTONS TO CHANGE SETTINGS</b>
"""
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"PROTECT CONTENT: {'❌' if protect else '✅'}", callback_data=f"file_protect_{'off' if protect else 'on'}")
        ],
        [
            InlineKeyboardButton(f"HIDE CAPTION: {'❌' if hide_caption else '✅'}", callback_data=f"file_caption_{'off' if hide_caption else 'on'}")
        ],
        [
            InlineKeyboardButton(f"CHANNEL BUTTON: {'✅' if channel_btn else '❌'}", callback_data=f"file_channel_{'off' if channel_btn else 'on'}")
        ],
        [
            InlineKeyboardButton("◈ SET BUTTON ◈", callback_data="file_set_button")
        ],
        [
            InlineKeyboardButton("🔄 REFRESH", callback_data="files_refresh"),
            InlineKeyboardButton("🔒 CLOSE", callback_data="close")
        ]
    ])
    
    await message.reply_text(text, reply_markup=buttons, quote=True)


# ========== AUTO DELETE SETTINGS (/auto_del command) ==========

@Client.on_message(filters.private & filters.user(ADMINS) & filters.command("auto_del"))
async def auto_del_command(client: Client, message: Message):
    """Auto delete configuration and timer settings"""
    
    from config import AUTO_DELETE_TIME
    
    # Get current settings
    if hasattr(client, "db") and client.db:
        auto_del_enabled = await client.db.get_setting("auto_delete")
        del_time = await client.db.get_setting("auto_delete_time") or AUTO_DELETE_TIME
    else:
        auto_del_enabled = AUTO_DELETE_TIME > 0
        del_time = AUTO_DELETE_TIME
        
    status_icon = "✅" if auto_del_enabled else "❌"
    minutes = del_time // 60 if del_time else 5
    
    text = f"""
🗑️ <b>AUTO DELETE SETTINGS</b>

🔔 <b>AUTO DELETE MODE:</b> {'ENABLED' if auto_del_enabled else 'DISABLED'} {status_icon}

⏱️ <b>DELETE TIMER:</b> {minutes} MINUTES

<b>CLICK BELOW BUTTONS TO CHANGE SETTINGS</b>
"""
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("DISABLE MODE ❌" if auto_del_enabled else "ENABLE MODE ✅", 
                                 callback_data="auto_del_toggle")
        ],
        [
            InlineKeyboardButton("◈ SET TIMER ⏱️", callback_data="auto_del_set_timer")
        ],
        [
            InlineKeyboardButton("🔄 REFRESH", callback_data="auto_del_refresh"),
            InlineKeyboardButton("🔒 CLOSE", callback_data="close")
        ]
    ])
    
    await message.reply_text(text, reply_markup=buttons, quote=True)

"""
============================================================================
Admin Database Commands - User Management & Broadcasting
Complete control over your bot's users
============================================================================
"""

@Client.on_message(filters.private & filters.command("broadcast"))
async def broadcast_handler(client: Client, message: Message):
    """High-speed broadcast to all users"""
    from config import ADMINS
    
    # Auth Check
    if message.from_user.id not in ADMINS:
        return

    if not message.reply_to_message:
        await message.reply_text(
            "📢 <b>BROADCAST</b>\n\n"
            "Reply to a message with <code>/broadcast</code> to send it to all users.",
            quote=True
        )
        return
    
    if not hasattr(client, "db") or not client.db:
        await message.reply_text("❌ Database not connected!", quote=True)
        return

    users = await client.db.get_all_users()
    total_users = await client.db.total_users_count()
    
    status_msg = await message.reply_text(
        f"🚀 <b>Broadcast Started!</b>\n\n"
        f"<b>Total Users:</b> <code>{total_users}</code>\n"
        f"<b>Progress:</b> <code>0%</code>",
        quote=True
    )
    
    done = 0
    failed = 0
    success = 0
    start_time = asyncio.get_event_loop().time()
    
    async for user in users:
        user_id = user["id"]
        try:
            await message.reply_to_message.copy(chat_id=user_id)
            success += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await message.reply_to_message.copy(chat_id=user_id)
            success += 1
        except (UserIsBlocked, InputUserDeactivated):
            await client.db.delete_user(user_id)
            failed += 1
        except Exception:
            failed += 1
        
        done += 1
        
        if done % 20 == 0:
            percentage = (done / total_users) * 100
            try:
                await status_msg.edit_text(
                    f"🚀 <b>Broadcast in Progress...</b>\n\n"
                    f"<b>Total:</b> <code>{total_users}</code>\n"
                    f"<b>Success:</b> <code>{success}</code>\n"
                    f"<b>Failed:</b> <code>{failed}</code>\n"
                    f"<b>Progress:</b> <code>{percentage:.1f}%</code>"
                )
            except:
                pass
    
    time_taken = asyncio.get_event_loop().time() - start_time
    
    await status_msg.edit_text(f"""
✅ <b>Broadcast Completed!</b>

📊 <b>Statistics:</b>
• <b>Total Users:</b> <code>{total_users}</code>
• <b>Success:</b> <code>{success}</code>
• <b>Failed:</b> <code>{failed}</code>
• <b>Time Taken:</b> <code>{time_taken:.2f}s</code>

<i>Inactive users were removed from database.</i>
""")


@Client.on_message(filters.private & filters.command("ban_user"))
async def ban_user_handler(client: Client, message: Message):
    """Ban a user from using the bot"""
    from config import ADMINS
    if message.from_user.id not in ADMINS:
        return
    
    if len(message.command) < 2:
        await message.reply_text("❌ <b>Usage:</b> <code>/ban_user [User ID] [Reason]</code>", quote=True)
        return
    
    try:
        user_id = int(message.command[1])
    except ValueError:
        return await message.reply_text("❌ Invalid User ID.")
        
    reason = " ".join(message.command[2:]) if len(message.command) > 2 else "No reason provided."
    
    if user_id in ADMINS:
        await message.reply_text("❌ You cannot ban an Admin!", quote=True)
        return
    
    if hasattr(client, "db") and client.db:
        await client.db.ban_user(user_id, reason)
        await message.reply_text(f"✅ <b>User {user_id} has been banned.</b>\nReason: {reason}", quote=True)
        
        try:
            await client.send_message(
                user_id,
                f"🚫 <b>You have been banned from using this bot!</b>\n\n"
                f"<b>Reason:</b> {reason}"
            )
        except:
            pass
    else:
        await message.reply_text("❌ Database not connected!", quote=True)


@Client.on_message(filters.private & filters.command("unban_user"))
async def unban_user_handler(client: Client, message: Message):
    """Unban a user"""
    from config import ADMINS
    if message.from_user.id not in ADMINS:
        return
    
    if len(message.command) < 2:
        await message.reply_text("❌ <b>Usage:</b> <code>/unban_user [User ID]</code>", quote=True)
        return
    
    try:
        user_id = int(message.command[1])
    except ValueError:
        return await message.reply_text("❌ Invalid User ID.")
    
    if hasattr(client, "db") and client.db:
        await client.db.unban_user(user_id)
        await message.reply_text(f"✅ <b>User {user_id} has been unbanned.</b>", quote=True)
        try:
            await client.send_message(user_id, "😇 <b>Congratulations! You have been unbanned.</b>")
        except:
            pass


"""
============================================================================
Stats & System Monitoring
============================================================================
"""

@Client.on_message(filters.private & filters.command("stats"))
async def stats_handler(client: Client, message: Message):
    """View bot statistics"""
    from config import ADMINS
    if message.from_user.id not in ADMINS:
        return
    
    if not hasattr(client, "db") or not client.db:
        await message.reply_text("❌ Database not connected!", quote=True)
        return
    
    total_users = await client.db.total_users_count()
    banned_users = len(await client.db.get_banned_users())
    
    text = f"""
📊 <b>BOT STATISTICS</b>

<b>🤖 Bot Info:</b>
• Name: {client.first_name}
• ID: <code>{client.id}</code>

<b>👥 Users:</b>
• Total: <code>{total_users}</code>
• Banned: <code>{banned_users}</code>
• Active: <code>{total_users - banned_users}</code>

<b>⚙️ System:</b>
• Database: ✅ Connected
"""
    
    buttons = InlineKeyboardMarkup([[
        InlineKeyboardButton("🔄 Refresh", callback_data="stats_refresh"),
        InlineKeyboardButton("🔒 Close", callback_data="close")
    ]])
    
    await message.reply_text(text, reply_markup=buttons, quote=True)

# Web Server for Render Health Checks
async def start_web_server():
    async def handle(request):
        return web.Response(text="Bot is running!")
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    """Main function to run the bot"""
    import config
    
    # Start web server first for Render
    await start_web_server()
    
    bot = Bot()
    await bot.start()
    
    # Configure DB Channel
    if config.CHANNELS and config.CHANNELS[0] != 0:
        try:
            channel = await bot.get_chat(config.CHANNELS[0])
            bot.db_channel = channel
            LOGGER.info(f"✅ DB Channel Set: {channel.title}")
        except Exception as e:
            LOGGER.error(f"❌ Channel Error: {e}")
    
    await idle()
    await bot.stop()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
