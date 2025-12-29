"""
Custom Batch Command - Store Multiple Random Messages
For non-sequential messages (moderators only)
"""

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from bot import bot
from config import ADMINS
from utils.helpers import encode

@bot.on_message(filters.private & filters.user(ADMINS) & filters.command("custom_batch"))
async def custom_batch_command(client: Client, message: Message):
    """Generate custom batch link for random messages"""
    
    if not hasattr(bot, 'db_channel'):
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
            if user_msg.forward_from_chat and user_msg.forward_from_chat.id == bot.db_channel.id:
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
        channel_id = abs(bot.db_channel.id)
        
        # Convert all IDs
        converted_ids = [str(msg_id * channel_id) for msg_id in message_ids]
        
        # Create link string: custombatch-id1-id2-id3...
        link_string = f"custombatch-{'-'.join(converted_ids)}"
        encoded = await encode(link_string)
        link = f"https://t.me/{bot.username}?start={encoded}"
        
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
