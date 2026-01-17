"""
Settings Handlers
================

All settings-related commands and panels:
- /settings - Main settings panel
- /files - File settings
- /auto_del - Auto-delete settings (3 features)
- /botsettings - Bot message settings
- /forcesub - Force subscribe settings

Features THREE AUTO-DELETE SYSTEM:
1. Clean Conversation - Delete previous bot message
2. Auto Delete Files - Delete files after timer
3. Show Instruction - Show resend button after deletion
"""

import logging
from pyrogram import filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import Config
from utils.helpers import get_random_pic

logger = logging.getLogger(__name__)

# Time options for auto-delete (in seconds)
AUTO_DELETE_TIMES = [60, 300, 600, 1800, 3600]  # 1min, 5min, 10min, 30min, 1hour


def format_time(seconds: int) -> str:
    """Format seconds to human readable time"""
    if seconds < 60:
        return f"{seconds} second{'s' if seconds != 1 else ''}"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''}"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''}"
    else:
        days = seconds // 86400
        return f"{days} day{'s' if days != 1 else ''}"


def create_files_settings_text(protect_content: bool, hide_caption: bool, channel_button: bool) -> str:
    """Create files settings text with blockquote support"""
    protect_status = "ᴇɴᴀʙʟᴇᴅ ✅" if protect_content else "ᴅɪsᴀʙʟᴇᴅ ❌"
    hide_status = "ᴇɴᴀʙʟᴇᴅ ✅" if hide_caption else "ᴅɪsᴀʙʟᴇᴅ ❌"
    button_status = "ᴇɴᴀʙʟᴇᴅ ✅" if channel_button else "ᴅɪsᴀʙʟᴇᴅ ❌"
    
    return (
        "<b>📁 𝗙𝗜𝗟𝗘𝗦 𝗥𝗘𝗟𝗔𝗧𝗘𝗗 𝗦𝗘𝗧𝗧𝗜𝗡𝗚𝗦</b>\n\n"
        f"<blockquote>"
        f"<b>🔒 ᴘʀᴏᴛᴇᴄᴛ ᴄᴏɴᴛᴇɴᴛ:</b> {protect_status}\n"
        f"<b>🫥 ʜɪᴅᴇ ᴄᴀᴘᴛɪᴏɴ:</b> {hide_status}\n"
        f"<b>📘 ᴄʜᴀɴɴᴇʟ ʙᴜᴛᴛᴏɴ:</b> {button_status}"
        f"</blockquote>\n\n"
        "<b>ᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴs ᴛᴏ ᴄʜᴀɴɢᴇ sᴇᴛᴛɪɴɢs</b>"
    )


def create_auto_delete_text(auto_delete: bool, auto_delete_time: int, clean_conv: bool, show_inst: bool) -> str:
    """Create auto delete settings text showing THREE separate features"""
    file_delete_status = "ᴇɴᴀʙʟᴇᴅ ✅" if auto_delete else "ᴅɪsᴀʙʟᴇᴅ ❌"
    time_text = format_time(auto_delete_time)
    clean_status = "ᴇɴᴀʙʟᴇᴅ ✅" if clean_conv else "ᴅɪsᴀʙʟᴇᴅ ❌"
    inst_status = "ᴇɴᴀʙʟᴇᴅ ✅" if show_inst else "ᴅɪsᴀʙʟᴇᴅ ❌"
    
    settings_content = (
        f"<b>🗑️ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ғɪʟᴇs:</b> {file_delete_status}\n"
        f"<b>⏱️ ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇʀ:</b> {time_text}\n"
        f"<b>💬 ᴄʟᴇᴀɴ ᴄᴏɴᴠᴇʀsᴀᴛɪᴏɴ:</b> {clean_status}\n"
        f"<b>📝 sʜᴏᴡ ɪɴsᴛʀᴜᴄᴛɪᴏɴ:</b> {inst_status}"
    )
    
    return (
        "<b>🤖 𝗔𝗨𝗧𝗢 𝗗𝗘𝗟𝗘𝗧𝗘 𝗦𝗘𝗧𝗧𝗜𝗡𝗚𝗦 ⚙️</b>\n\n"
        f"<blockquote>{settings_content}</blockquote>\n"
        "<b>ᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴs ᴛᴏ ᴄʜᴀɴɢᴇ sᴇᴛᴛɪɴɢs</b>"
    )


# ==========================================
# SETTINGS COMMANDS
# ==========================================

