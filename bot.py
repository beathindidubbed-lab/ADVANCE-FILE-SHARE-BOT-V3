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

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S'
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
LOGGER = logging.getLogger(__name__)

# Import config at module level
import config

# Global variables from config
ADMINS = config.ADMINS
BOT_PICS = config.BOT_PICS
WELCOME_TEXT = config.WELCOME_TEXT
HELP_TEXT = config.HELP_TEXT
ABOUT_TEXT = config.ABOUT_TEXT
FORCE_SUB_TEXT = config.FORCE_SUB_TEXT
FORCE_SUB_CHANNELS = config.FORCE_SUB_CHANNELS
REQUEST_FSUB = config.REQUEST_FSUB
PROTECT_CONTENT = config.PROTECT_CONTENT
HIDE_CAPTION = config.HIDE_CAPTION
CUSTOM_CAPTION = config.CUSTOM_CAPTION
AUTO_DELETE_TIME = config.AUTO_DELETE_TIME
CHANNEL_BUTTON = config.CHANNEL_BUTTON
CUSTOM_BUTTONS = config.CUSTOM_BUTTONS
SUPPORT_CHAT = config.SUPPORT_CHAT
UPDATES_CHANNEL = config.UPDATES_CHANNEL
CHANNELS = config.CHANNELS



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


def parse_custom_buttons(button_string: str) -> list:
    """Parse custom button string to button list"""
    if not button_string:
        return []
    
    buttons = []
    lines = button_string.strip().split('\n')
    
    for line in lines:
        if ':' in line:
            # Multiple buttons in same row
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
            # Single button
            parts = line.split('|', 1)
            if len(parts) == 2:
                text = parts[0].strip()
                url = parts[1].strip()
                buttons.append([InlineKeyboardButton(text, url=url)])
    
    return buttons

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
# Other options:
# "https://tinyurl.com/api-create.php"
# "https://is.gd/create.php?format=simple"
# "https://v.gd/create.php?format=simple"

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
    """Force subscribe settings - Like screenshot 7"""
    
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
    """Force subscribe settings panel"""
    
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
    """Request force subscribe settings - Like screenshot 8"""
    
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
    """Toggle request force subscribe"""
    
    if query.from_user.id not in ADMINS:
        await query.answer("❌ You're not authorized!", show_alert=True)
        return
    
    action = query.data.split("_")[2]
    new_value = True if action == "on" else False
    
    # Update in database
    if hasattr(client, "db") and client.db:
        await client.db.update_setting("request_fsub", new_value)
    
    # Update config
    config.REQUEST_FSUB = new_value
    
    await query.answer(f"✅ Request FSub {'Enabled' if new_value else 'Disabled'}!")
    
    # Refresh display
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
    """File settings - Like screenshot 9"""
    
    # Get current settings
    if hasattr(client, "db") and client.db:
        protect = await client.db.get_setting("protect_content")
        hide_caption = await client.db.get_setting("hide_caption")
        channel_btn = await client.db.get_setting("channel_button")
    else:
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


@Client.on_callback_query(filters.regex("^file_(protect|caption|channel)_(on|off)$"))
async def file_settings_toggle(client: Client, query: CallbackQuery):
    """Toggle file settings"""
    
    if query.from_user.id not in ADMINS:
        await query.answer("❌ You're not authorized!", show_alert=True)
        return
    
    parts = query.data.split("_")
    setting_type = parts[1]
    action = parts[2]
    
    new_value = True if action == "on" else False
    
    # Map to database keys
    db_keys = {
        "protect": "protect_content",
        "caption": "hide_caption",
        "channel": "channel_button"
    }
    
    # Update in database
    if hasattr(client, "db") and client.db:
        await client.db.update_setting(db_keys[setting_type], new_value)
    
    # Update config
    if setting_type == "protect":
        config.PROTECT_CONTENT = new_value
    elif setting_type == "caption":
        config.HIDE_CAPTION = new_value
    
    await query.answer(f"✅ Setting updated!")
    
    # Refresh display
    protect = await client.db.get_setting("protect_content") if client.db else PROTECT_CONTENT
    hide_caption = await client.db.get_setting("hide_caption") if client.db else HIDE_CAPTION
    channel_btn = await client.db.get_setting("channel_button") if client.db else True
    
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
    
    await query.message.edit_text(text, reply_markup=buttons)


@Client.on_callback_query(filters.regex("^files_refresh$"))
async def files_refresh(client: Client, query: CallbackQuery):
    """Refresh file settings"""
    await query.answer("♻️ Refreshing...")
    await file_settings_toggle(client, query)


# ========== AUTO DELETE SETTINGS (/auto_del command) ==========

@Client.on_message(filters.private & filters.user(ADMINS) & filters.command("auto_del"))
async def auto_del_command(client: Client, message: Message):
    """Auto delete settings - Like screenshot 10"""
    
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

🔔 <b>AUTO DELETE MODE:</b> {'ENABLED' if auto_del_enabled else 'ENABLED'} {status_icon}
⏱️ <b>DELETE TIMER:</b> {minutes} MINUTES

<b>CLICK BELOW BUTTONS TO CHANGE SETTINGS</b>
"""
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("DISABLE MODE ❌", callback_data="auto_del_disable")
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


@Client.on_callback_query(filters.regex("^auto_del_"))
async def auto_del_callbacks(client: Client, query: CallbackQuery):
    """Handle auto delete callbacks"""
    
    if query.from_user.id not in ADMINS:
        await query.answer("❌ You're not authorized!", show_alert=True)
        return
    
    action = query.data.replace("auto_del_", "")
    
    if action == "disable":
        if hasattr(client, "db") and client.db:
            await client.db.update_setting("auto_delete", False)
            await client.db.update_setting("auto_delete_time", 0)
        config.AUTO_DELETE_TIME = 0
        await query.answer("✅ Auto-delete disabled!")
    
    elif action == "refresh":
        await query.answer("♻️ Refreshing...")
    
    # Refresh display
    if hasattr(client, "db") and client.db:
        auto_del_enabled = await client.db.get_setting("auto_delete")
        del_time = await client.db.get_setting("auto_delete_time") or 0
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
            InlineKeyboardButton("DISABLE MODE ❌", callback_data="auto_del_disable")
        ],
        [
            InlineKeyboardButton("◈ SET TIMER ⏱️", callback_data="auto_del_set_timer")
        ],
        [
            InlineKeyboardButton("🔄 REFRESH", callback_data="auto_del_refresh"),
            InlineKeyboardButton("🔒 CLOSE", callback_data="close")
        ]
    ])
    
    await query.message.edit_text(text, reply_markup=buttons)


# ========== BACK TO SETTINGS ==========

@Client.on_callback_query(filters.regex("^file_set_button$"))
async def file_set_button(client: Client, query: CallbackQuery):
    """Set custom button"""
    
    if query.from_user.id not in ADMINS:
        await query.answer("❌ You're not authorized!", show_alert=True)
        return
    
    await query.answer()
    
    # Send instructions
    text = """
🔘 <b>CUSTOM BUTTON SETUP</b>

Send me your button in this format:

<code>Button Text | URL</code>

<b>Examples:</b>

Single button:
<code>Join Channel | https://t.me/yourchannel</code>

Multiple buttons (one per line):
<code>Join Channel | https://t.me/channel1
Support Group | https://t.me/group1</code>

Two buttons in same row:
<code>Channel | https://t.me/ch : Support | https://t.me/gr</code>

<b>💡 Tips:</b>
• Use <code>|</code> to separate text and URL
• Use <code>:</code> to put buttons in same row
• Use new line for new row

