"""
Start Command - Beautiful Interactive UI
Handles welcome message and file sharing
"""

import random
import asyncio
import config
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated

from config import *
from utils.helpers import encode, decode, get_messages, delete_files, is_subscribed, get_readable_time


def parse_custom_buttons(button_string: str) -> list:
    """
    Parse custom button string to button list
    Format: Text | URL or Text1 | URL1 : Text2 | URL2
    """
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


def format_caption_html(caption: str) -> str:
    """
    Format caption with full HTML support
    Auto-converts common formatting to HTML
    """
    if not caption:
        return ""
    
    # If caption already has HTML tags, return as is
    if any(tag in caption for tag in ['<b>', '<i>', '<u>', '<code>', '<a ', '<blockquote']):
        return caption
    
    # Auto-convert markdown-style to HTML
    # **bold** → <b>bold</b>
    import re
    
    # Bold: **text** or __text__
    caption = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', caption)
    caption = re.sub(r'__(.+?)__', r'<b>\1</b>', caption)
    
    # Italic: *text* or _text_ (but not __ which is bold)
    caption = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', caption)
    caption = re.sub(r'(?<!_)_(?!_)(.+?)(?<!_)_(?!_)', r'<i>\1</i>', caption)
    
    # Strikethrough: ~~text~~
    caption = re.sub(r'~~(.+?)~~', r'<s>\1</s>', caption)
    
    # Code: `text`
    caption = re.sub(r'`(.+?)`', r'<code>\1</code>', caption)
    
    # Underline: ++text++
    caption = re.sub(r'\+\+(.+?)\+\+', r'<u>\1</u>', caption)
    
    # Spoiler: ||text||
    caption = re.sub(r'\|\|(.+?)\|\|', r'<tg-spoiler>\1</tg-spoiler>', caption)
    
    return caption

@Client.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    """Main start handler - welcome and file sharing"""
    
    user_id = message.from_user.id
    
    # Add user to database
    if hasattr(client, "db") and client.db:
        if not await client.db.is_user_exist(user_id):
            await client.db.add_user(user_id)
    
    # Check if banned
    if bot.db and await client.db.is_user_banned(user_id):
        await message.reply_text(
            "❌ <b>You are Banned!</b>\n\n"
            "Contact admin for more info.",
            quote=True
        )
        return
    
    # Get text and check for parameter
    text = message.text
    
    # Check if has file parameter
    if ' ' in text and len(text.split()) > 1:
        # File sharing mode
        file_param = text.split(' ', 1)[1]
        await handle_file_request(client, message, file_param)
    else:
        # Welcome mode
        await show_welcome(client, message)


async def show_welcome(client: Client, message: Message):
    """Show beautiful welcome message"""
    
    # Get random pic
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
    
    # Add custom buttons
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
    
    # Send message
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
    
    await message.reply_text(
        text=welcome_text,
        reply_markup=reply_markup,
        disable_web_page_preview=True,
        quote=True
    )


async def handle_file_request(client: Client, message: Message, file_param: str):
    """Handle file sharing request"""
    
    user_id = message.from_user.id
    
    # Check force subscribe
    if FORCE_SUB_CHANNELS:
        is_sub = await is_subscribed(client, user_id, FORCE_SUB_CHANNELS)
        
        if not is_sub:
            await show_force_subscribe(client, message, file_param)
            return
    
    # User is subscribed, send file
    await send_file(client, message, file_param)


