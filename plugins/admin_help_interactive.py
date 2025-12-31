"""
Admin Help - Beautiful Interactive Command Menu
Shows all commands with descriptions and clickable buttons
"""

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import config

@Client.on_message(filters.command("help") & filters.private)
async def help_command(client: Client, message: Message):
    """Help command - different for admin and users"""
    
    # Check if admin
    if message.from_user.id in config.ADMINS:
        await show_admin_help(client, message)
    else:
        await show_user_help(client, message)


async def show_user_help(client: Client, message: Message):
    """Beautiful help for regular users"""
    
    help_image = "https://telegra.ph/file/9c4a742df32e42f286422.jpg"
    
    help_text = f"""
👋 <b>Hello {message.from_user.first_name} ~</b>

➜ <b>I AM A PRIVATE FILE SHARING BOT, MEANT TO PROVIDE FILES AND NECESSARY STUFF THROUGH SPECIAL LINK FOR SPECIFIC CHANNELS.</b>

➜ <b>IN ORDER TO GET THE FILES YOU HAVE TO JOIN THE ALL MENTIONED CHANNEL THAT I PROVIDE YOU TO JOIN. YOU CAN NOT ACCESS OR GET THE FILES UNLESS YOU JOINED ALL CHANNELS.</b>

➜ <b>SO JOIN MENTIONED CHANNELS TO GET FILES OR INITIATE MESSAGES...</b>

<b>• /help - OPEN THIS HELP MESSAGE !</b>

<i>➜ STILL HAVE DOUBTS, CONTACT BELOW PERSONS/ GROUP AS PER YOUR NEED!</i>
"""
    
    buttons = []
    
    if config.SUPPORT_CHAT:
        buttons.append([
            InlineKeyboardButton("🗨 Support Chat Group", url=f"https://t.me/{config.SUPPORT_CHAT.replace('@', '')}")
        ])
    
    owner_username = config.SUPPORT_CHAT or "YourOwner"
    developer_username = "YourDeveloper"
    
    buttons.append([
        InlineKeyboardButton("📥 Owner", url=f"https://t.me/{owner_username}"),
        InlineKeyboardButton("💫 Developer", url=f"https://t.me/{developer_username}")
    ])
    
    buttons.append([
        InlineKeyboardButton("🔐 Close", callback_data="close")
    ])
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    try:
        await message.reply_photo(
            photo=help_image,
            caption=help_text,
            reply_markup=reply_markup,
            quote=True
        )
    except:
        await message.reply_text(
            text=help_text,
            reply_markup=reply_markup,
            quote=True
        )