Send <code>cancel</code> to cancel.
"""
    
    await query.message.edit_text(text)
    
    # Wait for user input
    try:
        response = await client.listen(query.message.chat.id, timeout=300)
        
        if response.text and response.text.lower() == 'cancel':
            await response.reply_text("❌ Cancelled!")
            return
        
        # Save button config
        button_text = response.text
        
        # Update in database
        if hasattr(client, "db") and client.db:
            await client.db.update_setting("custom_button", button_text)
        
        # Update config
        import config
        config.CUSTOM_BUTTONS = button_text
        
        await response.reply_text(
            f"✅ <b>Custom Button Set!</b>\n\n"
            f"<b>Button Config:</b>\n<code>{button_text}</code>\n\n"
            f"This button will appear with all files!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back to Settings", callback_data="files_refresh")]
            ])
        )
    
    except:
        await query.message.reply_text("❌ <b>Timeout!</b> No response received.")


@Client.on_callback_query(filters.regex("^setting_"))
async def settings_callbacks(client: Client, query: CallbackQuery):
    """Handle main settings navigation"""
    
    if query.from_user.id not in ADMINS:
        await query.answer("❌ You're not authorized!", show_alert=True)
        return
    
    setting_type = query.data.replace("setting_", "")
    
    if setting_type == "protection":
        await query.answer("Use /files command for file settings")
    elif setting_type == "files":
        await query.answer("Use /files command")
    elif setting_type == "auto_delete":
        await query.answer("Use /auto_del command")
    elif setting_type == "force_sub":
        await query.answer("Use /forcesub command")
    elif setting_type == "req_fsub":
        await query.answer("Use /req_fsub command")


"""
============================================================================
Set Channel Command - Configure channel from inside the bot!
Supports: Channels, Groups, Supergroups, Usernames!
No need to restart!
============================================================================
"""

@Client.on_message(filters.private & filters.user(ADMINS) & filters.command("setchannel"))
async def set_channel_command(client: Client, message: Message):
    """Set database channel/group from inside bot"""
    
    await message.reply_text(
        "📁 <b>SET DATABASE CHANNEL/GROUP</b>\n\n"
        "<b>3 WAYS TO SET:</b>\n\n"
        "<b>Method 1:</b> Forward message from channel/group\n"
        "<b>Method 2:</b> Send channel/group username (e.g., @channelname)\n"
        "<b>Method 3:</b> Send channel/group ID (e.g., -1001234567890)\n\n"
        "<b>Note:</b> Bot must be admin in channel/group!\n\n"
        "⏱️ <b>Waiting for your input...</b>",
        quote=True
    )
    
    # Listen for message
    try:
        user_msg = await client.listen(message.chat.id, timeout=60)
    except:
        await message.reply_text("❌ <b>Timeout!</b> No message received.", quote=True)
        return
    
    channel_id = None
    channel_username = None
    
    # Check if forwarded message
    if user_msg.forward_from_chat:
        channel_id = user_msg.forward_from_chat.id
        channel_username = user_msg.forward_from_chat.username
    
    # Check if username sent
    elif user_msg.text:
        text = user_msg.text.strip()
        
        # Username format: @channelname or channelname
        if text.startswith('@'):
            channel_username = text[1:]
        elif text.startswith('-'):
            # Channel ID format: -1001234567890
            try:
                channel_id = int(text)
            except:
                await message.reply_text(
                    "❌ <b>Invalid ID!</b>\n\n"
                    "ID must be a number like: -1001234567890",
                    quote=True
                )
                return
        else:
            # Try as username without @
            channel_username = text
    else:
        await message.reply_text(
            "❌ <b>Invalid Input!</b>\n\n"
            "Please send:\n"
            "• Forward from channel/group\n"
            "• Channel username (@channelname)\n"
            "• Channel ID (-1001234567890)",
            quote=True
        )
        return
    
    # Try to access channel/group
    try:
        # Get chat by ID or username
        if channel_id:
            channel = await client.get_chat(channel_id)
        elif channel_username:
            channel = await client.get_chat(channel_username)
        else:
            raise ValueError("No ID or username provided")
        
        channel_id = channel.id
        channel_title = channel.title
        channel_type = str(channel.type).split('.')[-1].title()
        
        # Check if bot is admin
        try:
            member = await client.get_chat_member(channel_id, client.id)
            if member.status not in ["administrator", "creator"]:
                await message.reply_text(
                    f"⚠️ <b>Warning!</b>\n\n"
                    f"Bot is not admin in <b>{channel_title}</b>\n\n"
                    f"Make bot admin first for full functionality!",
                    quote=True
                )
        except:
            pass
        
        # Set as database channel
        client.db_channel = channel
        client.db_channel_id = channel_id
        
        # Update config
        config.CHANNELS = [channel_id]
        
        # Try to save to database
        if hasattr(client, "db") and client.db:
            try:
                await client.db.settings.update_one(
                    {"_id": "bot_settings"},
                    {"$set": {"db_channel_id": channel_id}},
                    upsert=True
                )
            except:
                pass
        
        username_text = f"@{channel.username}" if channel.username else "Private"
        
        await message.reply_text(
            f"✅ <b>{channel_type} Set Successfully!</b>\n\n"
            f"<b>📺 Name:</b> {channel_title}\n"
            f"<b>🆔 ID:</b> <code>{channel_id}</code>\n"
            f"<b>👥 Type:</b> {channel_type}\n"
            f"<b>🔗 Username:</b> {username_text}\n\n"
            f"<b>✅ Bot is now ready to share files!</b>\n\n"
            f"💡 Forward files to me and I'll generate shareable links!",
            quote=True
        )
    
    except Exception as e:
        error_msg = str(e)
        
        # Provide helpful error messages
        if "USERNAME_INVALID" in error_msg or "Username not found" in error_msg:
            await message.reply_text(
                f"❌ <b>Username Not Found!</b>\n\n"
                f"The username <code>{channel_username if channel_username else 'unknown'}</code> doesn't exist.\n\n"
                f"<b>Check:</b>\n"
                f"• Username is correct\n"
                f"• Channel/group is public\n"
                f"• No typos in username",
                quote=True
            )
        elif "CHAT_ADMIN_REQUIRED" in error_msg:
            await message.reply_text(
                f"❌ <b>Admin Rights Required!</b>\n\n"
                f"Bot must be admin in the channel/group.\n\n"
                f"<b>Steps:</b>\n"
                f"1. Go to channel/group settings\n"
                f"2. Add bot as administrator\n"
                f"3. Try again",
                quote=True
            )
        else:
            await message.reply_text(
                f"❌ <b>Error!</b>\n\n"
                f"<code>{error_msg}</code>\n\n"
                f"<b>Make sure:</b>\n"
                f"• Bot is ADMIN in channel/group\n"
                f"• Username/ID is correct\n"
                f"• Channel/group exists",
                quote=True
            )


@Client.on_message(filters.private & filters.user(ADMINS) & filters.command("checkchannel"))
async def check_channel_command(client: Client, message: Message):
    """Check current channel/group status"""
    
    if not hasattr(client, "db_channel") or not client.db_channel:
        await message.reply_text(
            "⚠️ <b>No Channel/Group Configured</b>\n\n"
            "Use /setchannel to configure:\n"
            "• Forward message from channel/group\n"
            "• Send @username\n"
            "• Send channel/group ID",
            quote=True
        )
        return
    
    channel = client.db_channel
    channel_type = str(channel.type).split('.')[-1].title()
    username_text = f"@{channel.username}" if channel.username else "Private"
    
    # Check admin status
    admin_status = "❓ Unknown"
    try:
        member = await client.get_chat_member(channel.id, client.id)
        if member.status == "creator":
            admin_status = "✅ Owner"
        elif member.status == "administrator":
            admin_status = "✅ Admin"
        else:
            admin_status = "❌ Not Admin"
    except:
        admin_status = "❌ Cannot Check"
    
    await message.reply_text(
        f"✅ <b>{channel_type} Status</b>\n\n"
        f"<b>📺 Name:</b> {channel.title}\n"
        f"<b>🆔 ID:</b> <code>{channel.id}</code>\n"
        f"<b>👥 Type:</b> {channel_type}\n"
        f"<b>🔗 Username:</b> {username_text}\n"
        f"<b>🔒 Bot Status:</b> {admin_status}\n\n"
        f"<b>{'✅ Channel is active and working!' if 'Admin' in admin_status or 'Owner' in admin_status else '⚠️ Make bot admin for full access!'}</b>",
        quote=True
    )


@Client.on_message(filters.private & filters.user(ADMINS) & filters.command("removechannel"))
async def remove_channel_command(client: Client, message: Message):
    """Remove configured channel/group"""
    
    if not hasattr(client, "db_channel") or not client.db_channel:
        await message.reply_text(
            "⚠️ <b>No Channel/Group Configured</b>\n\n"
            "Nothing to remove!",
            quote=True
        )
        return
    
    channel_name = client.db_channel.title
    
    # Remove channel
    client.db_channel = None
    client.db_channel_id = None
    config.CHANNELS = [0]
    
    # Remove from database
    if hasattr(client, "db") and client.db:
        try:
            await client.db.settings.update_one(
                {"_id": "bot_settings"},
                {"$set": {"db_channel_id": None}},
                upsert=True
            )
        except:
            pass
    
    await message.reply_text(
        f"✅ <b>Channel/Group Removed!</b>\n\n"
        f"<b>Removed:</b> {channel_name}\n\n"
        f"Use /setchannel to configure a new one.",
        quote=True
    )


"""
============================================================================
Genlink Command - Generate Single File Link
Store a single message/file (moderators only)
============================================================================
"""

@Client.on_message(filters.private & filters.user(ADMINS) & filters.command("genlink"))
async def genlink_command(client: Client, message: Message):
    """Generate link for single file"""
    
    if not hasattr(client, "db_channel"):
        await message.reply_text(
            "❌ <b>Database Channel Not Configured!</b>",
            quote=True
        )
        return
    
    await message.reply_text(
        "🔗 <b>GENERATE LINK</b>\n\n"
        "<b>Instructions:</b>\n"
        "Forward a message from your database channel to get a shareable link.\n\n"
        "⏱️ <b>Waiting for message...</b>",
        quote=True
    )
    
    # Listen for forwarded message
    try:
        forward_msg = await client.listen(message.chat.id, timeout=60, filters=filters.forwarded)
    except:
        await message.reply_text("❌ <b>Timeout!</b> No message received.", quote=True)
        return
    
    # Check if from database channel
    if not forward_msg.forward_from_chat or forward_msg.forward_from_chat.id != client.db_channel.id:
        await message.reply_text(
            "❌ <b>Invalid Message!</b>\n\n"
            "Please forward message from database channel.",
            quote=True
        )
        return
    
    # Generate link
    try:
        msg_id = forward_msg.forward_from_message_id
        channel_id = abs(client.db_channel.id)
        converted_id = msg_id * channel_id
        
        link_string = f"get-{converted_id}"
        encoded = await encode(link_string)
        link = f"https://t.me/{client.username}?start={encoded}"
        
        # Get file info
        if forward_msg.document:
            file_name = forward_msg.document.file_name
            file_size = forward_msg.document.file_size / (1024 * 1024)  # MB
        elif forward_msg.video:
            file_name = forward_msg.video.file_name or "video.mp4"
            file_size = forward_msg.video.file_size / (1024 * 1024)
        elif forward_msg.audio:
            file_name = forward_msg.audio.file_name or "audio.mp3"
            file_size = forward_msg.audio.file_size / (1024 * 1024)
        else:
            file_name = "file"
            file_size = 0
        
        # Create reply
        reply_text = f"""