async def show_force_subscribe(client: Client, message: Message, file_param: str):
    """Show force subscribe message - EXACT like screenshot 2"""
    
    # Get random pic for force sub message
    pic = random.choice(BOT_PICS) if BOT_PICS else None
    
    # Create warning text - exactly like screenshot
    force_text = f"""
⚠️ <b>Hey, {message.from_user.mention}</b>

<b>You haven't joined 1/4 channels yet. Please join the channels provided below, then try again..!</b>

<b>❗ Facing problems, use:</b> /help
"""
    
    # Create buttons
    buttons = []
    
    # Add all channel buttons
    for idx, channel_id in enumerate(FORCE_SUB_CHANNELS, 1):
        try:
            chat = await client.get_chat(channel_id)
            
            # Get chat title
            channel_title = chat.title
            
            # Get invite link
            if REQUEST_FSUB:
                try:
                    invite = await client.create_chat_invite_link(
                        chat_id=channel_id,
                        creates_join_request=True
                    )
                    url = invite.invite_link
                except:
                    url = f"https://t.me/{chat.username}" if chat.username else None
            else:
                url = bot.invitelink if hasattr(bot, 'invitelink') else f"https://t.me/{chat.username}" if chat.username else None
            
            if url:
                # Add channel button with title
                buttons.append([
                    InlineKeyboardButton(channel_title, url=url)
                ])
        except:
            continue
    
    # Add main channel join button (if you have one specific)
    # buttons.append([
    #     InlineKeyboardButton("Main Channel Join", url="https://t.me/yourchannel")
    # ])
    
    # Add try again button - exactly like screenshot
    try_again_link = f"https://t.me/{client.username}?start={file_param}"
    buttons.append([
        InlineKeyboardButton("🔄 Try Again", url=try_again_link)
    ])
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    # Send with image like screenshot 2
    if pic:
        try:
            await message.reply_photo(
                photo=pic,
                caption=force_text,
                reply_markup=reply_markup,
                quote=True
            )
            return
        except:
            pass
    
    # Fallback to text
    await message.reply_text(
        text=force_text,
        reply_markup=reply_markup,
        quote=True,
        disable_web_page_preview=True
    )


