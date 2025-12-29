"""
Advanced Auto Filter Bot V3
FINAL - Plugins will load properly
"""

import asyncio
import logging
from pyrogram import Client, idle
from pyrogram.enums import ParseMode
from pyromod import listen

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
            plugins={"root": "plugins"},
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
        
        try:
            from database.database import Database
            self.db = Database()
            await self.db.connect()
            LOGGER.info("✅ Database Connected")
        except Exception as e:
            LOGGER.error(f"❌ Database Error: {e}")
            self.db = None
        
        if CHANNELS:
            LOGGER.info(f"📁 File Channels Configured: {len(CHANNELS)}")
            self.db_channel_id = CHANNELS[0]
        else:
            LOGGER.warning("⚠️ No file channels configured!")
            self.db_channel_id = None
        
        if FORCE_SUB_CHANNELS:
            LOGGER.info(f"📢 Force-Sub Channels Configured: {len(FORCE_SUB_CHANNELS)}")
        
        if LOG_CHANNEL and LOG_CHANNEL != 0:
            try:
                await self.send_message(
                    LOG_CHANNEL,
                    f"<b>🤖 Bot Started!</b>\n\n"
                    f"<b>Bot:</b> @{me.username}\n"
                    f"<b>Status:</b> ✅ Online"
                )
                LOGGER.info("✅ Log channel notified")
            except Exception as e:
                LOGGER.warning(f"⚠️ Log channel error: {e}")
        
        LOGGER.info("")
        LOGGER.info("=" * 50)
        LOGGER.info("🔥 BOT IS READY!")
        LOGGER.info(f"   Bot: @{me.username}")
        LOGGER.info(f"   Database: {'✅' if self.db else '❌'}")
        LOGGER.info("=" * 50)
        LOGGER.info("")
    
    async def get_db_channel(self):
        if hasattr(self, 'db_channel'):
            return self.db_channel
        
        if not self.db_channel_id:
            LOGGER.error("❌ No database channel!")
            return None
        
        try:
            self.db_channel = await self.get_chat(self.db_channel_id)
            LOGGER.info(f"✅ Channel: {self.db_channel.title}")
            return self.db_channel
        except Exception as e:
            LOGGER.error(f"❌ Channel error: {e}")
            return None

    async def stop(self, *args):
        await super().stop()
        LOGGER.info("❌ Bot Stopped!")

bot = Bot()

async def start_bot():
    await bot.start()
    LOGGER.info("🔥 Running...")
    await idle()
    await bot.stop()

if __name__ == "__main__":
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        LOGGER.info("Stopped by user")
