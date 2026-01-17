#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
handlers/files.py
Complete File Management Handler - ALL FEATURES PRESERVED
Handles /genlink, /batch, /custom_batch, /special_link commands
"""

import logging
from pyrogram import filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import Config, MAX_BATCH_SIZE, MAX_SPECIAL_FILES, MAX_CUSTOM_BATCH
from utils.helpers import encode, decode

logger = logging.getLogger(__name__)


async def genlink_handler(bot, message: Message):
    """
    Handle /genlink command - COMPLETELY FIXED
    Generates shareable link for a single file
    """
    user_id = message.from_user.id
    
    if not await bot.is_user_admin(user_id):
        response = await message.reply("❌ <b>Admin only!</b>", parse_mode=enums.ParseMode.HTML)
        await bot.auto_delete.store_bot_message(user_id, response.id)
        return

    settings = await bot.db.get_settings()
    if settings.get("clean_conversation", True):
        await bot.auto_delete.delete_previous_bot_message(user_id)

    if not message.reply_to_message:
        response = await message.reply(
            "🔗 <b>GENERATE LINK</b>\n\n"
            "<blockquote>"
            "<b>How to use:</b>\n"
            "Reply to a file with /genlink to create a shareable link"
            "</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
        await bot.auto_delete.store_bot_message(user_id, response.id)
        return

    if not bot.db_channel:
        response = await message.reply("❌ <b>Set database channel first!</b>", parse_mode=enums.ParseMode.HTML)
        await bot.auto_delete.store_bot_message(user_id, response.id)
        return

    try:
        # Check if bot is admin in database channel
        me = await bot.get_me()
        bot_id = me.id
        member = await bot.get_chat_member(bot.db_channel, bot_id)
        if member.status not in ["administrator", "creator"]:
            response = await message.reply("❌ <b>Bot is not admin in the database channel!</b>", parse_mode=enums.ParseMode.HTML)
            await bot.auto_delete.store_bot_message(user_id, response.id)
            return
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        response = await message.reply("❌ <b>Cannot access database channel!</b>", parse_mode=enums.ParseMode.HTML)
        await bot.auto_delete.store_bot_message(user_id, response.id)
        return

    try:
        forwarded = await message.reply_to_message.forward(bot.db_channel)
        
        base64_id = await encode(str(forwarded.id))
        bot_username = Config.BOT_USERNAME
        link = f"https://t.me/{bot_username}?start={base64_id}"

        response = await message.reply(
            f"✅ <b>Link Generated!</b>\n\n"
            f"<blockquote>"
            f"<b>🔗 Link:</b>\n"
            f"<code>{link}</code>\n\n"
            f"<b>📝 File ID:</b> <code>{forwarded.id}</code>"
            f"</blockquote>",
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True
        )

        await bot.auto_delete.store_bot_message(user_id, response.id)

    except Exception as e:
        logger.error(f"Error forwarding message: {e}")
        response = await message.reply("❌ <b>Error forwarding message to database channel!</b>", parse_mode=enums.ParseMode.HTML)
        await bot.auto_delete.store_bot_message(user_id, response.id)


async def getlink_handler(bot, message: Message):
    """Handle /getlink command - Alias for genlink"""
    await genlink_handler(bot, message)


async def batch_handler(bot, message: Message):
    """
    Handle /batch command - First/Last Message Method
    ALL FEATURES PRESERVED
    """
    user_id = message.from_user.id
    
    if not await bot.is_user_admin(user_id):
        response = await message.reply("❌ <b>Admin only!</b>", parse_mode=enums.ParseMode.HTML)
        await bot.auto_delete.store_bot_message(user_id, response.id)
        return

    settings = await bot.db.get_settings()
    if settings.get("clean_conversation", True):
        await bot.auto_delete.delete_previous_bot_message(user_id)

    if not bot.db_channel:
        response = await message.reply("❌ <b>Set database channel first!</b>", parse_mode=enums.ParseMode.HTML)
        await bot.auto_delete.store_bot_message(user_id, response.id)
        return

    # Initialize batch state
    bot.batch_state[user_id] = {
        "method": "first_last",
        "step": "waiting_first",
        "first_msg_id": None,
        "last_msg_id": None,
        "channel_id": bot.db_channel
    }

    response = await message.reply(
        "📦 <b>BATCH MODE STARTED</b>\n\n"
        "<blockquote>"
        f"<b>Method:</b> First/Last Message\n"
        f"<b>Max files:</b> {MAX_BATCH_SIZE}\n\n"
        f"<b>📝 Step 1:</b>\n"
        "Go to your database channel and forward the <b>FIRST message</b> (starting file) to me.\n\n"
        f"<i>Example: If you want Episodes 1-50, forward Episode 1</i>"
        "</blockquote>",
        parse_mode=enums.ParseMode.HTML
    )

    await bot.auto_delete.store_bot_message(user_id, response.id)


async def custom_batch_handler(bot, message: Message):
    """Handle /custom_batch command - Random files selection"""
    user_id = message.from_user.id
    
    if not await bot.is_user_admin(user_id):
        response = await message.reply("❌ <b>Admin only!</b>", parse_mode=enums.ParseMode.HTML)
        await bot.auto_delete.store_bot_message(user_id, response.id)
        return

    settings = await bot.db.get_settings()
    if settings.get("clean_conversation", True):
        await bot.auto_delete.delete_previous_bot_message(user_id)

    if not bot.db_channel:
        response = await message.reply("❌ <b>Set database channel first!</b>", parse_mode=enums.ParseMode.HTML)
        await bot.auto_delete.store_bot_message(user_id, response.id)
        return

    # Initialize custom batch state
    bot.custom_batch_state[user_id] = {
        "method": "custom",
        "files": [],
        "channel_id": bot.db_channel
    }

    response = await message.reply(
        "🎯 <b>CUSTOM BATCH MODE</b>\n\n"
        "<blockquote>"
        f"<b>Max files:</b> {MAX_CUSTOM_BATCH}\n\n"
        "<b>📝 Instructions:</b>\n"
        "1. Forward any files from your database channel\n"
        "2. You can forward them in any order\n"
        "3. When done, send /done\n\n"
        "<i>Example: Forward Episode 5, 12, 20 for a custom batch</i>"
        "</blockquote>",
        parse_mode=enums.ParseMode.HTML
    )

    await bot.auto_delete.store_bot_message(user_id, response.id)


async def special_link_handler(bot, message: Message):
    """Handle /special_link command - Custom message with files"""
    user_id = message.from_user.id
    
    if not await bot.is_user_admin(user_id):
        response = await message.reply("❌ <b>Admin only!</b>", parse_mode=enums.ParseMode.HTML)
        await bot.auto_delete.store_bot_message(user_id, response.id)
        return

    settings = await bot.db.get_settings()
    if settings.get("clean_conversation", True):
        await bot.auto_delete.delete_previous_bot_message(user_id)

    if not bot.db_channel:
        response = await message.reply("❌ <b>Set database channel first!</b>", parse_mode=enums.ParseMode.HTML)
        await bot.auto_delete.store_bot_message(user_id, response.id)
        return

    # Initialize special link state
    bot.special_link_state[user_id] = {
        "step": "collecting_files",
        "files": [],
        "message": None,
        "channel_id": bot.db_channel
    }

    response = await message.reply(
        "⭐ <b>SPECIAL LINK MODE</b>\n\n"
        "<blockquote>"
        f"<b>Max files:</b> {MAX_SPECIAL_FILES}\n\n"
        "<b>📝 Step 1:</b> Forward files\n"
        "Forward the files from your database channel\n\n"
        "<b>📝 Step 2:</b> Send /done\n"
        "When you're done forwarding files\n\n"
        "<b>📝 Step 3:</b> Type your message\n"
        "This message will be shown to users before files"
        "</blockquote>",
        parse_mode=enums.ParseMode.HTML
    )

    await bot.auto_delete.store_bot_message(user_id, response.id)


async def done_handler(bot, message: Message):
    """Handle /done command - Finish batch/custom_batch/special_link"""
    user_id = message.from_user.id
    
    if not await bot.is_user_admin(user_id):
        return

    settings = await bot.db.get_settings()
    if settings.get("clean_conversation", True):
        await bot.auto_delete.delete_previous_bot_message(user_id)

    # Check custom batch
    if user_id in bot.custom_batch_state:
        await finish_custom_batch(bot, message)
        return

    # Check special link
    if user_id in bot.special_link_state:
        state = bot.special_link_state[user_id]
        if state["step"] == "collecting_files":
            # Move to message step
            state["step"] = "waiting_message"
            
            response = await message.reply(
                "✅ <b>Files collected!</b>\n\n"
                f"<blockquote>"
                f"<b>📁 Total files:</b> {len(state['files'])}\n\n"
                "<b>Now type your custom message:</b>\n"
                "This message will be shown to users before sending files."
                "</blockquote>",
                parse_mode=enums.ParseMode.HTML
            )
            
            await bot.auto_delete.store_bot_message(user_id, response.id)
            return
    
    response = await message.reply("❌ <b>No active batch/special link mode!</b>", parse_mode=enums.ParseMode.HTML)
    await bot.auto_delete.store_bot_message(user_id, response.id)


async def finish_custom_batch(bot, message: Message):
    """Finish custom batch and generate link"""
    user_id = message.from_user.id
    state = bot.custom_batch_state[user_id]
    
    files = state["files"]
    
    if not files:
        response = await message.reply("❌ <b>No files collected!</b>", parse_mode=enums.ParseMode.HTML)
        await bot.auto_delete.store_bot_message(user_id, response.id)
        del bot.custom_batch_state[user_id]
        return
    
    # Generate batch link
    file_ids_str = ",".join(map(str, files))
    encoded = await encode(file_ids_str)
    
    link = f"https://t.me/{Config.BOT_USERNAME}?start=batch_{encoded}"
    
    response = await message.reply(
        f"✅ <b>CUSTOM BATCH LINK GENERATED!</b>\n\n"
        f"<blockquote>"
        f"<b>📁 Total Files:</b> {len(files)}\n\n"
        f"<b>🔗 Link:</b>\n"
        f"<code>{link}</code>"
        f"</blockquote>",
        parse_mode=enums.ParseMode.HTML,
        disable_web_page_preview=True
    )
    
    await bot.auto_delete.store_bot_message(user_id, response.id)
    
    # Clear state
    del bot.custom_batch_state[user_id]


async def handle_batch_messages(bot, message: Message):
    """Handle forwarded messages for batch operations"""
    user_id = message.from_user.id
    
    # Check if message is forwarded from database channel
    if not message.forward_from_chat:
        return
    
    if message.forward_from_chat.id != bot.db_channel:
        return
    
    # Handle regular batch
    if user_id in bot.batch_state:
        await handle_regular_batch_message(bot, message)
        return
    
    # Handle custom batch
    if user_id in bot.custom_batch_state:
        await handle_custom_batch_message(bot, message)
        return
    
    # Handle special link
    if user_id in bot.special_link_state:
        await handle_special_link_message(bot, message)
        return


async def handle_regular_batch_message(bot, message: Message):
    """Handle regular batch forwarded messages"""
    user_id = message.from_user.id
    state = bot.batch_state[user_id]
    
    if state["step"] == "waiting_first":
        state["first_msg_id"] = message.forward_from_message_id
        state["step"] = "waiting_last"
        
        response = await message.reply(
            "✅ <b>First message received!</b>\n\n"
            "<blockquote>"
            "Now forward the <b>LAST message</b> from your database channel.\n\n"
            "<i>Example: If you want Episodes 1-50, now forward Episode 50</i>"
            "</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
        
        await bot.auto_delete.store_bot_message(user_id, response.id)
    
    elif state["step"] == "waiting_last":
        state["last_msg_id"] = message.forward_from_message_id
        
        first_id = state["first_msg_id"]
        last_id = state["last_msg_id"]
        
        if last_id < first_id:
            response = await message.reply(
                "❌ <b>Error!</b>\n\n"
                "Last message ID must be greater than first message ID!",
                parse_mode=enums.ParseMode.HTML
            )
            await bot.auto_delete.store_bot_message(user_id, response.id)
            return
        
        total_files = last_id - first_id + 1
        
        if total_files > MAX_BATCH_SIZE:
            response = await message.reply(
                f"❌ <b>Too many files!</b>\n\n"
                f"<blockquote>"
                f"<b>Your batch:</b> {total_files} files\n"
                f"<b>Maximum allowed:</b> {MAX_BATCH_SIZE} files"
                f"</blockquote>",
                parse_mode=enums.ParseMode.HTML
            )
            await bot.auto_delete.store_bot_message(user_id, response.id)
            return
        
        # Create file IDs list
        file_ids = list(range(first_id, last_id + 1))
        file_ids_str = ",".join(map(str, file_ids))
        encoded = await encode(file_ids_str)
        
        link = f"https://t.me/{Config.BOT_USERNAME}?start=batch_{encoded}"
        
        response = await message.reply(
            f"✅ <b>BATCH LINK GENERATED!</b>\n\n"
            f"<blockquote>"
            f"<b>📁 Total Files:</b> {total_files}\n"
            f"<b>📝 First ID:</b> {first_id}\n"
            f"<b>📝 Last ID:</b> {last_id}\n\n"
            f"<b>🔗 Link:</b>\n"
            f"<code>{link}</code>"
            f"</blockquote>",
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True
        )
        
        await bot.auto_delete.store_bot_message(user_id, response.id)
        
        # Clear state
        del bot.batch_state[user_id]


async def handle_custom_batch_message(bot, message: Message):
    """Handle custom batch forwarded messages"""
    user_id = message.from_user.id
    state = bot.custom_batch_state[user_id]
    
    file_id = message.forward_from_message_id
    
    if file_id not in state["files"]:
        state["files"].append(file_id)
        
        files_count = len(state["files"])
        
        if files_count >= MAX_CUSTOM_BATCH:
            await finish_custom_batch(bot, message)
        else:
            await message.reply(
                f"✅ <b>File added!</b> ({files_count}/{MAX_CUSTOM_BATCH})\n\n"
                f"Forward more files or send /done when finished.",
                parse_mode=enums.ParseMode.HTML
            )


async def handle_special_link_message(bot, message: Message):
    """Handle special link forwarded messages"""
    user_id = message.from_user.id
    state = bot.special_link_state[user_id]
    
    if state["step"] != "collecting_files":
        return
    
    file_id = message.forward_from_message_id
    
    if file_id not in state["files"]:
        state["files"].append(file_id)
        
        files_count = len(state["files"])
        
        if files_count >= MAX_SPECIAL_FILES:
            state["step"] = "waiting_message"
            
            response = await message.reply(
                f"✅ <b>Maximum files collected!</b> ({MAX_SPECIAL_FILES})\n\n"
                "<blockquote>"
                "<b>Now type your custom message:</b>\n"
                "This message will be shown to users before sending files."
                "</blockquote>",
                parse_mode=enums.ParseMode.HTML
            )
            
            await bot.auto_delete.store_bot_message(user_id, response.id)
        else:
            await message.reply(
                f"✅ <b>File added!</b> ({files_count}/{MAX_SPECIAL_FILES})\n\n"
                f"Forward more files or send /done when finished.",
                parse_mode=enums.ParseMode.HTML
            )


async def handle_special_link_text(bot, message: Message):
    """Handle special link custom message"""
    user_id = message.from_user.id
    
    if user_id not in bot.special_link_state:
        return
    
    state = bot.special_link_state[user_id]
    
    if state["step"] != "waiting_message":
        return
    
    custom_message = message.text
    files = state["files"]
    
    if not files:
        response = await message.reply("❌ <b>No files collected!</b>", parse_mode=enums.ParseMode.HTML)
        await bot.auto_delete.store_bot_message(user_id, response.id)
        del bot.special_link_state[user_id]
        return
    
    # Generate unique link ID
    import random
    import string
    link_id = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    
    # Save to database
    await bot.db.save_special_link(link_id, custom_message, files)
    
    link = f"https://t.me/{Config.BOT_USERNAME}?start=link_{link_id}"
    
    response = await message.reply(
        f"✅ <b>SPECIAL LINK CREATED!</b>\n\n"
        f"<blockquote>"
        f"<b>📁 Total Files:</b> {len(files)}\n"
        f"<b>💬 Custom Message:</b> Set\n\n"
        f"<b>🔗 Link:</b>\n"
        f"<code>{link}</code>"
        f"</blockquote>",
        parse_mode=enums.ParseMode.HTML,
        disable_web_page_preview=True
    )
    
    await bot.auto_delete.store_bot_message(user_id, response.id)
    
    # Clear state
    del bot.special_link_state[user_id]


def register(bot):
    """Register all file handlers"""
    
    bot.on_message(filters.command("genlink") & filters.private)(
        lambda c, m: genlink_handler(c, m)
    )
    
    bot.on_message(filters.command("getlink") & filters.private)(
        lambda c, m: getlink_handler(c, m)
    )
    
    bot.on_message(filters.command("batch") & filters.private)(
        lambda c, m: batch_handler(c, m)
    )
    
    bot.on_message(filters.command("custom_batch") & filters.private)(
        lambda c, m: custom_batch_handler(c, m)
    )
    
    bot.on_message(filters.command("special_link") & filters.private)(
        lambda c, m: special_link_handler(c, m)
    )
    
    bot.on_message(filters.command("done") & filters.private)(
        lambda c, m: done_handler(c, m)
    )
    
    # Handle forwarded messages for batch operations
    bot.on_message(
        filters.private & 
        filters.forwarded & 
        ~filters.command(["start", "help", "about", "batch", "custom_batch", "special_link", "done"])
    )(
        lambda c, m: handle_batch_messages(c, m)
    )
    
    # Handle text messages for special link custom message
    bot.on_message(
        filters.private & 
        filters.text & 
        ~filters.command(["start", "help", "about", "batch", "custom_batch", "special_link", "done"])
    )(
        lambda c, m: handle_special_link_text(c, m)
    )
