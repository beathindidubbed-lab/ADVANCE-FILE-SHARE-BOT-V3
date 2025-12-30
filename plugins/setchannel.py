"""
Set Channel Command - Configure channel from inside the bot!
Supports: Channels, Groups, Supergroups, Usernames!
No need to restart!
"""

from pyrogram import Client, filters
from pyrogram.types import Message
from config import ADMINS
import config

@Client.on_message(filters.private & filters.user(ADMINS) & filters.command("setchannel"))
async def set_channel_command(client: Client, message: Message):
    """Set database channel/group from inside bot"""
    
    await message.reply_text(
        "📁 <b>SET DATABASE CHANNEL/GROUP</b>\n\n"
        "<b>3 WAYS TO SET:</b>\n\n"
        "<b>Method 1:</b> Forward message from channel/group\n"
        "<b>Method 2:</b> Send channel/group username (e.g., @channelname)\n"
        "<b>Method 3:</b> Send channel/group ID (e.g., -1001234567890)\n\n"
        "<b>Note:</b> Bot must be admin in channel/group!\n\n"
        "⏱️ <b>Waiting for your input...</b>",
        quote=True
    )
    
    # Listen for message
    try:
        user_msg = await client.listen(message.chat.id, timeout=60)
    except:
        await message.reply_text("❌ <b>Timeout!</b> No message received.", quote=True)
        return
    
    channel_id = None
    channel_username = None
    
    # Check if forwarded message
    if user_msg.forward_from_chat:
        channel_id = user_msg.forward_from_chat.id
        channel_username = user_msg.forward_from_chat.username
    
    # Check if username sent
    elif user_msg.text:
        text = user_msg.text.strip()
        
        # Username format: @channelname or channelname
        if text.startswith('@'):
            channel_username = text[1:]
        elif text.startswith('-'):
            # Channel ID format: -1001234567890
            try:
                channel_id = int(text)
            except:
                await message.reply_text(
                    "❌ <b>Invalid ID!</b>\n\n"
                    "ID must be a number like: -1001234567890",
                    quote=True
                )
                return
        else:
            # Try as username without @
            channel_username = text
    else:
        await message.reply_text(
            "❌ <b>Invalid Input!</b>\n\n"
            "Please send:\n"
            "• Forward from channel/group\n"
            "• Channel username (@channelname)\n"
            "• Channel ID (-1001234567890)",
            quote=True
        )
        return
    
    # Try to access channel/group
    try:
        # Get chat by ID or username
        if channel_id:
            channel = await client.get_chat(channel_id)
        elif channel_username:
            channel = await client.get_chat(channel_username)
        else:
            raise ValueError("No ID or username provided")
        
        channel_id = channel.id
        channel_title = channel.title
        channel_type = str(channel.type).split('.')[-1].title()
        
        # Check if bot is admin
        try:
            member = await client.get_chat_member(channel_id, client.id)
            if member.status not in ["administrator", "creator"]:
                await message.reply_text(
                    f"⚠️ <b>Warning!</b>\n\n"
                    f"Bot is not admin in <b>{channel_title}</b>\n\n"
                    f"Make bot admin first for full functionality!",
                    quote=True
                )
        except:
            pass
        
        # Set as database channel
        client.db_channel = channel
        client.db_channel_id = channel_id
        
        # Update config
        config.CHANNELS = [channel_id]
        
        # Try to save to database
        if hasattr(client, "db") and client.db:
            try:
                await client.db.settings.update_one(
                    {"_id": "bot_settings"},
                    {"$set": {"db_channel_id": channel_id}},
                    upsert=True
                )
            except:
                pass
        
        username_text = f"@{channel.username}" if channel.username else "Private"
        
        await message.reply_text(
            f"✅ <b>{channel_type} Set Successfully!</b>\n\n"
            f"<b>📺 Name:</b> {channel_title}\n"
            f"<b>🆔 ID:</b> <code>{channel_id}</code>\n"
            f"<b>👥 Type:</b> {channel_type}\n"
            f"<b>🔗 Username:</b> {username_text}\n\n"
            f"<b>✅ Bot is now ready to share files!</b>\n\n"
            f"💡 Forward files to me and I'll generate shareable links!",
            quote=True
        )
    
    except Exception as e:
        error_msg = str(e)
        
        # Provide helpful error messages
        if "USERNAME_INVALID" in error_msg or "Username not found" in error_msg:
            await message.reply_text(
                f"❌ <b>Username Not Found!</b>\n\n"
                f"The username <code>{channel_username if channel_username else 'unknown'}</code> doesn't exist.\n\n"
                f"<b>Check:</b>\n"
                f"• Username is correct\n"
                f"• Channel/group is public\n"
                f"• No typos in username",
                quote=True
            )
        elif "CHAT_ADMIN_REQUIRED" in error_msg:
            await message.reply_text(
                f"❌ <b>Admin Rights Required!</b>\n\n"
                f"Bot must be admin in the channel/group.\n\n"
                f"<b>Steps:</b>\n"
                f"1. Go to channel/group settings\n"
                f"2. Add bot as administrator\n"
                f"3. Try again",
                quote=True
            )
        else:
            await message.reply_text(
                f"❌ <b>Error!</b>\n\n"
                f"<code>{error_msg}</code>\n\n"
                f"<b>Make sure:</b>\n"
                f"• Bot is ADMIN in channel/group\n"
                f"• Username/ID is correct\n"
                f"• Channel/group exists",
                quote=True
            )


