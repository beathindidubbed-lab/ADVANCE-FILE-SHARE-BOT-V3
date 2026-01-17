"""
Message Handlers
===============

Handles text messages for:
- Batch state management (first/last message collection)
- Custom batch message collection
- Special link creation states
- Button/Text setting states
- Admin input processing

This handler processes all non-command text messages based on user state.
"""

import logging
from pyrogram import filters, enums
from pyrogram.types import Message
from config import Config

logger = logging.getLogger(__name__)

# Maximum limits
MAX_BATCH_SIZE = 100
MAX_CUSTOM_BATCH = 50
MAX_SPECIAL_FILES = 50


# ==========================================
# TEXT MESSAGE HANDLER
# ==========================================

async def text_message_handler(bot, message: Message):
    """
    Handle all text messages (non-commands)
    
    Processes messages based on user state:
    - Batch collection (first/last message)
    - Custom batch messages
    - Special link creation
    - Settings input
    """
    user_id = message.from_user.id
    
    # Check if user is banned
    if await bot.db.is_user_banned(user_id):
        return
    
    # Update user activity
    await bot.db.update_user_activity(user_id)
    
    # ==========================================
    # BATCH STATE HANDLING
    # ==========================================
    
    if user_id in bot.batch_state:
        await handle_batch_state(bot, message)
        return
    
    # ==========================================
    # CUSTOM BATCH STATE HANDLING
    # ==========================================
    
    if user_id in bot.custom_batch_state:
        await handle_custom_batch_state(bot, message)
        return
    
    # ==========================================
    # SPECIAL LINK STATE HANDLING
    # ==========================================
    
    if user_id in bot.special_link_state:
        await handle_special_link_state(bot, message)
        return
    
    # ==========================================
    # BUTTON SETTING STATE HANDLING
    # ==========================================
    
    if user_id in bot.button_setting_state:
        await handle_button_setting_state(bot, message)
        return
    
    # ==========================================
    # TEXT SETTING STATE HANDLING
    # ==========================================
    
    if user_id in bot.text_setting_state:
        await handle_text_setting_state(bot, message)
        return
    
    # If no state, ignore the message
    logger.debug(f"Received text message from {user_id} with no active state")


# ==========================================
# BATCH STATE HANDLERS
# ==========================================

