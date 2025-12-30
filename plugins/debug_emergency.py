"""
EMERGENCY DEBUG - Catches ALL messages and shows what's happening
"""

from pyrogram import Client, filters
from pyrogram.types import Message

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
