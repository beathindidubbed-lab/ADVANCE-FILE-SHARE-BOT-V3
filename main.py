"""
Advanced Auto Filter Bot V3
Complete EvaMaria-style bot with beautiful interactive UI
FIXED VERSION - Better channel handling
"""

import asyncio
import logging
from pyrogram import Client, idle
from pyrogram.enums import ParseMode

ascii_art = """
██████╗░███████╗░█████╗░████████╗░░░█████╗░███╗░░██╗██╗███╗░░░███╗███████╗
██╔══██╗██╔════╝██╔══██╗╚══██╔══╝░░██╔══██╗████╗░██║██║████╗░████║██╔════╝
██████╦╝█████╗░░███████║░░░██║░░░░░███████║██╔██╗██║██║██╔████╔██║█████╗░░
██╔══██╗██╔══╝░░██╔══██║░░░██║░░░░░██╔══██║██║╚████║██║██║╚██╔╝██║██╔══╝░░
██████╦╝███████╗██║░░██║░░░██║░░░░░██║░░██║██║░╚███║██║██║░╚═╝░██║███████╗
╚═════╝░╚══════╝╚═╝░░╚═╝░░░╚═╝░░░░░╚═╝░░╚═╝╚═╝░░╚══╝╚═╝╚═╝░░░░░╚═╝╚══════╝
"""

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S'
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
LOGGER = logging.getLogger(__name__)