✅ <b>Link Generated!</b>

<b>📁 File:</b> <code>{file_name}</code>
<b>📊 Size:</b> <code>{file_size:.2f} MB</code>
<b>💾 Message ID:</b> <code>{msg_id}</code>

<b>🔗 Shareable Link:</b>
<code>{link}</code>

<b>💡 Share this link with users!</b>
"""
        
        # Add copy button
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
            f"❌ <b>Error Generating Link!</b>\n\n<code>{str(e)}</code>",
            quote=True
        )


"""
============================================================================
EMERGENCY DEBUG - Catches ALL messages and shows what's happening
============================================================================
"""

@Client.on_message(filters.private)
async def debug_all_messages(client: Client, message: Message):
    """Catches EVERY private message - for debugging"""
    
    # Log to console
    print(f"=" * 50)
    print(f"📨 RECEIVED MESSAGE!")
    print(f"From: {message.from_user.first_name} ({message.from_user.id})")
    print(f"Text: {message.text}")
    print(f"Chat ID: {message.chat.id}")
    print(f"=" * 50)
    
    # Reply to user
    await message.reply_text(
        f"🔍 <b>DEBUG INFO</b>\n\n"
        f"✅ Bot received your message!\n\n"
        f"<b>Your Message:</b> {message.text}\n"
        f"<b>Your ID:</b> <code>{message.from_user.id}</code>\n"
        f"<b>Your Name:</b> {message.from_user.first_name}\n\n"
        f"<b>If you see this, bot IS working!</b>",
        quote=True
    )

"""
============================================================================
Custom Batch Command - Store Multiple Random Messages
For non-sequential messages (moderators only)
============================================================================
"""

@Client.on_message(filters.private & filters.user(ADMINS) & filters.command("custom_batch"))
async def custom_batch_command(client: Client, message: Message):
    """Generate custom batch link for random messages"""
    
    if not hasattr(client, "db_channel"):
        await message.reply_text(
            "❌ <b>Database Channel Not Configured!</b>",
            quote=True
        )
        return
    
    await message.reply_text(
        "📦 <b>CUSTOM BATCH GENERATOR</b>\n\n"
        "<b>Instructions:</b>\n"
        "Forward multiple messages from your channel (can be random, not sequential)\n\n"
        "Send /done when finished\n"
        "Send /cancel to cancel\n\n"
        "⏱️ <b>Waiting for messages...</b>",
        quote=True
    )
    
    message_ids = []
    
    while True:
        try:
            # Listen for message
            user_msg = await client.listen(message.chat.id, timeout=300)
            
            # Check for done/cancel
            if user_msg.text:
                if user_msg.text.lower() == '/done':
                    break
                elif user_msg.text.lower() == '/cancel':
                    await user_msg.reply_text("❌ <b>Cancelled!</b>", quote=True)
                    return
            
            # Check if forwarded from database channel
            if user_msg.forward_from_chat and user_msg.forward_from_chat.id == client.db_channel.id:
                msg_id = user_msg.forward_from_message_id
                message_ids.append(msg_id)
                await user_msg.reply_text(
                    f"✅ <b>Added!</b> Total: {len(message_ids)}\n\n"
                    f"Send more or /done to finish",
                    quote=True
                )
            else:
                await user_msg.reply_text(
                    "❌ Please forward from database channel!",
                    quote=True
                )
        
        except:
            await message.reply_text("❌ <b>Timeout!</b> Use /custom_batch to try again.")
            return
    
    # Generate batch link
    if not message_ids:
        await message.reply_text("❌ <b>No messages added!</b>", quote=True)
        return
    
    try:
        channel_id = abs(client.db_channel.id)
        
        # Convert all IDs
        converted_ids = [str(msg_id * channel_id) for msg_id in message_ids]
        
        # Create link string: custombatch-id1-id2-id3...
        link_string = f"custombatch-{'-'.join(converted_ids)}"
        encoded = await encode(link_string)
        link = f"https://t.me/{client.username}?start={encoded}"
        
        # Create reply
        reply_text = f"""
✅ <b>Custom Batch Link Generated!</b>

<b>📊 Total Files:</b> <code>{len(message_ids)}</code>
<b>📦 Message IDs:</b> <code>{', '.join(map(str, message_ids))}</code>

<b>🔗 Custom Batch Link:</b>
<code>{link}</code>

<b>💡 This link will send all {len(message_ids)} files in the order you added them!</b>
"""
        
        # Add button
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
            f"❌ <b>Error Generating Link!</b>\n\n<code>{str(e)}</code>",
            quote=True
        )

"""
============================================================================
Channel Post Handler - Generate Shareable Links
When admin forwards files to bot
============================================================================
"""

@Client.on_message(filters.private & filters.user(ADMINS) & (filters.document | filters.video | filters.audio))
async def forward_to_channel(client: Client, message: Message):
    """Forward files to channel and generate link"""
    
    if not hasattr(client, "db_channel"):
        await message.reply_text(
            "❌ <b>Database Channel Not Configured!</b>\n\n"
            "Please set up database channel first.",
            quote=True
        )
        return
    
    # Forward to channel
    try:
        forwarded = await message.forward(client.db_channel.id)
        
        # Generate link
        converted_id = forwarded.id * abs(client.db_channel.id)
        link_string = f"get-{converted_id}"
        encoded = await encode(link_string)
        link = f"https://t.me/{client.username}?start={encoded}"
        
        # Get file info
        if message.document:
            file_name = message.document.file_name
            file_size = message.document.file_size
        elif message.video:
            file_name = message.video.file_name or "video.mp4"
            file_size = message.video.file_size
        elif message.audio:
            file_name = message.audio.file_name or "audio.mp3"
            file_size = message.audio.file_size
        else:
            file_name = "file"
            file_size = 0
        
        # Format size
        size = file_size / (1024 * 1024)  # Convert to MB
        
        # Create reply
        reply_text = f"""
✅ <b>File Uploaded Successfully!</b>

<b>📁 File Name:</b> <code>{file_name}</code>
<b>📊 Size:</b> <code>{size:.2f} MB</code>
<b>💾 Message ID:</b> <code>{forwarded.id}</code>

<b>🔗 Shareable Link:</b>
<code>{link}</code>

