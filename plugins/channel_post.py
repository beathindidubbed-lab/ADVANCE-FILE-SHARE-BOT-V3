"""
Channel Post Handler - Generate Shareable Links
When admin forwards files to bot
"""

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

#from bot import bot
from config import ADMINS, CHANNELS
from utils.helpers import encode

@Client.on_message(filters.private & filters.user(ADMINS) & (filters.document | filters.video | filters.audio))
async def forward_to_channel(client: Client, message: Message):
    """Forward files to channel and generate link"""
    
    if not hasattr(bot, 'db_channel'):
        await message.reply_text(
            "❌ <b>Database Channel Not Configured!</b>\n\n"
            "Please set up database channel first.",
            quote=True
        )
        return
    
    # Forward to channel
    try:
        forwarded = await message.forward(bot.db_channel.id)
        
        # Generate link
        converted_id = forwarded.id * abs(bot.db_channel.id)
        link_string = f"get-{converted_id}"
        encoded = await encode(link_string)
        link = f"https://t.me/{bot.username}?start={encoded}"
        
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
        link = f"https://t.me/{bot.username}?start={encoded}"
        
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
