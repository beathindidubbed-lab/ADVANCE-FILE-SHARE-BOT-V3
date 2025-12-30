"""
Start Command - GUARANTEED TO WORK!
Simple and direct response
"""

import random
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from config import *

@Client.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    """Start command - responds to every /start"""
    
    # Simple welcome text
    text = f"""
👋 <b>Hello {message.from_user.first_name}!</b>

I'm <b>{client.first_name}</b> - Your File Sharing Bot!

✅ <b>I'm Online and Ready!</b>

<b>Bot:</b> @{client.username}
<b>Status:</b> 🟢 Active
"""
    
    # Simple buttons
    buttons = [
        [
            InlineKeyboardButton("📚 Help", callback_data="help"),
            InlineKeyboardButton("ℹ️ About", callback_data="about")
        ]
    ]
    
    if SUPPORT_CHAT:
        buttons.append([
            InlineKeyboardButton("💬 Support", url=f"https://t.me/{SUPPORT_CHAT.replace('@', '')}")
        ])
    
    if UPDATES_CHANNEL:
        buttons.append([
            InlineKeyboardButton("📢 Updates", url=f"https://t.me/{UPDATES_CHANNEL.replace('@', '')}")
        ])
    
    buttons.append([
        InlineKeyboardButton("🔒 Close", callback_data="close")
    ])
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    # Try to send with photo first
    if BOT_PICS:
        try:
            pic = random.choice(BOT_PICS)
            await message.reply_photo(
                photo=pic,
                caption=text,
                reply_markup=reply_markup,
                quote=True
            )
            return
        except:
            pass
    
    # Fallback to text
    await message.reply_text(
        text=text,
        reply_markup=reply_markup,
        quote=True
    )


@Client.on_message(filters.command("help") & filters.private)
async def help_command(client: Client, message: Message):
    """Help command"""
    
    text = f"""
📚 <b>HELP MENU</b>

<b>I'm a file sharing bot!</b>

<b>How to use:</b>
1. Admin forwards files to me
2. I generate shareable links
3. Users click links to get files

<b>For more help:</b>
Contact support group below
"""
    
    buttons = [[InlineKeyboardButton("🔒 Close", callback_data="close")]]
    
    if SUPPORT_CHAT:
        buttons.insert(0, [InlineKeyboardButton("💬 Support", url=f"https://t.me/{SUPPORT_CHAT.replace('@', '')}")])
    
    await message.reply_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(buttons),
        quote=True
    )


@Client.on_message(filters.command("about") & filters.private)
async def about_command(client: Client, message: Message):
    """About command"""
    
    text = f"""
ℹ️ <b>ABOUT BOT</b>

<b>◈ Bot Name:</b> {client.first_name}
<b>◈ Username:</b> @{client.username}
<b>◈ Framework:</b> Pyrogram
<b>◈ Language:</b> Python 3
<b>◈ Version:</b> V3.0

<b>Made with ❤️</b>
"""
    
    buttons = [[InlineKeyboardButton("🔒 Close", callback_data="close")]]
    
    await message.reply_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(buttons),
        quote=True
    )