<b>💡 Tip:</b> Share this link with users!
"""
        
        # Add copy button
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
            f"❌ <b>Error Uploading File!</b>\n\n<code>{str(e)}</code>",
            quote=True
        )


@Client.on_message(filters.channel & filters.forwarded & (filters.document | filters.video | filters.audio))
async def auto_generate_link(client: Client, message: Message):
    """Auto-generate link for forwarded messages in channel"""
    
    # Check if this is the database channel
    if message.chat.id not in CHANNELS:
        return
    
    # Generate link
    try:
        converted_id = message.id * abs(message.chat.id)
        link_string = f"get-{converted_id}"
        encoded = await encode(link_string)
        link = f"https://t.me/{client.username}?start={encoded}"
        
        # Get file info
        if message.document:
            file_name = message.document.file_name
        elif message.video:
            file_name = message.video.file_name or "video.mp4"
        elif message.audio:
            file_name = message.audio.file_name or "audio.mp3"
        else:
            file_name = "file"
        
        # Reply with link
        await message.reply_text(
            f"🔗 <b>Link:</b> <code>{link}</code>\n\n"
            f"📁 <b>File:</b> <code>{file_name}</code>",
            quote=True,
            disable_web_page_preview=True
        )
    
    except Exception as e:
        print(f"Error generating link: {e}")

"""
============================================================================
Callback Query Handlers - Button Interactions
============================================================================
"""

@Client.on_callback_query(filters.regex("^help$"))
async def help_callback(client: Client, query: CallbackQuery):
    """Show help menu"""
    
    # Format help text
    help_text = HELP_TEXT.format(
        bot_name=client.first_name,
        username=client.username
    )
    
    # Create buttons
    buttons = []
    
    if SUPPORT_CHAT:
        buttons.append([
            InlineKeyboardButton("💬 Support Chat Group", url=f"https://t.me/{SUPPORT_CHAT.replace('@', '')}")
        ])
    
    if UPDATES_CHANNEL:
        buttons.append([
            InlineKeyboardButton("📢 Updates Channel", url=f"https://t.me/{UPDATES_CHANNEL.replace('@', '')}")
        ])
    
    buttons.append([
        InlineKeyboardButton("🏠 Home", callback_data="start"),
        InlineKeyboardButton("🔒 Close", callback_data="close")
    ])
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    try:
        await query.message.edit_text(
            text=help_text,
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
    except:
        await query.answer("❌ Error loading help menu!", show_alert=True)


@Client.on_callback_query(filters.regex("^about$"))
async def about_callback(client: Client, query: CallbackQuery):
    """Show about menu"""
    
    # Format about text
    about_text = ABOUT_TEXT.format(
        bot_name=client.first_name,
        username=client.username
    )
    
    # Create buttons
    buttons = []
    
    if SUPPORT_CHAT:
        buttons.append([
            InlineKeyboardButton("💬 Support", url=f"https://t.me/{SUPPORT_CHAT.replace('@', '')}")
        ])
    
    if UPDATES_CHANNEL:
        buttons.append([
            InlineKeyboardButton("📢 Updates", url=f"https://t.me/{UPDATES_CHANNEL.replace('@', '')}")
        ])
    
    buttons.append([
        InlineKeyboardButton("🏠 Home", callback_data="start"),
        InlineKeyboardButton("🔒 Close", callback_data="close")
    ])
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    try:
        await query.message.edit_text(
            text=about_text,
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
    except:
        await query.answer("❌ Error loading about menu!", show_alert=True)


@Client.on_callback_query(filters.regex("^start$"))
async def start_callback(client: Client, query: CallbackQuery):
    """Go back to start menu"""
    
    # Format welcome text
    welcome_text = WELCOME_TEXT.format(
        first=query.from_user.first_name,
        last=query.from_user.last_name or "",
        username=f"@{query.from_user.username}" if query.from_user.username else "None",
        mention=query.from_user.mention,
        id=query.from_user.id
    )
    
    # Create buttons
    buttons = [
        [
            InlineKeyboardButton("📚 Help", callback_data="help"),
            InlineKeyboardButton("ℹ️ About", callback_data="about")
        ]
    ]
    
    if UPDATES_CHANNEL:
        buttons.append([
            InlineKeyboardButton("📢 Updates", url=f"https://t.me/{UPDATES_CHANNEL.replace('@', '')}")
        ])
    
    if SUPPORT_CHAT:
        buttons.append([
            InlineKeyboardButton("💬 Support", url=f"https://t.me/{SUPPORT_CHAT.replace('@', '')}")
        ])
    
    buttons.append([
        InlineKeyboardButton("🔒 Close", callback_data="close")
    ])
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    try:
        await query.message.edit_text(
            text=welcome_text,
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
    except:
        await query.answer("❌ Error!", show_alert=True)


@Client.on_callback_query(filters.regex("^close$"))
async def close_callback(client: Client, query: CallbackQuery):
    """Close the message"""
    
    try:
        await query.message.delete()
    except:
        await query.answer("❌ Cannot delete this message!", show_alert=True)

"""
============================================================================
Bot Settings - Configure everything from inside bot!
Change welcome message, images, buttons, etc.
============================================================================
"""

@Client.on_message(filters.private & filters.user(ADMINS) & filters.command("botsettings"))
async def bot_settings_menu(client: Client, message: Message):
    """Main bot settings menu"""
    
    text = """
⚙️ <b>BOT SETTINGS</b>

<b>Configure your bot appearance and behavior:</b>

📸 <b>Welcome Images</b> - Set bot pics
💬 <b>Welcome Message</b> - Customize start message
📚 <b>Help Message</b> - Edit help text
ℹ️ <b>About Message</b> - Edit about text
🔘 <b>Custom Buttons</b> - Add channel/support buttons

<i>Click a button below to configure</i>
"""
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📸 Images", callback_data="settings_images"),
            InlineKeyboardButton("💬 Welcome", callback_data="settings_welcome")
        ],
        [
            InlineKeyboardButton("📚 Help", callback_data="settings_help"),
            InlineKeyboardButton("ℹ️ About", callback_data="settings_about")
        ],
        [
            InlineKeyboardButton("🔘 Buttons", callback_data="settings_buttons")
        ],
        [
            InlineKeyboardButton("👀 Preview", callback_data="settings_preview"),
            InlineKeyboardButton("🔒 Close", callback_data="close")
        ]
    ])
    
    await message.reply_text(text, reply_markup=buttons, quote=True)


# ========== IMAGES SETTINGS ==========

@Client.on_callback_query(filters.regex("^settings_images$"))
async def settings_images_callback(client: Client, query: CallbackQuery):
    """Configure bot images"""
    
    if query.from_user.id not in ADMINS:
        await query.answer("❌ Admin only!", show_alert=True)
        return
    
    current_pics = config.BOT_PICS
    pics_text = "\n".join([f"• {pic}" for pic in current_pics]) if current_pics else "No images set"
    
    text = f"""
📸 <b>WELCOME IMAGES</b>

<b>Current Images:</b>
{pics_text}

<b>To change:</b>
Reply with image URLs (one per line)

<b>Example:</b>
<code>https://telegra.ph/file/image1.jpg
https://telegra.ph/file/image2.jpg</code>

<i>Bot will randomly show one of these images</i>
"""
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Change Images", callback_data="edit_images")],
        [InlineKeyboardButton("🔙 Back", callback_data="botsettings_back")]
    ])
    
    await query.message.edit_text(text, reply_markup=buttons)


@Client.on_callback_query(filters.regex("^edit_images$"))
async def edit_images_callback(client: Client, query: CallbackQuery):
    """Start editing images"""
    
    if query.from_user.id not in ADMINS:
        await query.answer("❌ Admin only!", show_alert=True)
        return
    
    await query.answer()
    await query.message.edit_text(
        "📸 <b>Send Image URLs</b>\n\n"
        "Send image URLs (one per line)\n"
        "Or send <code>cancel</code> to cancel\n\n"
        "<b>Example:</b>\n"
        "<code>https://telegra.ph/file/pic1.jpg\n"
        "https://telegra.ph/file/pic2.jpg</code>"
    )
    
    # Listen for response
    try:
        response = await client.listen(query.message.chat.id, timeout=300)
        
        if response.text and response.text.lower() == 'cancel':
            await response.reply_text("❌ Cancelled!", quote=True)
            return
        
        if not response.text:
            await response.reply_text("❌ Please send text with URLs!", quote=True)
            return
        
        # Parse URLs
        urls = [url.strip() for url in response.text.split('\n') if url.strip()]
        
        if not urls:
            await response.reply_text("❌ No valid URLs found!", quote=True)
            return
        
        # Update config
        config.BOT_PICS = urls
        
        # Save to database
        if hasattr(client, "db") and client.db:
            try:
                await client.db.settings.update_one(
                    {"_id": "bot_settings"},
                    {"$set": {"bot_pics": urls}},
                    upsert=True
                )
            except:
                pass
        
        await response.reply_text(
            f"✅ <b>Images Updated!</b>\n\n"
            f"<b>Total Images:</b> {len(urls)}\n\n"
            f"Use /botsettings to configure more!",
            quote=True
        )
    
    except:
        await query.message.reply_text("❌ Timeout! Try again.")


# ========== WELCOME MESSAGE ==========

@Client.on_callback_query(filters.regex("^settings_welcome$"))
async def settings_welcome_callback(client: Client, query: CallbackQuery):
    """Configure welcome message"""
    
    if query.from_user.id not in ADMINS:
        await query.answer("❌ Admin only!", show_alert=True)
        return
    
    current_welcome = config.WELCOME_TEXT
    
    text = f"""
💬 <b>WELCOME MESSAGE</b>

<b>Current Message:</b>
{current_welcome[:500]}...

<b>Available Variables:</b>
<code>{{first}}</code> - User first name
<code>{{last}}</code> - User last name
<code>{{username}}</code> - Username
<code>{{mention}}</code> - Mention user
<code>{{id}}</code> - User ID

<b>Formatting:</b>
<code>&lt;b&gt;bold&lt;/b&gt;</code>
<code>&lt;i&gt;italic&lt;/i&gt;</code>
<code>&lt;code&gt;code&lt;/code&gt;</code>
"""
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Change Message", callback_data="edit_welcome")],
        [InlineKeyboardButton("🔙 Back", callback_data="botsettings_back")]
    ])
    
    await query.message.edit_text(text, reply_markup=buttons)


@Client.on_callback_query(filters.regex("^edit_welcome$"))
async def edit_welcome_callback(client: Client, query: CallbackQuery):
    """Start editing welcome message"""
    
    if query.from_user.id not in ADMINS:
        await query.answer("❌ Admin only!", show_alert=True)
        return
    
    await query.answer()
    await query.message.edit_text(
        "💬 <b>Send New Welcome Message</b>\n\n"
        "Send your new welcome text\n"
        "Or send <code>cancel</code> to cancel\n\n"
        "<b>You can use:</b>\n"
        "<code>{first}</code> - First name\n"
        "<code>{mention}</code> - Mention\n"
        "<code>{id}</code> - User ID"
    )
    
    # Listen for response
    try:
        response = await client.listen(query.message.chat.id, timeout=300)
        
        if response.text and response.text.lower() == 'cancel':
            await response.reply_text("❌ Cancelled!", quote=True)
            return
        
        if not response.text:
            await response.reply_text("❌ Please send text!", quote=True)
            return
        
        new_text = response.text
        
        # Update config
        config.WELCOME_TEXT = new_text
        
        # Save to database
        if hasattr(client, "db") and client.db:
            try:
                await client.db.settings.update_one(
                    {"_id": "bot_settings"},
                    {"$set": {"welcome_text": new_text}},
                    upsert=True
                )
            except:
                pass
        
        await response.reply_text(
            f"✅ <b>Welcome Message Updated!</b>\n\n"
            f"Preview:\n{new_text[:200]}...\n\n"
            f"Use /botsettings to configure more!",
            quote=True
        )
    
    except:
        await query.message.reply_text("❌ Timeout! Try again.")


# ========== HELP MESSAGE ==========

@Client.on_callback_query(filters.regex("^settings_help$"))
async def settings_help_callback(client: Client, query: CallbackQuery):
    """Configure help message"""
    
    if query.from_user.id not in ADMINS:
        await query.answer("❌ Admin only!", show_alert=True)
        return
    
    current_help = config.HELP_TEXT
    
    text = f"""
