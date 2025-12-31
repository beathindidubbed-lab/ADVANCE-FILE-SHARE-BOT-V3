"""
Bot Settings - Configure everything from inside bot!
Change welcome message, images, buttons, etc.
"""

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import ADMINS
import config

@Client.on_message(filters.private & filters.user(ADMINS) & filters.command("botsettings"))
async def bot_settings_menu(client: Client, message: Message):
    """Main bot settings menu"""
    
    text = """
⚙️ <b>BOT SETTINGS</b>

<b>Configure your bot appearance and behavior:</b>

📸 <b>Welcome Images</b> - Set bot pics
💬 <b>Welcome Message</b> - Customize start message
📚 <b>Help Message</b> - Edit help text
ℹ️ <b>About Message</b> - Edit about text
🔘 <b>Custom Buttons</b> - Add channel/support buttons

<i>Click a button below to configure</i>
"""
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📸 Images", callback_data="settings_images"),
            InlineKeyboardButton("💬 Welcome", callback_data="settings_welcome")
        ],
        [
            InlineKeyboardButton("📚 Help", callback_data="settings_help"),
            InlineKeyboardButton("ℹ️ About", callback_data="settings_about")
        ],
        [
            InlineKeyboardButton("🔘 Buttons", callback_data="settings_buttons")
        ],
        [
            InlineKeyboardButton("👀 Preview", callback_data="settings_preview"),
            InlineKeyboardButton("🔒 Close", callback_data="close")
        ]
    ])
    
    await message.reply_text(text, reply_markup=buttons, quote=True)


# ========== IMAGES SETTINGS ==========

@Client.on_callback_query(filters.regex("^settings_images$"))
async def settings_images_callback(client: Client, query: CallbackQuery):
    """Configure bot images"""
    
    if query.from_user.id not in ADMINS:
        await query.answer("❌ Admin only!", show_alert=True)
        return
    
    current_pics = config.BOT_PICS
    pics_text = "\n".join([f"• {pic}" for pic in current_pics]) if current_pics else "No images set"
    
    text = f"""
📸 <b>WELCOME IMAGES</b>

<b>Current Images:</b>
{pics_text}

<b>To change:</b>
Reply with image URLs (one per line)

<b>Example:</b>
<code>https://telegra.ph/file/image1.jpg
https://telegra.ph/file/image2.jpg</code>

<i>Bot will randomly show one of these images</i>
"""
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Change Images", callback_data="edit_images")],
        [InlineKeyboardButton("🔙 Back", callback_data="botsettings_back")]
    ])
    
    await query.message.edit_text(text, reply_markup=buttons)


@Client.on_callback_query(filters.regex("^edit_images$"))
async def edit_images_callback(client: Client, query: CallbackQuery):
    """Start editing images"""
    
    if query.from_user.id not in ADMINS:
        await query.answer("❌ Admin only!", show_alert=True)
        return
    
    await query.answer()
    await query.message.edit_text(
        "📸 <b>Send Image URLs</b>\n\n"
        "Send image URLs (one per line)\n"
        "Or send <code>cancel</code> to cancel\n\n"
        "<b>Example:</b>\n"
        "<code>https://telegra.ph/file/pic1.jpg\n"
        "https://telegra.ph/file/pic2.jpg</code>"
    )
    
    # Listen for response
    try:
        response = await client.listen(query.message.chat.id, timeout=300)
        
        if response.text and response.text.lower() == 'cancel':
            await response.reply_text("❌ Cancelled!", quote=True)
            return
        
        if not response.text:
            await response.reply_text("❌ Please send text with URLs!", quote=True)
            return
        
        # Parse URLs
        urls = [url.strip() for url in response.text.split('\n') if url.strip()]
        
        if not urls:
            await response.reply_text("❌ No valid URLs found!", quote=True)
            return
        
        # Update config
        config.BOT_PICS = urls
        
        # Save to database
        if hasattr(client, "db") and client.db:
            try:
                await client.db.settings.update_one(
                    {"_id": "bot_settings"},
                    {"$set": {"bot_pics": urls}},
                    upsert=True
                )
            except:
                pass
        
        await response.reply_text(
            f"✅ <b>Images Updated!</b>\n\n"
            f"<b>Total Images:</b> {len(urls)}\n\n"
            f"Use /botsettings to configure more!",
            quote=True
        )
    
    except:
        await query.message.reply_text("❌ Timeout! Try again.")


