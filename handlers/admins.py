"""
Admin Handlers
==============

All admin management commands:
- /admin_list - View admin commands
- /add_admins - Add admins (owner only)
- /del_admins - Remove admins (owner only)
- /banuser_list - View banned users
- /add_banuser - Ban users
- /del_banuser - Unban users
- /ban - Quick ban
- /unban - Quick unban
- /broadcast - Broadcast message to all users
- /users - User statistics
- /stats - Bot statistics
- /refresh - Refresh statistics
- /logs - View bot logs
"""

import os
import logging
import datetime
from pyrogram import filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import Config
from utils.helpers import get_random_pic

logger = logging.getLogger(__name__)


# ==========================================
# ADMIN MANAGEMENT COMMANDS
# ==========================================

async def admin_list_command(bot, message: Message):
    """Show admin management commands"""
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
    
    try:
        # Get admins
        db_admins = await bot.db.get_admins()
        all_admins = list(set(Config.ADMINS + db_admins))
        
        if not all_admins:
            response = await message.reply("❌ <b>No admins found!</b>", parse_mode=enums.ParseMode.HTML)
            await bot.store_bot_message(user_id, response.id)
            return
        
        # Format message
        admin_text = (
            "<b>🤖 𝗨𝗦𝗘𝗥 𝗦𝗘𝗧𝗧𝗜𝗡𝗚 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦 :</b>\n\n"
            "<blockquote expandable>"
            "<b>/admin_list</b> - ᴠɪᴇᴡ ᴛʜᴇ ᴀᴠᴀɪʟᴀʙʟᴇ ᴀᴅᴍɪɴ ʟɪsᴛ (ᴏᴡɴᴇʀ)\n\n"
            "<b>/add_admins</b> - ᴀᴅᴅ ᴏɴᴇ ᴏʀ ᴍᴜʟᴛɪᴘʟᴇ ᴜsᴇʀ ɪᴅs ᴀs ᴀᴅᴍɪɴ (ᴏᴡɴᴇʀ)\n\n"
            "<b>/del_admins</b> - ᴅᴇʟᴇᴛᴇ ᴏɴᴇ ᴏʀ ᴍᴜʟᴛɪᴘʟᴇ ᴜsᴇʀ ɪᴅs ғʀᴏᴍ ᴀᴅᴍɪɴs (ᴏᴡɴᴇʀ)\n\n"
            "<b>/banuser_list</b> - ᴠɪᴇᴡ ᴛʜᴇ ᴀᴠᴀɪʟᴀʙʟᴇ ʙᴀɴɴᴇᴅ ᴜsᴇʀ ʟɪsᴛ (ᴀᴅᴍɪɴs)\n\n"
            "<b>/add_banuser</b> - ᴀᴅᴅ ᴏɴᴇ ᴏʀ ᴍᴜʟᴛɪᴘʟᴇ ᴜsᴇʀ ɪᴅs ɪɴ ʙᴀɴɴᴇᴅ ʟɪsᴛ (ᴀᴅᴍɪɴs)\n\n"
            "<b>/del_banuser</b> - ᴅᴇʟᴇᴛᴇ ᴏɴᴇ ᴏʀ ᴍᴜʟᴛɪᴘʟᴇ ᴜsᴇʀ ɪᴅs ғʀᴏᴍ ʙᴀɴɴᴇᴅ ʟɪsᴛ (ᴀᴅᴍɪɴs)"
            "</blockquote>\n\n"
            f"<b>👑 Total Admins:</b> {len(all_admins)}"
        )
        
        buttons = [
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings_menu")],
            [InlineKeyboardButton("ᴄʟᴏsᴇ ✖️", callback_data="close")]
        ]
        
        keyboard = InlineKeyboardMarkup(buttons)
        
        response = await message.reply(
            admin_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
        
        await bot.store_bot_message(user_id, response.id)
        
    except Exception as e:
        logger.error(f"Error in admin_list command: {e}")
        response = await message.reply("❌ <b>Error fetching admin list!</b>", parse_mode=enums.ParseMode.HTML)
        await bot.store_bot_message(user_id, response.id)


async def add_admins_command(bot, message: Message):
    """Add admins (owner only)"""
    user_id = message.from_user.id
    
    # Check if user is owner
    if user_id != Config.OWNER_ID:
        response = await message.reply("❌ <b>Owner only!</b>", parse_mode=enums.ParseMode.HTML)
        await bot.store_bot_message(user_id, response.id)
        return
    
    # FEATURE 1: Delete previous bot message
    settings = await bot.db.get_settings()
    if settings.get("clean_conversation", True):
        await bot.delete_previous_bot_message(user_id)
    
    if len(message.command) < 2:
        response = await message.reply(
            "<b>➕ 𝗔𝗗𝗗 𝗔𝗗𝗠𝗜𝗡𝗦</b>\n\n"
            "<blockquote>"
            "<b>Usage:</b> <code>/add_admins user_id1,user_id2</code>\n\n"
            "<b>Example:</b> <code>/add_admins 123456789,987654321</code>"
            "</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
        await bot.store_bot_message(user_id, response.id)
        return
    
    try:
        args = message.command[1].split(",")
        added_admins = []
        
        for arg in args:
            arg = arg.strip()
            
            try:
                admin_id = int(arg)
                
                # Check if user exists
                try:
                    user = await bot.get_users(admin_id)
                    
                    # Add to database
                    await bot.db.add_admin(admin_id)
                    
                    # Add to Config.ADMINS if not already
                    if admin_id not in Config.ADMINS:
                        Config.ADMINS.append(admin_id)
                    
                    # Refresh admin cache
                    bot.admin_cache.add(admin_id)
                    
                    added_admins.append(f"{user.first_name} ({admin_id})")
                    
                except Exception as e:
                    await message.reply(f"❌ <b>Error adding {arg}:</b> {str(e)}", parse_mode=enums.ParseMode.HTML)
                    continue
                
            except ValueError:
                await message.reply(f"❌ <b>Invalid user ID:</b> {arg}", parse_mode=enums.ParseMode.HTML)
                continue
        
        if added_admins:
            response = await message.reply(
                f"✅ <b>ᴀᴅᴍɪɴs ᴀᴅᴅᴇᴅ!</b>\n\n"
                f"<blockquote>"
                f"<b>ᴀᴅᴅᴇᴅ {len(added_admins)} ᴀᴅᴍɪɴ(s):</b>\n"
                + "\n".join(f"• {admin}" for admin in added_admins) +
                "</blockquote>",
                parse_mode=enums.ParseMode.HTML
            )
        else:
            response = await message.reply("❌ <b>No admins were added!</b>", parse_mode=enums.ParseMode.HTML)
        
        await bot.store_bot_message(user_id, response.id)
    
    except Exception as e:
        logger.error(f"Error adding admins: {e}")
        response = await message.reply("❌ <b>Error adding admins!</b>", parse_mode=enums.ParseMode.HTML)
        await bot.store_bot_message(user_id, response.id)


async def del_admins_command(bot, message: Message):
    """Remove admins (owner only)"""
    user_id = message.from_user.id
    
    # Check if user is owner
    if user_id != Config.OWNER_ID:
        response = await message.reply("❌ <b>Owner only!</b>", parse_mode=enums.ParseMode.HTML)
        await bot.store_bot_message(user_id, response.id)
        return
    
    # FEATURE 1: Delete previous bot message
    settings = await bot.db.get_settings()
    if settings.get("clean_conversation", True):
        await bot.delete_previous_bot_message(user_id)
    
    if len(message.command) < 2:
        response = await message.reply(
            "<b>🗑️ ᴅᴇʟᴇᴛᴇ ᴀᴅᴍɪɴs</b>\n\n"
            "<blockquote>"
            "<b>Usage:</b> <code>/del_admins user_id1,user_id2</code>\n\n"
            "<b>Example:</b> <code>/del_admins 123456789,987654321</code>\n\n"
            "<b>Note:</b> Cannot remove owner!"
            "</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
        await bot.store_bot_message(user_id, response.id)
        return
    
    try:
        args = message.command[1].split(",")
        removed_admins = []
        
        for arg in args:
            arg = arg.strip()
            
            try:
                admin_id = int(arg)
                
                # Check if trying to remove owner
                if admin_id == Config.OWNER_ID:
                    await message.reply(f"❌ <b>Cannot remove owner ({admin_id})!</b>", parse_mode=enums.ParseMode.HTML)
                    continue
                
                # Remove from database
                await bot.db.remove_admin(admin_id)
                
                # Remove from Config.ADMINS if present
                if admin_id in Config.ADMINS:
                    Config.ADMINS.remove(admin_id)
                
                # Remove from cache
                if admin_id in bot.admin_cache:
                    bot.admin_cache.remove(admin_id)
                
                removed_admins.append(str(admin_id))
                
            except ValueError:
                await message.reply(f"❌ <b>Invalid user ID:</b> {arg}", parse_mode=enums.ParseMode.HTML)
                continue
        
        if removed_admins:
            response = await message.reply(
                f"✅ <b>Admins Removed!</b>\n\n"
                f"<blockquote>"
                f"<b>Removed {len(removed_admins)} admin(s):</b>\n"
                + "\n".join(f"• {admin}" for admin in removed_admins) +
                "</blockquote>",
                parse_mode=enums.ParseMode.HTML
            )
        else:
            response = await message.reply("❌ <b>No admins were removed!</b>", parse_mode=enums.ParseMode.HTML)
        
        await bot.store_bot_message(user_id, response.id)
    
    except Exception as e:
        logger.error(f"Error removing admins: {e}")
        response = await message.reply("❌ <b>Error removing admins!</b>", parse_mode=enums.ParseMode.HTML)
        await bot.store_bot_message(user_id, response.id)


# ==========================================
# BAN/UNBAN COMMANDS
# ==========================================

async def banuser_list_command(bot, message: Message):
    """View banned users list"""
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
    
    try:
        # Get banned users
        banned_users = await bot.db.get_banned_users()
        
        if not banned_users:
            response = await message.reply("✅ <b>No banned users found!</b>", parse_mode=enums.ParseMode.HTML)
            await bot.store_bot_message(user_id, response.id)
            return
        
        # Format message
        ban_text = "<b>🚫 𝗕𝗔𝗡𝗡𝗘𝗗 𝗨𝗦𝗘𝗥𝗦 𝗟𝗜𝗦𝗧</b>\n\n<blockquote expandable>"
        
        for i, ban in enumerate(banned_users[:10], 1):
            ban_user_id = ban["user_id"]
            reason = ban.get("reason", "No reason")
            banned_date = ban.get("banned_date", "").strftime("%Y-%m-%d") if ban.get("banned_date") else "Unknown"
            
            ban_text += f"<b>{i}. ID:</b> <code>{ban_user_id}</code>\n"
            ban_text += f"   <b>Reason:</b> {reason}\n"
            ban_text += f"   <b>Date:</b> {banned_date}\n\n"
        
        ban_text += f"</blockquote>\n\n<b>📊 Total Banned:</b> {len(banned_users)}"
        
        buttons = [
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="settings_menu")],
            [InlineKeyboardButton("ᴄʟᴏsᴇ ✖️", callback_data="close")]
        ]
        
        keyboard = InlineKeyboardMarkup(buttons)
        
        response = await message.reply(
            ban_text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )
        
        await bot.store_bot_message(user_id, response.id)
        
    except Exception as e:
        logger.error(f"Error in banuser_list command: {e}")
        response = await message.reply("❌ <b>Error fetching banned users list!</b>", parse_mode=enums.ParseMode.HTML)
        await bot.store_bot_message(user_id, response.id)


async def add_banuser_command(bot, message: Message):
    """Ban users"""
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
            "<b>🚫 𝗕𝗔𝗡 𝗨𝗦𝗘𝗥</b>\n\n"
            "<blockquote>"
            "<b>Usage:</b> <code>/add_banuser user_id1,user_id2 [reason]</code>\n\n"
            "<b>Example:</b> <code>/add_banuser 123456789,987654321 Spamming</code>"
            "</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
        await bot.store_bot_message(user_id, response.id)
        return
    
    try:
        args = message.command[1].split(",")
        reason = " ".join(message.command[2:]) if len(message.command) > 2 else "No reason provided"
        
        banned_users = []
        
        for arg in args:
            arg = arg.strip()
            
            try:
                ban_user_id = int(arg)
                
                # Check if user exists
                if not await bot.db.is_user_exist(ban_user_id):
                    try:
                        user = await bot.get_users(ban_user_id)
                        await bot.db.add_user(ban_user_id, user.first_name, user.username)
                    except:
                        pass
                
                # Ban the user
                await bot.db.ban_user(ban_user_id, reason)
                banned_users.append(str(ban_user_id))
                
                # Try to notify the user
                try:
                    await bot.send_message(
                        ban_user_id,
                        f"🚫 <b>ʏᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ʙᴀɴɴᴇᴅ!</b>\n\n"
                        f"<blockquote>"
                        f"<b>ʀᴇᴀsᴏɴ:</b> {reason}\n\n"
                        f"ᴄᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ ɪғ ᴛʜɪs ɪs ᴀ ᴍɪsᴛᴀᴋᴇ."
                        "</blockquote>",
                        parse_mode=enums.ParseMode.HTML
                    )
                except:
                    pass
                
            except ValueError:
                await message.reply(f"❌ <b>Invalid user ID:</b> {arg}", parse_mode=enums.ParseMode.HTML)
                continue
        
        if banned_users:
            response = await message.reply(
                f"✅ <b>Users Banned!</b>\n\n"
                f"<blockquote>"
                f"<b>Banned {len(banned_users)} user(s):</b>\n"
                + "\n".join(f"• {uid}" for uid in banned_users) +
                f"\n\n<b>Reason:</b> {reason}"
                "</blockquote>",
                parse_mode=enums.ParseMode.HTML
            )
        else:
            response = await message.reply("❌ <b>No users were banned!</b>", parse_mode=enums.ParseMode.HTML)
        
        await bot.store_bot_message(user_id, response.id)
    
    except Exception as e:
        logger.error(f"Error banning users: {e}")
        response = await message.reply("❌ <b>Error banning users!</b>", parse_mode=enums.ParseMode.HTML)
        await bot.store_bot_message(user_id, response.id)


async def del_banuser_command(bot, message: Message):
    """Unban users"""
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
            "<b>✅ 𝗨𝗡𝗕𝗔𝗡 𝗨𝗦𝗘𝗥</b>\n\n"
            "<blockquote>"
            "<b>Usage:</b> <code>/del_banuser user_id1,user_id2</code>\n\n"
            "<b>Example:</b> <code>/del_banuser 123456789,987654321</code>"
            "</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
        await bot.store_bot_message(user_id, response.id)
        return
    
    try:
        args = message.command[1].split(",")
        unbanned_users = []
        
        for arg in args:
            arg = arg.strip()
            
            try:
                unban_user_id = int(arg)
                
                # Check if user is banned
                if not await bot.db.is_user_banned(unban_user_id):
                    await message.reply(f"⚠️ <b>User {unban_user_id} is not banned!</b>", parse_mode=enums.ParseMode.HTML)
                    continue
                
                # Unban the user
                await bot.db.unban_user(unban_user_id)
                unbanned_users.append(str(unban_user_id))
                
                # Try to notify the user
                try:
                    await bot.send_message(
                        unban_user_id,
                        "<b>✅ ʏᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ᴜɴʙᴀɴɴᴇᴅ!</b>\n\n"
                        "ʏᴏᴜ ᴄᴀɴ ɴᴏᴡ ᴜsᴇ ᴛʜᴇ ʙᴏᴛ ᴀɢᴀɪɴ.",
                        parse_mode=enums.ParseMode.HTML
                    )
                except:
                    pass
                
            except ValueError:
                await message.reply(f"❌ <b>Invalid user ID: {arg}</b>", parse_mode=enums.ParseMode.HTML)
                continue
        
        if unbanned_users:
            response = await message.reply(
                f"<b>✅ 𝗨𝗦𝗘𝗥𝗦 𝗨𝗡𝗕𝗔𝗡𝗡𝗘𝗗!</b>\n\n"
                f"<blockquote>"
                f"<b>Unbanned {len(unbanned_users)} user(s):</b>\n"
                + "\n".join(f"• <code>{user_id}</code>" for user_id in unbanned_users) +
                "</blockquote>",
                parse_mode=enums.ParseMode.HTML
            )
        else:
            response = await message.reply("⚠️ <b>No users were unbanned!</b>", parse_mode=enums.ParseMode.HTML)
        
        await bot.store_bot_message(user_id, response.id)
    
    except Exception as e:
        logger.error(f"Error unbanning users: {e}")
        response = await message.reply("❌ <b>Error unbanning users!</b>", parse_mode=enums.ParseMode.HTML)
        await bot.store_bot_message(user_id, response.id)


# ==========================================
# STATISTICS COMMANDS
# ==========================================

async def users_command(bot, message: Message):
    """View user statistics"""
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
    
    try:
        # Get counts
        total_users = await bot.db.total_users_count()
        banned_users = await bot.db.get_banned_count()
        active_users = total_users - banned_users
        
        # Get stats picture
        welcome_pics = settings.get("welcome_pics", Config.WELCOME_PICS)
        stats_pic = get_random_pic(welcome_pics)
        
        # Format message
        stats_text = (
            "<b>👥 USER STATISTICS</b>\n\n"
            "<blockquote>"
            f"<b>📊 Total Users:</b> {total_users:,}\n"
            f"<b>✅ Active Users:</b> {active_users:,}\n"
            f"<b>🚫 Banned Users:</b> {banned_users:,}\n\n"
            f"<i>Last updated: {datetime.datetime.now().strftime('%H:%M:%S')}</i>"
            "</blockquote>"
        )
        
        buttons = [
            [
                InlineKeyboardButton("🔄 Refresh", callback_data="refresh_users"),
                InlineKeyboardButton("📊 Stats", callback_data="stats_menu")
            ],
            [
                InlineKeyboardButton("⬅️ Back", callback_data="settings_menu"),
                InlineKeyboardButton("❌ Close", callback_data="close")
            ]
        ]
        
        keyboard = InlineKeyboardMarkup(buttons)
        
        try:
            response = await message.reply_photo(
                photo=stats_pic,
                caption=stats_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Error sending stats photo: {e}")
            response = await message.reply(
                stats_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
        
        await bot.store_bot_message(user_id, response.id)
        
    except Exception as e:
        logger.error(f"Error in users command: {e}")
        response = await message.reply("❌ <b>Error fetching user statistics!</b>", parse_mode=enums.ParseMode.HTML)
        await bot.store_bot_message(user_id, response.id)


async def stats_command(bot, message: Message):
    """View bot statistics"""
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
    
    try:
        # Get counts
        total_users = await bot.db.total_users_count()
        banned_users = await bot.db.get_banned_count()
        active_users = total_users - banned_users
        
        # Get all admins
        db_admins = await bot.db.get_admins()
        all_admins = list(set(Config.ADMINS + db_admins))
        
        # Get force sub channels
        force_sub_channels = await bot.db.get_force_sub_channels()
        
        # Get db channel
        db_channel = await bot.db.get_db_channel()
        
        # Get stats picture
        welcome_pics = settings.get("welcome_pics", Config.WELCOME_PICS)
        stats_pic = get_random_pic(welcome_pics)
        
        # Format message
        stats_text = (
            "<b>📊 BOT STATISTICS</b>\n\n"
            "<blockquote>"
            f"<b>👥 Users:</b> {total_users:,}\n"
            f"<b>✅ Active:</b> {active_users:,}\n"
            f"<b>🚫 Banned:</b> {banned_users:,}\n"
            f"<b>👑 Admins:</b> {len(all_admins)}\n"
            f"<b>📢 Force Sub:</b> {len(force_sub_channels)}\n"
            f"<b>💾 DB Channel:</b> {'✅' if db_channel else '❌'}\n\n"
            f"<i>Updated: {datetime.datetime.now().strftime('%H:%M:%S')}</i>"
            "</blockquote>"
        )
        
        buttons = [
            [
                InlineKeyboardButton("👥 Users", callback_data="users_menu"),
                InlineKeyboardButton("🔄 Refresh", callback_data="refresh_stats")
            ],
            [
                InlineKeyboardButton("⬅️ Back", callback_data="settings_menu"),
                InlineKeyboardButton("❌ Close", callback_data="close")
            ]
        ]
        
        keyboard = InlineKeyboardMarkup(buttons)
        
        try:
            response = await message.reply_photo(
                photo=stats_pic,
                caption=stats_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Error sending stats photo: {e}")
            response = await message.reply(
                stats_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )
        
        await bot.store_bot_message(user_id, response.id)
        
    except Exception as e:
        logger.error(f"Error in stats command: {e}")
        response = await message.reply("❌ <b>Error fetching statistics!</b>", parse_mode=enums.ParseMode.HTML)
        await bot.store_bot_message(user_id, response.id)


async def refresh_command(bot, message: Message):
    """Refresh statistics"""
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

    response = await message.reply("🔄 <b>Refreshing...</b>", parse_mode=enums.ParseMode.HTML)

    # Get updated counts
    total_users = await bot.db.total_users_count()
    banned_users = await bot.db.get_banned_count()
    active_users = total_users - banned_users

    await response.edit_text(
        f"✅ <b>Refreshed!</b>\n\n"
        f"<blockquote>"
        f"<b>👥 Users:</b> {total_users:,}\n"
        f"<b>✅ Active:</b> {active_users:,}\n"
        f"<b>🚫 Banned:</b> {banned_users:,}\n\n"
        f"<b>Updated:</b> {datetime.datetime.now().strftime('%H:%M:%S')}"
        f"</blockquote>",
        parse_mode=enums.ParseMode.HTML
    )

    # FEATURE 1: Store this message for future deletion
    await bot.store_bot_message(user_id, response.id)


async def logs_command(bot, message: Message):
    """Send bot logs"""
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

    try:
        # Check if log file exists
        if not os.path.exists('bot.log'):
            response = await message.reply("❌ <b>Log file not found!</b>", parse_mode=enums.ParseMode.HTML)
            await bot.store_bot_message(user_id, response.id)
            return

        # Send the log file
        await message.reply_document(
            document='bot.log',
            caption="📊 <b>Bot Logs</b>\n\n<i>Latest logs from bot.log</i>",
            parse_mode=enums.ParseMode.HTML
        )

    except Exception as e:
        logger.error(f"Error in logs command: {e}")
        response = await message.reply(
            f"❌ <b>Error fetching logs:</b>\n<code>{str(e)}</code>",
            parse_mode=enums.ParseMode.HTML
        )
        await bot.store_bot_message(user_id, response.id)


# ==========================================
# HANDLER REGISTRATION
# ==========================================

def register_admin_handlers(bot):
    """Register all admin command handlers"""
    
    # Admin management
    @bot.on_message(filters.command("admin_list") & filters.private)
    async def admin_list_handler(client, message):
        await admin_list_command(bot, message)
    
    @bot.on_message(filters.command("add_admins") & filters.private)
    async def add_admins_handler(client, message):
        await add_admins_command(bot, message)
    
    @bot.on_message(filters.command("del_admins") & filters.private)
    async def del_admins_handler(client, message):
        await del_admins_command(bot, message)
    
    # Ban/unban commands
    @bot.on_message(filters.command("banuser_list") & filters.private)
    async def banuser_list_handler(client, message):
        await banuser_list_command(bot, message)
    
    @bot.on_message(filters.command("add_banuser") & filters.private)
    async def add_banuser_handler(client, message):
        await add_banuser_command(bot, message)
    
    @bot.on_message(filters.command("del_banuser") & filters.private)
    async def del_banuser_handler(client, message):
        await del_banuser_command(bot, message)
    
    # Statistics commands
    @bot.on_message(filters.command("users") & filters.private)
    async def users_handler(client, message):
        await users_command(bot, message)
    
    @bot.on_message(filters.command("stats") & filters.private)
    async def stats_handler(client, message):
        await stats_command(bot, message)
    
    @bot.on_message(filters.command("refresh") & filters.private)
    async def refresh_handler(client, message):
        await refresh_command(bot, message)
    
    @bot.on_message(filters.command("logs") & filters.private)
    async def logs_handler(client, message):
        await logs_command(bot, message)
    
    logger.info("✓ Admin handlers registered")