📚 <b>HELP MESSAGE</b>

<b>Current Message:</b>
{current_help[:300]}...

<b>This message shows when users click Help button</b>
"""
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Change Message", callback_data="edit_help")],
        [InlineKeyboardButton("🔙 Back", callback_data="botsettings_back")]
    ])
    
    await query.message.edit_text(text, reply_markup=buttons)


@Client.on_callback_query(filters.regex("^edit_help$"))
async def edit_help_callback(client: Client, query: CallbackQuery):
    """Start editing help message"""
    
    if query.from_user.id not in ADMINS:
        await query.answer("❌ Admin only!", show_alert=True)
        return
    
    await query.answer()
    await query.message.edit_text(
        "📚 <b>Send New Help Message</b>\n\n"
        "Send your help text or <code>cancel</code>"
    )
    
    try:
        response = await client.listen(query.message.chat.id, timeout=300)
        
        if response.text and response.text.lower() == 'cancel':
            await response.reply_text("❌ Cancelled!", quote=True)
            return
        
        if not response.text:
            await response.reply_text("❌ Please send text!", quote=True)
            return
        
        new_text = response.text
        config.HELP_TEXT = new_text
        
        if hasattr(client, "db") and client.db:
            try:
                await client.db.settings.update_one(
                    {"_id": "bot_settings"},
                    {"$set": {"help_text": new_text}},
                    upsert=True
                )
            except:
                pass
        
        await response.reply_text(
            f"✅ <b>Help Message Updated!</b>",
            quote=True
        )
    
    except:
        await query.message.reply_text("❌ Timeout!")


# ========== ABOUT MESSAGE ==========

@Client.on_callback_query(filters.regex("^settings_about$"))
async def settings_about_callback(client: Client, query: CallbackQuery):
    """Configure about message"""
    
    if query.from_user.id not in ADMINS:
        await query.answer("❌ Admin only!", show_alert=True)
        return
    
    current_about = config.ABOUT_TEXT
    
    text = f"""
ℹ️ <b>ABOUT MESSAGE</b>

<b>Current Message:</b>
{current_about[:300]}...

<b>Variables:</b>
<code>{{bot_name}}</code> - Bot name
<code>{{username}}</code> - Bot username
"""
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Change Message", callback_data="edit_about")],
        [InlineKeyboardButton("🔙 Back", callback_data="botsettings_back")]
    ])
    
    await query.message.edit_text(text, reply_markup=buttons)


@Client.on_callback_query(filters.regex("^edit_about$"))
async def edit_about_callback(client: Client, query: CallbackQuery):
    """Start editing about message"""
    
    if query.from_user.id not in ADMINS:
        await query.answer("❌ Admin only!", show_alert=True)
        return
    
    await query.answer()
    await query.message.edit_text(
        "ℹ️ <b>Send New About Message</b>\n\n"
        "Send your about text or <code>cancel</code>"
    )
    
    try:
        response = await client.listen(query.message.chat.id, timeout=300)
        
        if response.text and response.text.lower() == 'cancel':
            await response.reply_text("❌ Cancelled!", quote=True)
            return
        
        if not response.text:
            await response.reply_text("❌ Please send text!", quote=True)
            return
        
        new_text = response.text
        config.ABOUT_TEXT = new_text
        
        if hasattr(client, "db") and client.db:
            try:
                await client.db.settings.update_one(
                    {"_id": "bot_settings"},
                    {"$set": {"about_text": new_text}},
                    upsert=True
                )
            except:
                pass
        
        await response.reply_text(
            f"✅ <b>About Message Updated!</b>",
            quote=True
        )
    
    except:
        await query.message.reply_text("❌ Timeout!")


# ========== CUSTOM BUTTONS ==========

@Client.on_callback_query(filters.regex("^settings_buttons$"))
async def settings_buttons_callback(client: Client, query: CallbackQuery):
    """Configure custom buttons"""
    
    if query.from_user.id not in ADMINS:
        await query.answer("❌ Admin only!", show_alert=True)
        return
    
    text = """
🔘 <b>CUSTOM BUTTONS</b>

<b>Add buttons to start message:</b>

<b>Format:</b>
<code>Text | URL</code>

<b>Examples:</b>

Single button:
<code>📢 Channel | https://t.me/yourchannel</code>

Multiple buttons (one per line):
<code>📢 Channel | https://t.me/channel
💬 Support | https://t.me/support</code>

Two in same row (use : separator):
<code>Channel | t.me/ch : Support | t.me/sup</code>
"""
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Set Buttons", callback_data="edit_buttons")],
        [InlineKeyboardButton("❌ Clear Buttons", callback_data="clear_buttons")],
        [InlineKeyboardButton("🔙 Back", callback_data="botsettings_back")]
    ])
    
    await query.message.edit_text(text, reply_markup=buttons)


@Client.on_callback_query(filters.regex("^edit_buttons$"))
async def edit_buttons_callback(client: Client, query: CallbackQuery):
    """Start editing buttons"""
    
    if query.from_user.id not in ADMINS:
        await query.answer("❌ Admin only!", show_alert=True)
        return
    
    await query.answer()
    await query.message.edit_text(
        "🔘 <b>Send Button Configuration</b>\n\n"
        "<b>Format:</b> <code>Text | URL</code>\n\n"
        "Send <code>cancel</code> to cancel"
    )
    
    try:
        response = await client.listen(query.message.chat.id, timeout=300)
        
        if response.text and response.text.lower() == 'cancel':
            await response.reply_text("❌ Cancelled!", quote=True)
            return
        
        if not response.text:
            await response.reply_text("❌ Please send text!", quote=True)
            return
        
        button_config = response.text
        config.CUSTOM_BUTTONS = button_config
        
        if hasattr(client, "db") and client.db:
            try:
                await client.db.settings.update_one(
                    {"_id": "bot_settings"},
                    {"$set": {"custom_buttons": button_config}},
                    upsert=True
                )
            except:
                pass
        
        await response.reply_text(
            f"✅ <b>Buttons Updated!</b>\n\n"
            f"Config:\n<code>{button_config}</code>",
            quote=True
        )
    
    except:
        await query.message.reply_text("❌ Timeout!")


@Client.on_callback_query(filters.regex("^clear_buttons$"))
async def clear_buttons_callback(client: Client, query: CallbackQuery):
    """Clear custom buttons"""
    
    if query.from_user.id not in ADMINS:
        await query.answer("❌ Admin only!", show_alert=True)
        return
    
    config.CUSTOM_BUTTONS = ""
    
    if hasattr(client, "db") and client.db:
        try:
            await client.db.settings.update_one(
                {"_id": "bot_settings"},
                {"$set": {"custom_buttons": ""}},
                upsert=True
            )
        except:
            pass
    
    await query.answer("✅ Buttons cleared!")
    await query.message.edit_text(
        "✅ <b>Custom Buttons Cleared!</b>\n\n"
        "Use /botsettings to configure again."
    )


# ========== PREVIEW ==========

@Client.on_callback_query(filters.regex("^settings_preview$"))
async def settings_preview_callback(client: Client, query: CallbackQuery):
    """Preview current settings"""
    
    if query.from_user.id not in ADMINS:
        await query.answer("❌ Admin only!", show_alert=True)
        return
    
    await query.answer("📤 Sending preview...")
    
    # Send a test /start message
    await query.message.reply_text(
        "📤 <b>Sending preview...</b>\n\n"
        "This is how users will see /start command:",
        quote=False
    )
    
    # Trigger start command for preview
    # This will use current settings
    await query.message.reply_text("/start", quote=False)


# ========== BACK BUTTON ==========

@Client.on_callback_query(filters.regex("^botsettings_back$"))
async def botsettings_back_callback(client: Client, query: CallbackQuery):
    """Go back to main settings"""
    
    text = """
⚙️ <b>BOT SETTINGS</b>

<b>Configure your bot appearance and behavior:</b>

📸 <b>Welcome Images</b> - Set bot pics
💬 <b>Welcome Message</b> - Customize start message
📚 <b>Help Message</b> - Edit help text
ℹ️ <b>About Message</b> - Edit about text
🔘 <b>Custom Buttons</b> - Add channel/support buttons

