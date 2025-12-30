"""
Advanced Auto Filter Bot V3
CORRECTED - Using YOUR bot's structure (not VJ-Filter-Bot)
"""

import asyncio
import logging
from pyrogram import Client, idle
from pyrogram.enums import ParseMode

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
            plugins={"root": "plugins"},  # ✅ CRITICAL: This enables auto-discovery
            workers=WORKERS,
            parse_mode=ParseMode.HTML
        )
        self.LOGGER = LOGGER

    async def start(self):
        from config import LOG_CHANNEL, CHANNELS
        from utils import temp
        
        await super().start()
        
        me = await self.get_me()
        self.username = me.username
        self.id = me.id
        self.mention = me.mention
        self.first_name = me.first_name
        
        # Set temp variables for plugins to use
        temp.ME = me.id
        temp.U_NAME = me.username
        temp.B_NAME = me.first_name
        temp.BOT = self
        
        LOGGER.info(f"✅ Bot Started as @{me.username}")
        
        # Try to connect database (don't fail if it doesn't exist)
        try:
            from database.database import Database
            self.db = Database()
            await self.db.connect()
            LOGGER.info("✅ Database Connected")
        except Exception as e:
            LOGGER.warning(f"⚠️ Database not available: {e}")
            self.db = None
        
        # Setup channels
        if CHANNELS:
            LOGGER.info(f"📁 File Channels Configured: {len(CHANNELS)}")
            self.db_channel_id = CHANNELS[0]
            try:
                self.db_channel = await self.get_chat(self.db_channel_id)
                LOGGER.info(f"✅ DB Channel: {self.db_channel.title}")
            except Exception as e:
                LOGGER.error(f"❌ Channel error: {e}")
                self.db_channel = None
        else:
            LOGGER.warning("⚠️ No file channels configured!")
            self.db_channel_id = None
        
        # Log channel notification
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
        LOGGER.info(f"   Database: {'✅' if self.db else '⚠️ Not connected'}")
        LOGGER.info("=" * 50)
        LOGGER.info("")

    async def stop(self, *args):
        await super().stop()
        LOGGER.info("❌ Bot Stopped!")

# Create bot instance
bot = Bot()

async def main():
    """Start the bot"""
    try:
        await bot.start()
        LOGGER.info("🔥 Running...")
        await idle()
    except KeyboardInterrupt:
        LOGGER.info("Stopped by user")
    except Exception as e:
        LOGGER.error(f"❌ Error: {e}")
    finally:
        await bot.stop()

if __name__ == "__main__":
    asyncio.run(main())
