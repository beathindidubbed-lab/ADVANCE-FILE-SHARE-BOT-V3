# ============================================================================
# handlers/__init__.py
# ============================================================================
"""
Handlers Package Initialization
Registers all handlers with the bot
"""

def register_all_handlers(bot):
    """Register all handlers with bot instance"""
    from handlers import start, callback, files, settings, admin, fsub, messages
    
    start.register(bot)
    callback.register(bot)
    files.register(bot)
    settings.register(bot)
    admin.register(bot)
    fsub.register(bot)
    messages.register(bot)