<i>Click a button below to configure</i>
"""
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📸 Images", callback_data="settings_images"),
            InlineKeyboardButton("💬 Welcome", callback_data="settings_welcome")
        ],
        [
            InlineKeyboardButton("📚 Help", callback_data="settings_help"),
            InlineKeyboardButton("ℹ️ About", callback_data="settings_about")
        ],
        [
            InlineKeyboardButton("🔘 Buttons", callback_data="settings_buttons")
        ],
        [
            InlineKeyboardButton("👀 Preview", callback_data="settings_preview"),
            InlineKeyboardButton("🔒 Close", callback_data="close")
        ]
    ])
    
    await query.message.edit_text(text, reply_markup=buttons)

"""
============================================================================
Batch Command - Generate Batch Links
Upload multiple files at once
============================================================================
"""

@Client.on_message(filters.private & filters.user(ADMINS) & filters.command("batch"))
async def batch_command(client: Client, message: Message):
    """Generate batch link"""
    
    if not hasattr(client, "db_channel"):
        await message.reply_text(
            "❌ <b>Database Channel Not Configured!</b>",
            quote=True
        )
        return
    
    await message.reply_text(
        "📦 <b>BATCH LINK GENERATOR</b>\n\n"
        "<b>Instructions:</b>\n"
        "1. Forward the FIRST message from channel\n"
        "2. Forward the LAST message from channel\n"
        "3. Bot will generate a batch link\n\n"
        "⏱️ <b>Waiting for first message...</b>",
        quote=True
    )
    
    # Listen for first message
    try:
        first_msg = await client.listen(message.chat.id, timeout=60, filters=filters.forwarded)
    except:
        await message.reply_text("❌ <b>Timeout!</b> No message received.", quote=True)
        return
    
    if not first_msg.forward_from_chat or first_msg.forward_from_chat.id != client.db_channel.id:
        await message.reply_text(
            "❌ <b>Invalid Message!</b>\n\n"
            "Please forward message from database channel.",
            quote=True
        )
        return
    
    first_id = first_msg.forward_from_message_id
    
    await message.reply_text(
        "✅ <b>First message received!</b>\n\n"
        f"<b>Message ID:</b> <code>{first_id}</code>\n\n"
        "⏱️ <b>Now forward the LAST message...</b>",
        quote=True
    )
    
    # Listen for last message
    try:
        last_msg = await client.listen(message.chat.id, timeout=60, filters=filters.forwarded)
    except:
        await message.reply_text("❌ <b>Timeout!</b> No message received.", quote=True)
        return
    
    if not last_msg.forward_from_chat or last_msg.forward_from_chat.id != client.db_channel.id:
        await message.reply_text(
            "❌ <b>Invalid Message!</b>\n\n"
            "Please forward message from database channel.",
            quote=True
        )
        return
    
    last_id = last_msg.forward_from_message_id
    
    # Generate batch link
    try:
        channel_id = abs(client.db_channel.id)
        converted_first = first_id * channel_id
        converted_last = last_id * channel_id
        
        link_string = f"get-{converted_first}-{converted_last}"
        encoded = await encode(link_string)
        link = f"https://t.me/{client.username}?start={encoded}"
        
        # Calculate total files
        total = abs(last_id - first_id) + 1
        
        # Create reply
        reply_text = f"""
✅ <b>Batch Link Generated!</b>

<b>📦 First Message ID:</b> <code>{first_id}</code>
<b>📦 Last Message ID:</b> <code>{last_id}</code>
<b>📊 Total Files:</b> <code>{total}</code>

<b>🔗 Batch Link:</b>
<code>{link}</code>

<b>💡 Tip:</b> Share this link to send all {total} files at once!
"""
        
        # Add button
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
            f"❌ <b>Error Generating Link!</b>\n\n<code>{str(e)}</code>",
            quote=True
        )


"""
============================================================================
Admin Help - Beautiful Interactive Command Menu
Shows all commands with descriptions and clickable buttons
============================================================================
"""

@Client.on_message(filters.command("help") & filters.private)
async def help_command(client: Client, message: Message):
    """Help command - different for admin and users"""
    
    # Check if admin
    if message.from_user.id in config.ADMINS:
        await show_admin_help(client, message)
    else:
        await show_user_help(client, message)


async def show_user_help(client: Client, message: Message):
    """Beautiful help for regular users"""
    
    help_image = "https://telegra.ph/file/9c4a742df32e42f286422.jpg"
    
    help_text = f"""
👋 <b>Hello {message.from_user.first_name} ~</b>

➜ <b>I AM A PRIVATE FILE SHARING BOT, MEANT TO PROVIDE FILES AND NECESSARY STUFF THROUGH SPECIAL LINK FOR SPECIFIC CHANNELS.</b>

➜ <b>IN ORDER TO GET THE FILES YOU HAVE TO JOIN THE ALL MENTIONED CHANNEL THAT I PROVIDE YOU TO JOIN. YOU CAN NOT ACCESS OR GET THE FILES UNLESS YOU JOINED ALL CHANNELS.</b>

➜ <b>SO JOIN MENTIONED CHANNELS TO GET FILES OR INITIATE MESSAGES...</b>

<b>• /help - OPEN THIS HELP MESSAGE !</b>

<i>➜ STILL HAVE DOUBTS, CONTACT BELOW PERSONS/ GROUP AS PER YOUR NEED!</i>
"""
    
    buttons = []
    
    if config.SUPPORT_CHAT:
        buttons.append([
            InlineKeyboardButton("🗨 Support Chat Group", url=f"https://t.me/{config.SUPPORT_CHAT.replace('@', '')}")
        ])
    
    owner_username = config.SUPPORT_CHAT or "YourOwner"
    developer_username = "YourDeveloper"
    
    buttons.append([
        InlineKeyboardButton("📥 Owner", url=f"https://t.me/{owner_username}"),
        InlineKeyboardButton("💫 Developer", url=f"https://t.me/{developer_username}")
    ])
    
    buttons.append([
        InlineKeyboardButton("🔐 Close", callback_data="close")
    ])
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    try:
        await message.reply_photo(
            photo=help_image,
            caption=help_text,
            reply_markup=reply_markup,
            quote=True
        )
    except:
        await message.reply_text(
            text=help_text,
            reply_markup=reply_markup,
            quote=True
        )


async def show_admin_help(client: Client, message: Message):
    """Beautiful admin help with ALL commands"""
    
    admin_help_image = "https://telegra.ph/file/d8d2e9cc6d60741c7e77d.jpg"
    
    admin_text = f"""
👑 <b>ADMIN COMMANDS PANEL</b>

<b>Hello {message.from_user.first_name}! You have full admin access.</b>

━━━━━━━━━━━━━━━━━━━━

<b>📁 FILE MANAGEMENT:</b>
• <code>/genlink</code> - Generate single file link
• <code>/batch</code> - Create batch link (sequential)
• <code>/custom_batch</code> - Create custom batch link
• <code>/special_link</code> - Link with custom message

<b>⚙️ CHANNEL SETTINGS:</b>
• <code>/setchannel</code> - Configure database channel
• <code>/checkchannel</code> - Check channel status
• <code>/removechannel</code> - Remove channel

<b>👥 USER MANAGEMENT:</b>
• <code>/users</code> - View user statistics
• <code>/ban</code> - Ban a user
• <code>/unban</code> - Unban a user
• <code>/broadcast</code> - Broadcast message

<b>📊 BOT SETTINGS:</b>
• <code>/settings</code> - Main settings panel
• <code>/botsettings</code> - Configure bot appearance
• <code>/files</code> - File protection settings
• <code>/forcesub</code> - Force subscribe settings
• <code>/auto_del</code> - Auto-delete settings

<b>📈 STATISTICS:</b>
• <code>/stats</code> - Complete bot statistics

<b>🔗 UTILITIES:</b>
• <code>/shortener</code> - Shorten any URL
• <code>/ping</code> - Check bot status
• <code>/test</code> - Test bot functionality

━━━━━━━━━━━━━━━━━━━━