# ========== WELCOME MESSAGE ==========

@Client.on_callback_query(filters.regex("^settings_welcome$"))
async def settings_welcome_callback(client: Client, query: CallbackQuery):
    """Configure welcome message"""
    
    if query.from_user.id not in ADMINS:
        await query.answer("❌ Admin only!", show_alert=True)
        return
    
    current_welcome = config.WELCOME_TEXT
    
    text = f"""
💬 <b>WELCOME MESSAGE</b>

<b>Current Message:</b>
{current_welcome[:500]}...

<b>Available Variables:</b>
<code>{{first}}</code> - User first name
<code>{{last}}</code> - User last name
<code>{{username}}</code> - Username
<code>{{mention}}</code> - Mention user
<code>{{id}}</code> - User ID

<b>Formatting:</b>
<code>&lt;b&gt;bold&lt;/b&gt;</code>
<code>&lt;i&gt;italic&lt;/i&gt;</code>
<code>&lt;code&gt;code&lt;/code&gt;</code>
"""
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Change Message", callback_data="edit_welcome")],
        [InlineKeyboardButton("🔙 Back", callback_data="botsettings_back")]
    ])
    
    await query.message.edit_text(text, reply_markup=buttons)


@Client.on_callback_query(filters.regex("^edit_welcome$"))
async def edit_welcome_callback(client: Client, query: CallbackQuery):
    """Start editing welcome message"""
    
    if query.from_user.id not in ADMINS:
        await query.answer("❌ Admin only!", show_alert=True)
        return
    
    await query.answer()
    await query.message.edit_text(
        "💬 <b>Send New Welcome Message</b>\n\n"
        "Send your new welcome text\n"
        "Or send <code>cancel</code> to cancel\n\n"
        "<b>You can use:</b>\n"
        "<code>{first}</code> - First name\n"
        "<code>{mention}</code> - Mention\n"
        "<code>{id}</code> - User ID"
    )
    
    # Listen for response
    try:
        response = await client.listen(query.message.chat.id, timeout=300)
        
        if response.text and response.text.lower() == 'cancel':
            await response.reply_text("❌ Cancelled!", quote=True)
            return
        
        if not response.text:
            await response.reply_text("❌ Please send text!", quote=True)
            return
        
        new_text = response.text
        
        # Update config
        config.WELCOME_TEXT = new_text
        
        # Save to database
        if hasattr(client, "db") and client.db:
            try:
                await client.db.settings.update_one(
                    {"_id": "bot_settings"},
                    {"$set": {"welcome_text": new_text}},
                    upsert=True
                )
            except:
                pass
        
        await response.reply_text(
            f"✅ <b>Welcome Message Updated!</b>\n\n"
            f"Preview:\n{new_text[:200]}...\n\n"
            f"Use /botsettings to configure more!",
            quote=True
        )
    
    except:
        await query.message.reply_text("❌ Timeout! Try again.")


# ========== HELP MESSAGE ==========

@Client.on_callback_query(filters.regex("^settings_help$"))
async def settings_help_callback(client: Client, query: CallbackQuery):
    """Configure help message"""
    
    if query.from_user.id not in ADMINS:
        await query.answer("❌ Admin only!", show_alert=True)
        return
    
    current_help = config.HELP_TEXT
    
    text = f"""
📚 <b>HELP MESSAGE</b>

<b>Current Message:</b>
{current_help[:300]}...

<b>This message shows when users click Help button</b>
"""
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Change Message", callback_data="edit_help")],
        [InlineKeyboardButton("🔙 Back", callback_data="botsettings_back")]
    ])
    
    await query.message.edit_text(text, reply_markup=buttons)


