"""
Admin Commands - Beautiful Interactive Panels
Like EvaMaria UI with toggles and settings
"""

from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
import asyncio

from bot import bot
from config import ADMINS

# ========== USERS COMMAND ==========

@bot.on_message(filters.private & filters.user(ADMINS) & filters.command("users"))
async def users_command(client: Client, message: Message):
    """Show user statistics with beautiful UI"""
    
    if not bot.db:
        await message.reply_text("❌ Database not connected!", quote=True)
        return
    
    msg = await message.reply_text("⏳ <b>Counting users...</b>", quote=True)
    
    total = await bot.db.total_users_count()
    banned = len(await bot.db.get_banned_users())
    
    text = f"""
👥 <b>USER STATISTICS</b>

<b>📊 Total Users:</b> <code>{total}</code>
<b>🚫 Banned Users:</b> <code>{banned}</code>
<b>✅ Active Users:</b> <code>{total - banned}</code>
"""
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔄 Refresh", callback_data="users_refresh"),
            InlineKeyboardButton("🔒 Close", callback_data="close")
        ]
    ])
    
    await msg.edit_text(text, reply_markup=buttons)


@bot.on_callback_query(filters.regex("^users_refresh$"))
async def users_refresh_callback(client: Client, query: CallbackQuery):
    """Refresh user statistics"""
    
    if query.from_user.id not in ADMINS:
        await query.answer("❌ You're not authorized!", show_alert=True)
        return
    
    await query.answer("♻️ Refreshing...")
    
    total = await bot.db.total_users_count()
    banned = len(await bot.db.get_banned_users())
    
    text = f"""
👥 <b>USER STATISTICS</b>

<b>📊 Total Users:</b> <code>{total}</code>
<b>🚫 Banned Users:</b> <code>{banned}</code>
<b>✅ Active Users:</b> <code>{total - banned}</code>

<i>Last updated: Just now</i>
"""
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔄 Refresh", callback_data="users_refresh"),
            InlineKeyboardButton("🔒 Close", callback_data="close")
        ]
    ])
    
    await query.message.edit_text(text, reply_markup=buttons)


# ========== BROADCAST COMMAND ==========

@bot.on_message(filters.private & filters.user(ADMINS) & filters.command("broadcast"))
async def broadcast_command(client: Client, message: Message):
    """Broadcast message to all users"""
    
    if not bot.db:
        await message.reply_text("❌ Database not connected!", quote=True)
        return
    
    if not message.reply_to_message:
        await message.reply_text(
            "❌ <b>Reply to a message to broadcast!</b>\n\n"
            "<b>Usage:</b> <code>/broadcast</code> (reply to message)",
            quote=True
        )
        return
    
    users = await bot.db.get_all_users()
    broadcast_msg = message.reply_to_message
    
    status_msg = await message.reply_text(
        "📢 <b>BROADCASTING...</b>\n\n"
        f"<b>Total users:</b> <code>{len(users)}</code>\n"
        "⏳ <i>Please wait...</i>",
        quote=True
    )
    
    successful = 0
    blocked = 0
    deleted = 0
    failed = 0
    
    for user_id in users:
        try:
            await broadcast_msg.copy(user_id)
            successful += 1
        except UserIsBlocked:
            await bot.db.delete_user(user_id)
            blocked += 1
        except InputUserDeactivated:
            await bot.db.delete_user(user_id)
            deleted += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
            try:
                await broadcast_msg.copy(user_id)
                successful += 1
            except:
                failed += 1
        except:
            failed += 1
        
        # Update status every 50 users
        if (successful + blocked + deleted + failed) % 50 == 0:
            await status_msg.edit_text(
                f"📢 <b>BROADCASTING...</b>\n\n"
                f"<b>Progress:</b> {successful + blocked + deleted + failed}/{len(users)}\n"
                f"✅ Success: {successful}\n"
                f"🚫 Blocked: {blocked}\n"
                f"❌ Deleted: {deleted}\n"
                f"⚠️ Failed: {failed}"
            )
    
    # Final status
    await status_msg.edit_text(
        f"✅ <b>BROADCAST COMPLETED!</b>\n\n"
        f"<b>📊 Statistics:</b>\n"
        f"• Total: <code>{len(users)}</code>\n"
        f"• Successful: <code>{successful}</code>\n"
        f"• Blocked: <code>{blocked}</code>\n"
        f"• Deleted: <code>{deleted}</code>\n"
        f"• Failed: <code>{failed}</code>"
    )


# ========== BAN/UNBAN COMMANDS ==========

