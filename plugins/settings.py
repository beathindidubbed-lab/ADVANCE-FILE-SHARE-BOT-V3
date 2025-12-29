"""
Settings Command - Beautiful Interactive UI with Toggles
EXACTLY like EvaMaria screenshots - /forcesub, /files, /auto_del, /req_fsub
"""

from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from bot import bot
from config import ADMINS, PROTECT_CONTENT, HIDE_CAPTION, AUTO_DELETE_TIME, REQUEST_FSUB
import config

# ========== MAIN SETTINGS COMMAND ==========

@bot.on_message(filters.private & filters.user(ADMINS) & filters.command("settings"))
async def settings_command(client: Client, message: Message):
    """Main settings menu"""
    
    text = """
⚙️ <b>SETTINGS PANEL</b>

<b>Configure your bot settings below:</b>

🔒 <b>Protection Settings</b>
📁 <b>File Settings</b>
🗑️ <b>Auto Delete Settings</b>
📢 <b>Force Subscribe Settings</b>

<i>Click a button to configure</i>
"""
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔒 Protection", callback_data="setting_protection"),
            InlineKeyboardButton("📁 Files", callback_data="setting_files")
        ],
        [
            InlineKeyboardButton("🗑️ Auto Delete", callback_data="setting_auto_delete"),
            InlineKeyboardButton("📢 Force Sub", callback_data="setting_force_sub")
        ],
        [
            InlineKeyboardButton("⚙️ Request FSub", callback_data="setting_req_fsub")
        ],
        [
            InlineKeyboardButton("🔒 Close", callback_data="close")
        ]
    ])
    
    await message.reply_text(text, reply_markup=buttons, quote=True)


# ========== FORCE SUBSCRIBE SETTINGS (/forcesub command) ==========

@bot.on_message(filters.private & filters.user(ADMINS) & filters.command("forcesub"))
async def forcesub_command(client: Client, message: Message):
    """Force subscribe settings - Like screenshot 7"""
    
    from config import FORCE_SUB_CHANNELS
    
    # Get current status
    is_enabled = len(FORCE_SUB_CHANNELS) > 0 and FORCE_SUB_CHANNELS[0] != 0
    status_icon = "✅" if is_enabled else "❌"
    status_text = "ENABLED" if is_enabled else "DISABLED"
    
    text = f"""
👥 <b>FORCE SUB COMMANDS</b>

<b>Current Status:</b> {status_icon} <b>{status_text}</b>

<b>Available Commands:</b>

<b>/fsub_chnl</b> - Check current force-sub channels (Admins)

<b>/add_fsub</b> - Add one or multiple force sub channels (Owner)

<b>/del_fsub</b> - Delete one or multiple force sub channels (Owner)
"""
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔒 Close", callback_data="close")]
    ])
    
    await message.reply_text(text, reply_markup=buttons, quote=True)


@bot.on_callback_query(filters.regex("^setting_force_sub$"))
async def force_sub_callback(client: Client, query: CallbackQuery):
    """Force subscribe settings panel"""
    
    from config import FORCE_SUB_CHANNELS
    
    is_enabled = len(FORCE_SUB_CHANNELS) > 0 and FORCE_SUB_CHANNELS[0] != 0
    status_icon = "✅" if is_enabled else "❌"
    
    text = f"""
📢 <b>FORCE SUBSCRIBE SETTINGS</b>

<b>Status:</b> {status_icon} <b>{'ENABLED' if is_enabled else 'DISABLED'}</b>

<b>Description:</b>
Force users to join your channel(s) before accessing files.

<b>Commands:</b>
• <code>/forcesub</code> - View commands
• <code>/fsub_chnl</code> - Check channels
• <code>/add_fsub</code> - Add channel
• <code>/del_fsub</code> - Remove channel
"""
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="settings_main")],
        [InlineKeyboardButton("🔒 Close", callback_data="close")]
    ])
    
    await query.message.edit_text(text, reply_markup=buttons)


# ========== REQUEST FORCE SUBSCRIBE (/req_fsub command) ==========

