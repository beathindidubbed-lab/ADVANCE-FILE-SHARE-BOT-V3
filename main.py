"""
Advanced Auto Filter Bot V3
Complete EvaMaria-style bot with beautiful interactive UI
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
        
        # Verify channels
        for channel_id in CHANNELS:
            try:
                chat = await self.get_chat(channel_id)
                self.db_channel = chat
                LOGGER.info(f"✅ File Channel: {chat.title}")
            except Exception as e:
                LOGGER.warning(f"⚠️ Channel {channel_id}: {e}")
        
        # Verify force sub channels
        for channel_id in FORCE_SUB_CHANNELS:
            if channel_id:
                try:
                    chat = await self.get_chat(channel_id)
                    # Try to get invite link
                    try:
                        invite = await self.create_chat_invite_link(channel_id)
                        self.invitelink = invite.invite_link
                    except:
                        self.invitelink = f"https://t.me/{chat.username}" if chat.username else None
                    LOGGER.info(f"✅ Force Sub: {chat.title}")
                except Exception as e:
                    LOGGER.warning(f"⚠️ Force Sub {channel_id}: {e}")
        
        # Log channel notification
        if LOG_CHANNEL:
            try:
                await self.send_message(
                    LOG_CHANNEL,
                    f"<b>🤖 Bot Started Successfully!</b>\n\n"
                    f"<b>Bot:</b> @{me.username}\n"
                    f"<b>Name:</b> {me.first_name}\n"
                    f"<b>ID:</b> <code>{me.id}</code>\n"
                    f"<b>Mention:</b> {me.mention}"
                )
            except:
                pass

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
