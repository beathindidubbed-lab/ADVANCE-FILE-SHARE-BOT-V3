"""
Special Link Command - Create Links with Custom Start Message
Get an editable link with custom message (moderators only)
"""

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

#from bot import bot
from config import ADMINS
from utils.helpers import encode

# Store special links in database
special_links = {}

@Client.on_message(filters.private & filters.user(ADMINS) & filters.command("special_link"))
async def special_link_command(client: Client, message: Message):
    """Generate special link with custom message"""
    
    if not hasattr(bot, 'db_channel'):
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
            
            if user_msg.forward_from_chat and user_msg.forward_from_chat.id == bot.db_channel.id:
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
        channel_id = abs(bot.db_channel.id)
        
        # Encode message IDs
        if len(message_ids) == 1:
            converted = message_ids[0] * channel_id
            link_string = f"get-{converted}"
        else:
            converted_ids = [str(msg_id * channel_id) for msg_id in message_ids]
            link_string = f"custombatch-{'-'.join(converted_ids)}"
        
        encoded = await encode(link_string)
        
        # Store custom message
        if bot.db:
            await bot.db.settings.update_one(
                {"_id": f"special_{encoded}"},
                {"$set": {"message": custom_text}},
                upsert=True
            )
        
        link = f"https://t.me/{bot.username}?start={encoded}"
        
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
    if bot.db:
        special_data = await bot.db.settings.find_one({"_id": f"special_{file_param}"})
        
        if special_data and 'message' in special_data:
            # Show custom message first
            await message.reply_text(
                special_data['message'],
                quote=True
            )
    
    # Continue with normal file sending
    # (This is called from start.py's file handling)