@bot.on_message(filters.private & filters.user(ADMINS) & filters.command("req_fsub"))
async def req_fsub_command(client: Client, message: Message):
    """Request force subscribe settings - Like screenshot 8"""
    
    # Get current status from database
    if bot.db:
        req_fsub_enabled = await bot.db.get_setting("request_fsub")
    else:
        req_fsub_enabled = REQUEST_FSUB
    
    status_icon = "✅" if req_fsub_enabled else "❌"
    on_btn = "🟢 ON" if req_fsub_enabled else "ON"
    off_btn = "OFF" if req_fsub_enabled else "🔴 OFF"
    
    text = f"""
👥 <b>REQUEST FSUB SETTINGS</b>

🔔 <b>REQUEST FSUB MODE:</b> {status_icon}

<b>CLICK BELOW BUTTONS TO CHANGE SETTINGS</b>
"""
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(on_btn, callback_data="req_fsub_on"),
            InlineKeyboardButton(off_btn, callback_data="req_fsub_off")
        ],
        [
            InlineKeyboardButton("⚙️ MORE SETTINGS ⚙️", callback_data="req_fsub_more")
        ],
        [
            InlineKeyboardButton("🔒 Close", callback_data="close")
        ]
    ])
    
    await message.reply_text(text, reply_markup=buttons, quote=True)


@bot.on_callback_query(filters.regex("^req_fsub_(on|off)$"))
async def req_fsub_toggle(client: Client, query: CallbackQuery):
    """Toggle request force subscribe"""
    
    if query.from_user.id not in ADMINS:
        await query.answer("❌ You're not authorized!", show_alert=True)
        return
    
    action = query.data.split("_")[2]
    new_value = True if action == "on" else False
    
    # Update in database
    if bot.db:
        await bot.db.update_setting("request_fsub", new_value)
    
    # Update config
    config.REQUEST_FSUB = new_value
    
    await query.answer(f"✅ Request FSub {'Enabled' if new_value else 'Disabled'}!")
    
    # Refresh display
    status_icon = "✅" if new_value else "❌"
    on_btn = "🟢 ON" if new_value else "ON"
    off_btn = "OFF" if new_value else "🔴 OFF"
    
    text = f"""
👥 <b>REQUEST FSUB SETTINGS</b>

🔔 <b>REQUEST FSUB MODE:</b> {status_icon}

<b>CLICK BELOW BUTTONS TO CHANGE SETTINGS</b>
"""
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(on_btn, callback_data="req_fsub_on"),
            InlineKeyboardButton(off_btn, callback_data="req_fsub_off")
        ],
        [
            InlineKeyboardButton("⚙️ MORE SETTINGS ⚙️", callback_data="req_fsub_more")
        ],
        [
            InlineKeyboardButton("🔒 Close", callback_data="close")
        ]
    ])
    
    await query.message.edit_text(text, reply_markup=buttons)


# ========== FILES SETTINGS (/files command) ==========

@bot.on_message(filters.private & filters.user(ADMINS) & filters.command("files"))
async def files_command(client: Client, message: Message):
    """File settings - Like screenshot 9"""
    
    # Get current settings
    if bot.db:
        protect = await bot.db.get_setting("protect_content")
        hide_caption = await bot.db.get_setting("hide_caption")
        channel_btn = await bot.db.get_setting("channel_button")
    else:
        protect = PROTECT_CONTENT
        hide_caption = HIDE_CAPTION
        channel_btn = True
    
    protect_icon = "❌" if protect else "✅"
    hide_icon = "❌" if hide_caption else "✅"
    channel_icon = "✅" if channel_btn else "❌"
    
    text = f"""
📁 <b>FILES RELATED SETTINGS</b>

🔒 <b>PROTECT CONTENT:</b> {'DISABLED' if not protect else 'ENABLED'} {protect_icon}
🎭 <b>HIDE CAPTION:</b> {'DISABLED' if not hide_caption else 'ENABLED'} {hide_icon}
📢 <b>CHANNEL BUTTON:</b> {'ENABLED' if channel_btn else 'DISABLED'} {channel_icon}

<b>CLICK BELOW BUTTONS TO CHANGE SETTINGS</b>
"""
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"PROTECT CONTENT: {'❌' if protect else '✅'}", callback_data=f"file_protect_{'off' if protect else 'on'}")
        ],
        [
            InlineKeyboardButton(f"HIDE CAPTION: {'❌' if hide_caption else '✅'}", callback_data=f"file_caption_{'off' if hide_caption else 'on'}")
        ],
        [
            InlineKeyboardButton(f"CHANNEL BUTTON: {'✅' if channel_btn else '❌'}", callback_data=f"file_channel_{'off' if channel_btn else 'on'}")
        ],
        [
            InlineKeyboardButton("◈ SET BUTTON ◈", callback_data="file_set_button")
        ],
        [
            InlineKeyboardButton("🔄 REFRESH", callback_data="files_refresh"),
            InlineKeyboardButton("🔒 CLOSE", callback_data="close")
        ]
    ])
    
    await message.reply_text(text, reply_markup=buttons, quote=True)