<b>💡 Click any command below to execute it!</b>
"""
    
    # Create clickable command buttons - organized by category
    buttons = [
        # File Management
        [
            InlineKeyboardButton("📝 Generate Link", callback_data="cmd_genlink"),
            InlineKeyboardButton("📦 Batch Link", callback_data="cmd_batch")
        ],
        [
            InlineKeyboardButton("🎯 Custom Batch", callback_data="cmd_custom_batch"),
            InlineKeyboardButton("⭐ Special Link", callback_data="cmd_special_link")
        ],
        
        # Channel Settings
        [
            InlineKeyboardButton("📺 Set Channel", callback_data="cmd_setchannel"),
            InlineKeyboardButton("✅ Check Channel", callback_data="cmd_checkchannel")
        ],
        
        # User Management
        [
            InlineKeyboardButton("👥 Users Stats", callback_data="cmd_users"),
            InlineKeyboardButton("📊 Bot Stats", callback_data="cmd_stats")
        ],
        
        # Settings
        [
            InlineKeyboardButton("⚙️ Settings", callback_data="cmd_settings"),
            InlineKeyboardButton("🎨 Bot Settings", callback_data="cmd_botsettings")
        ],
        [
            InlineKeyboardButton("📁 Files Settings", callback_data="cmd_files"),
            InlineKeyboardButton("📢 Force Sub", callback_data="cmd_forcesub")
        ],
        
        # Utilities
        [
            InlineKeyboardButton("🔗 URL Shortener", callback_data="cmd_shortener"),
            InlineKeyboardButton("🏓 Ping", callback_data="cmd_ping")
        ],
        
        # Close
        [
            InlineKeyboardButton("🔐 Close", callback_data="close")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    try:
        await message.reply_photo(
            photo=admin_help_image,
            caption=admin_text,
            reply_markup=reply_markup,
            quote=True
        )
    except:
        await message.reply_text(
            text=admin_text,
            reply_markup=reply_markup,
            quote=True
        )


# ========== COMMAND CALLBACKS ==========

@Client.on_callback_query(filters.regex("^cmd_"))
async def command_callbacks(client: Client, query: CallbackQuery):
    """Handle command button clicks"""
    
    if query.from_user.id not in config.ADMINS:
        await query.answer("❌ Admin only!", show_alert=True)
        return
    
    # Extract command from callback data
    command = query.data.replace("cmd_", "")
    
    # Command descriptions for confirmation
    command_info = {
        "genlink": "📝 Generate single file link\n\nForward a message from your database channel to get a shareable link.",
        "batch": "📦 Batch Link Generator\n\nForward FIRST and LAST messages from channel to create batch link.",
        "custom_batch": "🎯 Custom Batch\n\nForward multiple random messages, then send /done to create link.",
        "special_link": "⭐ Special Link\n\nCreate link with custom welcome message for users.",
        "setchannel": "📺 Set Database Channel\n\nConfigure your file storage channel/group.",
        "checkchannel": "✅ Check Channel Status\n\nView current channel configuration and status.",
        "users": "👥 User Statistics\n\nView total users, banned users, and active users.",
        "stats": "📊 Bot Statistics\n\nView complete bot statistics and information.",
        "settings": "⚙️ Main Settings\n\nAccess all bot configuration settings.",
        "botsettings": "🎨 Bot Appearance\n\nConfigure welcome message, images, buttons, etc.",
        "files": "📁 File Settings\n\nConfigure file protection, captions, and buttons.",
        "forcesub": "📢 Force Subscribe\n\nManage force subscribe channels and settings.",
        "shortener": "🔗 URL Shortener\n\nShorten any long URL to a short link.",
        "ping": "🏓 Ping Bot\n\nCheck if bot is online and responsive."
    }
    
    info_text = command_info.get(command, f"Execute /{command} command")
    
    # Create confirmation buttons
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Execute Command", callback_data=f"exec_{command}"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_cmd")
        ]
    ])
    
    await query.message.reply_text(
        f"<b>📋 COMMAND INFO</b>\n\n"
        f"{info_text}\n\n"
        f"<b>Command:</b> <code>/{command}</code>\n\n"
        f"Click <b>Execute</b> to run this command.",
        reply_markup=buttons,
        quote=True
    )
    
    await query.answer()


@Client.on_callback_query(filters.regex("^exec_"))
async def execute_command_callback(client: Client, query: CallbackQuery):
    """Execute the selected command"""
    
    if query.from_user.id not in config.ADMINS:
        await query.answer("❌ Admin only!", show_alert=True)
        return
    
    command = query.data.replace("exec_", "")
    
    await query.answer(f"✅ Executing /{command}...")
    
    # Send the command as if user typed it
    await query.message.reply_text(f"/{command}")


@Client.on_callback_query(filters.regex("^cancel_cmd$"))
async def cancel_command_callback(client: Client, query: CallbackQuery):
    """Cancel command execution"""
    
    await query.answer("❌ Cancelled")
    await query.message.delete()


# ========== HELP CALLBACK (for start menu) ==========

@Client.on_callback_query(filters.regex("^help$"))
async def help_callback(client: Client, query: CallbackQuery):
    """Help button callback from start menu"""
    
    # Check if admin
    if query.from_user.id in config.ADMINS:
        # Show admin help
        admin_help_image = "https://telegra.ph/file/d8d2e9cc6d60741c7e77d.jpg"
        
        admin_text = f"""
👑 <b>ADMIN COMMANDS PANEL</b>

<b>Hello {query.from_user.first_name}! You have full admin access.</b>

━━━━━━━━━━━━━━━━━━━━

<b>📁 FILE MANAGEMENT:</b>
• <code>/genlink</code> - Generate single file link
• <code>/batch</code> - Create batch link
• <code>/custom_batch</code> - Custom batch link
• <code>/special_link</code> - Link with custom message

<b>⚙️ CHANNEL SETTINGS:</b>
• <code>/setchannel</code> - Configure channel
• <code>/checkchannel</code> - Check status

<b>👥 USER MANAGEMENT:</b>
• <code>/users</code> - User statistics
• <code>/ban</code> / <code>/unban</code> - Manage users
• <code>/broadcast</code> - Send to all

<b>📊 SETTINGS & STATS:</b>
• <code>/settings</code> - Bot settings
• <code>/botsettings</code> - Appearance
• <code>/stats</code> - Statistics

━━━━━━━━━━━━━━━━━━━━

<b>💡 Click commands below to execute!</b>
"""
        
        buttons = [
            [
                InlineKeyboardButton("📝 Generate Link", callback_data="cmd_genlink"),
                InlineKeyboardButton("📦 Batch", callback_data="cmd_batch")
            ],
            [
                InlineKeyboardButton("📺 Set Channel", callback_data="cmd_setchannel"),
                InlineKeyboardButton("👥 Users", callback_data="cmd_users")
            ],
            [
                InlineKeyboardButton("⚙️ Settings", callback_data="cmd_settings"),
                InlineKeyboardButton("📊 Stats", callback_data="cmd_stats")
            ],
            [
                InlineKeyboardButton("🏠 Home", callback_data="start"),
                InlineKeyboardButton("🔐 Close", callback_data="close")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(buttons)
        
        try:
            await query.message.edit_caption(
                caption=admin_text,
                reply_markup=reply_markup
            )
        except:
            try:
                await query.message.edit_text(
                    text=admin_text,
                    reply_markup=reply_markup
                )
            except:
                await query.answer("Error!", show_alert=True)
    
    else:
        # Show user help
        help_text = f"""
👋 <b>Hello {query.from_user.first_name} ~</b>

➜ <b>I AM A PRIVATE FILE SHARING BOT, MEANT TO PROVIDE FILES AND NECESSARY STUFF THROUGH SPECIAL LINK FOR SPECIFIC CHANNELS.</b>

➜ <b>IN ORDER TO GET THE FILES YOU HAVE TO JOIN THE ALL MENTIONED CHANNEL THAT I PROVIDE YOU TO JOIN. YOU CAN NOT ACCESS OR GET THE FILES UNLESS YOU JOINED ALL CHANNELS.</b>

➜ <b>SO JOIN MENTIONED CHANNELS TO GET FILES OR INITIATE MESSAGES...</b>

<b>• /help - OPEN THIS HELP MESSAGE !</b>

<i>➜ STILL HAVE DOUBTS, CONTACT BELOW PERSONS/ GROUP AS PER YOUR NEED!</i>
"""
        
        buttons = []
        
        if config.SUPPORT_CHAT:
            buttons.append([
                InlineKeyboardButton("🗨 Support Chat Group", url=f"https://t.me/{config.SUPPORT_CHAT.replace('@', '')}")
            ])
        
        buttons.append([
            InlineKeyboardButton("🏠 Home", callback_data="start"),
            InlineKeyboardButton("🔐 Close", callback_data="close")
        ])
        
        reply_markup = InlineKeyboardMarkup(buttons)
        
        try:
            await query.message.edit_caption(
                caption=help_text,
                reply_markup=reply_markup
            )
        except:
            try:
                await query.message.edit_text(
                    text=help_text,
                    reply_markup=reply_markup
                )
            except:
                await query.answer("Error!", show_alert=True)


"""
============================================================================
Admin Commands - Beautiful Interactive Panels
Like EvaMaria UI with toggles and settings
============================================================================
"""

# ========== USERS COMMAND ==========

@Client.on_message(filters.private & filters.user(ADMINS) & filters.command("users"))
async def users_command(client: Client, message: Message):
    """Show user statistics with beautiful UI"""
    
    if not (hasattr(client, "db") and client.db):
        await message.reply_text("❌ Database not connected!", quote=True)
        return
    
    msg = await message.reply_text("⏳ <b>Counting users...</b>", quote=True)
    
    total = await client.db.total_users_count()
    banned = len(await client.db.get_banned_users())
    
    text = f"""
👥 <b>USER STATISTICS</b>

<b>📊 Total Users:</b> <code>{total}</code>
<b>🚫 Banned Users:</b> <code>{banned}</code>
<b>✅ Active Users:</b> <code>{total - banned}</code>
"""
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔄 Refresh", callback_data="users_refresh"),
            InlineKeyboardButton("🔒 Close", callback_data="close")
        ]
    ])
    
    await msg.edit_text(text, reply_markup=buttons)


@Client.on_callback_query(filters.regex("^users_refresh$"))
async def users_refresh_callback(client: Client, query: CallbackQuery):
    """Refresh user statistics"""
    
    if query.from_user.id not in ADMINS:
        await query.answer("❌ You're not authorized!", show_alert=True)
        return
    
    await query.answer("♻️ Refreshing...")
    
    total = await client.db.total_users_count()
    banned = len(await client.db.get_banned_users())
    
    text = f"""