async def send_file(client: Client, message: Message, file_param: str):
    """Decode parameter and send file(s)"""
    
    # Check for special link custom message
    if hasattr(client, "db") and client.db:
        special_data = await client.db.settings.find_one({"_id": f"special_{file_param}"})
        if special_data and 'message' in special_data:
            # Show custom message first
            await message.reply_text(
                special_data['message'],
                quote=True
            )
    
    # Check if db_channel exists
    if not hasattr(client, "db_channel"):
        await message.reply_text(
            "❌ <b>Bot Configuration Error!</b>\n\n"
            "Database channel not configured. Contact admin.",
            quote=True
        )
        return
    
    # Decode parameter
    try:
        decoded = await decode(file_param)
    except Exception as e:
        await message.reply_text(
            "❌ <b>Invalid Link!</b>\n\n"
            "This link is corrupted or expired.",
            quote=True
        )
        return
    
    # Parse decoded string: get-{id} or get-{start}-{end} or custombatch-{id1}-{id2}-{id3}
    parts = decoded.split('-')
    
    if len(parts) < 2:
        await message.reply_text(
            "❌ <b>Invalid Link Format!</b>",
            quote=True
        )
        return
    
    # Calculate message IDs
    try:
        channel_id = abs(client.db_channel.id)
        
        if parts[0] == 'custombatch':
            # Custom batch: custombatch-id1-id2-id3...
            converted_ids = [int(id_str) for id_str in parts[1:]]
            message_ids = [int(conv_id / channel_id) for conv_id in converted_ids]
        elif parts[0] == 'get':
            if len(parts) == 2:
                # Single file
                msg_id = int(int(parts[1]) / channel_id)
                message_ids = [msg_id]
            elif len(parts) == 3:
                # Batch
                start_id = int(int(parts[1]) / channel_id)
                end_id = int(int(parts[2]) / channel_id)
                
                if start_id <= end_id:
                    message_ids = list(range(start_id, end_id + 1))
                else:
                    message_ids = list(range(start_id, end_id - 1, -1))
            else:
                raise ValueError("Invalid format")
        else:
            raise ValueError("Unknown link type")
    
    except Exception as e:
        await message.reply_text(
            f"❌ <b>Error Processing Link!</b>\n\n<code>{str(e)}</code>",
            quote=True
        )
        return
    
    # Show loading message
    temp_msg = await message.reply_text(
        f"⏳ <b>Fetching {len(message_ids)} file(s)...</b>",
        quote=True
    )
    
    # Fetch messages
    try:
        messages = await get_messages(client, message_ids)
    except Exception as e:
        await temp_msg.edit_text(
            "❌ <b>Error Fetching Files!</b>\n\n"
            "Files may have been deleted or link is invalid."
        )
        return
    
    await temp_msg.delete()
    
    # Send files
    sent_messages = []
    
    for msg in messages:
        try:
            # Get file details
            if msg.document:
                file_name = msg.document.file_name
                file_size = msg.document.file_size
                mime_type = msg.document.mime_type
            elif msg.video:
                file_name = msg.video.file_name or "video.mp4"
                file_size = msg.video.file_size
                mime_type = msg.video.mime_type
            elif msg.audio:
                file_name = msg.audio.file_name or "audio.mp3"
                file_size = msg.audio.file_size
                mime_type = msg.audio.mime_type
            else:
                file_name = "file"
                file_size = 0
                mime_type = "unknown"
            
            # Format file size
            size_mb = file_size / (1024 * 1024) if file_size else 0
            
            # Prepare caption with FULL HTML SUPPORT
            caption = ""
            
            if CUSTOM_CAPTION:
                # Use custom caption template
                caption = CUSTOM_CAPTION.format(
                    previouscaption=msg.caption.html if msg.caption else "",
                    filename=file_name,
                    filesize=f"{size_mb:.2f} MB",
                    mime_type=mime_type
                )
            elif not HIDE_CAPTION and msg.caption:
                # Use original caption
                caption = msg.caption.html
            else:
                # No caption
                caption = ""
            
            # Parse caption for HTML formatting
            # Supports: bold, italic, underline, strikethrough, spoiler, code, pre, links, blockquote
            if caption:
                caption = format_caption_html(caption)
            
            # Prepare buttons
            reply_markup = None
            
            # First, get custom buttons from config
            custom_buttons = []
            if config.CUSTOM_BUTTONS:
                custom_buttons = parse_custom_buttons(config.CUSTOM_BUTTONS)
            
            # Add original message buttons if not hidden
            if not HIDE_CAPTION and msg.reply_markup:
                # Combine custom buttons with original buttons
                if custom_buttons:
                    # Custom buttons first, then original buttons
                    all_buttons = custom_buttons + [[btn] for row in msg.reply_markup.inline_keyboard for btn in row]
                    reply_markup = InlineKeyboardMarkup(all_buttons)
                else:
                    reply_markup = msg.reply_markup
            elif custom_buttons:
                # Only custom buttons
                reply_markup = InlineKeyboardMarkup(custom_buttons)
            
            # Send file
            copied_msg = await msg.copy(
                chat_id=message.from_user.id,
                caption=caption,
                reply_markup=reply_markup,
                protect_content=PROTECT_CONTENT,
                parse_mode=None  # Use HTML formatting
            )
            
            sent_messages.append(copied_msg)
            
            # Small delay
            await asyncio.sleep(0.5)
        
        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                copied_msg = await msg.copy(
                    chat_id=message.from_user.id,
                    caption=caption,
                    reply_markup=reply_markup,
                    protect_content=PROTECT_CONTENT,
                    parse_mode=None
                )
                sent_messages.append(copied_msg)
            except:
                continue
        except:
            continue
    
    # Auto delete if enabled
    if sent_messages and AUTO_DELETE_TIME > 0:
        link = f"https://t.me/{client.username}?start={file_param}"
        
        # Create delete warning message with "Click Here" button - exactly like screenshot 4
        delete_text = f"""
<b>Previous Message was Deleted</b>

If you want to get the files again, then click [ 🔄 <b>Click Here</b> ] button below else close this message.
"""
        
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔄 Click Here", url=link),
                InlineKeyboardButton("Close ❌", callback_data="close")
            ]
        ])
        
        delete_msg = await message.reply_text(
            delete_text,
            reply_markup=buttons,
            quote=True
        )
        
        # Schedule deletion
        asyncio.create_task(delete_files(sent_messages, client, delete_msg, link))
