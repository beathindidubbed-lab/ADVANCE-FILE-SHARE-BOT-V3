"""
Features Package
================

Advanced bot features:
- auto_delete.py: THREE auto-delete features system
- broadcast.py: Broadcast messaging system
- batch.py: Batch file operations

Each feature is self-contained and can be easily enabled/disabled.
"""

from .auto_delete import AutoDeleteManager

__all__ = [
    'AutoDeleteManager',
]
