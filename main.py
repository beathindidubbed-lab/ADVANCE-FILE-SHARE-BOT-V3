#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main Entry Point - Advanced Auto Filter Bot V3
Modular Structure with Three Auto-Delete Features
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from bot.bot_client import Bot
from config import BOT_PICS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ASCII Art Banner
BANNER = r"""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║ ██████╗░███████╗░█████╗░████████╗░░░█████╗░███╗░░██╗██╗███╗░░░███╗███████╗  ║
║ ██╔══██╗██╔════╝██╔══██╗╚══██╔══╝░░██╔══██╗████╗░██║██║████╗░████║██╔════╝   ║
║ ██████╦╝█████╗░░███████║░░░██║░░░░░███████║██╔██╗██║██║██╔████╔██║█████╗░░   ║
║ ██╔══██╗██╔══╝░░██╔══██║░░░██║░░░░░██╔══██║██║╚████║██║██║╚██╔╝██║██╔══╝░░   ║
║ ██████╦╝███████╗██║░░██║░░░██║░░░░░██║░░██║██║░╚███║██║██║░╚═╝░██║███████╗   ║
║ ╚═════╝░╚══════╝╚═╝░░╚═╝░░░╚═╝░░░░░╚═╝░░╚═╝╚═╝░░╚══╝╚═╝╚═╝░░░░░╚═╝╚══════╝   ║
║                                                                             ║
║               𝙁𝙄𝙇𝙀 𝙎𝙃𝘼𝙍𝙄𝙉𝙂 𝘽𝙊𝙏 - 𝙏𝙃𝙍𝙀𝙀 𝘼𝙐𝙏𝙊-𝘿𝙀𝙇𝙀𝙏𝙀 𝙁𝙀𝘼𝙏𝙐𝙍𝙀𝙎              ║
║               𝘽𝙇𝙊𝘾𝙆𝙌𝙐𝙊𝙏𝙀 𝙀𝙓𝙋𝘼𝙉𝘿𝘼𝘽𝙇𝙀 𝙎𝙐𝙋𝙋𝙊𝙍𝙏                            ║
╚════════════════════════════════════════════════════════════════════════════╝
"""


async def main():
    """Main function to start the bot"""
    print(BANNER)
    logger.info("=" * 70)
    logger.info("🤖 FILE SHARING BOT - MODULAR STRUCTURE")
    logger.info("=" * 70)
    
    # Create and start bot
    bot = Bot()
    
    try:
        # Start the bot
        logger.info("Starting bot...")
        await bot.start()
        logger.info("✅ Bot started successfully!")
        
        # Keep running
        logger.info("Bot is now running. Press Ctrl+C to stop.")
        await asyncio.Event().wait()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        logger.info("Stopping bot...")
        await bot.stop()
        logger.info("Bot stopped successfully")


if __name__ == "__main__":
    # Run the bot
    asyncio.run(main())