async def show_admin_help(client: Client, message: Message):
    """Beautiful admin help with ALL commands"""
    
    admin_help_image = "https://telegra.ph/file/d8d2e9cc6d60741c7e77d.jpg"
    
    admin_text = f"""
👑 <b>ADMIN COMMANDS PANEL</b>

<b>Hello {message.from_user.first_name}! You have full admin access.</b>

━━━━━━━━━━━━━━━━━━━━

<b>📁 FILE MANAGEMENT:</b>
• <code>/genlink</code> - Generate single file link
• <code>/batch</code> - Create batch link (sequential)
• <code>/custom_batch</code> - Create custom batch link
• <code>/special_link</code> - Link with custom message

<b>⚙️ CHANNEL SETTINGS:</b>
• <code>/setchannel</code> - Configure database channel
• <code>/checkchannel</code> - Check channel status
• <code>/removechannel</code> - Remove channel

<b>👥 USER MANAGEMENT:</b>
• <code>/users</code> - View user statistics
• <code>/ban</code> - Ban a user
• <code>/unban</code> - Unban a user
• <code>/broadcast</code> - Broadcast message

<b>📊 BOT SETTINGS:</b>
• <code>/settings</code> - Main settings panel
• <code>/botsettings</code> - Configure bot appearance
• <code>/files</code> - File protection settings
• <code>/forcesub</code> - Force subscribe settings
• <code>/auto_del</code> - Auto-delete settings

<b>📈 STATISTICS:</b>
• <code>/stats</code> - Complete bot statistics

<b>🔗 UTILITIES:</b>
• <code>/shortener</code> - Shorten any URL
• <code>/ping</code> - Check bot status
• <code>/test</code> - Test bot functionality

━━━━━━━━━━━━━━━━━━━━

<b>💡 Click any command below to execute it!</b>
"""
    
    # Create clickable command buttons - organized by category
    buttons = [
        # File Management
        [
            InlineKeyboardButton("📝 Generate Link", callback_data="cmd_genlink"),
            InlineKeyboardButton("📦 Batch Link", callback_data="cmd_batch")
        ],
        [
            InlineKeyboardButton("🎯 Custom Batch", callback_data="cmd_custom_batch"),
            InlineKeyboardButton("⭐ Special Link", callback_data="cmd_special_link")
        ],
        
        # Channel Settings
        [
            InlineKeyboardButton("📺 Set Channel", callback_data="cmd_setchannel"),
            InlineKeyboardButton("✅ Check Channel", callback_data="cmd_checkchannel")
        ],
        
        # User Management
        [
            InlineKeyboardButton("👥 Users Stats", callback_data="cmd_users"),
            InlineKeyboardButton("📊 Bot Stats", callback_data="cmd_stats")
        ],
        
        # Settings
        [
            InlineKeyboardButton("⚙️ Settings", callback_data="cmd_settings"),
            InlineKeyboardButton("🎨 Bot Settings", callback_data="cmd_botsettings")
        ],
        [
            InlineKeyboardButton("📁 Files Settings", callback_data="cmd_files"),
            InlineKeyboardButton("📢 Force Sub", callback_data="cmd_forcesub")
        ],
        
        # Utilities
        [
            InlineKeyboardButton("🔗 URL Shortener", callback_data="cmd_shortener"),
            InlineKeyboardButton("🏓 Ping", callback_data="cmd_ping")
        ],
        
        # Close
        [
            InlineKeyboardButton("🔐 Close", callback_data="close")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    try:
        await message.reply_photo(
            photo=admin_help_image,
            caption=admin_text,
            reply_markup=reply_markup,
            quote=True
        )
    except:
        await message.reply_text(
            text=admin_text,
            reply_markup=reply_markup,
            quote=True
        )


# ========== COMMAND CALLBACKS ==========

@Client.on_callback_query(filters.regex("^cmd_"))
async def command_callbacks(client: Client, query: CallbackQuery):
    """Handle command button clicks"""
    
    if query.from_user.id not in config.ADMINS:
        await query.answer("❌ Admin only!", show_alert=True)
        return
    
    # Extract command from callback data
    command = query.data.replace("cmd_", "")
    
    # Command descriptions for confirmation
    command_info = {
        "genlink": "📝 Generate single file link\n\nForward a message from your database channel to get a shareable link.",
        "batch": "📦 Batch Link Generator\n\nForward FIRST and LAST messages from channel to create batch link.",
        "custom_batch": "🎯 Custom Batch\n\nForward multiple random messages, then send /done to create link.",
        "special_link": "⭐ Special Link\n\nCreate link with custom welcome message for users.",
        "setchannel": "📺 Set Database Channel\n\nConfigure your file storage channel/group.",
        "checkchannel": "✅ Check Channel Status\n\nView current channel configuration and status.",
        "users": "👥 User Statistics\n\nView total users, banned users, and active users.",
        "stats": "📊 Bot Statistics\n\nView complete bot statistics and information.",
        "settings": "⚙️ Main Settings\n\nAccess all bot configuration settings.",
        "botsettings": "🎨 Bot Appearance\n\nConfigure welcome message, images, buttons, etc.",
        "files": "📁 File Settings\n\nConfigure file protection, captions, and buttons.",
        "forcesub": "📢 Force Subscribe\n\nManage force subscribe channels and settings.",
        "shortener": "🔗 URL Shortener\n\nShorten any long URL to a short link.",
        "ping": "🏓 Ping Bot\n\nCheck if bot is online and responsive."
    }
    
    info_text = command_info.get(command, f"Execute /{command} command")
    
    # Create confirmation buttons
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Execute Command", callback_data=f"exec_{command}"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_cmd")
        ]
    ])
    
    await query.message.reply_text(
        f"<b>📋 COMMAND INFO</b>\n\n"
        f"{info_text}\n\n"
        f"<b>Command:</b> <code>/{command}</code>\n\n"
        f"Click <b>Execute</b> to run this command.",
        reply_markup=buttons,
        quote=True
    )
    
    await query.answer()


@Client.on_callback_query(filters.regex("^exec_"))
async def execute_command_callback(client: Client, query: CallbackQuery):
    """Execute the selected command"""
    
    if query.from_user.id not in config.ADMINS:
        await query.answer("❌ Admin only!", show_alert=True)
        return
    
    command = query.data.replace("exec_", "")
    
    await query.answer(f"✅ Executing /{command}...")
    
    # Send the command as if user typed it
    await query.message.reply_text(f"/{command}")