@bot.on_callback_query(filters.regex("^file_(protect|caption|channel)_(on|off)$"))
async def file_settings_toggle(client: Client, query: CallbackQuery):
    """Toggle file settings"""
    
    if query.from_user.id not in ADMINS:
        await query.answer("❌ You're not authorized!", show_alert=True)
        return
    
    parts = query.data.split("_")
    setting_type = parts[1]
    action = parts[2]
    
    new_value = True if action == "on" else False
    
    # Map to database keys
    db_keys = {
        "protect": "protect_content",
        "caption": "hide_caption",
        "channel": "channel_button"
    }
    
    # Update in database
    if bot.db:
        await bot.db.update_setting(db_keys[setting_type], new_value)
    
    # Update config
    if setting_type == "protect":
        config.PROTECT_CONTENT = new_value
    elif setting_type == "caption":
        config.HIDE_CAPTION = new_value
    
    await query.answer(f"✅ Setting updated!")
    
    # Refresh display
    protect = await bot.db.get_setting("protect_content") if bot.db else PROTECT_CONTENT
    hide_caption = await bot.db.get_setting("hide_caption") if bot.db else HIDE_CAPTION
    channel_btn = await bot.db.get_setting("channel_button") if bot.db else True
    
    protect_icon = "❌" if protect else "✅"
    hide_icon = "❌" if hide_caption else "✅"
    channel_icon = "✅" if channel_btn else "❌"
    
    text = f"""
📁 <b>FILES RELATED SETTINGS</b>

🔒 <b>PROTECT CONTENT:</b> {'DISABLED' if not protect else 'ENABLED'} {protect_icon}
🎭 <b>HIDE CAPTION:</b> {'DISABLED' if not hide_caption else 'ENABLED'} {hide_icon}
📢 <b>CHANNEL BUTTON:</b> {'ENABLED' if channel_btn else 'DISABLED'} {channel_icon}

<b>CLICK BELOW BUTTONS TO CHANGE SETTINGS</b>
"""
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"PROTECT CONTENT: {'❌' if protect else '✅'}", callback_data=f"file_protect_{'off' if protect else 'on'}")
        ],
        [
            InlineKeyboardButton(f"HIDE CAPTION: {'❌' if hide_caption else '✅'}", callback_data=f"file_caption_{'off' if hide_caption else 'on'}")
        ],
        [
            InlineKeyboardButton(f"CHANNEL BUTTON: {'✅' if channel_btn else '❌'}", callback_data=f"file_channel_{'off' if channel_btn else 'on'}")
        ],
        [
            InlineKeyboardButton("◈ SET BUTTON ◈", callback_data="file_set_button")
        ],
        [
            InlineKeyboardButton("🔄 REFRESH", callback_data="files_refresh"),
            InlineKeyboardButton("🔒 CLOSE", callback_data="close")
        ]
    ])
    
    await query.message.edit_text(text, reply_markup=buttons)


@bot.on_callback_query(filters.regex("^files_refresh$"))
async def files_refresh(client: Client, query: CallbackQuery):
    """Refresh file settings"""
    await query.answer("♻️ Refreshing...")
    await file_settings_toggle(client, query)


# ========== AUTO DELETE SETTINGS (/auto_del command) ==========

@bot.on_message(filters.private & filters.user(ADMINS) & filters.command("auto_del"))
async def auto_del_command(client: Client, message: Message):
    """Auto delete settings - Like screenshot 10"""
    
    # Get current settings
    if bot.db:
        auto_del_enabled = await bot.db.get_setting("auto_delete")
        del_time = await bot.db.get_setting("auto_delete_time") or AUTO_DELETE_TIME
    else:
        auto_del_enabled = AUTO_DELETE_TIME > 0
        del_time = AUTO_DELETE_TIME
    
    status_icon = "✅" if auto_del_enabled else "❌"
    minutes = del_time // 60 if del_time else 5
    
    text = f"""
🗑️ <b>AUTO DELETE SETTINGS</b>

🔔 <b>AUTO DELETE MODE:</b> {'ENABLED' if auto_del_enabled else 'ENABLED'} {status_icon}
⏱️ <b>DELETE TIMER:</b> {minutes} MINUTES

<b>CLICK BELOW BUTTONS TO CHANGE SETTINGS</b>
"""
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("DISABLE MODE ❌", callback_data="auto_del_disable")
        ],
        [
            InlineKeyboardButton("◈ SET TIMER ⏱️", callback_data="auto_del_set_timer")
        ],
        [
            InlineKeyboardButton("🔄 REFRESH", callback_data="auto_del_refresh"),
            InlineKeyboardButton("🔒 CLOSE", callback_data="close")
        ]
    ])
    
    await message.reply_text(text, reply_markup=buttons, quote=True)


