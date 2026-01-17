"""
Force Subscribe Handlers
========================

All force subscribe management commands:
- /forcesub - Main force subscribe panel
- /req_fsub - Request FSub toggle
- /fsub_chnl - Manage FSub channels
- /add_fsub - Add force subscribe channel
- /del_fsub - Remove force subscribe channel
- test_fsub - Test user subscription status

Features:
- Multiple channel support
- Auto-invite link generation for private channels
- Request FSub mode (optional FSub)
- Channel subscription verification
"""

import logging
from pyrogram import filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import Config
from utils.helpers import get_random_pic, is_subscribed

logger = logging.getLogger(__name__)


# ==========================================
# FORCE SUBSCRIBE COMMANDS
# ==========================================

async def forcesub_command(bot, message: Message):
    """
    Handle /forcesub command - Main force subscribe panel
    
    Shows:
    - Request FSub status (optional vs required)
    - List of configured channels
    - Management buttons
    """
    user_id = message.from_user.id
    
    # Check admin permission
    if not await bot.is_user_admin(user_id):
        response = await message.reply("❌ <b>Admin only!</b>", parse_mode=enums.ParseMode.HTML)
        await bot.store_bot_message(user_id, response.id)
        return

    # FEATURE 1: Delete previous bot message
    settings = await bot.db.get_settings()
    if settings.get("clean_conversation", True):
        await bot.delete_previous_bot_message(user_id)

    # Get current force sub channels
    force_sub_channels = await bot.db.get_force_sub_channels()
    
    # Get force sub pictures
    force_sub_pics = settings.get("force_sub_pics", Config.FORCE_SUB_PICS)
    force_sub_pic = get_random_pic(force_sub_pics)
    
    # Check request_fsub setting
    request_fsub = settings.get("request_fsub", False)
    request_status = "✅ ENABLED" if request_fsub else "❌ DISABLED"
    
    # Format message
    if force_sub_channels:
        channels_text = "<b>📢 FORCE SUBSCRIBE SETTINGS</b>\n\n"
        channels_text += f"🔄 <b>Request FSub:</b> {request_status}\n\n"
        channels_text += "<b>Current Channels:</b>\n<blockquote>"
        
        for i, channel in enumerate(force_sub_channels, 1):
            channel_id = channel.get("channel_id")
            username = channel.get("channel_username", "No username")
            
            channels_text += f"{i}. <b>ID:</b> <code>{channel_id}</code>\n"
            channels_text += f"   <b>@{username}</b>\n\n"
        
        channels_text += f"</blockquote>\n📊 <b>Total:</b> {len(force_sub_channels)} channels"
    else:
        channels_text = "<b>📢 FORCE SUBSCRIBE SETTINGS</b>\n\n"
        channels_text += f"🔄 <b>Request FSub:</b> {request_status}\n\n"
        channels_text += "<blockquote>"
        channels_text += "No force subscribe channels configured.\n"
        channels_text += "Use /add_fsub to add channels."
        channels_text += "</blockquote>"
    
    # Create buttons
    buttons = []
    
    # Toggle Request FSub
    if request_fsub:
        buttons.append([
            InlineKeyboardButton("❌ DISABLE FSUB", callback_data="reqfsub_off"),
            InlineKeyboardButton("⚙️ CHANNELS", callback_data="fsub_chnl_menu")
        ])
    else:
        buttons.append([
            InlineKeyboardButton("✅ ENABLE FSUB", callback_data="reqfsub_on"),
            InlineKeyboardButton("⚙️ CHANNELS", callback_data="fsub_chnl_menu")
        ])
    
    # Management buttons
    buttons.append([
        InlineKeyboardButton("➕ ADD CHANNEL", callback_data="add_fsub_menu"),
        InlineKeyboardButton("➖ REMOVE CHANNEL", callback_data="del_fsub_menu")
    ])
    
    buttons.append([
        InlineKeyboardButton("🔄 REFRESH", callback_data="refresh_fsub"),
        InlineKeyboardButton("📊 TEST", callback_data="test_fsub")
    ])
    
    buttons.append([
        InlineKeyboardButton("🔙 BACK", callback_data="settings_menu"),
        InlineKeyboardButton("❌ CLOSE", callback_data="close")
    ])
    
    keyboard = InlineKeyboardMarkup(buttons)
    
    try:
        response = await message.reply_photo(
            photo=force_sub_pic,
            caption=channels_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"Error sending forcesub photo: {e}")
        response = await message.reply(
            channels_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
    
    await bot.store_bot_message(user_id, response.id)


async def req_fsub_command(bot, message: Message):
    """
    Handle /req_fsub command - Request FSub toggle
    
    Request FSub = Optional force subscribe
    When enabled, users MUST join all channels before using bot
    """
    user_id = message.from_user.id
    
    # Check admin permission
    if not await bot.is_user_admin(user_id):
        response = await message.reply("❌ <b>Admin only!</b>", parse_mode=enums.ParseMode.HTML)
        await bot.store_bot_message(user_id, response.id)
        return

    # FEATURE 1: Delete previous bot message
    settings = await bot.db.get_settings()
    if settings.get("clean_conversation", True):
        await bot.delete_previous_bot_message(user_id)

    # Get current settings
    request_fsub = settings.get("request_fsub", False)
    force_sub_pics = settings.get("force_sub_pics", Config.FORCE_SUB_PICS)
    
    # Get random force sub picture
    force_sub_pic = get_random_pic(force_sub_pics)
    
    # Format
    status = "✅ ENABLED" if request_fsub else "❌ DISABLED"
    
    req_fsub_text = (
        "<b>📢 REQUEST FSUB SETTINGS</b>\n\n"
        f"<blockquote>"
        f"<b>Status:</b> {status}\n\n"
        f"<i>When enabled, users must join all force subscribe channels before using the bot.</i>"
        f"</blockquote>"
    )
    
    # Create toggle buttons
    buttons = []
    
    if request_fsub:
        buttons.append([
            InlineKeyboardButton("❌ DISABLE", callback_data="reqfsub_off"),
            InlineKeyboardButton("⚙️ CHANNELS", callback_data="fsub_chnl_menu")
        ])
    else:
        buttons.append([
            InlineKeyboardButton("✅ ENABLE", callback_data="reqfsub_on"),
            InlineKeyboardButton("⚙️ CHANNELS", callback_data="fsub_chnl_menu")
        ])
    
    buttons.append([
        InlineKeyboardButton("🔙 BACK", callback_data="settings_menu"),
        InlineKeyboardButton("❌ CLOSE", callback_data="close")
    ])
    
    keyboard = InlineKeyboardMarkup(buttons)
    
    try:
        response = await message.reply_photo(
            photo=force_sub_pic,
            caption=req_fsub_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"Error sending force sub photo: {e}")
        response = await message.reply(
            req_fsub_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
    
    await bot.store_bot_message(user_id, response.id)


async def fsub_chnl_command(bot, message: Message):
    """
    Handle /fsub_chnl command - Manage FSub channels
    
    Shows list of all force subscribe channels with management options
    """
    user_id = message.from_user.id
    
    # Check admin permission
    if not await bot.is_user_admin(user_id):
        response = await message.reply("❌ <b>Admin only!</b>", parse_mode=enums.ParseMode.HTML)
        await bot.store_bot_message(user_id, response.id)
        return

    # FEATURE 1: Delete previous bot message
    settings = await bot.db.get_settings()
    if settings.get("clean_conversation", True):
        await bot.delete_previous_bot_message(user_id)

    # Get force sub channels
    force_sub_channels = await bot.db.get_force_sub_channels()
    
    # Get force sub pictures
    force_sub_pics = settings.get("force_sub_pics", Config.FORCE_SUB_PICS)
    force_sub_pic = get_random_pic(force_sub_pics)
    
    # Format message
    if force_sub_channels:
        channels_text = "<b>📢 FORCE SUBSCRIBE CHANNELS</b>\n\n"
        channels_text += "<blockquote>"
        
        for i, channel in enumerate(force_sub_channels, 1):
            channel_id = channel.get("channel_id")
            username = channel.get("channel_username", "No username")
            
            channels_text += f"<b>{i}. Channel ID:</b> <code>{channel_id}</code>\n"
            channels_text += f"   <b>Username:</b> @{username}\n\n"
        
        channels_text += f"</blockquote>\n\n"
        channels_text += f"📊 <b>Total Channels:</b> {len(force_sub_channels)}"
    else:
        channels_text = "<b>📢 FORCE SUBSCRIBE CHANNELS</b>\n\n"
        channels_text += "<blockquote>"
        channels_text += "No force subscribe channels configured.\n"
        channels_text += "Use /add_fsub to add channels."
        channels_text += "</blockquote>"
    
    # Create buttons
    buttons = []
    
    if force_sub_channels:
        buttons.append([
            InlineKeyboardButton("➕ ADD CHANNEL", callback_data="add_fsub_menu"),
            InlineKeyboardButton("➖ REMOVE CHANNEL", callback_data="del_fsub_menu")
        ])
    else:
        buttons.append([
            InlineKeyboardButton("➕ ADD CHANNEL", callback_data="add_fsub_menu")
        ])
    
    buttons.append([
        InlineKeyboardButton("🔄 REFRESH", callback_data="refresh_fsub"),
        InlineKeyboardButton("🔙 BACK", callback_data="force_sub_settings")
    ])
    
    buttons.append([
        InlineKeyboardButton("❌ CLOSE", callback_data="close")
    ])
    
    keyboard = InlineKeyboardMarkup(buttons)
    
    try:
        response = await message.reply_photo(
            photo=force_sub_pic,
            caption=channels_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"Error sending fsub channels photo: {e}")
        response = await message.reply(
            channels_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
    
    await bot.store_bot_message(user_id, response.id)


async def add_fsub_command(bot, message: Message):
    """
    Handle /add_fsub command - Add force subscribe channel
    
    Usage: /add_fsub channel_id [username]
    Example: /add_fsub -100123456789 @channel_username
    """
    user_id = message.from_user.id
    
    # Check admin permission
    if not await bot.is_user_admin(user_id):
        response = await message.reply("❌ <b>Admin only!</b>", parse_mode=enums.ParseMode.HTML)
        await bot.store_bot_message(user_id, response.id)
        return

    # FEATURE 1: Delete previous bot message
    settings = await bot.db.get_settings()
    if settings.get("clean_conversation", True):
        await bot.delete_previous_bot_message(user_id)

    if len(message.command) < 2:
        response = await message.reply(
            "➕ <b>ADD FORCE SUB CHANNEL</b>\n\n"
            "<blockquote>"
            "<b>Usage:</b> <code>/add_fsub channel_id [username]</code>\n\n"
            "<b>Examples:</b>\n"
            "<code>/add_fsub -100123456789 @channel_username</code>\n"
            "<code>/add_fsub -100123456789</code>\n\n"
            "<b>Note:</b> Bot must be admin in the channel!"
            "</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
        await bot.store_bot_message(user_id, response.id)
        return

    try:
        channel_id = int(message.command[1])
        username = message.command[2] if len(message.command) > 2 else None
        
        if username:
            username = username.lstrip('@')
        
        # Check if bot is admin in channel
        try:
            me = await bot.get_me()
            await bot.get_chat_member(channel_id, me.id)
        except Exception as e:
            response = await message.reply(
                f"❌ <b>Bot is not admin in channel {channel_id}!</b>\n\n"
                f"<blockquote>Error: {str(e)[:100]}</blockquote>",
                parse_mode=enums.ParseMode.HTML
            )
            await bot.store_bot_message(user_id, response.id)
            return
        
        # Add channel to database
        await bot.db.add_force_sub_channel(channel_id, username)
        
        # Update local cache
        bot.force_sub_channels = await bot.db.get_force_sub_channels()
        
        response = await message.reply(
            f"✅ <b>Channel Added!</b>\n\n"
            f"<blockquote>"
            f"<b>📢 Channel ID:</b> <code>{channel_id}</code>\n"
            f"<b>👤 Username:</b> @{username if username else 'Private'}\n\n"
            f"<b>Total channels:</b> {len(bot.force_sub_channels)}"
            f"</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
        
        await bot.store_bot_message(user_id, response.id)
        
    except ValueError:
        response = await message.reply("❌ <b>Invalid channel ID! Must be a number.</b>", parse_mode=enums.ParseMode.HTML)
        await bot.store_bot_message(user_id, response.id)
    except Exception as e:
        logger.error(f"Error adding force sub channel: {e}")
        response = await message.reply("❌ <b>Error adding channel!</b>", parse_mode=enums.ParseMode.HTML)
        await bot.store_bot_message(user_id, response.id)


async def del_fsub_command(bot, message: Message):
    """
    Handle /del_fsub command - Remove force subscribe channel
    
    Usage: /del_fsub channel_id
    Example: /del_fsub -100123456789
    """
    user_id = message.from_user.id
    
    # Check admin permission
    if not await bot.is_user_admin(user_id):
        response = await message.reply("❌ <b>Admin only!</b>", parse_mode=enums.ParseMode.HTML)
        await bot.store_bot_message(user_id, response.id)
        return

    # FEATURE 1: Delete previous bot message
    settings = await bot.db.get_settings()
    if settings.get("clean_conversation", True):
        await bot.delete_previous_bot_message(user_id)

    if len(message.command) < 2:
        response = await message.reply(
            "➖ <b>REMOVE FORCE SUB CHANNEL</b>\n\n"
            "<blockquote>"
            "<b>Usage:</b> <code>/del_fsub channel_id</code>\n\n"
            "<b>Example:</b> <code>/del_fsub -100123456789</code>"
            "</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
        await bot.store_bot_message(user_id, response.id)
        return

    try:
        channel_id = int(message.command[1])
        
        # Remove channel from database
        await bot.db.remove_force_sub_channel(channel_id)
        
        # Update local cache
        bot.force_sub_channels = await bot.db.get_force_sub_channels()
        
        response = await message.reply(
            f"✅ <b>Channel Removed!</b>\n\n"
            f"<blockquote>"
            f"<b>📢 Channel ID:</b> <code>{channel_id}</code>\n\n"
            f"<b>Remaining channels:</b> {len(bot.force_sub_channels)}"
            f"</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
        
        await bot.store_bot_message(user_id, response.id)
        
    except ValueError:
        response = await message.reply("❌ <b>Invalid channel ID!</b>", parse_mode=enums.ParseMode.HTML)
        await bot.store_bot_message(user_id, response.id)
    except Exception as e:
        logger.error(f"Error removing force sub channel: {e}")
        response = await message.reply("❌ <b>Error removing channel!</b>", parse_mode=enums.ParseMode.HTML)
        await bot.store_bot_message(user_id, response.id)


# ==========================================
# HANDLER REGISTRATION
# ==========================================

def register_fsub_handlers(bot):
    """Register all force subscribe command handlers"""
    
    @bot.on_message(filters.command("forcesub") & filters.private)
    async def forcesub_handler(client, message):
        await forcesub_command(bot, message)
    
    @bot.on_message(filters.command("req_fsub") & filters.private)
    async def req_fsub_handler(client, message):
        await req_fsub_command(bot, message)
    
    @bot.on_message(filters.command("fsub_chnl") & filters.private)
    async def fsub_chnl_handler(client, message):
        await fsub_chnl_command(bot, message)
    
    @bot.on_message(filters.command("add_fsub") & filters.private)
    async def add_fsub_handler(client, message):
        await add_fsub_command(bot, message)
    
    @bot.on_message(filters.command("del_fsub") & filters.private)
    async def del_fsub_handler(client, message):
        await del_fsub_command(bot, message)
    
    logger.info("✓ Force subscribe handlers registered")
