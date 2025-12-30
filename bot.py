"""
Advanced Auto Filter Bot V3
WORKS WITHOUT CHANNEL - Configure channel later from bot commands!
"""

import sys
import glob
import importlib
import importlib.util
import logging
import asyncio
from pathlib import Path
from pyrogram import Client, idle
from pyrogram.enums import ParseMode

# CRITICAL: Import pyromod for listen() functionality
try:
    from pyromod import listen
except ImportError:
    print("ERROR: pyromod not installed!")
    print("Install it: pip install pyromod")
    sys.exit(1)

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


def load_plugins_sync():
    """Load all plugins BEFORE bot starts (synchronous)"""
    LOGGER.info("📦 Loading plugins...")
    
    plugins_dir = Path("plugins")
    
    if not plugins_dir.exists():
        LOGGER.error("❌ Plugins directory not found!")
        return 0, 0
    
    plugin_files = list(plugins_dir.glob("*.py"))
    
    if not plugin_files:
        LOGGER.warning("⚠️ No plugin files found!")
        return 0, 0
    
    loaded = 0
    failed = 0
    
    for plugin_file in plugin_files:
        plugin_name = plugin_file.stem
        
        # Skip __init__.py
        if plugin_name.startswith("__"):
            continue
        
        try:
            # Import the plugin module
            import_path = f"plugins.{plugin_name}"
            
            # Check if already imported
            if import_path in sys.modules:
                # Reload if already imported
                importlib.reload(sys.modules[import_path])
            else:
                # Import for first time
                spec = importlib.util.spec_from_file_location(
                    import_path,
                    plugin_file
                )
                module = importlib.util.module_from_spec(spec)
                sys.modules[import_path] = module
                spec.loader.exec_module(module)
            
            LOGGER.info(f"   ✅ Loaded: {plugin_name}")
            loaded += 1
            
        except Exception as e:
            LOGGER.error(f"   ❌ Failed: {plugin_name} - {e}")
            failed += 1
    
    LOGGER.info(f"📦 Plugins loaded: {loaded} ✅ | {failed} ❌")
    return loaded, failed


class Bot(Client):
    def __init__(self):
        from config import API_ID, API_HASH, BOT_TOKEN, WORKERS
        
        # Load plugins BEFORE initializing Client
        LOGGER.info("🔧 Pre-loading plugins...")
        self.plugins_loaded, self.plugins_failed = load_plugins_sync()
        
        super().__init__(
            name="AdvanceAutoFilterBot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=WORKERS,
            parse_mode=ParseMode.HTML
        )
        self.LOGGER = LOGGER
        
        # Initialize channel as None - can be set later
        self.db_channel = None
        self.db_channel_id = None

    async def start(self):
        from config import LOG_CHANNEL, CHANNELS, FORCE_SUB_CHANNELS
        
        await super().start()
        
        me = await self.get_me()
        self.username = me.username
        self.id = me.id
        self.mention = me.mention
        self.first_name = me.first_name
        
        LOGGER.info(f"✅ Bot Started as @{me.username}")
        
        # Connect to database
        try:
            from database.database import Database
            self.db = Database()
            await self.db.connect()
            LOGGER.info("✅ Database Connected")
        except Exception as e:
            LOGGER.error(f"❌ Database Error: {e}")
            LOGGER.warning("⚠️ Bot will continue without database")
            self.db = None
        
        # Try to setup channel but DON'T FAIL if it doesn't work
        if CHANNELS and CHANNELS[0] != 0:
            LOGGER.info(f"📁 Attempting to configure channel...")
            self.db_channel_id = CHANNELS[0]
            asyncio.create_task(self.try_setup_channel())
        else:
            LOGGER.info("⚠️ No channel configured - use /setchannel command later")
        
        if FORCE_SUB_CHANNELS:
            LOGGER.info(f"📢 Force-Sub Channels: {len(FORCE_SUB_CHANNELS)}")
        
        # Send log message (non-blocking)
        if LOG_CHANNEL and LOG_CHANNEL != 0:
            asyncio.create_task(self.send_log_notification())
        
        LOGGER.info("")
        LOGGER.info("=" * 70)
        LOGGER.info("🎉 BOT IS RUNNING AND READY!")
        LOGGER.info("=" * 70)
        LOGGER.info(f"   ✅ Bot: @{me.username}")
        LOGGER.info(f"   ✅ Bot ID: {me.id}")
        LOGGER.info(f"   ✅ Plugins: {self.plugins_loaded} loaded")
        LOGGER.info(f"   ✅ Database: {'Connected' if self.db else 'Disabled'}")
        LOGGER.info(f"   ⚙️ Channel: {'Checking...' if self.db_channel_id else 'Not configured yet'}")
        LOGGER.info("")
        LOGGER.info("💡 TRY THESE COMMANDS NOW:")
        LOGGER.info("   👉 /start  - Start the bot")
        LOGGER.info("   👉 /test   - Test bot response")
        LOGGER.info("   👉 /help   - Get help")
        LOGGER.info("   👉 /setchannel - Configure channel (admin only)")
        LOGGER.info("")
        LOGGER.info("🟢 BOT IS ONLINE AND RESPONDING!")
        LOGGER.info("=" * 70)
        LOGGER.info("")
    
    async def try_setup_channel(self):
        """Try to setup channel but don't fail if it doesn't work"""
        try:
            await asyncio.sleep(3)
            self.db_channel = await self.get_chat(self.db_channel_id)
            LOGGER.info(f"✅ Channel Connected: {self.db_channel.title}")
            LOGGER.info(f"   Channel ID: {self.db_channel.id}")
        except Exception as e:
            LOGGER.warning(f"⚠️ Channel setup failed: {e}")
            LOGGER.warning(f"⚠️ Don't worry! Use /setchannel command to configure it later")
            LOGGER.warning(f"⚠️ Bot will work for other commands")
            self.db_channel = None
    
    async def send_log_notification(self):
        """Send log notification in background"""
        from config import LOG_CHANNEL
        try:
            await asyncio.sleep(1)
            await self.send_message(
                LOG_CHANNEL,
                f"<b>🤖 Bot Started!</b>\n\n"
                f"<b>Bot:</b> @{self.username}\n"
                f"<b>Plugins:</b> {self.plugins_loaded} loaded\n"
                f"<b>Status:</b> ✅ Online"
            )
            LOGGER.info("✅ Log channel notified")
        except Exception as e:
            LOGGER.warning(f"⚠️ Log channel error: {e}")
    
    async def get_db_channel(self):
        """Get database channel details"""
        return self.db_channel

    async def stop(self, *args):
        await super().stop()
        LOGGER.info("❌ Bot Stopped!")


# Create bot instance
bot = Bot()


async def start_bot():
    """Start the bot"""
    print(ascii_art)
    LOGGER.info("🚀 Starting bot...")
    
    try:
        await bot.start()
        LOGGER.info("🔥 Bot is fully operational!")
        LOGGER.info("🔥 Send /start to your bot now!")
        await idle()
    except KeyboardInterrupt:
        LOGGER.info("⚠️ Keyboard interrupt received")
    except Exception as e:
        LOGGER.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await bot.stop()


if __name__ == "__main__":
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        LOGGER.info("👋 Stopped by user")
    except Exception as e:
        LOGGER.error(f"❌ Fatal error: {e}")