@Client.on_callback_query(filters.regex("^cancel_cmd$"))
async def cancel_command_callback(client: Client, query: CallbackQuery):
    """Cancel command execution"""
    
    await query.answer("❌ Cancelled")
    await query.message.delete()


# ========== HELP CALLBACK (for start menu) ==========

@Client.on_callback_query(filters.regex("^help$"))
async def help_callback(client: Client, query: CallbackQuery):
    """Help button callback from start menu"""
    
    # Check if admin
    if query.from_user.id in config.ADMINS:
        # Show admin help
        admin_help_image = "https://telegra.ph/file/d8d2e9cc6d60741c7e77d.jpg"
        
        admin_text = f"""
👑 <b>ADMIN COMMANDS PANEL</b>

<b>Hello {query.from_user.first_name}! You have full admin access.</b>

━━━━━━━━━━━━━━━━━━━━

<b>📁 FILE MANAGEMENT:</b>
• <code>/genlink</code> - Generate single file link
• <code>/batch</code> - Create batch link
• <code>/custom_batch</code> - Custom batch link
• <code>/special_link</code> - Link with custom message

<b>⚙️ CHANNEL SETTINGS:</b>
• <code>/setchannel</code> - Configure channel
• <code>/checkchannel</code> - Check status

<b>👥 USER MANAGEMENT:</b>
• <code>/users</code> - User statistics
• <code>/ban</code> / <code>/unban</code> - Manage users
• <code>/broadcast</code> - Send to all

<b>📊 SETTINGS & STATS:</b>
• <code>/settings</code> - Bot settings
• <code>/botsettings</code> - Appearance
• <code>/stats</code> - Statistics

━━━━━━━━━━━━━━━━━━━━

<b>💡 Click commands below to execute!</b>
"""
        
        buttons = [
            [
                InlineKeyboardButton("📝 Generate Link", callback_data="cmd_genlink"),
                InlineKeyboardButton("📦 Batch", callback_data="cmd_batch")
            ],
            [
                InlineKeyboardButton("📺 Set Channel", callback_data="cmd_setchannel"),
                InlineKeyboardButton("👥 Users", callback_data="cmd_users")
            ],
            [
                InlineKeyboardButton("⚙️ Settings", callback_data="cmd_settings"),
                InlineKeyboardButton("📊 Stats", callback_data="cmd_stats")
            ],
            [
                InlineKeyboardButton("🏠 Home", callback_data="start"),
                InlineKeyboardButton("🔐 Close", callback_data="close")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(buttons)
        
        try:
            await query.message.edit_caption(
                caption=admin_text,
                reply_markup=reply_markup
            )
        except:
            try:
                await query.message.edit_text(
                    text=admin_text,
                    reply_markup=reply_markup
                )
            except:
                await query.answer("Error!", show_alert=True)
    
    else:
        # Show user help
        help_text = f"""
👋 <b>Hello {query.from_user.first_name} ~</b>

➜ <b>I AM A PRIVATE FILE SHARING BOT, MEANT TO PROVIDE FILES AND NECESSARY STUFF THROUGH SPECIAL LINK FOR SPECIFIC CHANNELS.</b>

➜ <b>IN ORDER TO GET THE FILES YOU HAVE TO JOIN THE ALL MENTIONED CHANNEL THAT I PROVIDE YOU TO JOIN. YOU CAN NOT ACCESS OR GET THE FILES UNLESS YOU JOINED ALL CHANNELS.</b>

➜ <b>SO JOIN MENTIONED CHANNELS TO GET FILES OR INITIATE MESSAGES...</b>

<b>• /help - OPEN THIS HELP MESSAGE !</b>

<i>➜ STILL HAVE DOUBTS, CONTACT BELOW PERSONS/ GROUP AS PER YOUR NEED!</i>
"""
        
        buttons = []
        
        if config.SUPPORT_CHAT:
            buttons.append([
                InlineKeyboardButton("🗨 Support Chat Group", url=f"https://t.me/{config.SUPPORT_CHAT.replace('@', '')}")
            ])
        
        buttons.append([
            InlineKeyboardButton("🏠 Home", callback_data="start"),
            InlineKeyboardButton("🔐 Close", callback_data="close")
        ])
        
        reply_markup = InlineKeyboardMarkup(buttons)
        
        try:
            await query.message.edit_caption(
                caption=help_text,
                reply_markup=reply_markup
            )
        except:
            try:
                await query.message.edit_text(
                    text=help_text,
                    reply_markup=reply_markup
                )
            except:
                await query.answer("Error!", show_alert=True)
