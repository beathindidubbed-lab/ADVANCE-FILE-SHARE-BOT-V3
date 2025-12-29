"""
Advanced Auto Filter Bot V3
FIXED VERSION - Channels verified only when first used (like VJ-Filter-Bot)
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
        
        # Start the client
        await super().start()
        
        # Get bot info
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
        
        # DON'T verify channels on startup - just save them
        # They'll be verified when first used (lazy loading like VJ-Filter-Bot)
        if CHANNELS:
            LOGGER.info(f"📁 File Channels Configured: {len(CHANNELS)}")
            # Just save the first channel ID for later use
            self.db_channel_id = CHANNELS[0]
        else:
            LOGGER.warning("⚠️ No file channels configured!")
            self.db_channel_id = None
        
        # Same for force sub channels
        if FORCE_SUB_CHANNELS:
            LOGGER.info(f"📢 Force-Sub Channels Configured: {len(FORCE_SUB_CHANNELS)}")
        
        # Log channel notification
        if LOG_CHANNEL:
            try:
                await self.send_message(
                    LOG_CHANNEL,
                    f"<b>🤖 Bot Started Successfully!</b>\n\n"
                    f"<b>Bot:</b> @{me.username}\n"
                    f"<b>Name:</b> {me.first_name}\n"
                    f"<b>ID:</b> <code>{me.id}</code>\n\n"
                    f"<b>Status:</b> ✅ Online\n"
                    f"<b>Database:</b> {'✅ Connected' if self.db else '❌ Not Connected'}\n"
                    f"<b>File Channels:</b> {len(CHANNELS) if CHANNELS else 0}"
                )
                LOGGER.info("✅ Log channel notification sent")
            except Exception as e:
                LOGGER.warning(f"⚠️ Cannot send to log channel: {e}")
        
        LOGGER.info("")
        LOGGER.info("=" * 50)
        LOGGER.info("🔥 BOT IS READY!")
        LOGGER.info(f"   Bot: @{me.username}")
        LOGGER.info(f"   Database: {'✅' if self.db else '❌'}")
        LOGGER.info(f"   Channels: {len(CHANNELS) if CHANNELS else 0} configured")
        LOGGER.info("=" * 50)
        LOGGER.info("")
        LOGGER.info("💡 Channels will be verified when first used")
        LOGGER.info("")
    
    async def get_db_channel(self):
        """Get database channel (lazy loading - only called when needed)"""
        if hasattr(self, 'db_channel'):
            return self.db_channel
        
        if not self.db_channel_id:
            LOGGER.error("❌ No database channel configured!")
            return None
        
        # First time accessing - verify channel now
        try:
            LOGGER.info(f"🔄 Connecting to database channel {self.db_channel_id}...")
            self.db_channel = await self.get_chat(self.db_channel_id)
            LOGGER.info(f"✅ Database Channel Connected: {self.db_channel.title}")
            return self.db_channel
        except Exception as e:
            LOGGER.error(f"❌ Error accessing database channel: {e}")
            LOGGER.error(f"   Channel ID: {self.db_channel_id}")
            LOGGER.error(f"   Make sure:")
            LOGGER.error(f"   1. Bot is admin in the channel")
            LOGGER.error(f"   2. Channel ID is correct")
            LOGGER.error(f"   3. Bot has required permissions")
            return None

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