👥 <b>USER STATISTICS</b>

<b>📊 Total Users:</b> <code>{total}</code>
<b>🚫 Banned Users:</b> <code>{banned}</code>
<b>✅ Active Users:</b> <code>{total - banned}</code>

<i>Last updated: Just now</i>
"""
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔄 Refresh", callback_data="users_refresh"),
            InlineKeyboardButton("🔒 Close", callback_data="close")
        ]
    ])
    
    await query.message.edit_text(text, reply_markup=buttons)


# ========== BROADCAST COMMAND ==========

@Client.on_message(filters.private & filters.user(ADMINS) & filters.command("broadcast"))
async def broadcast_command(client: Client, message: Message):
    """Broadcast message to all users"""
    
    if not (hasattr(client, "db") and client.db):
        await message.reply_text("❌ Database not connected!", quote=True)
        return
    
    if not message.reply_to_message:
        await message.reply_text(
            "❌ <b>Reply to a message to broadcast!</b>\n\n"
            "<b>Usage:</b> <code>/broadcast</code> (reply to message)",
            quote=True
        )
        return
    
    users = await client.db.get_all_users()
    broadcast_msg = message.reply_to_message
    
    status_msg = await message.reply_text(
        "📢 <b>BROADCASTING...</b>\n\n"
        f"<b>Total users:</b> <code>{len(users)}</code>\n"
        "⏳ <i>Please wait...</i>",
        quote=True
    )
    
    successful = 0
    blocked = 0
    deleted = 0
    failed = 0
    
    for user_id in users:
        try:
            await broadcast_msg.copy(user_id)
            successful += 1
        except UserIsBlocked:
            await client.db.delete_user(user_id)
            blocked += 1
        except InputUserDeactivated:
            await client.db.delete_user(user_id)
            deleted += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                await broadcast_msg.copy(user_id)
                successful += 1
            except:
                failed += 1
        except:
            failed += 1
        
        # Update status every 50 users
        if (successful + blocked + deleted + failed) % 50 == 0:
            await status_msg.edit_text(
                f"📢 <b>BROADCASTING...</b>\n\n"
                f"<b>Progress:</b> {successful + blocked + deleted + failed}/{len(users)}\n"
                f"✅ Success: {successful}\n"
                f"🚫 Blocked: {blocked}\n"
                f"❌ Deleted: {deleted}\n"
                f"⚠️ Failed: {failed}"
            )
    
    # Final status
    await status_msg.edit_text(
        f"✅ <b>BROADCAST COMPLETED!</b>\n\n"
        f"<b>📊 Statistics:</b>\n"
        f"• Total: <code>{len(users)}</code>\n"
        f"• Successful: <code>{successful}</code>\n"
        f"• Blocked: <code>{blocked}</code>\n"
        f"• Deleted: <code>{deleted}</code>\n"
        f"• Failed: <code>{failed}</code>"
    )


# ========== BAN/UNBAN COMMANDS ==========

@Client.on_message(filters.private & filters.user(ADMINS) & filters.command("ban"))
async def ban_user_command(client: Client, message: Message):
    """Ban a user"""
    
    if not (hasattr(client, "db") and client.db):
        await message.reply_text("❌ Database not connected!", quote=True)
        return
    
    if len(message.command) < 2:
        await message.reply_text(
            "❌ <b>Invalid Usage!</b>\n\n"
            "<b>Usage:</b> <code>/ban user_id</code>",
            quote=True
        )
        return
    
    try:
        user_id = int(message.command[1])
    except:
        await message.reply_text("❌ Invalid user ID!", quote=True)
        return
    
    if await client.db.is_user_banned(user_id):
        await message.reply_text(
            f"⚠️ User <code>{user_id}</code> is already banned!",
            quote=True
        )
        return
    
    await client.db.ban_user(user_id)
    await message.reply_text(
        f"✅ <b>User Banned!</b>\n\n"
        f"<b>User ID:</b> <code>{user_id}</code>",
        quote=True
    )


@Client.on_message(filters.private & filters.user(ADMINS) & filters.command("unban"))
async def unban_user_command(client: Client, message: Message):
    """Unban a user"""
    
    if not (hasattr(client, "db") and client.db):
        await message.reply_text("❌ Database not connected!", quote=True)
        return
    
    if len(message.command) < 2:
        await message.reply_text(
            "❌ <b>Invalid Usage!</b>\n\n"
            "<b>Usage:</b> <code>/unban user_id</code>",
            quote=True
        )
        return
    
    try:
        user_id = int(message.command[1])
    except:
        await message.reply_text("❌ Invalid user ID!", quote=True)
        return
    
    if not await client.db.is_user_banned(user_id):
        await message.reply_text(
            f"⚠️ User <code>{user_id}</code> is not banned!",
            quote=True
        )
        return
    
    await client.db.unban_user(user_id)
    await message.reply_text(
        f"✅ <b>User Unbanned!</b>\n\n"
        f"<b>User ID:</b> <code>{user_id}</code>",
        quote=True
    )


# ========== STATS COMMAND ==========

@Client.on_message(filters.private & filters.user(ADMINS) & filters.command("stats"))
async def stats_command(client: Client, message: Message):
    """Show bot statistics"""
    
    if not (hasattr(client, "db") and client.db):
        await message.reply_text("❌ Database not connected!", quote=True)
        return
    
    total_users = await client.db.total_users_count()
    banned_users = len(await client.db.get_banned_users())
    
    text = f"""
📊 <b>BOT STATISTICS</b>

<b>🤖 Bot Info:</b>
• Name: {client.first_name}
• Username: @{client.username}
• ID: <code>{client.id}</code>

<b>👥 Users:</b>
• Total: <code>{total_users}</code>
• Banned: <code>{banned_users}</code>
• Active: <code>{total_users - banned_users}</code>

<b>⚙️ System:</b>
• Database: ✅ Connected
• Channels: ✅ Configured
"""
    
    if hasattr(client, "db_channel"):
        text += f"• File Channel: {client.db_channel.title}\n"
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔄 Refresh", callback_data="stats_refresh"),
            InlineKeyboardButton("🔒 Close", callback_data="close")
        ]
    ])
    
    await message.reply_text(text, reply_markup=buttons, quote=True)


@Client.on_callback_query(filters.regex("^stats_refresh$"))
async def stats_refresh_callback(client: Client, query: CallbackQuery):
    """Refresh statistics"""
    
    if query.from_user.id not in ADMINS:
        await query.answer("❌ You're not authorized!", show_alert=True)
        return
    
    await query.answer("♻️ Refreshing...")
    
    total_users = await client.db.total_users_count()
    banned_users = len(await client.db.get_banned_users())
    
    text = f"""
📊 <b>BOT STATISTICS</b>

<b>🤖 Bot Info:</b>
• Name: {client.first_name}
• Username: @{client.username}
• ID: <code>{client.id}</code>

<b>👥 Users:</b>
• Total: <code>{total_users}</code>
• Banned: <code>{banned_users}</code>
• Active: <code>{total_users - banned_users}</code>

<b>⚙️ System:</b>
• Database: ✅ Connected
• Channels: ✅ Configured
"""
    
    if hasattr(client, "db_channel"):
        text += f"• File Channel: {client.db_channel.title}\n"
    
    text += f"\n<i>Last updated: Just now</i>"
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔄 Refresh", callback_data="stats_refresh"),
            InlineKeyboardButton("🔒 Close", callback_data="close")
        ]
    ])
    
    await query.message.edit_text(text, reply_markup=buttons)

# Add web server for Render (at the end of bot.py, before main())
from aiohttp import web
import os

async def health_check(request):
    """Health check endpoint for Render"""
    return web.Response(text="✅ Bot is running!")

async def start_web_server():
    """Start HTTP server for Render's port requirement"""
    app = web.Application()
    app.router.add_get('/', health_check)
    app.router.add_get('/health', health_check)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.environ.get('PORT', 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    LOGGER.info(f"✅ Web server started on port {port}")
    return runner

async def main():
    """Main function to run the bot"""
    import config
    
    # Create bot instance
    bot = Bot()
    
    # Configure database channel
    if config.CHANNELS and config.CHANNELS[0] != 0:
        try:
            channel = await bot.get_chat(config.CHANNELS[0])
            bot.db_channel = channel
            bot.db_channel_id = channel.id
        except:
            pass
    
    # Start web server FIRST (for Render)
    web_runner = await start_web_server()
    
    # Start bot
    await bot.start()
    
    LOGGER.info("🤖 Bot is now running. Press Ctrl+C to stop.")
    
    # Create event to keep running
    stop_event = asyncio.Event()
    
    # Keep running until stop event is set
    try:
        await stop_event.wait()
    except (KeyboardInterrupt, SystemExit):
        LOGGER.info("⏹️ Stopping bot...")
    finally:
        # Cleanup
        await bot.stop()
        await web_runner.cleanup()

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("👋 Bye!")
