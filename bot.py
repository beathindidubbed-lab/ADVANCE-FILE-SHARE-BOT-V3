# bot.py - Import wrapper for Railway compatibility
# Railway expects main.py, but plugins import from bot
# This file bridges the gap

from main import bot, app

__all__ = ['bot', 'app']
