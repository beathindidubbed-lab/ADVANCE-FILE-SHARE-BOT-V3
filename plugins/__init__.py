"""
Plugins Initialization
Import all plugin modules to register handlers
"""

# Import all plugins
from . import start
from . import callbacks
from . import admin_commands
from . import batch
from . import genlink
from . import custom_batch
from . import channel_post
from . import settings
from . import shortener
from . import special_link

# List all modules
__all__ = [
    'start',
    'callbacks',
    'admin_commands',
    'batch',
    'genlink',
    'custom_batch',
    'channel_post',
    'settings',
    'shortener',
    'special_link'
]

print("✅ All plugins loaded successfully!")
