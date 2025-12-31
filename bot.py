"""
Advanced Auto Filter Bot V3
FIXED FOR RENDER: Runs web server + bot together
"""

import sys
import logging
import asyncio
import os
import glob
import importlib
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
        
        LOGGER.info("")
        LOGGER.info("=" * 70)
        LOGGER.info("🎉 BOT IS READY!")
        LOGGER.info(f"   Bot: @{self.username}")
        LOGGER.info(f"   ID: {self.id}")
        LOGGER.info("   All plugins loaded!")
        LOGGER.info("=" * 70)
        LOGGER.info("")

    async def stop(self, *args):
        await super().stop()
        LOGGER.info("❌ Bot Stopped")


def load_plugins():
    """Load all plugins from plugins folder"""
    LOGGER.info("📦 Loading plugins...")
    
    plugins_dir = "plugins"
    if not os.path.exists(plugins_dir):
        LOGGER.warning(f"⚠️ {plugins_dir} folder not found!")
        return 0
    
    plugin_files = glob.glob(f"{plugins_dir}/*.py")
    loaded = 0
    
    for file_path in plugin_files:
        plugin_name = os.path.basename(file_path)[:-3]  # Remove .py
        
        # Skip __init__ and certain debug files
        if plugin_name in ['__init__', 'debug_emergency', 'verbose_logger', 'ultra_simple']:
            continue
        
        try:
            module_name = f"plugins.{plugin_name}"
            importlib.import_module(module_name)
            LOGGER.info(f"  ✅ Loaded: {plugin_name}")
            loaded += 1
        except Exception as e:
            LOGGER.error(f"  ❌ Failed to load {plugin_name}: {e}")
    
    LOGGER.info(f"✅ Loaded {loaded} plugins!")
    return loaded


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
    
    # Load plugins FIRST
    load_plugins()
    
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