@Client.on_callback_query(filters.regex("^edit_help$"))
async def edit_help_callback(client: Client, query: CallbackQuery):
    """Start editing help message"""
    
    if query.from_user.id not in ADMINS:
        await query.answer("❌ Admin only!", show_alert=True)
        return
    
    await query.answer()
    await query.message.edit_text(
        "📚 <b>Send New Help Message</b>\n\n"
        "Send your help text or <code>cancel</code>"
    )
    
    try:
        response = await client.listen(query.message.chat.id, timeout=300)
        
        if response.text and response.text.lower() == 'cancel':
            await response.reply_text("❌ Cancelled!", quote=True)
            return
        
        if not response.text:
            await response.reply_text("❌ Please send text!", quote=True)
            return
        
        new_text = response.text
        config.HELP_TEXT = new_text
        
        if hasattr(client, "db") and client.db:
            try:
                await client.db.settings.update_one(
                    {"_id": "bot_settings"},
                    {"$set": {"help_text": new_text}},
                    upsert=True
                )
            except:
                pass
        
        await response.reply_text(
            f"✅ <b>Help Message Updated!</b>",
            quote=True
        )
    
    except:
        await query.message.reply_text("❌ Timeout!")


# ========== ABOUT MESSAGE ==========

@Client.on_callback_query(filters.regex("^settings_about$"))
async def settings_about_callback(client: Client, query: CallbackQuery):
    """Configure about message"""
    
    if query.from_user.id not in ADMINS:
        await query.answer("❌ Admin only!", show_alert=True)
        return
    
    current_about = config.ABOUT_TEXT
    
    text = f"""
ℹ️ <b>ABOUT MESSAGE</b>

<b>Current Message:</b>
{current_about[:300]}...

<b>Variables:</b>
<code>{{bot_name}}</code> - Bot name
<code>{{username}}</code> - Bot username
"""
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Change Message", callback_data="edit_about")],
        [InlineKeyboardButton("🔙 Back", callback_data="botsettings_back")]
    ])
    
    await query.message.edit_text(text, reply_markup=buttons)


@Client.on_callback_query(filters.regex("^edit_about$"))
async def edit_about_callback(client: Client, query: CallbackQuery):
    """Start editing about message"""
    
    if query.from_user.id not in ADMINS:
        await query.answer("❌ Admin only!", show_alert=True)
        return
    
    await query.answer()
    await query.message.edit_text(
        "ℹ️ <b>Send New About Message</b>\n\n"
        "Send your about text or <code>cancel</code>"
    )
    
    try:
        response = await client.listen(query.message.chat.id, timeout=300)
        
        if response.text and response.text.lower() == 'cancel':
            await response.reply_text("❌ Cancelled!", quote=True)
            return
        
        if not response.text:
            await response.reply_text("❌ Please send text!", quote=True)
            return
        
        new_text = response.text
        config.ABOUT_TEXT = new_text
        
        if hasattr(client, "db") and client.db:
            try:
                await client.db.settings.update_one(
                    {"_id": "bot_settings"},
                    {"$set": {"about_text": new_text}},
                    upsert=True
                )
            except:
                pass
        
        await response.reply_text(
            f"✅ <b>About Message Updated!</b>",
            quote=True
        )
    
    except:
        await query.message.reply_text("❌ Timeout!")


# ========== CUSTOM BUTTONS ==========

@Client.on_callback_query(filters.regex("^settings_buttons$"))
async def settings_buttons_callback(client: Client, query: CallbackQuery):
    """Configure custom buttons"""
    
    if query.from_user.id not in ADMINS:
        await query.answer("❌ Admin only!", show_alert=True)
        return
    
    text = """
🔘 <b>CUSTOM BUTTONS</b>

<b>Add buttons to start message:</b>

<b>Format:</b>
<code>Text | URL</code>

<b>Examples:</b>

Single button:
<code>📢 Channel | https://t.me/yourchannel</code>

Multiple buttons (one per line):
<code>📢 Channel | https://t.me/channel
💬 Support | https://t.me/support</code>

Two in same row (use : separator):
<code>Channel | t.me/ch : Support | t.me/sup</code>
"""
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Set Buttons", callback_data="edit_buttons")],
        [InlineKeyboardButton("❌ Clear Buttons", callback_data="clear_buttons")],
        [InlineKeyboardButton("🔙 Back", callback_data="botsettings_back")]
    ])
    
    await query.message.edit_text(text, reply_markup=buttons)