class Bot(Client):
    def __init__(self):
        from config import API_ID, API_HASH, BOT_TOKEN, WORKERS
        super().__init__(
            name="AdvanceAutoFilterBot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="plugins"),
            workers=WORKERS,
            parse_mode=ParseMode.HTML
        )
        self.LOGGER = LOGGER

    async def start(self):
        from config import LOG_CHANNEL, CHANNELS, FORCE_SUB_CHANNELS
        await super().start()
        me = await self.get_me()
        
        self.username = me.username
        self.id = me.id
        self.mention = me.mention
        self.first_name = me.first_name
        
        LOGGER.info(f"✅ Bot Started as @{me.username}")
        
        # Setup database
        try:
            from database.database import Database
            self.db = Database()
            await self.db.connect()
            LOGGER.info("✅ Database Connected")
        except Exception as e:
            LOGGER.error(f"❌ Database Error: {e}")
            self.db = None
        
        # Verify channels with better error handling
        channel_verified = False
        for channel_id in CHANNELS:
            try:
                LOGGER.info(f"🔄 Verifying channel {channel_id}...")
                
                # Try to get chat info
                chat = await self.get_chat(channel_id)
                self.db_channel = chat
                
                LOGGER.info(f"✅ Channel Found!")
                LOGGER.info(f"   📝 Title: {chat.title}")
                LOGGER.info(f"   🆔 ID: {channel_id}")
                LOGGER.info(f"   🔗 Type: {chat.type}")
                if chat.username:
                    LOGGER.info(f"   👤 Username: @{chat.username}")
                
                # Test bot permissions
                try:
                    me_member = await self.get_chat_member(channel_id, "me")
                    LOGGER.info(f"   🤖 Bot Status: {me_member.status}")
                    
                    if me_member.status == "administrator":
                        LOGGER.info(f"   ✅ Bot is Admin!")
                        if me_member.privileges:
                            LOGGER.info(f"   - Post Messages: {me_member.privileges.can_post_messages}")
                            LOGGER.info(f"   - Edit Messages: {me_member.privileges.can_edit_messages}")
                            LOGGER.info(f"   - Delete Messages: {me_member.privileges.can_delete_messages}")
                    else:
                        LOGGER.warning(f"   ⚠️ Bot is NOT admin! Status: {me_member.status}")
                        LOGGER.warning(f"   Please make bot admin in the channel!")
                except Exception as perm_error:
                    LOGGER.warning(f"   ⚠️ Cannot check bot permissions: {perm_error}")
                
                # Test by reading messages
                try:
                    message_count = 0
                    async for message in self.get_chat_history(channel_id, limit=1):
                        message_count += 1
                        LOGGER.info(f"   ✅ Channel Access Verified! (Found message ID: {message.id})")
                        break
                    
                    if message_count == 0:
                        LOGGER.warning(f"   ⚠️ Channel is empty or bot cannot read messages")
                        LOGGER.info(f"   💡 This is OK if channel is new. Bot can still work!")
                        
                except Exception as read_error:
                    LOGGER.warning(f"   ⚠️ Cannot read channel messages: {read_error}")
                    LOGGER.info(f"   💡 Bot may still work for sending files")
                
                channel_verified = True
                LOGGER.info(f"✅ File Channel Setup Complete!")
                break
                
            except Exception as e:
                LOGGER.error(f"❌ Error accessing channel {channel_id}")
                LOGGER.error(f"   Error: {e}")
                LOGGER.error(f"   ")
                LOGGER.error(f"   🔧 Troubleshooting Steps:")
                LOGGER.error(f"   1. Make sure bot is admin in the channel")
                LOGGER.error(f"   2. Give bot these permissions:")
                LOGGER.error(f"      - Post Messages")
                LOGGER.error(f"      - Edit Messages")
                LOGGER.error(f"      - Delete Messages")
                LOGGER.error(f"   3. Check if channel ID is correct")
                LOGGER.error(f"   4. Verify channel is not deleted")
                continue
        
        if not channel_verified:
            LOGGER.warning("⚠️ No valid channel found! Bot will run but file sharing won't work.")
            LOGGER.warning("   Please fix channel configuration and restart bot.")
        
        # Verify force sub channels
        if FORCE_SUB_CHANNELS:
            for idx, channel_id in enumerate(FORCE_SUB_CHANNELS, 1):
                if not channel_id or channel_id == 0:
                    continue
                    
                try:
                    LOGGER.info(f"🔄 Verifying force-sub channel {idx}: {channel_id}")
                    chat = await self.get_chat(channel_id)
                    LOGGER.info(f"   ✅ Channel: {chat.title}")
                    
                    # Try to get invite link
                    try:
                        invite = await self.create_chat_invite_link(channel_id)
                        self.invitelink = invite.invite_link
                        LOGGER.info(f"   ✅ Invite link created")
                    except:
                        if chat.username:
                            self.invitelink = f"https://t.me/{chat.username}"
                            LOGGER.info(f"   ✅ Using public link: @{chat.username}")
                        else:
                            LOGGER.warning(f"   ⚠️ Cannot create invite link")
                            
                    LOGGER.info(f"✅ Force-Sub Channel {idx} Ready!")
                    
                except Exception as e:
                    LOGGER.warning(f"⚠️ Force-sub channel {channel_id} error: {e}")
                    LOGGER.warning(f"   Force subscribe may not work for this channel")
        
        # Log channel notification
        if LOG_CHANNEL:
            try:
                await self.send_message(
                    LOG_CHANNEL,
                    f"<b>🤖 Bot Started Successfully!</b>\n\n"
                    f"<b>Bot:</b> @{me.username}\n"
                    f"<b>Name:</b> {me.first_name}\n"
                    f"<b>ID:</b> <code>{me.id}</code>\n"
                    f"<b>Mention:</b> {me.mention}\n\n"
                    f"<b>Status:</b> ✅ Online\n"
                    f"<b>Database:</b> {'✅ Connected' if self.db else '❌ Not Connected'}\n"
                    f"<b>File Channel:</b> {'✅ Ready' if channel_verified else '⚠️ Check Logs'}"
                )
                LOGGER.info("✅ Log channel notification sent")
            except Exception as e:
                LOGGER.warning(f"⚠️ Cannot send to log channel: {e}")
        
        LOGGER.info("")
        LOGGER.info("=" * 50)
        LOGGER.info("🔥 BOT IS READY!")
        LOGGER.info(f"   Bot: @{me.username}")
        LOGGER.info(f"   Database: {'✅' if self.db else '❌'}")
        LOGGER.info(f"   Channel: {'✅' if channel_verified else '❌'}")
        LOGGER.info("=" * 50)
        LOGGER.info("")

    async def stop(self, *args):
        await super().stop()
        LOGGER.info("❌ Bot Stopped!")

# Create bot instance
bot = Bot()

async def start_bot():
    await bot.start()
    LOGGER.info("🔥 Bot is running... Press Ctrl+C to stop")
    await idle()
    await bot.stop()

if __name__ == "__main__":
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        LOGGER.info("Bot Stopped by User")
