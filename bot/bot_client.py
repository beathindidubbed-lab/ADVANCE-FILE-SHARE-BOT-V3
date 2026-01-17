#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot Client - Main Bot Class
Manages bot instance, handlers, and features
"""

import logging
import asyncio
import datetime
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, UserNotParticipant

# Import configurations
from config import (
    API_ID, API_HASH, BOT_TOKEN, WORKERS,
    ADMINS, CHANNELS, FORCE_SUB_CHANNELS,
    BOT_PICS, WELCOME_TEXT, HELP_TEXT, ABOUT_TEXT
)

# Import database
from database.database import Database

# Import utilities
from utils.helpers import encode, decode, is_subscribed, get_size

logger = logging.getLogger(__name__)


class Bot(Client):
    """
    Main Bot Class
    Handles all bot operations and state management
    """
    
    def __init__(self):
        """Initialize the bot"""
        super().__init__(
            name="AdvanceAutoFilterBot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=WORKERS,
            plugins=None  # We'll register handlers manually
        )
        
        # Initialize database
        self.db = Database()
        
        # Bot info (will be set on startup)
        self.username = None
        self.id = None
        
        # Database channel
        self.db_channel = None
        
        # State management
        self.batch_state = {}
        self.broadcast_state = {}
        
        # Auto-delete tracking (THREE FEATURES)
        self.user_last_message = {}  # Feature 1: Clean conversation
        self.user_file_messages = {}  # Feature 2: Auto-delete files
        self.user_delete_tasks = {}   # Feature 3: Delete task tracking
        
        logger.info("Bot instance created")
    
    async def start(self):
        """Start the bot"""
        try:
            # Start Pyrogram client
            await super().start()
            
            # Get bot info
            me = await self.get_me()
            self.username = me.username
            self.id = me.id
            
            logger.info(f"Bot started as @{self.username}")
            
            # Connect to database
            await self.db.connect()
            logger.info("Database connected")
            
            # Set database channel
            if CHANNELS and CHANNELS[0] != 0:
                self.db_channel = CHANNELS[0]
                logger.info(f"Database channel: {self.db_channel}")
            
            # Register all handlers
            self.register_handlers()
            logger.info("All handlers registered")
            
            logger.info("=" * 60)
            logger.info("✅ BOT IS READY!")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            raise
    
    async def stop(self):
        """Stop the bot"""
        try:
            # Cancel all auto-delete tasks
            for user_id in list(self.user_delete_tasks.keys()):
                for task in self.user_delete_tasks[user_id]:
                    if not task.done():
                        task.cancel()
            
            logger.info("All tasks cancelled")
            
            # Stop Pyrogram client
            await super().stop()
            logger.info("Bot stopped")
            
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")
    
    def register_handlers(self):
        """Register all message and callback handlers"""
        
        # ============================================
        # BASIC COMMANDS
        # ============================================
        
        @self.on_message(filters.command("start") & filters.private)
        async def start_command(client, message: Message):
            """Handle /start command"""
            await self.handle_start(message)
        
        @self.on_message(filters.command("help") & filters.private)
        async def help_command(client, message: Message):
            """Handle /help command"""
            await self.handle_help(message)
        
        @self.on_message(filters.command("about") & filters.private)
        async def about_command(client, message: Message):
            """Handle /about command"""
            await self.handle_about(message)
        
        # ============================================
        # ADMIN COMMANDS
        # ============================================
        
        @self.on_message(filters.command("users") & filters.private)
        async def users_command(client, message: Message):
            """Handle /users command"""
            if message.from_user.id not in ADMINS:
                return
            await self.handle_users(message)
        
        @self.on_message(filters.command("broadcast") & filters.private)
        async def broadcast_command(client, message: Message):
            """Handle /broadcast command"""
            if message.from_user.id not in ADMINS:
                return
            await self.handle_broadcast(message)
        
        @self.on_message(filters.command("ban") & filters.private)
        async def ban_command(client, message: Message):
            """Handle /ban command"""
            if message.from_user.id not in ADMINS:
                return
            await self.handle_ban(message)
        
        @self.on_message(filters.command("unban") & filters.private)
        async def unban_command(client, message: Message):
            """Handle /unban command"""
            if message.from_user.id not in ADMINS:
                return
            await self.handle_unban(message)
        
        # ============================================
        # FILE COMMANDS
        # ============================================
        
        @self.on_message(filters.command("batch") & filters.private)
        async def batch_command(client, message: Message):
            """Handle /batch command"""
            if message.from_user.id not in ADMINS:
                return
            await self.handle_batch_start(message)
        
        @self.on_message(filters.private & filters.forwarded & ~filters.command(["start", "help", "about", "batch", "users", "broadcast", "ban", "unban"]))
        async def handle_forwarded(client, message: Message):
            """Handle forwarded messages for batch"""
            await self.handle_batch_messages(message)
        
        # ============================================
        # CALLBACK HANDLERS
        # ============================================
        
        @self.on_callback_query()
        async def callback_handler(client, query: CallbackQuery):
            """Handle all callback queries"""
            await self.handle_callback(query)
        
        logger.info("All handlers registered successfully")
    
    # ============================================
    # COMMAND HANDLERS
    # ============================================
    
    async def handle_start(self, message: Message):
        """Handle /start command"""
        user_id = message.from_user.id
        
        # Check if banned
        if await self.db.is_user_banned(user_id):
            await message.reply("❌ You are banned from using this bot!")
            return
        
        # Add user to database
        if not await self.db.is_user_exist(user_id):
            await self.db.add_user(user_id)
        
        # Check for file/batch link in start parameter
        if len(message.command) > 1:
            arg = message.command[1]
            
            # Check if it's a file link
            if arg.startswith("file_"):
                file_id = arg.replace("file_", "")
                await self.send_file(message, file_id)
                return
            
            # Check if it's a batch link
            elif arg.startswith("batch_"):
                batch_data = arg.replace("batch_", "")
                await self.send_batch(message, batch_data)
                return
        
        # Check force subscribe
        if FORCE_SUB_CHANNELS:
            is_subscribed_all = await is_subscribed(self, user_id, FORCE_SUB_CHANNELS)
            if not is_subscribed_all:
                await self.show_force_subscribe(message)
                return
        
        # Show welcome message
        await self.show_welcome(message)
    
    async def show_welcome(self, message: Message):
        """Show welcome message"""
        user = message.from_user
        
        # Format welcome text
        text = WELCOME_TEXT.format(
            mention=user.mention,
            first=user.first_name,
            last=user.last_name or "",
            username=f"@{user.username}" if user.username else "No username",
            id=user.id
        )
        
        # Create buttons
        buttons = [
            [
                InlineKeyboardButton("📚 Help", callback_data="help_menu"),
                InlineKeyboardButton("ℹ️ About", callback_data="about_menu")
            ],
            [InlineKeyboardButton("❌ Close", callback_data="close")]
        ]
        
        try:
            if BOT_PICS:
                import random
                pic = random.choice(BOT_PICS)
                await message.reply_photo(
                    photo=pic,
                    caption=text,
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
            else:
                await message.reply(
                    text,
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
        except Exception as e:
            logger.error(f"Error sending welcome: {e}")
            await message.reply(
                text,
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    
    async def show_force_subscribe(self, message: Message):
        """Show force subscribe message"""
        user = message.from_user
        
        text = f"👋 Hello {user.mention}!\n\n"
        text += "You must join the following channels to use this bot:\n\n"
        
        buttons = []
        
        for channel_id in FORCE_SUB_CHANNELS:
            try:
                chat = await self.get_chat(channel_id)
                if chat.username:
                    url = f"https://t.me/{chat.username}"
                else:
                    # Create invite link for private channel
                    invite = await self.create_chat_invite_link(channel_id)
                    url = invite.invite_link
                
                buttons.append([InlineKeyboardButton(f"Join {chat.title}", url=url)])
            except Exception as e:
                logger.error(f"Error getting channel {channel_id}: {e}")
        
        buttons.append([InlineKeyboardButton("🔄 Try Again", callback_data="check_fsub")])
        
        await message.reply(text, reply_markup=InlineKeyboardMarkup(buttons))
    
    async def handle_help(self, message: Message):
        """Handle /help command"""
        user = message.from_user
        
        text = HELP_TEXT.format(
            mention=user.mention,
            first=user.first_name,
            last=user.last_name or "",
            username=f"@{user.username}" if user.username else "No username",
            id=user.id
        )
        
        buttons = [
            [InlineKeyboardButton("🏠 Home", callback_data="start_menu")],
            [InlineKeyboardButton("❌ Close", callback_data="close")]
        ]
        
        await message.reply(text, reply_markup=InlineKeyboardMarkup(buttons))
    
    async def handle_about(self, message: Message):
        """Handle /about command"""
        text = ABOUT_TEXT.format(
            bot_name=self.username,
            username=self.username
        )
        
        buttons = [
            [InlineKeyboardButton("🏠 Home", callback_data="start_menu")],
            [InlineKeyboardButton("❌ Close", callback_data="close")]
        ]
        
        await message.reply(text, reply_markup=InlineKeyboardMarkup(buttons))
    
    async def handle_users(self, message: Message):
        """Handle /users command (admin only)"""
        total = await self.db.total_users_count()
        banned = len(await self.db.get_banned_users())
        
        text = f"📊 **User Statistics**\n\n"
        text += f"👥 Total Users: {total}\n"
        text += f"✅ Active Users: {total - banned}\n"
        text += f"🚫 Banned Users: {banned}"
        
        await message.reply(text)
    
    async def handle_broadcast(self, message: Message):
        """Handle /broadcast command (admin only)"""
        if not message.reply_to_message:
            await message.reply("❌ Please reply to a message to broadcast!")
            return
        
        users = await self.db.get_all_users()
        total = len(users)
        success = 0
        failed = 0
        
        status = await message.reply(f"📢 Broadcasting to {total} users...")
        
        for user_id in users:
            try:
                await message.reply_to_message.copy(user_id)
                success += 1
            except FloodWait as e:
                await asyncio.sleep(e.value)
                await message.reply_to_message.copy(user_id)
                success += 1
            except Exception as e:
                failed += 1
                logger.error(f"Broadcast failed for {user_id}: {e}")
            
            # Update status every 100 users
            if (success + failed) % 100 == 0:
                await status.edit_text(
                    f"📢 Broadcasting...\n\n"
                    f"✅ Success: {success}\n"
                    f"❌ Failed: {failed}\n"
                    f"📊 Total: {total}"
                )
        
        await status.edit_text(
            f"✅ Broadcast Complete!\n\n"
            f"✅ Success: {success}\n"
            f"❌ Failed: {failed}\n"
            f"📊 Total: {total}"
        )
    
    async def handle_ban(self, message: Message):
        """Handle /ban command (admin only)"""
        if len(message.command) < 2:
            await message.reply("❌ Usage: /ban <user_id>")
            return
        
        try:
            user_id = int(message.command[1])
            await self.db.ban_user(user_id)
            await message.reply(f"✅ User {user_id} has been banned!")
        except ValueError:
            await message.reply("❌ Invalid user ID!")
        except Exception as e:
            await message.reply(f"❌ Error: {e}")
    
    async def handle_unban(self, message: Message):
        """Handle /unban command (admin only)"""
        if len(message.command) < 2:
            await message.reply("❌ Usage: /unban <user_id>")
            return
        
        try:
            user_id = int(message.command[1])
            await self.db.unban_user(user_id)
            await message.reply(f"✅ User {user_id} has been unbanned!")
        except ValueError:
            await message.reply("❌ Invalid user ID!")
        except Exception as e:
            await message.reply(f"❌ Error: {e}")
    
    async def handle_batch_start(self, message: Message):
        """Start batch mode"""
        user_id = message.from_user.id
        
        self.batch_state[user_id] = {
            'step': 'waiting_first',
            'first_msg': None,
            'last_msg': None
        }
        
        await message.reply(
            "📦 **Batch Mode Started**\n\n"
            "Please forward the **FIRST** message from your database channel."
        )
    
    async def handle_batch_messages(self, message: Message):
        """Handle batch messages"""
        user_id = message.from_user.id
        
        if user_id not in self.batch_state:
            return
        
        state = self.batch_state[user_id]
        
        if state['step'] == 'waiting_first':
            state['first_msg'] = message.forward_from_message_id
            state['step'] = 'waiting_last'
            
            await message.reply(
                "✅ First message received!\n\n"
                "Now forward the **LAST** message from your database channel."
            )
        
        elif state['step'] == 'waiting_last':
            state['last_msg'] = message.forward_from_message_id
            
            # Generate batch link
            first_id = state['first_msg']
            last_id = state['last_msg']
            
            # Create batch data string
            batch_data = f"{first_id}-{last_id}"
            encoded = await encode(batch_data)
            
            link = f"https://t.me/{self.username}?start=batch_{encoded}"
            
            await message.reply(
                f"✅ **Batch Link Generated!**\n\n"
                f"**Total Files:** {last_id - first_id + 1}\n\n"
                f"**Link:** `{link}`\n\n"
                f"Share this link to send all files!",
                disable_web_page_preview=True
            )
            
            # Clear state
            del self.batch_state[user_id]
    
    # ============================================
    # FILE SENDING
    # ============================================
    
    async def send_file(self, message: Message, file_id_encoded: str):
        """Send a single file"""
        user_id = message.from_user.id
        
        # Check force subscribe
        if FORCE_SUB_CHANNELS:
            is_subscribed_all = await is_subscribed(self, user_id, FORCE_SUB_CHANNELS)
            if not is_subscribed_all:
                await self.show_force_subscribe(message)
                return
        
        try:
            # Decode file ID
            file_id = int(await decode(file_id_encoded))
            
            # Get file from database channel
            if not self.db_channel:
                await message.reply("❌ Database channel not configured!")
                return
            
            # Copy file to user
            msg = await self.copy_message(
                chat_id=user_id,
                from_chat_id=self.db_channel,
                message_id=file_id
            )
            
            # Auto-delete setup (if enabled)
            from config import AUTO_DELETE_TIME
            if AUTO_DELETE_TIME and AUTO_DELETE_TIME > 0:
                # Schedule deletion
                task = asyncio.create_task(self.auto_delete_file(msg, AUTO_DELETE_TIME))
                
                if user_id not in self.user_delete_tasks:
                    self.user_delete_tasks[user_id] = []
                self.user_delete_tasks[user_id].append(task)
        
        except Exception as e:
            logger.error(f"Error sending file: {e}")
            await message.reply("❌ File not found or expired!")
    
    async def send_batch(self, message: Message, batch_data_encoded: str):
        """Send batch of files"""
        user_id = message.from_user.id
        
        # Check force subscribe
        if FORCE_SUB_CHANNELS:
            is_subscribed_all = await is_subscribed(self, user_id, FORCE_SUB_CHANNELS)
            if not is_subscribed_all:
                await self.show_force_subscribe(message)
                return
        
        try:
            # Decode batch data
            batch_data = await decode(batch_data_encoded)
            first_id, last_id = map(int, batch_data.split('-'))
            
            if not self.db_channel:
                await message.reply("❌ Database channel not configured!")
                return
            
            total = last_id - first_id + 1
            sent = 0
            
            status = await message.reply(f"📤 Sending {total} files...")
            
            for msg_id in range(first_id, last_id + 1):
                try:
                    await self.copy_message(
                        chat_id=user_id,
                        from_chat_id=self.db_channel,
                        message_id=msg_id
                    )
                    sent += 1
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                except Exception as e:
                    logger.error(f"Error sending file {msg_id}: {e}")
            
            await status.edit_text(f"✅ Sent {sent} out of {total} files!")
        
        except Exception as e:
            logger.error(f"Error sending batch: {e}")
            await message.reply("❌ Batch not found or expired!")
    
    async def auto_delete_file(self, message: Message, seconds: int):
        """Auto-delete file after specified seconds"""
        try:
            await asyncio.sleep(seconds)
            await message.delete()
            logger.info(f"Auto-deleted message {message.id}")
        except Exception as e:
            logger.error(f"Error auto-deleting: {e}")
    
    # ============================================
    # CALLBACK HANDLERS
    # ============================================
    
    async def handle_callback(self, query: CallbackQuery):
        """Handle callback queries"""
        data = query.data
        user_id = query.from_user.id
        
        if data == "start_menu":
            await query.message.delete()
            msg = await self.send_message(user_id, "Loading...")
            await self.handle_start(msg)
            await msg.delete()
        
        elif data == "help_menu":
            await query.message.delete()
            msg = await self.send_message(user_id, "Loading...")
            await self.handle_help(msg)
            await msg.delete()
        
        elif data == "about_menu":
            await query.message.delete()
            msg = await self.send_message(user_id, "Loading...")
            await self.handle_about(msg)
            await msg.delete()
        
        elif data == "check_fsub":
            # Check force subscribe again
            if FORCE_SUB_CHANNELS:
                is_subscribed_all = await is_subscribed(self, user_id, FORCE_SUB_CHANNELS)
                if is_subscribed_all:
                    await query.message.delete()
                    msg = await self.send_message(user_id, "Loading...")
                    await self.show_welcome(msg)
                    await msg.delete()
                else:
                    await query.answer("❌ Please join all channels first!", show_alert=True)
            else:
                await query.answer("✅ No force subscribe configured!", show_alert=True)
        
        elif data == "close":
            await query.message.delete()
            await query.answer()
        
        else:
            await query.answer("⚠️ This button is under development!")
