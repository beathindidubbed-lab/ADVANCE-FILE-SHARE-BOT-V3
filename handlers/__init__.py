"""
Handlers Package
================

This package contains all message and callback handlers for the bot.

Structure:
---------
- start.py: /start, /help, /about, /ping commands
- admin.py: Admin management commands
- files.py: File operations (/genlink, /batch, etc.)
- settings.py: Settings panel commands
- fsub.py: Force subscribe management
- callback.py: All callback query handlers
- messages.py: Text message handlers

Usage:
------
from handlers import register_all_handlers
register_all_handlers(bot)
"""

from .admin import register_admin_handlers
from .settings import register_settings_handlers
from .fsub import register_fsub_handlers
from .messages import register_message_handlers

def register_all_handlers(bot):
    """
    Register all handlers with the bot instance
    
    Args:
        bot: Bot instance to register handlers with
    """
    # Register admin handlers
    register_admin_handlers(bot)
    
    # Register settings handlers
    register_settings_handlers(bot)
    
    # Register force subscribe handlers
    register_fsub_handlers(bot)
    
    # Register message handlers (must be last - catches non-command text)
    register_message_handlers(bot)
    
    # TODO: Add remaining handler registrations
    # register_start_handlers(bot)
    # register_file_handlers(bot)
    # register_callback_handlers(bot)

__all__ = [
    'register_all_handlers',
    'register_admin_handlers',
    'register_settings_handlers',
    'register_fsub_handlers',
    'register_message_handlers',
]
