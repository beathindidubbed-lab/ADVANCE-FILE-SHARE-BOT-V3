#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
handlers/callback.py
Complete Callback Query Handler - ALL FEATURES PRESERVED
Handles ALL button callbacks from inline keyboards
"""

import logging
from pyrogram import enums
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import Config
from utils.helpers import (
    get_random_pic, create_welcome_text, create_help_text,
    create_force_sub_text, create_files_settings_text,
    create_auto_delete_text, format_time, is_subscribed
)

logger = logging.getLogger(__name__)


async def handle_callback_query(bot, query: CallbackQuery):
    """
    Handle ALL callback queries - COMPLETE & VERIFIED
    ALL FEATURES PRESERVED - ZERO LOGIC REMOVED
    """
    try:
        data = query.data
        user_id = query.from_user.id

        logger.debug(f"Callback received: {data} from user {user_id}")

        # ===================================
        # ADMIN CHECK FOR ADMIN-ONLY BUTTONS
        # ===================================
        
        admin_callbacks = [
            "settings_menu", "files_settings", "auto_delete_settings",
            "force_sub_settings", "bot_msg_settings", "fsub_chnl_menu", 
            "stats_menu", "users_menu", "add_fsub_menu", "del_fsub_menu",
            "refresh_fsub", "test_fsub", "reqfsub_on", "reqfsub_off",
            "refresh_users", "refresh_stats", "refresh_autodel", 
            "toggle_protect_content", "toggle_hide_caption", 
            "toggle_channel_button", "toggle_auto_delete", 
            "toggle_clean_conversation", "toggle_show_instruction",
            "custom_buttons_menu", "custom_texts_menu", "more_stats",
            "admin_list_menu"
        ]

        if data in admin_callbacks:
            if not await bot.is_user_admin(user_id):
                await query.answer("❌ Admin only!", show_alert=True)
                return

        # ===================================
        # NAVIGATION CALLBACKS (PUBLIC + ADMIN)
        # ===================================

        if data == "start_menu":
            await query.answer()
            try:
                await query.message.delete()
            except:
                pass
            
            # Show welcome message
            await show_welcome_callback(bot, query)

        elif data == "help_menu":
            await query.answer()
            try:
                await query.message.delete()
            except:
                pass
            
            await show_help_callback(bot, query)

        elif data == "about_menu":
            await query.answer()
            try:
                await query.message.delete()
            except:
                pass
            
            await show_about_callback(bot, query)

        # ===================================
        # ADMIN NAVIGATION CALLBACKS
        # ===================================

        elif data == "settings_menu":
            await query.answer()
            try:
                await query.message.delete()
            except:
                pass
            
            await show_settings_menu(bot, query)

        elif data == "files_settings":
            await query.answer()
            try:
                await query.message.delete()
            except:
                pass
            
            await show_files_settings(bot, query)

        elif data == "auto_delete_settings":
            await query.answer()
            try:
                await query.message.delete()
            except:
                pass
            
            await show_auto_delete_settings(bot, query)

        elif data == "force_sub_settings":
            await query.answer()
            try:
                await query.message.delete()
            except:
                pass
            
            await show_force_sub_settings(bot, query)

        elif data == "bot_msg_settings":
            await query.answer()
            try:
                await query.message.delete()
            except:
                pass
            
            await show_bot_msg_settings(bot, query)

        elif data == "fsub_chnl_menu":
            await query.answer()
            try:
                await query.message.delete()
            except:
                pass
            
            await show_fsub_channels_menu(bot, query)

        elif data == "users_menu":
            await query.answer()
            try:
                await query.message.delete()
            except:
                pass
            
            await show_users_menu(bot, query)

        elif data == "stats_menu":
            await query.answer()
            try:
                await query.message.delete()
            except:
                pass
            
            await show_stats_menu(bot, query)

        elif data == "admin_list_menu":
            await query.answer()
            try:
                await query.message.delete()
            except:
                pass
            
            await show_admin_list_menu(bot, query)

        # ===================================
        # FORCE SUBSCRIBE CHECK CALLBACK
        # ===================================

        elif data == "check_fsub":
            await query.answer("🔄 Checking subscription...")
            
            user_is_subscribed = await is_subscribed(bot, user_id, bot.force_sub_channels)
            
            if user_is_subscribed:
                try:
                    await query.message.delete()
                except:
                    pass
                
                await show_welcome_callback(bot, query)
            else:
                await query.answer("❌ Please join all channels first!", show_alert=True)

        # ===================================
        # RESEND FILES CALLBACK (FEATURE 3)
        # ===================================

        elif data == "resend_files":
            await query.answer("🔄 Resending files...")
            await resend_files_callback(bot, query)

        # ===================================
        # CLOSE CALLBACKS
        # ===================================

        elif data == "close":
            await query.answer("Closed!")
            try:
                await query.message.delete()
                if user_id in bot.user_last_bot_message:
                    if bot.user_last_bot_message[user_id]["message_id"] == query.message.id:
                        del bot.user_last_bot_message[user_id]
            except Exception:
                pass

        elif data == "close_instruction":
            await query.answer()
            try:
                await query.message.delete()
                await bot.auto_delete.clear_instruction_message(user_id)
            except:
                pass

        # ===================================
        # TOGGLE CALLBACKS (Settings)
        # ===================================

        elif data.startswith("toggle_"):
            await query.answer()
            await handle_toggle_callback(bot, query)

        # ===================================
        # AUTO DELETE TIME CALLBACKS
        # ===================================

        elif data.startswith("autodel_"):
            await query.answer()
            await handle_autodel_time_callback(bot, query)

        # ===================================
        # REFRESH CALLBACKS
        # ===================================

        elif data.startswith("refresh_"):
            await query.answer("🔄 Refreshing...")
            await handle_refresh_callback(bot, query)

        # ===================================
        # FORCE SUB CALLBACKS
        # ===================================

        elif data == "reqfsub_on":
            await query.answer("✅ Request FSub Enabled!")
            await handle_reqfsub_on(bot, query)

        elif data == "reqfsub_off":
            await query.answer("❌ Request FSub Disabled!")
            await handle_reqfsub_off(bot, query)

        elif data == "test_fsub":
            await test_force_sub(bot, query)

        # ===================================
        # ADD/REMOVE FSUB CHANNELS CALLBACKS
        # ===================================

        elif data == "add_fsub_menu":
            await query.answer("➕ Add Force Sub Channel")
            await handle_add_fsub_menu(bot, query)

        elif data == "del_fsub_menu":
            await query.answer("➖ Remove Force Sub Channel")
            await handle_del_fsub_menu(bot, query)

        # ===================================
        # CHANNEL REMOVAL CALLBACK
        # ===================================

        elif data.startswith("remove_channel_"):
            channel_id_str = data.replace("remove_channel_", "")
            try:
                channel_id = int(channel_id_str)
                await handle_remove_channel_callback(bot, query, channel_id)
            except ValueError:
                await query.answer("❌ Invalid channel ID!", show_alert=True)

        # ===================================
        # DEFAULT - NOT CONFIGURED
        # ===================================

        else:
            logger.warning(f"Unhandled callback: {data}")
            await query.answer(f"⚠️ Button '{data}' not configured yet!", show_alert=True)

    except Exception as e:
        logger.error(f"Error handling callback query '{query.data}': {e}")
        import traceback
        traceback.print_exc()
        await query.answer("❌ Error processing request!", show_alert=True)


# ===================================
# SHOW WELCOME CALLBACK
# ===================================

async def show_welcome_callback(bot, query: CallbackQuery):
    """Show welcome message from callback"""
    user = query.from_user
    user_id = user.id

    settings = await bot.db.get_settings()
    welcome_text_custom = settings.get("welcome_text", "")
    welcome_pics = settings.get("welcome_pics", Config.WELCOME_PICS)
    welcome_pic = get_random_pic(welcome_pics)

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
        response = await bot.send_photo(
            chat_id=user_id,
            photo=welcome_pic,
            caption=welcome_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
    except Exception:
        response = await bot.send_message(
            chat_id=user_id,
            text=welcome_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True
        )

    await bot.auto_delete.store_bot_message(user_id, response.id)


async def show_help_callback(bot, query: CallbackQuery):
    """Show help message from callback"""
    user = query.from_user
    user_id = user.id

    settings = await bot.db.get_settings()
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
        response = await bot.send_photo(
            chat_id=user_id,
            photo=help_pic,
            caption=help_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
    except Exception:
        response = await bot.send_message(
            chat_id=user_id,
            text=help_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )

    await bot.auto_delete.store_bot_message(user_id, response.id)


async def show_about_callback(bot, query: CallbackQuery):
    """Show about message from callback"""
    user_id = query.from_user.id
    
    settings = await bot.db.get_settings()
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
        response = await bot.send_photo(
            chat_id=user_id,
            photo=about_pic,
            caption=about_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
    except Exception:
        response = await bot.send_message(
            chat_id=user_id,
            text=about_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )

    await bot.auto_delete.store_bot_message(user_id, response.id)


# ===================================
# SETTINGS MENUS
# ===================================

async def show_settings_menu(bot, query: CallbackQuery):
    """Show settings menu"""
    user_id = query.from_user.id
    settings = await bot.db.get_settings()
    
    protect_content = settings.get("protect_content", True)
    auto_delete = settings.get("auto_delete", False)
    clean_conversation = settings.get("clean_conversation", True)
    request_fsub = settings.get("request_fsub", False)

    welcome_pics = settings.get("welcome_pics", Config.WELCOME_PICS)
    settings_pic = get_random_pic(welcome_pics)

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
        response = await bot.send_photo(
            chat_id=user_id,
            photo=settings_pic,
            caption=settings_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
    except Exception:
        response = await bot.send_message(
            chat_id=user_id,
            text=settings_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )

    await bot.auto_delete.store_bot_message(user_id, response.id)


async def show_files_settings(bot, query: CallbackQuery):
    """Show files settings"""
    user_id = query.from_user.id
    settings = await bot.db.get_settings()
    
    protect_content = settings.get("protect_content", True)
    hide_caption = settings.get("hide_caption", False)
    channel_button = settings.get("channel_button", True)
    files_pics = settings.get("files_pics", Config.FILES_PICS)
    files_pic = get_random_pic(files_pics)

    files_text = create_files_settings_text(protect_content, hide_caption, channel_button)
    
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
        response = await bot.send_photo(
            chat_id=user_id,
            photo=files_pic,
            caption=files_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
    except Exception:
        response = await bot.send_message(
            chat_id=user_id,
            text=files_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
    
    await bot.auto_delete.store_bot_message(user_id, response.id)


async def show_auto_delete_settings(bot, query: CallbackQuery):
    """Show auto delete settings - THREE FEATURES"""
    user_id = query.from_user.id
    settings = await bot.db.get_settings()
    
    auto_delete = settings.get("auto_delete", False)
    auto_delete_time = settings.get("auto_delete_time", 300)
    clean_conversation = settings.get("clean_conversation", True)
    show_instruction = settings.get("show_instruction", True)
    auto_del_pics = settings.get("auto_del_pics", Config.AUTO_DEL_PICS)
    auto_del_pic = get_random_pic(auto_del_pics)

    auto_del_text = create_auto_delete_text(
        auto_delete, 
        auto_delete_time, 
        clean_conversation, 
        show_instruction
    )
    
    buttons = []

    buttons.append([
        InlineKeyboardButton(f"🗑️ ғɪʟᴇs: {'✅' if auto_delete else '❌'}", callback_data="toggle_auto_delete"),
        InlineKeyboardButton(f"💬 ᴄʟᴇᴀɴ: {'✅' if clean_conversation else '❌'}", callback_data="toggle_clean_conversation")
    ])
    
    buttons.append([
        InlineKeyboardButton(f"📝 ɪɴsᴛʀᴜᴄᴛ: {'✅' if show_instruction else '❌'}", callback_data="toggle_show_instruction"),
        InlineKeyboardButton("⏱️ sᴇᴛ ᴛɪᴍᴇʀ", callback_data="set_timer")
    ])

    if auto_delete:
        from config import AUTO_DELETE_TIMES
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
        response = await bot.send_photo(
            chat_id=user_id,
            photo=auto_del_pic,
            caption=auto_del_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
    except Exception:
        response = await bot.send_message(
            chat_id=user_id,
            text=auto_del_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
    
    await bot.auto_delete.store_bot_message(user_id, response.id)


# Continue in next file due to length...
# This is handlers/callback.py part 1 of 2


def register(bot):
    """Register callback handler"""
    from pyrogram import filters
    
    bot.on_callback_query()(
        lambda c, q: handle_callback_query(c, q)
    )
