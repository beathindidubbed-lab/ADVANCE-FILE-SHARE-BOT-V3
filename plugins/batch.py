"""
Batch Command - Generate Batch Links
Upload multiple files at once
"""

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from bot import bot
from config import ADMINS
from utils.helpers import encode

@bot.on_message(filters.private & filters.user(ADMINS) & filters.command("batch"))
async def batch_command(client: Client, message: Message):
    """Generate batch link"""
    
    if not hasattr(bot, 'db_channel'):
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
    
    if not first_msg.forward_from_chat or first_msg.forward_from_chat.id != bot.db_channel.id:
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
    
    if not last_msg.forward_from_chat or last_msg.forward_from_chat.id != bot.db_channel.id:
        await message.reply_text(
            "❌ <b>Invalid Message!</b>\n\n"
            "Please forward message from database channel.",
            quote=True
        )
        return
    
    last_id = last_msg.forward_from_message_id
    
    # Generate batch link
    try:
        channel_id = abs(bot.db_channel.id)
        converted_first = first_id * channel_id
        converted_last = last_id * channel_id
        
        link_string = f"get-{converted_first}-{converted_last}"
        encoded = await encode(link_string)
        link = f"https://t.me/{bot.username}?start={encoded}"
        
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
