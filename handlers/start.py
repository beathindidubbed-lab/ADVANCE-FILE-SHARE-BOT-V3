# ============================================================================
# handlers/start.py - Start, Help, About Commands
# ============================================================================
"""
Start Command Handlers
/start, /help, /about, /ping commands
"""

import random
import datetime
from pyrogram import filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import Config, REACTIONS
from utils.helpers import get_random_pic, create_welcome_text, create_help_text

async def start_handler(bot, message: Message):
    """Handle /start command - ALL FEATURES PRESERVED"""
    user_id = message.from_user.id
    chat_id = message.chat.id

    # FEATURE 1: Delete previous bot message (Clean Conversation)
    settings = await bot.db.get_settings()
    if settings.get("clean_conversation", True):
        await bot.auto_delete.delete_previous_bot_message(user_id)

    # Check if user is banned
    if await bot.db.is_user_banned(user_id):
        response = await message.reply(
            "🚫 <b>You are banned from using this bot!</b>",
            parse_mode=enums.ParseMode.HTML
        )
        await bot.auto_delete.store_bot_message(user_id, response.id)
        return

    # Add user to database
    await bot.db.add_user(
        user_id=user_id,
        first_name=message.from_user.first_name,
        username=message.from_user.username
    )

    # Update activity
    await bot.db.update_user_activity(user_id)

    # Send reaction using user account
    try:
        await bot.send_reaction(chat_id, message.id)
    except Exception as e:
        pass

    # Check for start arguments (file links, batch links, etc.)
    if len(message.command) > 1:
        start_arg = message.command[1]
        await handle_start_argument(bot, message, start_arg)
        return

    # Check force subscribe - ONLY if request_fsub is enabled
    request_fsub = settings.get("request_fsub", False)
    
    if request_fsub and bot.force_sub_channels:
        from utils.helpers import is_subscribed
        user_is_subscribed = await is_subscribed(bot, user_id, bot.force_sub_channels)
        if not user_is_subscribed:
            await show_force_subscribe(bot, message)
            return

    # Show welcome message
    await show_welcome_message(bot, message)


