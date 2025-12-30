"""
Test Plugin - Check if plugins are working
"""

from pyrogram import Client, filters
from pyrogram.types import Message

@Client.on_message(filters.command("test") & filters.private)
async def test_command(client: Client, message: Message):
    """Test if bot is responding"""
    await message.reply_text(
        "✅ <b>Bot is working!</b>\n\n"
        f"<b>Bot:</b> @{client.username}\n"
        f"<b>User:</b> {message.from_user.mention}\n"
        f"<b>User ID:</b> <code>{message.from_user.id}</code>",
        quote=True
    )

@Client.on_message(filters.command("ping") & filters.private)
async def ping_command(client: Client, message: Message):
    """Check bot response time"""
    await message.reply_text("🏓 Pong!", quote=True)
