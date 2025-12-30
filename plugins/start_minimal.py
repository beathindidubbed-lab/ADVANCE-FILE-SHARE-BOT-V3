"""
MINIMAL START - NO FILTERS, NO BLOCKS, WORKS FOR EVERYONE
"""

from pyrogram import Client, filters
from pyrogram.types import Message

@Client.on_message(filters.command("start"))
async def start_handler(client: Client, message: Message):
    """Responds to /start - NO RESTRICTIONS"""
    
    await message.reply_text(
        f"✅ <b>BOT IS WORKING!</b>\n\n"
        f"👋 Hello {message.from_user.first_name}!\n\n"
        f"<b>Bot:</b> @{client.username}\n"
        f"<b>Your ID:</b> <code>{message.from_user.id}</code>\n\n"
        f"🟢 <b>I'm online and responding!</b>",
        quote=True
    )


@Client.on_message(filters.command("test"))
async def test_handler(client: Client, message: Message):
    """Test command - NO RESTRICTIONS"""
    
    await message.reply_text(
        f"✅ <b>TEST SUCCESSFUL!</b>\n\n"
        f"Bot is receiving messages!\n"
        f"Your ID: <code>{message.from_user.id}</code>",
        quote=True
    )


@Client.on_message(filters.command("ping"))
async def ping_handler(client: Client, message: Message):
    """Ping command - NO RESTRICTIONS"""
    
    await message.reply_text("🏓 <b>PONG!</b>", quote=True)


@Client.on_message(filters.command("help"))
async def help_handler(client: Client, message: Message):
    """Help command - NO RESTRICTIONS"""
    
    await message.reply_text(
        f"📚 <b>HELP</b>\n\n"
        f"<b>Available Commands:</b>\n"
        f"• /start - Start bot\n"
        f"• /test - Test bot\n"
        f"• /ping - Check status\n"
        f"• /help - This menu",
        quote=True
    )