@Client.on_message(filters.private & filters.user(ADMINS) & filters.command("checkchannel"))
async def check_channel_command(client: Client, message: Message):
    """Check current channel/group status"""
    
    if not hasattr(client, "db_channel") or not client.db_channel:
        await message.reply_text(
            "⚠️ <b>No Channel/Group Configured</b>\n\n"
            "Use /setchannel to configure:\n"
            "• Forward message from channel/group\n"
            "• Send @username\n"
            "• Send channel/group ID",
            quote=True
        )
        return
    
    channel = client.db_channel
    channel_type = str(channel.type).split('.')[-1].title()
    username_text = f"@{channel.username}" if channel.username else "Private"
    
    # Check admin status
    admin_status = "❓ Unknown"
    try:
        member = await client.get_chat_member(channel.id, client.id)
        if member.status == "creator":
            admin_status = "✅ Owner"
        elif member.status == "administrator":
            admin_status = "✅ Admin"
        else:
            admin_status = "❌ Not Admin"
    except:
        admin_status = "❌ Cannot Check"
    
    await message.reply_text(
        f"✅ <b>{channel_type} Status</b>\n\n"
        f"<b>📺 Name:</b> {channel.title}\n"
        f"<b>🆔 ID:</b> <code>{channel.id}</code>\n"
        f"<b>👥 Type:</b> {channel_type}\n"
        f"<b>🔗 Username:</b> {username_text}\n"
        f"<b>🔒 Bot Status:</b> {admin_status}\n\n"
        f"<b>{'✅ Channel is active and working!' if 'Admin' in admin_status or 'Owner' in admin_status else '⚠️ Make bot admin for full access!'}</b>",
        quote=True
    )


@Client.on_message(filters.private & filters.user(ADMINS) & filters.command("removechannel"))
async def remove_channel_command(client: Client, message: Message):
    """Remove configured channel/group"""
    
    if not hasattr(client, "db_channel") or not client.db_channel:
        await message.reply_text(
            "⚠️ <b>No Channel/Group Configured</b>\n\n"
            "Nothing to remove!",
            quote=True
        )
        return
    
    channel_name = client.db_channel.title
    
    # Remove channel
    client.db_channel = None
    client.db_channel_id = None
    config.CHANNELS = [0]
    
    # Remove from database
    if hasattr(client, "db") and client.db:
        try:
            await client.db.settings.update_one(
                {"_id": "bot_settings"},
                {"$set": {"db_channel_id": None}},
                upsert=True
            )
        except:
            pass
    
    await message.reply_text(
        f"✅ <b>Channel/Group Removed!</b>\n\n"
        f"<b>Removed:</b> {channel_name}\n\n"
        f"Use /setchannel to configure a new one.",
        quote=True
    )