@Client.on_callback_query(filters.regex("^edit_buttons$"))
async def edit_buttons_callback(client: Client, query: CallbackQuery):
    """Start editing buttons"""
    
    if query.from_user.id not in ADMINS:
        await query.answer("❌ Admin only!", show_alert=True)
        return
    
    await query.answer()
    await query.message.edit_text(
        "🔘 <b>Send Button Configuration</b>\n\n"
        "<b>Format:</b> <code>Text | URL</code>\n\n"
        "Send <code>cancel</code> to cancel"
    )
    
    try:
        response = await client.listen(query.message.chat.id, timeout=300)
        
        if response.text and response.text.lower() == 'cancel':
            await response.reply_text("❌ Cancelled!", quote=True)
            return
        
        if not response.text:
            await response.reply_text("❌ Please send text!", quote=True)
            return
        
        button_config = response.text
        config.CUSTOM_BUTTONS = button_config
        
        if hasattr(client, "db") and client.db:
            try:
                await client.db.settings.update_one(
                    {"_id": "bot_settings"},
                    {"$set": {"custom_buttons": button_config}},
                    upsert=True
                )
            except:
                pass
        
        await response.reply_text(
            f"✅ <b>Buttons Updated!</b>\n\n"
            f"Config:\n<code>{button_config}</code>",
            quote=True
        )
    
    except:
        await query.message.reply_text("❌ Timeout!")


@Client.on_callback_query(filters.regex("^clear_buttons$"))
async def clear_buttons_callback(client: Client, query: CallbackQuery):
    """Clear custom buttons"""
    
    if query.from_user.id not in ADMINS:
        await query.answer("❌ Admin only!", show_alert=True)
        return
    
    config.CUSTOM_BUTTONS = ""
    
    if hasattr(client, "db") and client.db:
        try:
            await client.db.settings.update_one(
                {"_id": "bot_settings"},
                {"$set": {"custom_buttons": ""}},
                upsert=True
            )
        except:
            pass
    
    await query.answer("✅ Buttons cleared!")
    await query.message.edit_text(
        "✅ <b>Custom Buttons Cleared!</b>\n\n"
        "Use /botsettings to configure again."
    )


# ========== PREVIEW ==========

@Client.on_callback_query(filters.regex("^settings_preview$"))
async def settings_preview_callback(client: Client, query: CallbackQuery):
    """Preview current settings"""
    
    if query.from_user.id not in ADMINS:
        await query.answer("❌ Admin only!", show_alert=True)
        return
    
    await query.answer("📤 Sending preview...")
    
    # Send a test /start message
    await query.message.reply_text(
        "📤 <b>Sending preview...</b>\n\n"
        "This is how users will see /start command:",
        quote=False
    )
    
    # Trigger start command for preview
    # This will use current settings
    await query.message.reply_text("/start", quote=False)


# ========== BACK BUTTON ==========

@Client.on_callback_query(filters.regex("^botsettings_back$"))
async def botsettings_back_callback(client: Client, query: CallbackQuery):
    """Go back to main settings"""
    
    text = """
⚙️ <b>BOT SETTINGS</b>

<b>Configure your bot appearance and behavior:</b>

📸 <b>Welcome Images</b> - Set bot pics
💬 <b>Welcome Message</b> - Customize start message
📚 <b>Help Message</b> - Edit help text
ℹ️ <b>About Message</b> - Edit about text
🔘 <b>Custom Buttons</b> - Add channel/support buttons

<i>Click a button below to configure</i>
"""
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📸 Images", callback_data="settings_images"),
            InlineKeyboardButton("💬 Welcome", callback_data="settings_welcome")
        ],
        [
            InlineKeyboardButton("📚 Help", callback_data="settings_help"),
            InlineKeyboardButton("ℹ️ About", callback_data="settings_about")
        ],
        [
            InlineKeyboardButton("🔘 Buttons", callback_data="settings_buttons")
        ],
        [
            InlineKeyboardButton("👀 Preview", callback_data="settings_preview"),
            InlineKeyboardButton("🔒 Close", callback_data="close")
        ]
    ])
    
    await query.message.edit_text(text, reply_markup=buttons)
