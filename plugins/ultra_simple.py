"""
FINAL FIX - Unique handler that CANNOT conflict
"""

from pyrogram import Client, filters
from pyrogram.types import Message

@Client.on_message(filters.private & filters.regex("^/start"))
async def ultra_start_handler(client: Client, message: Message):
    """START - Catches /start with regex"""
    await message.reply_text(
        f"✅ <b>BOT WORKS!</b>\n\n"
        f"Hello {message.from_user.first_name}!\n"
        f"Bot: @{client.username}\n"
        f"Your ID: {message.from_user.id}",
        quote=True
    )

@Client.on_message(filters.private & filters.text)
async def catch_everything(client: Client, message: Message):
    """Catches ALL text messages as backup"""
    
    text = message.text.lower()
    
    if text in ['/start', 'start', 'hi', 'hello', 'hey']:
        await message.reply_text(
            f"👋 Hello {message.from_user.first_name}!\n\n"
            f"✅ Bot is working!\n"
            f"Your ID: <code>{message.from_user.id}</code>",
            quote=True
        )
    elif text in ['/test', 'test']:
        await message.reply_text(
            f"✅ TEST PASSED!\n\n"
            f"Bot is receiving messages!",
            quote=True
        )
    elif text in ['/ping', 'ping']:
        await message.reply_text("🏓 PONG!", quote=True)
