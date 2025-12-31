"""
Advanced Auto Filter Bot V3
FIXED FOR RENDER: Runs web server + bot together
"""

import sys
import logging
import asyncio
from aiohttp import web
from pyrogram import Client, filters, idle
from pyrogram.enums import ParseMode
from pyrogram.types import Message

try:
    from pyromod import listen
except ImportError:
    print("ERROR: pyromod not installed!")
    sys.exit(1)

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
            workers=WORKERS,
            parse_mode=ParseMode.HTML
        )
        self.LOGGER = LOGGER
        self.db_channel = None
        self.db_channel_id = None

    async def start(self):
        await super().start()
        
        me = await self.get_me()
        self.username = me.username
        self.id = me.id
        self.mention = me.mention
        self.first_name = me.first_name
        
        LOGGER.info(f"✅ Bot Started: @{me.username}")
        
        # Connect database
        try:
            from database.database import Database
            self.db = Database()
            await self.db.connect()
            LOGGER.info("✅ Database Connected")
        except Exception as e:
            LOGGER.warning(f"⚠️ Database: {e}")
            self.db = None
        
        # Register handlers
        self.register_handlers()
        
        LOGGER.info("")
        LOGGER.info("=" * 70)
        LOGGER.info("🎉 BOT IS READY AND WILL RESPOND!")
        LOGGER.info(f"   Bot: @{self.username}")
        LOGGER.info(f"   ID: {self.id}")
        LOGGER.info("=" * 70)
        LOGGER.info("")
    
    def register_handlers(self):
        """Register all handlers"""
        
        LOGGER.info("📝 Registering handlers...")
        
        # /start command
        @self.on_message(filters.command("start") & filters.private)
        async def start_handler(client, message: Message):
            LOGGER.info(f"📨 /start from {message.from_user.id}")
            await message.reply_text(
                f"✅ <b>BOT IS WORKING!</b>\n\n"
                f"👋 Hello {message.from_user.first_name}!\n\n"
                f"<b>Bot:</b> @{client.username}\n"
                f"<b>Your ID:</b> <code>{message.from_user.id}</code>\n\n"
                f"🟢 I'm online and responding!\n\n"
                f"<b>Try these commands:</b>\n"
                f"• /test - Test bot\n"
                f"• /ping - Check status\n"
                f"• /help - Get help",
                quote=True
            )
        
        # /test command
        @self.on_message(filters.command("test") & filters.private)
        async def test_handler(client, message: Message):
            LOGGER.info(f"📨 /test from {message.from_user.id}")
            await message.reply_text(
                f"✅ <b>TEST SUCCESSFUL!</b>\n\n"
                f"<b>User:</b> {message.from_user.first_name}\n"
                f"<b>ID:</b> <code>{message.from_user.id}</code>\n"
                f"<b>Bot:</b> @{client.username}\n\n"
                f"🎉 Everything is working perfectly!",
                quote=True
            )
        
        # /ping command
        @self.on_message(filters.command("ping") & filters.private)
        async def ping_handler(client, message: Message):
            LOGGER.info(f"📨 /ping from {message.from_user.id}")
            await message.reply_text("🏓 <b>PONG!</b>\n\nBot is alive!", quote=True)
        
        # /help command
        @self.on_message(filters.command("help") & filters.private)
        async def help_handler(client, message: Message):
            await message.reply_text(
                f"📚 <b>HELP MENU</b>\n\n"
                f"<b>Available Commands:</b>\n"
                f"• /start - Start bot\n"
                f"• /test - Test functionality\n"
                f"• /ping - Check if online\n"
                f"• /help - This menu\n\n"
                f"<b>Bot Status:</b> 🟢 Online",
                quote=True
            )
        
        # Catch other text
        @self.on_message(filters.private & filters.text)
        async def text_handler(client, message: Message):
            LOGGER.info(f"📨 Text from {message.from_user.id}: {message.text}")
            
            text = message.text.lower()
            if text in ['hi', 'hello', 'hey', 'test']:
                await message.reply_text(
                    f"👋 Hey {message.from_user.first_name}!\n\n"
                    f"I'm working! Try /start",
                    quote=True
                )
        
        LOGGER.info("✅ Handlers registered! Bot will respond now!")

    async def stop(self, *args):
        await super().stop()
        LOGGER.info("❌ Bot Stopped")


# Web server for Render (keeps service alive)
async def handle_health(request):
    """Health check endpoint"""
    return web.Response(text="Bot is running!")

async def handle_root(request):
    """Root endpoint"""
    return web.Response(text="Telegram Bot is Online!")


async def start_web_server():
    """Start web server for Render"""
    import os
    
    app = web.Application()
    app.router.add_get('/', handle_root)
    app.router.add_get('/health', handle_health)
    
    # Render provides PORT environment variable
    port = int(os.environ.get('PORT', 8080))
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    LOGGER.info(f"🌐 Web server started on port {port}")
    return runner


async def main():
    """Main function - runs bot + web server"""
    
    ascii_art = """
██████╗░███████╗░█████╗░████████╗░░░█████╗░███╗░░██╗██╗███╗░░░███╗███████╗
██╔══██╗██╔════╝██╔══██╗╚══██╔══╝░░██╔══██╗████╗░██║██║████╗░████║██╔════╝
██████╦╝█████╗░░███████║░░░██║░░░░░███████║██╔██╗██║██║██╔████╔██║█████╗░░
██╔══██╗██╔══╝░░██╔══██║░░░██║░░░░░██╔══██║██║╚████║██║██║╚██╔╝██║██╔══╝░░
██████╦╝███████╗██║░░██║░░░██║░░░░░██║░░██║██║░╚███║██║██║░╚═╝░██║███████╗
╚═════╝░╚══════╝╚═╝░░╚═╝░░░╚═╝░░░░░╚═╝░░╚═╝╚═╝░░╚══╝╚═╝╚═╝░░░░░╚═╝╚══════╝
"""
    
    print(ascii_art)
    print("\n" + "=" * 70)
    print("🚀 Starting Bot with Web Server...")
    print("=" * 70 + "\n")
    
    bot = Bot()
    web_runner = None
    
    try:
        # Start web server (for Render)
        web_runner = await start_web_server()
        LOGGER.info("✅ Web server running")
        
        # Start bot
        await bot.start()
        LOGGER.info("✅ Bot running")
        
        # Keep running
        LOGGER.info("🔥 Everything is running! Send /start to bot!")
        await idle()
        
    except KeyboardInterrupt:
        LOGGER.info("⚠️ Stopped by user")
    except Exception as e:
        LOGGER.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if web_runner:
            await web_runner.cleanup()
        await bot.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("👋 Bye!")
