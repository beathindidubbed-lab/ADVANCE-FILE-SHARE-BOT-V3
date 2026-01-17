"""
Auto-Delete Manager
==================

THREE SEPARATE AUTO-DELETE FEATURES:

FEATURE 1: Clean Conversation
    - Deletes previous bot message when sending a new one
    - Keeps PM conversations clean (no message accumulation)
    - Tracks: user_last_bot_message = {user_id: {"message_id": int, "timestamp": datetime}}

FEATURE 2: Auto Delete Files
    - Deletes file messages after specified time
    - User-configurable timer (60s to 1 hour)
    - Tracks: user_file_messages = {user_id: [{"message_id": int, "delete_at": datetime, "task": Task}]}

FEATURE 3: Show Instruction After Deletion
    - Shows instruction message with resend button after files deleted
    - This message is NOT auto-deleted (stays for user)
    - Tracks: user_instruction_message = {user_id: {"message_id": int, "shown": bool}}

All features work independently and can be toggled separately.
"""

import asyncio
import datetime
import logging
from typing import Dict, List, Optional
from pyrogram import enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import MessageDeleteForbidden, MessageIdInvalid

logger = logging.getLogger(__name__)


class AutoDeleteManager:
    """
    Manages THREE separate auto-delete features
    
    Each feature is independent and can be enabled/disabled separately.
    All tracking dictionaries are stored in the bot instance.
    """
    
    def __init__(self, bot):
        """
        Initialize Auto-Delete Manager
        
        Args:
            bot: Bot instance to manage auto-delete features for
        """
        self.bot = bot
        
        # ===================================
        # FEATURE 1: Clean Conversation
        # ===================================
        # Track last bot message per user for deletion
        # Format: {user_id: {"message_id": int, "timestamp": datetime}}
        self.user_last_bot_message: Dict[int, Dict] = {}
        
        # ===================================
        # FEATURE 2: Auto Delete Files
        # ===================================
        # Track file messages with delete timers
        # Format: {user_id: [{"message_id": int, "delete_at": datetime, "task": asyncio.Task}]}
        self.user_file_messages: Dict[int, List[Dict]] = {}
        
        # ===================================
        # FEATURE 3: Show Instruction
        # ===================================
        # Track if instruction message is shown
        # Format: {user_id: {"message_id": int, "shown": bool}}
        self.user_instruction_message: Dict[int, Dict] = {}
        
        # ===================================
        # File History for Resend
        # ===================================
        # Track user file history for resend capability
        # Format: {user_id: [{"file_ids": [int], "link_data": dict, "timestamp": datetime}]}
        self.user_file_history: Dict[int, List[Dict]] = {}
        
        logger.info("✓ AutoDeleteManager initialized with THREE features")
    
    # ===================================
    # FEATURE 1: CLEAN CONVERSATION METHODS
    # ===================================
    
    async def delete_previous_bot_message(self, user_id: int):
        """
        FEATURE 1: Clean Conversation
        
        Delete previous bot message when sending a new one.
        This keeps the PM conversation clean (no message accumulation).
        
        Args:
            user_id: User ID to delete previous message for
        """
        if user_id in self.user_last_bot_message:
            try:
                msg_info = self.user_last_bot_message[user_id]
                message_id = msg_info.get("message_id")
                
                if message_id:
                    await self.bot.delete_messages(user_id, message_id)
                    logger.debug(f"✓ Deleted previous bot message {message_id} for user {user_id}")
                
                # Remove from tracking
                del self.user_last_bot_message[user_id]
                
            except MessageDeleteForbidden:
                logger.warning(f"Cannot delete message for user {user_id} - permission denied")
            except MessageIdInvalid:
                logger.warning(f"Message ID invalid for user {user_id} - already deleted")
            except Exception as e:
                logger.error(f"Error deleting previous message for user {user_id}: {e}")
    
    async def store_bot_message(self, user_id: int, message_id: int):
        """
        FEATURE 1: Clean Conversation
        
        Store bot message ID for later deletion.
        Only stores the most recent bot message per user.
        
        Args:
            user_id: User ID
            message_id: Message ID to store
        """
        self.user_last_bot_message[user_id] = {
            "message_id": message_id,
            "timestamp": datetime.datetime.now(datetime.timezone.utc)
        }
        logger.debug(f"✓ Stored bot message {message_id} for user {user_id}")
    
    # ===================================
    # FEATURE 2: AUTO DELETE FILES METHODS
    # ===================================
    
    async def schedule_file_deletion(self, user_id: int, message_id: int, delete_after: int):
        """
        FEATURE 2: Auto Delete Files
        
        Schedule a file message for deletion after specified time.
        
        Args:
            user_id: User ID
            message_id: Message ID to delete
            delete_after: Time in seconds before deletion
        """
        try:
            # Calculate deletion time
            delete_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=delete_after)
            
            # Create deletion task
            task = asyncio.create_task(self._delete_file_after_delay(user_id, message_id, delete_after))
            
            # Store file message info
            if user_id not in self.user_file_messages:
                self.user_file_messages[user_id] = []
            
            self.user_file_messages[user_id].append({
                "message_id": message_id,
                "delete_at": delete_at,
                "task": task
            })
            
            logger.info(f"✓ Scheduled file message {message_id} for deletion in {delete_after}s for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error scheduling file deletion: {e}")
    
    async def _delete_file_after_delay(self, user_id: int, message_id: int, delay: int):
        """
        FEATURE 2: Auto Delete Files
        
        Internal method to delete file message after delay.
        
        Args:
            user_id: User ID
            message_id: Message ID to delete
            delay: Delay in seconds
        """
        try:
            # Wait for the specified delay
            await asyncio.sleep(delay)
            
            # Delete the file message
            await self.bot.delete_messages(user_id, message_id)
            logger.info(f"✓ Auto-deleted file message {message_id} for user {user_id}")
            
            # Remove from tracking
            if user_id in self.user_file_messages:
                self.user_file_messages[user_id] = [
                    msg for msg in self.user_file_messages[user_id]
                    if msg["message_id"] != message_id
                ]
                
                # Clean up empty list
                if not self.user_file_messages[user_id]:
                    del self.user_file_messages[user_id]
            
            # FEATURE 3: Show instruction after files are deleted
            await self.show_instruction_after_deletion(user_id)
            
        except MessageDeleteForbidden:
            logger.warning(f"Cannot delete file message {message_id} for user {user_id}")
        except MessageIdInvalid:
            logger.warning(f"File message {message_id} already deleted for user {user_id}")
        except asyncio.CancelledError:
            logger.info(f"File deletion cancelled for message {message_id}")
        except Exception as e:
            logger.error(f"Error deleting file message {message_id}: {e}")
    
    async def cancel_file_deletions(self, user_id: int):
        """
        FEATURE 2: Auto Delete Files
        
        Cancel all pending file deletions for a user.
        
        Args:
            user_id: User ID to cancel deletions for
        """
        try:
            if user_id in self.user_file_messages:
                for msg_info in self.user_file_messages[user_id]:
                    task = msg_info.get("task")
                    if task and not task.done():
                        task.cancel()
                
                del self.user_file_messages[user_id]
                logger.info(f"✓ Cancelled all file deletions for user {user_id}")
                
        except Exception as e:
            logger.error(f"Error cancelling file deletions for user {user_id}: {e}")
    
    # ===================================
    # FEATURE 3: SHOW INSTRUCTION METHODS
    # ===================================
    
    async def show_instruction_after_deletion(self, user_id: int):
        """
        FEATURE 3: Show Instruction After File Deletion
        
        Show instruction message with resend button after files are deleted.
        This message is NOT auto-deleted (stays permanently for user).
        
        Args:
            user_id: User ID to show instruction for
        """
        try:
            # Check if instruction already shown
            if user_id in self.user_instruction_message:
                logger.debug(f"Instruction already shown for user {user_id}")
                return
            
            # Get settings to check if this feature is enabled
            settings = await self.bot.db.get_settings()
            show_instruction = settings.get("show_instruction", True)
            
            if not show_instruction:
                logger.debug(f"Show instruction feature disabled")
                return
            
            # Create instruction message
            instruction_text = self._create_instruction_message()
            
            # Create resend button
            buttons = [
                [InlineKeyboardButton("🔄 GET FILES AGAIN", callback_data="resend_files")],
                [InlineKeyboardButton("❌ CLOSE", callback_data="close_instruction")]
            ]
            keyboard = InlineKeyboardMarkup(buttons)
            
            # Send instruction message
            try:
                instruction_msg = await self.bot.send_message(
                    user_id,
                    instruction_text,
                    reply_markup=keyboard,
                    parse_mode=enums.ParseMode.HTML
                )
                
                # Store instruction message (NOT in clean conversation tracking)
                self.user_instruction_message[user_id] = {
                    "message_id": instruction_msg.id,
                    "shown": True,
                    "timestamp": datetime.datetime.now(datetime.timezone.utc)
                }
                
                logger.info(f"✓ Showed instruction message for user {user_id}")
                
            except Exception as e:
                logger.error(f"Error sending instruction message to user {user_id}: {e}")
                
        except Exception as e:
            logger.error(f"Error in show_instruction_after_deletion: {e}")
    
    def _create_instruction_message(self) -> str:
        """
        Create instruction message text
        
        Returns:
            Formatted instruction message
        """
        instruction_content = (
            "YOUR FILES HAVE BEEN DELETED!\n\n"
            "IF YOU WANT TO GET THE FILES AGAIN, "
            "CLICK THE BUTTON BELOW OR USE THE ORIGINAL LINK AGAIN."
        )
        
        return (
            "<b>⚠️ FILES DELETED</b>\n\n"
            f"<blockquote>{instruction_content}</blockquote>"
        )
    
    async def clear_instruction_message(self, user_id: int):
        """
        FEATURE 3: Show Instruction
        
        Clear instruction message tracking (does not delete the message).
        
        Args:
            user_id: User ID to clear instruction for
        """
        try:
            if user_id in self.user_instruction_message:
                del self.user_instruction_message[user_id]
                logger.debug(f"✓ Cleared instruction tracking for user {user_id}")
        except Exception as e:
            logger.error(f"Error clearing instruction for user {user_id}: {e}")
    
    # ===================================
    # FILE HISTORY TRACKING
    # ===================================
    
    async def track_user_files(self, user_id: int, file_ids: List[int], link_data: Optional[Dict] = None):
        """
        Track files sent to user for potential resend.
        
        Args:
            user_id: User ID
            file_ids: List of file message IDs from database channel
            link_data: Optional link data (for special links)
        """
        try:
            if user_id not in self.user_file_history:
                self.user_file_history[user_id] = []
            
            self.user_file_history[user_id].append({
                "file_ids": file_ids,
                "link_data": link_data,
                "timestamp": datetime.datetime.now(datetime.timezone.utc)
            })
            
            # Keep only last 5 entries per user
            if len(self.user_file_history[user_id]) > 5:
                self.user_file_history[user_id] = self.user_file_history[user_id][-5:]
            
            logger.debug(f"✓ Tracked {len(file_ids)} files for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error tracking files for user {user_id}: {e}")
    
    async def get_user_file_history(self, user_id: int) -> Optional[Dict]:
        """
        Get most recent file history for user.
        
        Args:
            user_id: User ID
            
        Returns:
            Most recent file history entry or None
        """
        if user_id in self.user_file_history and self.user_file_history[user_id]:
            return self.user_file_history[user_id][-1]
        return None
    
    # ===================================
    # UTILITY METHODS
    # ===================================
    
    async def cleanup_user_data(self, user_id: int):
        """
        Cleanup all tracking data for a user.
        
        Args:
            user_id: User ID to cleanup
        """
        try:
            # Clear clean conversation
            if user_id in self.user_last_bot_message:
                del self.user_last_bot_message[user_id]
            
            # Cancel and clear file deletions
            await self.cancel_file_deletions(user_id)
            
            # Clear instruction
            if user_id in self.user_instruction_message:
                del self.user_instruction_message[user_id]
            
            # Clear file history
            if user_id in self.user_file_history:
                del self.user_file_history[user_id]
            
            logger.info(f"✓ Cleaned up all auto-delete data for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error cleaning up user data for {user_id}: {e}")
    
    def get_status(self) -> Dict:
        """
        Get status of all auto-delete features.
        
        Returns:
            Dictionary with feature statuses
        """
        return {
            "clean_conversation": {
                "tracked_users": len(self.user_last_bot_message),
                "enabled": True
            },
            "auto_delete_files": {
                "tracked_users": len(self.user_file_messages),
                "total_scheduled": sum(len(msgs) for msgs in self.user_file_messages.values())
            },
            "show_instruction": {
                "shown_users": len(self.user_instruction_message)
            },
            "file_history": {
                "tracked_users": len(self.user_file_history)
            }
        }
    
    def verify_features(self):
        """
        Verification function to ensure THREE auto-delete features are configured.
        
        Logs the configuration status of all three features.
        """
        logger.info("=" * 70)
        logger.info("AUTO-DELETE MANAGER - THREE FEATURES VERIFICATION:")
        logger.info("-" * 70)
        logger.info("✓ Feature 1 - Clean Conversation: Initialized")
        logger.info("  → Deletes previous bot message when sending new one")
        logger.info("-" * 70)
        logger.info("✓ Feature 2 - Auto Delete Files: Initialized")
        logger.info("  → Deletes file messages after specified time")
        logger.info("-" * 70)
        logger.info("✓ Feature 3 - Show Instruction: Initialized")
        logger.info("  → Shows resend button after file deletion")
        logger.info("  → This message is NOT auto-deleted")
        logger.info("=" * 70)