async def handle_batch_state(bot, message: Message):
    """
    Handle batch collection state
    
    Collects first and last message IDs from database channel
    """
    user_id = message.from_user.id
    state = bot.batch_state[user_id]
    
    # Check if message is forwarded from database channel
    if not message.forward_from_chat:
        await message.reply(
            "❌ <b>Please forward a message from your database channel!</b>",
            parse_mode=enums.ParseMode.HTML
        )
        return
    
    if message.forward_from_chat.id != bot.db_channel:
        await message.reply(
            "❌ <b>Please forward from the correct database channel!</b>",
            parse_mode=enums.ParseMode.HTML
        )
        return
    
    # Get the original message ID
    original_msg_id = message.forward_from_message_id
    
    # Step 1: Waiting for first message
    if state["step"] == "waiting_first":
        state["first_msg_id"] = original_msg_id
        state["step"] = "waiting_last"
        
        response = await message.reply(
            f"✅ <b>First message saved!</b>\n\n"
            f"<blockquote>"
            f"<b>📝 Step 2:</b>\n"
            f"Now forward the <b>LAST message</b> (ending file) to me.\n\n"
            f"<b>First ID:</b> <code>{original_msg_id}</code>\n\n"
            f"<i>Example: If you want Episodes 1-50, you already sent Episode 1, now send Episode 50</i>"
            f"</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
        await bot.store_bot_message(user_id, response.id)
        return
    
    # Step 2: Waiting for last message
    if state["step"] == "waiting_last":
        state["last_msg_id"] = original_msg_id
        first_id = state["first_msg_id"]
        last_id = original_msg_id
        
        # Validate range
        if last_id < first_id:
            await message.reply(
                "❌ <b>Last message ID must be greater than first message ID!</b>\n\n"
                f"First: <code>{first_id}</code>\n"
                f"Last: <code>{last_id}</code>",
                parse_mode=enums.ParseMode.HTML
            )
            return
        
        # Calculate file count
        file_count = last_id - first_id + 1
        
        if file_count > MAX_BATCH_SIZE:
            await message.reply(
                f"❌ <b>Too many files!</b>\n\n"
                f"<blockquote>"
                f"<b>Requested:</b> {file_count} files\n"
                f"<b>Maximum:</b> {MAX_BATCH_SIZE} files\n\n"
                f"Please select a smaller range."
                f"</blockquote>",
                parse_mode=enums.ParseMode.HTML
            )
            return
        
        # Generate batch link
        from utils.helpers import encode
        
        # Create file IDs list
        file_ids = list(range(first_id, last_id + 1))
        file_ids_str = ",".join(str(x) for x in file_ids)
        
        # Encode batch
        batch_encoded = await encode(file_ids_str)
        bot_username = Config.BOT_USERNAME
        batch_link = f"https://t.me/{bot_username}?start=batch_{batch_encoded}"
        
        # Clear state
        del bot.batch_state[user_id]
        
        response = await message.reply(
            f"✅ <b>Batch Link Generated!</b>\n\n"
            f"<blockquote>"
            f"<b>📊 File Range:</b> {first_id} - {last_id}\n"
            f"<b>📁 Total Files:</b> {file_count}\n\n"
            f"<b>🔗 Batch Link:</b>\n"
            f"<code>{batch_link}</code>"
            f"</blockquote>",
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True
        )
        await bot.store_bot_message(user_id, response.id)


async def handle_custom_batch_state(bot, message: Message):
    """Handle custom batch with custom message state"""
    user_id = message.from_user.id
    state = bot.custom_batch_state[user_id]
    
    # Collect custom message
    if "custom_message" not in state:
        state["custom_message"] = message.text
        
        response = await message.reply(
            "✅ <b>Custom message saved!</b>\n\n"
            "<blockquote>"
            "<b>📝 Next step:</b>\n"
            "Forward files from your database channel.\n"
            "Send /done when finished."
            "</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
        await bot.store_bot_message(user_id, response.id)
        return


async def handle_special_link_state(bot, message: Message):
    """Handle special link creation state"""
    user_id = message.from_user.id
    state = bot.special_link_state[user_id]
    
    # Collect custom message for special link
    if "custom_message" not in state:
        state["custom_message"] = message.text
        
        response = await message.reply(
            "✅ <b>Special message saved!</b>\n\n"
            "<blockquote>"
            "<b>📝 Next step:</b>\n"
            "Forward files from your database channel.\n"
            "Send /done when finished.\n\n"
            f"<b>Max files:</b> {MAX_SPECIAL_FILES}"
            "</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
        await bot.store_bot_message(user_id, response.id)
        return


async def handle_button_setting_state(bot, message: Message):
    """Handle custom button configuration state"""
    user_id = message.from_user.id
    state = bot.button_setting_state[user_id]
    
    button_type = state.get("type")
    
    if button_type == "custom_button":
        # Save custom button configuration
        button_text = message.text
        
        # Parse and save to database
        await bot.db.update_setting("custom_button", button_text)
        
        # Clear state
        del bot.button_setting_state[user_id]
        
        response = await message.reply(
            "✅ <b>Custom button saved!</b>\n\n"
            "<blockquote>"
            "Your custom button configuration has been saved.\n"
            "It will be shown with file messages."
            "</blockquote>",
            parse_mode=enums.ParseMode.HTML
        )
        await bot.store_bot_message(user_id, response.id)
    
    elif button_type == "add_fsub":
        # Handle add force sub channel input
        text = message.text.strip()
        
        try:
            # Parse input: channel_id username
            parts = text.split()
            
            if len(parts) < 1:
                await message.reply(
                    "❌ <b>Invalid format!</b>\n\n"
                    "Send: <code>channel_id username</code>",
                    parse_mode=enums.ParseMode.HTML
                )
                return
            
            channel_id = int(parts[0])
            username = parts[1].lstrip('@') if len(parts) > 1 else None
            
            # Check if bot is admin
            try:
                me = await bot.get_me()
                await bot.get_chat_member(channel_id, me.id)
            except Exception as e:
                await message.reply(
                    f"❌ <b>Bot is not admin in channel!</b>\n\n<code>{str(e)[:100]}</code>",
                    parse_mode=enums.ParseMode.HTML
                )
                return
            
            # Add to database
            await bot.db.add_force_sub_channel(channel_id, username)
            bot.force_sub_channels = await bot.db.get_force_sub_channels()
            
            # Clear state
            del bot.button_setting_state[user_id]
            
            response = await message.reply(
                f"✅ <b>Force Sub Channel Added!</b>\n\n"
                f"<blockquote>"
                f"<b>ID:</b> <code>{channel_id}</code>\n"
                f"<b>Username:</b> @{username if username else 'Private'}"
                f"</blockquote>",
                parse_mode=enums.ParseMode.HTML
            )
            await bot.store_bot_message(user_id, response.id)
            
        except ValueError:
            await message.reply(
                "❌ <b>Invalid channel ID!</b>\n\n"
                "Channel ID must be a number.",
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Error adding force sub channel: {e}")
            await message.reply("❌ <b>Error adding channel!</b>", parse_mode=enums.ParseMode.HTML)


async def handle_text_setting_state(bot, message: Message):
    """Handle custom text configuration state"""
    user_id = message.from_user.id
    state = bot.text_setting_state[user_id]
    
    text_type = state.get("type")
    text_value = message.text
    
    # Save to database based on type
    if text_type == "welcome_text":
        await bot.db.update_setting("welcome_text", text_value)
        setting_name = "Welcome Text"
    elif text_type == "help_text":
        await bot.db.update_setting("help_text", text_value)
        setting_name = "Help Text"
    elif text_type == "about_text":
        await bot.db.update_setting("about_text", text_value)
        setting_name = "About Text"
    else:
        setting_name = "Custom Text"
    
    # Clear state
    del bot.text_setting_state[user_id]
    
    response = await message.reply(
        f"✅ <b>{setting_name} Updated!</b>\n\n"
        "<blockquote>"
        "Your custom text has been saved."
        "</blockquote>",
        parse_mode=enums.ParseMode.HTML
    )
    await bot.store_bot_message(user_id, response.id)


# ==========================================
# HANDLER REGISTRATION
# ==========================================

def register_message_handlers(bot):
    """Register text message handler"""
    
    # Get all command names to exclude
    from handlers import BOT_COMMANDS
    
    all_commands = []
    for cmd_list in BOT_COMMANDS.values():
        all_commands.extend([cmd.command for cmd in cmd_list])
    
    @bot.on_message(filters.private & filters.text & ~filters.command(all_commands))
    async def message_handler(client, message):
        await text_message_handler(bot, message)
    
    logger.info("✓ Message handlers registered")


# Export BOT_COMMANDS for use in handler registration
BOT_COMMANDS = {
    "all_users": [],
    "admins": []
}
