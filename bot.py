"""
Advanced Auto Filter Bot V3
FIXED - Plugins will load properly with manual import system
"""

import sys
import glob
import importlib
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


class Bot(Client):
    def __init__(self):
        from config import API_ID, API_HASH, BOT_TOKEN, WORKERS
        
        super().__init__(
            name="AdvanceAutoFilterBot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=WORKERS,
            parse_mode=ParseMode.HTML,
            plugins=None  # We'll load manually
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
        
        # Connect to database
        try:
            from database.database import Database
            self.db = Database()
            await self.db.connect()
            LOGGER.info("✅ Database Connected")
        except Exception as e:
            LOGGER.error(f"❌ Database Error: {e}")
            self.db = None
        
        # Setup channels
        if CHANNELS:
            LOGGER.info(f"📁 File Channels Configured: {len(CHANNELS)}")
            self.db_channel_id = CHANNELS[0]
            
            # Get channel details
            try:
                await self.get_db_channel()
            except Exception as e:
                LOGGER.error(f"❌ Error getting channel: {e}")
        else:
            LOGGER.warning("⚠️ No file channels configured!")
            self.db_channel_id = None
        
        if FORCE_SUB_CHANNELS:
            LOGGER.info(f"📢 Force-Sub Channels: {len(FORCE_SUB_CHANNELS)}")
        
        # Send log message
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
        
        # Load plugins manually
        await self.load_plugins()
        
        LOGGER.info("")
        LOGGER.info("=" * 50)
        LOGGER.info("🔥 BOT IS READY!")
        LOGGER.info(f"   Bot: @{me.username}")
        LOGGER.info(f"   Database: {'✅' if self.db else '❌'}")
        LOGGER.info(f"   Plugins: ✅ Loaded")
        LOGGER.info("=" * 50)
        LOGGER.info("")
    
    async def load_plugins(self):
        """Load all plugins manually"""
        LOGGER.info("📦 Loading plugins...")
        
        plugins_dir = Path("plugins")
        
        if not plugins_dir.exists():
            LOGGER.error("❌ Plugins directory not found!")
            return
        
        # Get all Python files in plugins directory
        plugin_files = list(plugins_dir.glob("*.py"))
        
        if not plugin_files:
            LOGGER.warning("⚠️ No plugin files found!")
            return
        
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
    
    async def get_db_channel(self):
        """Get database channel details"""
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


# Create bot instance
bot = Bot()


async def start_bot():
    """Start the bot"""
    print(ascii_art)
    LOGGER.info("🚀 Starting bot...")
    
    try:
        await bot.start()
        LOGGER.info("🔥 Bot is running...")
        await idle()
    except KeyboardInterrupt:
        LOGGER.info("⚠️ Keyboard interrupt received")
    except Exception as e:
        LOGGER.error(f"❌ Error: {e}")
    finally:
        await bot.stop()


if __name__ == "__main__":
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        LOGGER.info("👋 Stopped by user")
    except Exception as e:
        LOGGER.error(f"❌ Fatal error: {e}")