async def show_welcome_message(bot, message: Message):
    """Show welcome message with photo and blockquote expandable"""
    user = message.from_user
    user_id = user.id

    # Get settings
    settings = await bot.db.get_settings()
    welcome_text_custom = settings.get("welcome_text", "")
    welcome_pics = settings.get("welcome_pics", Config.WELCOME_PICS)

    # Get random welcome picture
    welcome_pic = get_random_pic(welcome_pics)

    # Create welcome text with blockquote expandable
    if welcome_text_custom:
        try:
            welcome_text = welcome_text_custom.format(
                first=user.first_name,
                last=user.last_name or "",
                username=f"@{user.username}" if user.username else "None",
                mention=f"<a href='tg://user?id={user.id}'>{user.first_name}</a>",
                id=user.id
            )
        except KeyError:
            welcome_text = create_welcome_text(user.first_name, expandable=True)
    else:
        welcome_text = create_welcome_text(user.first_name, expandable=True)

    # Create buttons
    buttons = [
        [
            InlineKeyboardButton("≋ʜᴇʟᴘ", callback_data="help_menu"),
            InlineKeyboardButton("ᴀʙᴏᴜᴛ 📖", callback_data="about_menu")
        ],
        [
            InlineKeyboardButton("ᴄʟᴏsᴇ ✖️", callback_data="close")
        ]
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    try:
        response = await message.reply_photo(
            photo=welcome_pic,
            caption=welcome_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
    except Exception:
        response = await message.reply(
            welcome_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True
        )

    # FEATURE 1: Store this message for future deletion
    await bot.auto_delete.store_bot_message(user_id, response.id)


async def show_force_subscribe(bot, message: Message):
    """Show force subscribe message - ALL FEATURES PRESERVED"""
    user = message.from_user
    user_id = user.id

    settings = await bot.db.get_settings()
    force_sub_pics = settings.get("force_sub_pics", Config.FORCE_SUB_PICS)
    force_sub_pic = get_random_pic(force_sub_pics)

    # Count joined/total channels
    total_channels = len(bot.force_sub_channels)
    joined_count = 0

    from utils.helpers import is_subscribed
    for channel in bot.force_sub_channels:
        try:
            user_is_sub = await is_subscribed(bot, user.id, [channel])
            if user_is_sub:
                joined_count += 1
        except:
            pass

    # Create force sub text
    from utils.helpers import create_force_sub_text
    fsub_text = create_force_sub_text(user.first_name, joined_count, total_channels, expandable=True)

    # Create buttons for each channel
    buttons = []
    for channel in bot.force_sub_channels:
        channel_id = channel.get("channel_id")
        username = channel.get("channel_username")
    
        if username:
            button_text = "ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ"
            button_url = f"https://t.me/{username}"
        else:
            button_text = "ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀɴɴᴇʟ"
            try:
                invite_link = await bot.create_invite_link(channel_id)
                if invite_link:
                    button_url = invite_link
                else:
                    button_url = f"https://t.me/c/{str(channel_id)[4:]}"
            except:
                button_url = f"https://t.me/c/{str(channel_id)[4:]}"
    
        buttons.append([InlineKeyboardButton(button_text, url=button_url)])

    buttons.append([InlineKeyboardButton("🔄 ᴛʀʏ ᴀɢᴀɪɴ", callback_data="check_fsub")])
    buttons.append([InlineKeyboardButton("≋ ʜᴇʟᴘ", callback_data="help_menu")])

    keyboard = InlineKeyboardMarkup(buttons)

    try:
        response = await message.reply_photo(
            photo=force_sub_pic,
            caption=fsub_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
    except Exception:
        response = await message.reply(
            fsub_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )

    await bot.auto_delete.store_bot_message(user_id, response.id)


async def handle_start_argument(bot, message: Message, start_arg: str):
    """Handle start command arguments - ALL FEATURES PRESERVED"""
    try:
        user_id = message.from_user.id
        
        # Check if it's a special link
        if start_arg.startswith("link_"):
            link_id = start_arg.replace("link_", "")
            await handle_special_link(bot, message, link_id)
        # Check if it's a file link
        elif start_arg.startswith("file_"):
            file_id_encoded = start_arg.replace("file_", "")
            await handle_file_link(bot, message, file_id_encoded)
        # Check if it's a batch link
        elif start_arg.startswith("batch_"):
            batch_id = start_arg.replace("batch_", "")
            await handle_batch_link(bot, message, batch_id)
        else:
            # Try to decode as file ID
            try:
                from utils.helpers import decode
                decoded = await decode(start_arg)
                if decoded:
                    await handle_file_link(bot, message, start_arg)
                else:
                    raise ValueError("Invalid link")
            except:
                error_msg = await message.reply("❌ <b>Invalid or expired link!</b>", parse_mode=enums.ParseMode.HTML)
                await bot.auto_delete.store_bot_message(user_id, error_msg.id)
                
    except Exception as e:
        error_msg = await message.reply("❌ <b>Error processing link!</b>", parse_mode=enums.ParseMode.HTML)
        await bot.auto_delete.store_bot_message(message.from_user.id, error_msg.id)


async def handle_special_link(bot, message: Message, link_id: str):
    """Handle special link access - ALL FEATURES PRESERVED"""
    user_id = message.from_user.id
    
    link_data = await bot.db.get_special_link(link_id)
    if not link_data:
        error_msg = await message.reply("❌ <b>Link not found or expired!</b>", parse_mode=enums.ParseMode.HTML)
        await bot.auto_delete.store_bot_message(user_id, error_msg.id)
        return
    
    custom_msg = link_data.get("message")
    if custom_msg:
        msg = await message.reply(custom_msg, parse_mode=enums.ParseMode.HTML)
        await bot.auto_delete.store_bot_message(user_id, msg.id)
    
    files = link_data.get("files", [])
    if files:
        file_ids = []
        sent_message_ids = []
        
        from config import MAX_SPECIAL_FILES
        for file_id in files[:MAX_SPECIAL_FILES]:
            try:
                response = await bot.copy_message(
                    chat_id=message.chat.id,
                    from_chat_id=bot.db_channel,
                    message_id=file_id,
                    protect_content=bot.settings.get("protect_content", True)
                )
                file_ids.append(file_id)
                sent_message_ids.append(response.id)
                
                # FEATURE 2: Schedule file for auto-deletion
                settings = await bot.db.get_settings()
                auto_delete = settings.get("auto_delete", False)
                if auto_delete:
                    delete_time = settings.get("auto_delete_time", 300)
                    await bot.auto_delete.schedule_file_deletion(user_id, response.id, delete_time)
                
            except Exception:
                pass
        
        if file_ids:
            await bot.auto_delete.track_user_files(user_id, file_ids, link_data)
        
        success_msg = await message.reply(
            f"✅ <b>Files sent successfully!</b>\n\n📁 Total: {len(file_ids)} files",
            parse_mode=enums.ParseMode.HTML
        )
        await bot.auto_delete.store_bot_message(user_id, success_msg.id)


async def handle_file_link(bot, message: Message, file_id_encoded: str):
    """Handle single file link - ALL FEATURES PRESERVED"""
    user_id = message.from_user.id
    
    from utils.helpers import decode
    decoded = await decode(file_id_encoded)
    if not decoded or not decoded.isdigit():
        error_msg = await message.reply("❌ <b>Invalid file link!</b>", parse_mode=enums.ParseMode.HTML)
        await bot.auto_delete.store_bot_message(user_id, error_msg.id)
        return
    
    file_id = int(decoded)
    
    if not bot.db_channel:
        error_msg = await message.reply("❌ <b>Database channel not set!</b>", parse_mode=enums.ParseMode.HTML)
        await bot.auto_delete.store_bot_message(user_id, error_msg.id)
        return
    
    # Check if bot is admin
    try:
        me = await bot.get_me()
        bot_id = me.id
        member = await bot.get_chat_member(bot.db_channel, bot_id)
        if member.status not in ["administrator", "creator"]:
            error_msg = await message.reply("❌ <b>Bot is not admin in database channel!</b>", parse_mode=enums.ParseMode.HTML)
            await bot.auto_delete.store_bot_message(user_id, error_msg.id)
            return
    except Exception:
        error_msg = await message.reply("❌ <b>Cannot access database channel!</b>", parse_mode=enums.ParseMode.HTML)
        await bot.auto_delete.store_bot_message(user_id, error_msg.id)
        return
    
    try:
        response = await bot.copy_message(
            chat_id=message.chat.id,
            from_chat_id=bot.db_channel,
            message_id=file_id,
            protect_content=bot.settings.get("protect_content", True)
        )
        
        # FEATURE 2: Auto-delete
        settings = await bot.db.get_settings()
        auto_delete = settings.get("auto_delete", False)
        if auto_delete:
            delete_time = settings.get("auto_delete_time", 300)
            await bot.auto_delete.schedule_file_deletion(user_id, response.id, delete_time)
        
        await bot.auto_delete.track_user_files(user_id, [file_id])
        
    except Exception:
        error_msg = await message.reply("❌ <b>File not found or access denied!</b>", parse_mode=enums.ParseMode.HTML)
        await bot.auto_delete.store_bot_message(user_id, error_msg.id)


async def handle_batch_link(bot, message: Message, batch_id: str):
    """Handle batch file link - ALL FEATURES PRESERVED"""
    user_id = message.from_user.id
    
    from utils.helpers import decode
    decoded = await decode(batch_id)
    if not decoded:
        error_msg = await message.reply("❌ <b>Invalid batch link!</b>", parse_mode=enums.ParseMode.HTML)
        await bot.auto_delete.store_bot_message(user_id, error_msg.id)
        return
    
    file_ids = [int(x) for x in decoded.split(",") if x.isdigit()]
    
    if not file_ids:
        error_msg = await message.reply("❌ <b>No files found in batch!</b>", parse_mode=enums.ParseMode.HTML)
        await bot.auto_delete.store_bot_message(user_id, error_msg.id)
        return
    
    if not bot.db_channel:
        error_msg = await message.reply("❌ <b>Database channel not set!</b>", parse_mode=enums.ParseMode.HTML)
        await bot.auto_delete.store_bot_message(user_id, error_msg.id)
        return
    
    progress_msg = await message.reply(
        f"📤 <b>Sending {len(file_ids)} files...</b>",
        parse_mode=enums.ParseMode.HTML
    )
    
    sent_file_ids = []
    
    from config import MAX_BATCH_SIZE
    for file_id in file_ids[:MAX_BATCH_SIZE]:
        try:
            response = await bot.copy_message(
                chat_id=message.chat.id,
                from_chat_id=bot.db_channel,
                message_id=file_id,
                protect_content=bot.settings.get("protect_content", True)
            )
            sent_file_ids.append(file_id)
            
            # FEATURE 2: Auto-delete
            settings = await bot.db.get_settings()
            auto_delete = settings.get("auto_delete", False)
            if auto_delete:
                delete_time = settings.get("auto_delete_time", 300)
                await bot.auto_delete.schedule_file_deletion(user_id, response.id, delete_time)
            
        except Exception:
            pass
    
    try:
        await progress_msg.delete()
    except:
        pass
    
    if sent_file_ids:
        await bot.auto_delete.track_user_files(user_id, sent_file_ids)
    
    success_msg = await message.reply(
        f"✅ <b>Batch sent successfully!</b>\n\n📁 Total: {len(sent_file_ids)} files",
        parse_mode=enums.ParseMode.HTML
    )
    await bot.auto_delete.store_bot_message(user_id, success_msg.id)


async def help_handler(bot, message: Message):
    """Handle /help command - ALL FEATURES PRESERVED"""
    user_id = message.from_user.id
    user = message.from_user

    settings = await bot.db.get_settings()
    if settings.get("clean_conversation", True):
        await bot.auto_delete.delete_previous_bot_message(user_id)

    help_text_custom = settings.get("help_text", "")
    help_pics = settings.get("help_pics", Config.HELP_PICS)
    help_pic = get_random_pic(help_pics)

    if help_text_custom:
        help_text = help_text_custom
    else:
        help_text = create_help_text(user.first_name, expandable=True)

    buttons = [
        [
            InlineKeyboardButton("ᴀɴɪᴍᴇ ᴄʜᴀɴɴᴇʟ", url=f"https://t.me/{Config.UPDATE_CHANNEL}"),
            InlineKeyboardButton("ᴄᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ", url=f"https://t.me/{Config.SUPPORT_CHAT}")
        ],
        [
            InlineKeyboardButton("ᴀʙᴏᴜᴛ ᴍᴇ 📖", callback_data="about_menu"),
            InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="start_menu")
        ],
        [
            InlineKeyboardButton("ᴄʟᴏsᴇ ✖️", callback_data="close")
        ]
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    try:
        response = await message.reply_photo(
            photo=help_pic,
            caption=help_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
    except Exception:
        response = await message.reply(
            help_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )

    await bot.auto_delete.store_bot_message(user_id, response.id)


async def about_handler(bot, message: Message):
    """Handle /about command - ALL FEATURES PRESERVED"""
    user_id = message.from_user.id
    
    settings = await bot.db.get_settings()
    if settings.get("clean_conversation", True):
        await bot.auto_delete.delete_previous_bot_message(user_id)

    about_text_custom = settings.get("about_text", "")
    about_pics = settings.get("welcome_pics", Config.WELCOME_PICS)
    about_pic = get_random_pic(about_pics)

    if about_text_custom:
        about_text = about_text_custom
    else:
        about_content = (
            f"<b>• Bot Name:</b> {Config.BOT_NAME}\n"
            f"<b>• Framework:</b> Pyrogram\n"
            f"<b>• Language:</b> Python 3\n"
            f"<b>• Version:</b> V3.0\n"
            f"<b>• Features:</b> Three Auto-Delete System\n"
            f"<b>• Database:</b> MongoDB\n\n"
            f"<b>Developed by @{Config.UPDATE_CHANNEL}</b>"
        )
        
        about_text = (
            "ℹ️ <b>About Bot</b>\n\n"
            f'<blockquote>{about_content}</blockquote>'
        )

    buttons = [
        [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="start_menu")],
        [InlineKeyboardButton("ᴄʟᴏsᴇ ✖️", callback_data="close")]
    ]

    keyboard = InlineKeyboardMarkup(buttons)

    try:
        response = await message.reply_photo(
            photo=about_pic,
            caption=about_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
    except Exception:
        response = await message.reply(
            about_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )

    await bot.auto_delete.store_bot_message(user_id, response.id)


async def ping_handler(bot, message: Message):
    """Handle /ping command"""
    import time
    user_id = message.from_user.id
    
    settings = await bot.db.get_settings()
    if settings.get("clean_conversation", True):
        await bot.auto_delete.delete_previous_bot_message(user_id)

    start_time = time.time()
    response = await message.reply("🏓 <b>Pinging...</b>", parse_mode=enums.ParseMode.HTML)
    end_time = time.time()

    ping_time = round((end_time - start_time) * 1000, 2)

    await response.edit_text(
        f"🏓 <b>Pong!</b>\n\n"
        f"<blockquote>"
        f"<b>📡 Ping:</b> {ping_time}ms\n"
        f"<b>⏰ Time:</b> {datetime.datetime.now().strftime('%H:%M:%S')}\n"
        f"<b>📅 Date:</b> {datetime.datetime.now().strftime('%Y-%m-%d')}"
        f"</blockquote>",
        parse_mode=enums.ParseMode.HTML
    )

    await bot.auto_delete.store_bot_message(user_id, response.id)


def register(bot):
    """Register all start handlers"""
    from pyrogram import filters
    
    bot.on_message(filters.command("start") & filters.private)(
        lambda c, m: start_handler(c, m)
    )
    
    bot.on_message(filters.command("help") & filters.private)(
        lambda c, m: help_handler(c, m)
    )
    
    bot.on_message(filters.command("about") & filters.private)(
        lambda c, m: about_handler(c, m)
    )
    
    bot.on_message(filters.command("ping") & filters.private)(
        lambda c, m: ping_handler(c, m)
    )
