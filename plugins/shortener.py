"""
Shortener Command - Shorten Any Shareable Links
Uses URL shortener API (moderators only)
"""

import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message

#from bot import bot
from config import ADMINS

# Popular URL shortener APIs (choose one or add your own)
SHORTENER_API = "https://ulvis.net/api.php"  # Free, no API key needed
# Other options:
# "https://tinyurl.com/api-create.php"
# "https://is.gd/create.php?format=simple"
# "https://v.gd/create.php?format=simple"

@Client.on_message(filters.private & filters.user(ADMINS) & filters.command("shortener"))
async def shortener_command(client: Client, message: Message):
    """Shorten any URL"""
    
    # Check if URL provided
    if len(message.command) < 2:
        await message.reply_text(
            "🔗 <b>URL SHORTENER</b>\n\n"
            "<b>Usage:</b> <code>/shortener [URL]</code>\n\n"
            "<b>Example:</b>\n"
            "<code>/shortener https://t.me/YourBot?start=ABC123XYZ</code>\n\n"
            "Or reply to a message containing a URL with /shortener",
            quote=True
        )
        return
    
    # Get URL
    if len(message.command) >= 2:
        url = message.command[1]
    elif message.reply_to_message and message.reply_to_message.text:
        url = message.reply_to_message.text.strip()
    else:
        await message.reply_text("❌ Please provide a URL!", quote=True)
        return
    
    # Validate URL
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Show loading
    status_msg = await message.reply_text("⏳ <b>Shortening URL...</b>", quote=True)
    
    # Shorten URL
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{SHORTENER_API}?url={url}") as response:
                if response.status == 200:
                    short_url = await response.text()
                    short_url = short_url.strip()
                    
                    # Create reply
                    reply_text = f"""
✅ <b>URL Shortened Successfully!</b>

<b>🔗 Original URL:</b>
<code>{url}</code>

<b>✂️ Short URL:</b>
<code>{short_url}</code>

<b>💡 Share the short URL with users!</b>
"""
                    
                    await status_msg.edit_text(reply_text)
                else:
                    await status_msg.edit_text(
                        f"❌ <b>Error!</b> Status: {response.status}\n\n"
                        "Try another URL shortener or check your link."
                    )
    
    except Exception as e:
        await status_msg.edit_text(
            f"❌ <b>Error Shortening URL!</b>\n\n<code>{str(e)}</code>\n\n"
            "Try again or use a different URL shortener."
        )


@Client.on_message(filters.private & filters.user(ADMINS) & filters.command("shortener_settings"))
async def shortener_settings(client: Client, message: Message):
    """Configure URL shortener"""
    
    await message.reply_text(
        "⚙️ <b>SHORTENER SETTINGS</b>\n\n"
        "<b>Current Shortener:</b> ulvis.net\n\n"
        "<b>Available Shorteners:</b>\n"
        "• ulvis.net (current)\n"
        "• tinyurl.com\n"
        "• is.gd\n"
        "• v.gd\n\n"
        "<b>To change:</b> Edit <code>plugins/shortener.py</code>\n"
        "Update SHORTENER_API variable\n\n"
        "<b>Custom API:</b> You can add your own API like:\n"
        "• bit.ly (needs API key)\n"
        "• short.io (needs API key)\n"
        "• rebrandly.com (needs API key)",
        quote=True
    )
