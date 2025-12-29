"""
Genlink Command - Generate Single File Link
Store a single message/file (moderators only)
"""

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from bot import bot
from config import ADMINS
from utils.helpers import encode

@bot.on_message(filters.private & filters.user(ADMINS) & filters.command("genlink"))
async def genlink_command(client: Client, message: Message):
    """Generate link for single file"""
    
    if not hasattr(bot, 'db_channel'):
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
    if not forward_msg.forward_from_chat or forward_msg.forward_from_chat.id != bot.db_channel.id:
        await message.reply_text(
            "❌ <b>Invalid Message!</b>\n\n"
            "Please forward message from database channel.",
            quote=True
        )
        return
    
    # Generate link
    try:
        msg_id = forward_msg.forward_from_message_id
        channel_id = abs(bot.db_channel.id)
        converted_id = msg_id * channel_id
        
        link_string = f"get-{converted_id}"
        encoded = await encode(link_string)
        link = f"https://t.me/{bot.username}?start={encoded}"
        
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
