"""
Test Channel Access - Temporary debugging command
Add this file to plugins/ folder to test channel access
"""

from pyrogram import Client, filters
from pyrogram.types import Message
from bot import bot
from config import ADMINS, CHANNELS

@bot.on_message(filters.private & filters.user(ADMINS) & filters.command("test_channel"))
async def test_channel(client: Client, message: Message):
    """Test channel access and get correct ID"""
    
    # If user provides a channel username or ID
    if len(message.command) > 1:
        channel = message.command[1]
        
        # Remove @ if present
        if channel.startswith('@'):
            channel = channel[1:]
        
        # Try to get chat
        try:
            chat = await client.get_chat(channel)
            
            text = f"""
✅ <b>Channel Found!</b>

<b>📝 Title:</b> {chat.title}
<b>🆔 ID:</b> <code>{chat.id}</code>
<b>🔗 Type:</b> {chat.type}
"""
            
            if chat.username:
                text += f"<b>👤 Username:</b> @{chat.username}\n"
            
            # Check bot permissions
            try:
                me = await client.get_chat_member(chat.id, "me")
                text += f"\n<b>🤖 Bot Status:</b> {me.status}\n"
                
                if me.status == "administrator":
                    text += "\n<b>✅ Bot Permissions:</b>\n"
                    if me.privileges:
                        text += f"• Post Messages: {'✅' if me.privileges.can_post_messages else '❌'}\n"
                        text += f"• Edit Messages: {'✅' if me.privileges.can_edit_messages else '❌'}\n"
                        text += f"• Delete Messages: {'✅' if me.privileges.can_delete_messages else '❌'}\n"
                else:
                    text += "\n⚠️ <b>Bot is NOT admin!</b>\n"
                    text += "Please make bot admin with these permissions:\n"
                    text += "• Post Messages\n"
                    text += "• Edit Messages\n"
                    text += "• Delete Messages\n"
            except Exception as e:
                text += f"\n⚠️ <b>Cannot check permissions:</b> {e}\n"
            
            # Test message read
            try:
                count = 0
                async for msg in client.get_chat_history(chat.id, limit=1):
                    count += 1
                    text += f"\n✅ <b>Can read messages!</b> (Last: {msg.id})\n"
                
                if count == 0:
                    text += "\n⚠️ <b>Channel is empty or cannot read messages</b>\n"
            except Exception as e:
                text += f"\n⚠️ <b>Cannot read messages:</b> {e}\n"
            
            text += f"\n<b>💡 Use this ID in your config:</b>\n<code>CHANNELS={chat.id}</code>"
            
            await message.reply_text(text, quote=True)
            
        except Exception as e:
            await message.reply_text(
                f"❌ <b>Error accessing channel!</b>\n\n"
                f"<b>Error:</b> <code>{e}</code>\n\n"
                f"<b>Make sure:</b>\n"
                f"1. Bot is added to the channel\n"
                f"2. Bot is admin with required permissions\n"
                f"3. Channel username/ID is correct",
                quote=True
            )
    
    else:
        # Test configured channels
        text = "🔍 <b>Testing Configured Channels...</b>\n\n"
        
        for idx, channel_id in enumerate(CHANNELS, 1):
            text += f"<b>Channel {idx}:</b> <code>{channel_id}</code>\n"
            
            try:
                chat = await client.get_chat(channel_id)
                text += f"✅ Title: {chat.title}\n"
                
                # Check access
                try:
                    me = await client.get_chat_member(channel_id, "me")
                    if me.status == "administrator":
                        text += f"✅ Bot is Admin\n"
                    else:
                        text += f"⚠️ Bot is: {me.status}\n"
                except:
                    text += "❌ Cannot check permissions\n"
                
            except Exception as e:
                text += f"❌ Error: {e}\n"
            
            text += "\n"
        
        text += "<b>💡 Usage:</b> <code>/test_channel @channel_username</code>"
        text += "\nor <code>/test_channel -1001234567890</code>"
        
        await message.reply_text(text, quote=True)


@bot.on_message(filters.private & filters.user(ADMINS) & filters.command("get_chat_id"))
async def get_chat_id(client: Client, message: Message):
    """Forward a message from channel to get its ID"""
    
    if not message.reply_to_message:
        await message.reply_text(
            "📋 <b>How to get Channel ID:</b>\n\n"
            "1. Forward any message from your channel to me\n"
            "2. Reply to that forwarded message with /get_chat_id\n"
            "3. I'll show you the channel ID\n\n"
            "<b>Or use:</b> <code>/test_channel @channel_username</code>",
            quote=True
        )
        return
    
    msg = message.reply_to_message
    
    if msg.forward_from_chat:
        chat = msg.forward_from_chat
        
        text = f"""
✅ <b>Channel ID Found!</b>

<b>📝 Title:</b> {chat.title}
<b>🆔 ID:</b> <code>{chat.id}</code>
<b>🔗 Type:</b> {chat.type}
"""
        
        if chat.username:
            text += f"<b>👤 Username:</b> @{chat.username}\n"
        
        text += f"\n<b>💡 Use this in your .env file:</b>\n<code>CHANNELS={chat.id}</code>"
        
        await message.reply_text(text, quote=True)
    else:
        await message.reply_text(
            "❌ <b>This is not a forwarded message from a channel!</b>\n\n"
            "Please forward a message from your channel.",
            quote=True
        )
