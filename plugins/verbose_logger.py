"""
MAXIMUM VERBOSITY - Logs EVERYTHING
"""

from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineQuery
import logging

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@Client.on_message()
async def log_all_messages(client: Client, message: Message):
    """Logs EVERY single message received"""
    
    logger.info("=" * 80)
    logger.info("MESSAGE RECEIVED!")
    logger.info(f"Chat ID: {message.chat.id}")
    logger.info(f"Chat Type: {message.chat.type}")
    logger.info(f"From User: {message.from_user.first_name if message.from_user else 'None'}")
    logger.info(f"User ID: {message.from_user.id if message.from_user else 'None'}")
    logger.info(f"Text: {message.text}")
    logger.info(f"Message ID: {message.id}")
    logger.info("=" * 80)
    
    # Also print to console
    print("=" * 80)
    print("🔔 MESSAGE RECEIVED!")
    print(f"From: {message.from_user.first_name if message.from_user else 'Unknown'}")
    print(f"User ID: {message.from_user.id if message.from_user else 'Unknown'}")
    print(f"Text: {message.text}")
    print(f"Chat Type: {message.chat.type}")
    print("=" * 80)
    
    # Try to respond
    try:
        await message.reply_text(
            f"✅ <b>MESSAGE RECEIVED!</b>\n\n"
            f"<b>Your message:</b> {message.text}\n"
            f"<b>Your ID:</b> <code>{message.from_user.id}</code>\n"
            f"<b>Chat Type:</b> {message.chat.type}\n\n"
            f"<b>Bot is definitely working!</b>",
            quote=True
        )
        print("✅ Response sent successfully!")
    except Exception as e:
        print(f"❌ Failed to respond: {e}")
        logger.error(f"Failed to respond: {e}")

@Client.on_callback_query()
async def log_callbacks(client: Client, query: CallbackQuery):
    """Logs all callback queries"""
    print(f"🔘 CALLBACK: {query.data} from {query.from_user.id}")

@Client.on_inline_query()
async def log_inline(client: Client, query: InlineQuery):
    """Logs all inline queries"""
    print(f"🔍 INLINE QUERY: {query.query} from {query.from_user.id}")