async def settings_command(bot, message: Message):
    """
    Handle /settings command - Main settings panel
    
    Shows overview of all settings with navigation to specific panels
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
    protect_content = settings.get("protect_content", True)
    auto_delete = settings.get("auto_delete", False)
    clean_conversation = settings.get("clean_conversation", True)
    request_fsub = settings.get("request_fsub", False)

    # Get settings picture
    welcome_pics = settings.get("welcome_pics", Config.WELCOME_PICS)
    settings_pic = get_random_pic(welcome_pics)

    # Format settings text
    settings_text = (
        "⚙️ <b>BOT SETTINGS PANEL</b>\n\n"
        "<blockquote>"
        f"🔒 <b>Protect Content:</b> {'✅' if protect_content else '❌'}\n"
        f"🗑️ <b>Auto Delete Files:</b> {'✅' if auto_delete else '❌'}\n"
        f"💬 <b>Clean Conversation:</b> {'✅' if clean_conversation else '❌'}\n"
        f"📢 <b>Force Subscribe:</b> {'✅' if request_fsub else '❌'}"
        "</blockquote>\n\n"
        "<b>Select a category to configure:</b>"
    )

    # Create button grid
    buttons = [
        [
            InlineKeyboardButton("📁 ғɪʟᴇs", callback_data="files_settings"),
            InlineKeyboardButton("🗑️ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ", callback_data="auto_delete_settings")
        ],
        [
            InlineKeyboardButton("📢 ғᴏʀᴄᴇ sᴜʙ", callback_data="force_sub_settings"),
            InlineKeyboardButton("💬 ʙᴏᴛ ᴍsɢs", callback_data="bot_msg_settings")
        ],
        [
            InlineKeyboardButton("📊 sᴛᴀᴛɪsᴛɪᴄs", callback_data="stats_menu"),
            InlineKeyboardButton("👥 ᴜsᴇʀs", callback_data="users_menu")
        ],
        [
            InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="start_menu"),
            InlineKeyboardButton("❌ ᴄʟᴏsᴇ", callback_data="close")
        ]
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    try:
        response = await message.reply_photo(
            photo=settings_pic,
            caption=settings_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"Error sending settings photo: {e}")
        response = await message.reply(
            settings_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )

    # FEATURE 1: Store for clean conversation
    await bot.store_bot_message(user_id, response.id)


async def files_command(bot, message: Message):
    """
    Handle /files command - File protection settings
    
    Configure:
    - Protect Content (prevent forward/save)
    - Hide Caption
    - Channel Button
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
    protect_content = settings.get("protect_content", True)
    hide_caption = settings.get("hide_caption", False)
    channel_button = settings.get("channel_button", True)
    files_pics = settings.get("files_pics", Config.FILES_PICS)

    # Get random files picture
    files_pic = get_random_pic(files_pics)

    # Create files settings text
    files_text = create_files_settings_text(protect_content, hide_caption, channel_button)
    
    # Create toggle buttons
    buttons = [
        [
            InlineKeyboardButton(f"🔒 ᴘʀᴏᴛᴇᴄᴛ: {'✅' if protect_content else '❌'}", callback_data="toggle_protect_content"),
            InlineKeyboardButton(f"🫥 ʜɪᴅᴇ: {'✅' if hide_caption else '❌'}", callback_data="toggle_hide_caption")
        ],
        [
            InlineKeyboardButton(f"📘 ʙᴜᴛᴛᴏɴ: {'✅' if channel_button else '❌'}", callback_data="toggle_channel_button"),
            InlineKeyboardButton("📘 ᴄᴜsᴛᴏᴍ ʙᴜᴛᴛᴏɴ", callback_data="custom_buttons_menu")
        ],
        [
            InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings_menu"),
            InlineKeyboardButton("❌ ᴄʟᴏsᴇ", callback_data="close")
        ]
    ]
    
    keyboard = InlineKeyboardMarkup(buttons)
    
    try:
        response = await message.reply_photo(
            photo=files_pic,
            caption=files_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"Error sending files photo: {e}")
        response = await message.reply(
            files_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
    
    await bot.store_bot_message(user_id, response.id)


async def auto_del_command(bot, message: Message):
    """
    Handle /auto_del command - THREE AUTO-DELETE FEATURES
    
    Features:
    1. Clean Conversation - Delete previous bot message
    2. Auto Delete Files - Delete files after timer
    3. Show Instruction - Show resend button after deletion
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

    # Get current settings for ALL THREE FEATURES
    auto_delete = settings.get("auto_delete", False)
    auto_delete_time = settings.get("auto_delete_time", 300)
    clean_conversation = settings.get("clean_conversation", True)
    show_instruction = settings.get("show_instruction", True)
    auto_del_pics = settings.get("auto_del_pics", Config.AUTO_DEL_PICS)

    # Get random auto delete picture
    auto_del_pic = get_random_pic(auto_del_pics)

    # Create auto delete text (shows all 3 features)
    auto_del_text = create_auto_delete_text(
        auto_delete, 
        auto_delete_time, 
        clean_conversation, 
        show_instruction
    )
    
    buttons = []

    # Toggle buttons for each feature
    buttons.append([
        InlineKeyboardButton(f"🗑️ ғɪʟᴇs: {'✅' if auto_delete else '❌'}", callback_data="toggle_auto_delete"),
        InlineKeyboardButton(f"💬 ᴄʟᴇᴀɴ: {'✅' if clean_conversation else '❌'}", callback_data="toggle_clean_conversation")
    ])
    
    buttons.append([
        InlineKeyboardButton(f"📝 ɪɴsᴛʀᴜᴄᴛ: {'✅' if show_instruction else '❌'}", callback_data="toggle_show_instruction"),
        InlineKeyboardButton("⏱️ sᴇᴛ ᴛɪᴍᴇʀ", callback_data="set_timer")
    ])

    # Time buttons (only show if auto delete files is enabled)
    if auto_delete:
        time_row1 = []
        time_row2 = []
        
        for i, time_sec in enumerate(AUTO_DELETE_TIMES):
            time_display = format_time(time_sec)
            btn = InlineKeyboardButton(
                f"{'✅ ' if time_sec == auto_delete_time else ''}{time_display}", 
                callback_data=f"autodel_{time_sec}"
            )
            if i < 3:
                time_row1.append(btn)
            else:
                time_row2.append(btn)
        
        if time_row1:
            buttons.append(time_row1)
        if time_row2:
            buttons.append(time_row2)
    
    buttons.append([
        InlineKeyboardButton("🔄 ʀᴇғʀᴇsʜ", callback_data="refresh_autodel"),
        InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings_menu")
    ])
    
    buttons.append([
        InlineKeyboardButton("❌ ᴄʟᴏsᴇ", callback_data="close")
    ])
    
    keyboard = InlineKeyboardMarkup(buttons)
    
    try:
        response = await message.reply_photo(
            photo=auto_del_pic,
            caption=auto_del_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"Error sending auto delete photo: {e}")
        response = await message.reply(
            auto_del_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
    
    await bot.store_bot_message(user_id, response.id)


async def botsettings_command(bot, message: Message):
    """
    Handle /botsettings command - Bot message behavior settings
    
    Configure:
    - Clean Conversation (Feature 1)
    - Show Instruction (Feature 3)
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
    clean_conversation = settings.get("clean_conversation", True)
    show_instruction = settings.get("show_instruction", True)
    welcome_pics = settings.get("welcome_pics", Config.WELCOME_PICS)
    
    # Get random picture
    settings_pic = get_random_pic(welcome_pics)
    
    settings_text = (
        "<b>🤖 BOT MESSAGE SETTINGS</b>\n\n"
        "<blockquote>"
        f"<b>💬 Clean Conversation:</b> {'✅ ENABLED' if clean_conversation else '❌ DISABLED'}\n"
        f"<b>📝 Show Instruction:</b> {'✅ ENABLED' if show_instruction else '❌ DISABLED'}"
        "</blockquote>\n\n"
        "<b>Feature Explanation:</b>\n"
        "<blockquote expandable>"
        "<b>Clean Conversation:</b>\n"
        "Deletes previous bot message when sending new one. Keeps PM clean.\n\n"
        "<b>Show Instruction:</b>\n"
        "After files are deleted, shows instruction message with resend button. This message is NOT auto-deleted."
        "</blockquote>"
    )
    
    buttons = [
        [
            InlineKeyboardButton(f"💬 {'✅' if clean_conversation else '❌'}", callback_data="toggle_clean_conversation"),
            InlineKeyboardButton(f"📝 {'✅' if show_instruction else '❌'}", callback_data="toggle_show_instruction")
        ],
        [
            InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings_menu"),
            InlineKeyboardButton("❌ ᴄʟᴏsᴇ", callback_data="close")
        ]
    ]
    
    keyboard = InlineKeyboardMarkup(buttons)
    
    try:
        response = await message.reply_photo(
            photo=settings_pic,
            caption=settings_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"Error sending bot settings photo: {e}")
        response = await message.reply(
            settings_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
    
    await bot.store_bot_message(user_id, response.id)


# ==========================================
# HANDLER REGISTRATION
# ==========================================

def register_settings_handlers(bot):
    """Register all settings command handlers"""
    
    @bot.on_message(filters.command("settings") & filters.private)
    async def settings_handler(client, message):
        await settings_command(bot, message)
    
    @bot.on_message(filters.command("files") & filters.private)
    async def files_handler(client, message):
        await files_command(bot, message)
    
    @bot.on_message(filters.command("auto_del") & filters.private)
    async def auto_del_handler(client, message):
        await auto_del_command(bot, message)
    
    @bot.on_message(filters.command("botsettings") & filters.private)
    async def botsettings_handler(client, message):
        await botsettings_command(bot, message)
    
    logger.info("✓ Settings handlers registered")