@bot.on_callback_query(filters.regex("^auto_del_"))
async def auto_del_callbacks(client: Client, query: CallbackQuery):
    """Handle auto delete callbacks"""
    
    if query.from_user.id not in ADMINS:
        await query.answer("❌ You're not authorized!", show_alert=True)
        return
    
    action = query.data.replace("auto_del_", "")
    
    if action == "disable":
        if bot.db:
            await bot.db.update_setting("auto_delete", False)
            await bot.db.update_setting("auto_delete_time", 0)
        config.AUTO_DELETE_TIME = 0
        await query.answer("✅ Auto-delete disabled!")
    
    elif action == "refresh":
        await query.answer("♻️ Refreshing...")
    
    # Refresh display
    if bot.db:
        auto_del_enabled = await bot.db.get_setting("auto_delete")
        del_time = await bot.db.get_setting("auto_delete_time") or 0
    else:
        auto_del_enabled = AUTO_DELETE_TIME > 0
        del_time = AUTO_DELETE_TIME
    
    status_icon = "✅" if auto_del_enabled else "❌"
    minutes = del_time // 60 if del_time else 5
    
    text = f"""
🗑️ <b>AUTO DELETE SETTINGS</b>

🔔 <b>AUTO DELETE MODE:</b> {'ENABLED' if auto_del_enabled else 'DISABLED'} {status_icon}
⏱️ <b>DELETE TIMER:</b> {minutes} MINUTES

<b>CLICK BELOW BUTTONS TO CHANGE SETTINGS</b>
"""
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("DISABLE MODE ❌", callback_data="auto_del_disable")
        ],
        [
            InlineKeyboardButton("◈ SET TIMER ⏱️", callback_data="auto_del_set_timer")
        ],
        [
            InlineKeyboardButton("🔄 REFRESH", callback_data="auto_del_refresh"),
            InlineKeyboardButton("🔒 CLOSE", callback_data="close")
        ]
    ])
    
    await query.message.edit_text(text, reply_markup=buttons)


# ========== BACK TO SETTINGS ==========

@bot.on_callback_query(filters.regex("^file_set_button$"))
async def file_set_button(client: Client, query: CallbackQuery):
    """Set custom button"""
    
    if query.from_user.id not in ADMINS:
        await query.answer("❌ You're not authorized!", show_alert=True)
        return
    
    await query.answer()
    
    # Send instructions
    text = """
🔘 <b>CUSTOM BUTTON SETUP</b>

Send me your button in this format:

<code>Button Text | URL</code>

<b>Examples:</b>

Single button:
<code>Join Channel | https://t.me/yourchannel</code>

Multiple buttons (one per line):
<code>Join Channel | https://t.me/channel1
Support Group | https://t.me/group1</code>

Two buttons in same row:
<code>Channel | https://t.me/ch : Support | https://t.me/gr</code>

<b>💡 Tips:</b>
• Use <code>|</code> to separate text and URL
• Use <code>:</code> to put buttons in same row
• Use new line for new row

Send <code>cancel</code> to cancel.
"""
    
    await query.message.edit_text(text)
    
    # Wait for user input
    try:
        response = await client.listen(query.message.chat.id, timeout=300)
        
        if response.text and response.text.lower() == 'cancel':
            await response.reply_text("❌ Cancelled!")
            return
        
        # Save button config
        button_text = response.text
        
        # Update in database
        if bot.db:
            await bot.db.update_setting("custom_button", button_text)
        
        # Update config
        import config
        config.CUSTOM_BUTTONS = button_text
        
        await response.reply_text(
            f"✅ <b>Custom Button Set!</b>\n\n"
            f"<b>Button Config:</b>\n<code>{button_text}</code>\n\n"
            f"This button will appear with all files!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back to Settings", callback_data="files_refresh")]
            ])
        )
    
    except:
        await query.message.reply_text("❌ <b>Timeout!</b> No response received.")


@bot.on_callback_query(filters.regex("^setting_"))
async def settings_callbacks(client: Client, query: CallbackQuery):
    """Handle main settings navigation"""
    
    if query.from_user.id not in ADMINS:
        await query.answer("❌ You're not authorized!", show_alert=True)
        return
    
    setting_type = query.data.replace("setting_", "")
    
    if setting_type == "protection":
        await query.answer("Use /files command for file settings")
    elif setting_type == "files":
        await query.answer("Use /files command")
    elif setting_type == "auto_delete":
        await query.answer("Use /auto_del command")
    elif setting_type == "force_sub":
        await query.answer("Use /forcesub command")
    elif setting_type == "req_fsub":
        await query.answer("Use /req_fsub command")
