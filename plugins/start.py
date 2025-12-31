"""
Start Command - Welcome users and handle file links
Complete file sharing functionality
"""

import random
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant

from config import *
from utils.helpers import encode, decode, get_messages, delete_files, is_subscribed

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
