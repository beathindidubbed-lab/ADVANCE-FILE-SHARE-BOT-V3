"""
Callback Query Handlers - Button Interactions
"""

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from bot import bot
from config import *

@bot.on_callback_query(filters.regex("^help$"))
async def help_callback(client: Client, query: CallbackQuery):
    """Show help menu"""
    
    # Format help text
    help_text = HELP_TEXT.format(
        bot_name=bot.first_name,
        username=bot.username
    )
    
    # Create buttons
    buttons = []
    
    if SUPPORT_CHAT:
        buttons.append([
            InlineKeyboardButton("💬 Support Chat Group", url=f"https://t.me/{SUPPORT_CHAT.replace('@', '')}")
        ])
    
    if UPDATES_CHANNEL:
        buttons.append([
            InlineKeyboardButton("📢 Updates Channel", url=f"https://t.me/{UPDATES_CHANNEL.replace('@', '')}")
        ])
    
    buttons.append([
        InlineKeyboardButton("🏠 Home", callback_data="start"),
        InlineKeyboardButton("🔒 Close", callback_data="close")
    ])
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    try:
        await query.message.edit_text(
            text=help_text,
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
    except:
        await query.answer("❌ Error loading help menu!", show_alert=True)


@bot.on_callback_query(filters.regex("^about$"))
async def about_callback(client: Client, query: CallbackQuery):
    """Show about menu"""
    
    # Format about text
    about_text = ABOUT_TEXT.format(
        bot_name=bot.first_name,
        username=bot.username
    )
    
    # Create buttons
    buttons = []
    
    if SUPPORT_CHAT:
        buttons.append([
            InlineKeyboardButton("💬 Support", url=f"https://t.me/{SUPPORT_CHAT.replace('@', '')}")
        ])
    
    if UPDATES_CHANNEL:
        buttons.append([
            InlineKeyboardButton("📢 Updates", url=f"https://t.me/{UPDATES_CHANNEL.replace('@', '')}")
        ])
    
    buttons.append([
        InlineKeyboardButton("🏠 Home", callback_data="start"),
        InlineKeyboardButton("🔒 Close", callback_data="close")
    ])
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    try:
        await query.message.edit_text(
            text=about_text,
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
    except:
        await query.answer("❌ Error loading about menu!", show_alert=True)


@bot.on_callback_query(filters.regex("^start$"))
async def start_callback(client: Client, query: CallbackQuery):
    """Go back to start menu"""
    
    # Format welcome text
    welcome_text = WELCOME_TEXT.format(
        first=query.from_user.first_name,
        last=query.from_user.last_name or "",
        username=f"@{query.from_user.username}" if query.from_user.username else "None",
        mention=query.from_user.mention,
        id=query.from_user.id
    )
    
    # Create buttons
    buttons = [
        [
            InlineKeyboardButton("📚 Help", callback_data="help"),
            InlineKeyboardButton("ℹ️ About", callback_data="about")
        ]
    ]
    
    if UPDATES_CHANNEL:
        buttons.append([
            InlineKeyboardButton("📢 Updates", url=f"https://t.me/{UPDATES_CHANNEL.replace('@', '')}")
        ])
    
    if SUPPORT_CHAT:
        buttons.append([
            InlineKeyboardButton("💬 Support", url=f"https://t.me/{SUPPORT_CHAT.replace('@', '')}")
        ])
    
    buttons.append([
        InlineKeyboardButton("🔒 Close", callback_data="close")
    ])
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    try:
        await query.message.edit_text(
            text=welcome_text,
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
    except:
        await query.answer("❌ Error!", show_alert=True)


@bot.on_callback_query(filters.regex("^close$"))
async def close_callback(client: Client, query: CallbackQuery):
    """Close the message"""
    
    try:
        await query.message.delete()
    except:
        await query.answer("❌ Cannot delete this message!", show_alert=True)