@bot.on_message(filters.private & filters.user(ADMINS) & filters.command("ban"))
async def ban_user_command(client: Client, message: Message):
    """Ban a user"""
    
    if not bot.db:
        await message.reply_text("❌ Database not connected!", quote=True)
        return
    
    if len(message.command) < 2:
        await message.reply_text(
            "❌ <b>Invalid Usage!</b>\n\n"
            "<b>Usage:</b> <code>/ban user_id</code>",
            quote=True
        )
        return
    
    try:
        user_id = int(message.command[1])
    except:
        await message.reply_text("❌ Invalid user ID!", quote=True)
        return
    
    if await bot.db.is_user_banned(user_id):
        await message.reply_text(
            f"⚠️ User <code>{user_id}</code> is already banned!",
            quote=True
        )
        return
    
    await bot.db.ban_user(user_id)
    await message.reply_text(
        f"✅ <b>User Banned!</b>\n\n"
        f"<b>User ID:</b> <code>{user_id}</code>",
        quote=True
    )


@bot.on_message(filters.private & filters.user(ADMINS) & filters.command("unban"))
async def unban_user_command(client: Client, message: Message):
    """Unban a user"""
    
    if not bot.db:
        await message.reply_text("❌ Database not connected!", quote=True)
        return
    
    if len(message.command) < 2:
        await message.reply_text(
            "❌ <b>Invalid Usage!</b>\n\n"
            "<b>Usage:</b> <code>/unban user_id</code>",
            quote=True
        )
        return
    
    try:
        user_id = int(message.command[1])
    except:
        await message.reply_text("❌ Invalid user ID!", quote=True)
        return
    
    if not await bot.db.is_user_banned(user_id):
        await message.reply_text(
            f"⚠️ User <code>{user_id}</code> is not banned!",
            quote=True
        )
        return
    
    await bot.db.unban_user(user_id)
    await message.reply_text(
        f"✅ <b>User Unbanned!</b>\n\n"
        f"<b>User ID:</b> <code>{user_id}</code>",
        quote=True
    )


# ========== STATS COMMAND ==========

@bot.on_message(filters.private & filters.user(ADMINS) & filters.command("stats"))
async def stats_command(client: Client, message: Message):
    """Show bot statistics"""
    
    if not bot.db:
        await message.reply_text("❌ Database not connected!", quote=True)
        return
    
    total_users = await bot.db.total_users_count()
    banned_users = len(await bot.db.get_banned_users())
    
    text = f"""
📊 <b>BOT STATISTICS</b>

<b>🤖 Bot Info:</b>
• Name: {bot.first_name}
• Username: @{bot.username}
• ID: <code>{bot.id}</code>

<b>👥 Users:</b>
• Total: <code>{total_users}</code>
• Banned: <code>{banned_users}</code>
• Active: <code>{total_users - banned_users}</code>

<b>⚙️ System:</b>
• Database: ✅ Connected
• Channels: ✅ Configured
"""
    
    if hasattr(bot, 'db_channel'):
        text += f"• File Channel: {bot.db_channel.title}\n"
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔄 Refresh", callback_data="stats_refresh"),
            InlineKeyboardButton("🔒 Close", callback_data="close")
        ]
    ])
    
    await message.reply_text(text, reply_markup=buttons, quote=True)


@bot.on_callback_query(filters.regex("^stats_refresh$"))
async def stats_refresh_callback(client: Client, query: CallbackQuery):
    """Refresh statistics"""
    
    if query.from_user.id not in ADMINS:
        await query.answer("❌ You're not authorized!", show_alert=True)
        return
    
    await query.answer("♻️ Refreshing...")
    
    total_users = await bot.db.total_users_count()
    banned_users = len(await bot.db.get_banned_users())
    
    text = f"""
📊 <b>BOT STATISTICS</b>

<b>🤖 Bot Info:</b>
• Name: {bot.first_name}
• Username: @{bot.username}
• ID: <code>{bot.id}</code>

<b>👥 Users:</b>
• Total: <code>{total_users}</code>
• Banned: <code>{banned_users}</code>
• Active: <code>{total_users - banned_users}</code>

<b>⚙️ System:</b>
• Database: ✅ Connected
• Channels: ✅ Configured
"""
    
    if hasattr(bot, 'db_channel'):
        text += f"• File Channel: {bot.db_channel.title}\n"
    
    text += f"\n<i>Last updated: Just now</i>"
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔄 Refresh", callback_data="stats_refresh"),
            InlineKeyboardButton("🔒 Close", callback_data="close")
        ]
    ])
    
    await query.message.edit_text(text, reply_markup=buttons)
