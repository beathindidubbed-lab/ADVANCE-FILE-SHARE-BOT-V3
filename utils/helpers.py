"""
Helper Functions - Utilities for the bot
"""

import base64
import asyncio
from pyrogram.errors import FloodWait
from pyrogram.types import Message

# ========== ENCODING/DECODING ==========

async def encode(string):
    """Encode string to base64"""
    string_bytes = string.encode("ascii")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    return base64_bytes.decode("ascii")

async def decode(base64_string):
    """Decode base64 to string"""
    base64_bytes = base64_string.encode("ascii")
    string_bytes = base64.urlsafe_b64decode(base64_bytes)
    return string_bytes.decode("ascii")

# ========== MESSAGE FETCHING ==========

async def get_messages(client, message_ids):
    """Fetch messages from database channel"""
    from bot import bot
    
    if not hasattr(bot, 'db_channel'):
        return []
    
    messages = []
    total = len(message_ids)
    
    while len(message_ids) > 0:
        temp_ids = message_ids[:200]
        message_ids = message_ids[200:]
        
        try:
            msgs = await client.get_messages(
                chat_id=bot.db_channel.id,
                message_ids=temp_ids
            )
            messages.extend(msgs)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            msgs = await client.get_messages(
                chat_id=bot.db_channel.id,
                message_ids=temp_ids
            )
            messages.extend(msgs)
        except Exception as e:
            print(f"Error fetching messages: {e}")
            continue
    
    return messages

# ========== AUTO DELETE ==========

async def delete_files(messages, client, notification_msg, link):
    """Auto-delete files after specified time"""
    from config import AUTO_DELETE_TIME
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    if not AUTO_DELETE_TIME or AUTO_DELETE_TIME == 0:
        return
    
    await asyncio.sleep(AUTO_DELETE_TIME)
    
    # Delete all file messages
    for msg in messages:
        try:
            await msg.delete()
        except:
            pass
    
    # The notification message already has the "Click Here" button
    # So we don't need to update it - it stays as is
    # User can click "Click Here" to get files again or "Close" to dismiss

# ========== FORCE SUBSCRIBE CHECK ==========

async def is_subscribed(client, user_id, channel_ids):
    """Check if user is subscribed to all channels"""
    if not channel_ids:
        return True
    
    for channel_id in channel_ids:
        if not channel_id or channel_id == 0:
            continue
            
        try:
            member = await client.get_chat_member(channel_id, user_id)
            if member.status in ["kicked", "left"]:
                return False
        except:
            return False
    
    return True

# ========== FILE SIZE FORMATTER ==========

def get_size(size):
    """Convert size to readable format"""
    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units)-1:
        i += 1
        size /= 1024.0
    return "%.2f %s" % (size, units[i])

# ========== TIME FORMATTER ==========

def get_readable_time(seconds):
    """Convert seconds to readable time"""
    result = ''
    (days, remainder) = divmod(seconds, 86400)
    days = int(days)
    if days != 0:
        result += f'{days}d '
    (hours, remainder) = divmod(remainder, 3600)
    hours = int(hours)
    if hours != 0:
        result += f'{hours}h '
    (minutes, seconds) = divmod(remainder, 60)
    minutes = int(minutes)
    if minutes != 0:
        result += f'{minutes}m '
    seconds = int(seconds)
    result += f'{seconds}s'
    return result

# ========== BUTTON PARSER ==========

def parse_buttons(button_string):
    """Parse button string to button list"""
    if not button_string:
        return []
    
    buttons = []
    rows = button_string.split(":")
    
    for row in rows:
        button_row = []
        cols = row.split("|")
        
        if len(cols) == 2:
            button_row.append({
                "text": cols[0].strip(),
                "url": cols[1].strip()
            })
        
        if button_row:
            buttons.append(button_row)
    
    return buttons
