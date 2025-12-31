import sys
import logging
import asyncio
import os
import random
import aiohttp
from aiohttp import web
from pyrogram import Client, filters, idle
from pyrogram.enums import ParseMode
from pyrogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, 
    InlineKeyboardButton
)
from pyrogram.errors import (
    FloodWait, UserIsBlocked, InputUserDeactivated,
    UserNotParticipant
)

try:
    from pyromod import listen
except ImportError:
    print("ERROR: pyromod not installed!")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S'
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
LOGGER = logging.getLogger(__name__)

# ============================================================================
# WEB SERVER FOR RENDER (FIXES SIGTERM & KEEPS BOT ONLINE)
# ============================================================================

async def handle_route(request):
    return web.Response(text="Bot is Running Successfully on Render!")

async def start_web_server():
    """Starts the web server for Render health checks"""
    app = web.Application()
    app.router.add_get("/", handle_route)
    runner = web.AppRunner(app)
    await runner.setup()
    # Render assigns the port via environment variable
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    LOGGER.info(f"✅ Web Server started on port {port}")

# ============================================================================
# BOT CLASS
# ============================================================================

class Bot(Client):
    def __init__(self):
        # Import config inside class to avoid circular imports if config uses Bot
        try:
            from config import API_ID, API_HASH, BOT_TOKEN, WORKERS
        except ImportError:
            # Fallbacks if config.py is missing
            API_ID = int(os.environ.get("API_ID", 0))
            API_HASH = os.environ.get("API_HASH", "")
            BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
            WORKERS = int(os.environ.get("WORKERS", 4))

        super().__init__(
            name="AdvanceAutoFilterBot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=WORKERS,
            parse_mode=ParseMode.HTML
        )
        self.LOGGER = LOGGER
        self.db_channel = None
        self.db_channel_id = None

    async def start(self):
        await super().start()
        
        me = await self.get_me()
        self.username = me.username
        self.id = me.id
        self.mention = me.mention
        self.first_name = me.first_name
        
        LOGGER.info(f"✅ Bot Started: @{me.username}")
        
        # Connect database
        try:
            from database.database import Database
            self.db = Database()
            await self.db.connect()
            LOGGER.info("✅ Database Connected")
        except Exception as e:
            LOGGER.warning(f"⚠️ Database Connection Error: {e}")
            self.db = None
        
        LOGGER.info("=" * 70)
        LOGGER.info("🎉 BOT IS READY!")
        LOGGER.info(f"   Bot: @{self.username}")
        LOGGER.info(f"   ID: {self.id}")
        LOGGER.info("=" * 70)

    async def stop(self, *args):
        await super().stop()
        LOGGER.info("❌ Bot Stopped")

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

async def encode(string: str) -> str:
    import base64
    string_bytes = string.encode("ascii")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    return base64_bytes.decode("ascii").rstrip("=")

async def decode(base64_string: str) -> str:
    import base64
    base64_string += "=" * (-len(base64_string) % 4)
    base64_bytes = base64_string.encode("ascii")
    string_bytes = base64.urlsafe_b64decode(base64_bytes)
    return string_bytes.decode("ascii")

async def is_subscribed(client: Client, user_id: int, channels: list) -> bool:
    for channel_id in channels:
        if channel_id == 0: continue
        try:
            member = await client.get_chat_member(channel_id, user_id)
            if member.status not in ["administrator", "creator", "member"]:
                return False
        except UserNotParticipant: return False
        except: return False
    return True

async def delete_files(messages: list, client: Client, notification: Message, link: str):
    from config import AUTO_DELETE_TIME
    await asyncio.sleep(AUTO_DELETE_TIME)
    for msg in messages:
        try: await msg.delete()
        except: pass
    try:
        await notification.edit_text(
            f"⏱️ <b>Files Deleted!</b>\n\nClick below to get files again:",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Get Files Again", url=link)]])
        )
    except: pass

def parse_custom_buttons(button_string: str) -> list:
    if not button_string: return []
    buttons = []
    lines = button_string.strip().split('\n')
    for line in lines:
        if ':' in line:
            button_row = []
            pairs = line.split(':')
            for pair in pairs:
                if '|' in pair:
                    parts = pair.split('|', 1)
                    if len(parts) == 2:
                        button_row.append(InlineKeyboardButton(parts[0].strip(), url=parts[1].strip()))
            if button_row: buttons.append(button_row)
        elif '|' in line:
            parts = line.split('|', 1)
            if len(parts) == 2:
                buttons.append([InlineKeyboardButton(parts[0].strip(), url=parts[1].strip())])
    return buttons

# ============================================================================
# START COMMAND & FILE HANDLER
# ============================================================================

@Client.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id
    
    # Database check
    if hasattr(client, "db") and client.db:
        if not await client.db.is_user_exist(user_id):
            await client.db.add_user(user_id)
        if await client.db.is_user_banned(user_id):
            await message.reply_text("🚫 <b>You are banned!</b>\n\nContact support.", quote=True)
            return
    
    # Handle File Link
    if len(message.command) > 1:
        file_param = message.command[1]
        await handle_file_request(client, message, file_param)
        return
    
    # SHOW WELCOME (Updated with your Requested Text)
    await show_welcome(client, message)

async def show_welcome(client: Client, message: Message):
    import config
    
    # YOUR REQUESTED TEXT STYLE
    welcome_text = (
        f"👋 ʜᴇʟʟᴏ {message.from_user.mention},\n\n"
        f"➪ I ᴀᴍ ᴀ ᴘʀɪᴠᴀᴛᴇ ғɪʟᴇ sʜᴀʀɪɴɢ ʙᴏᴛ, ᴍᴇᴀɴᴛ ᴛᴏ ᴘʀᴏᴠɪᴅᴇ ғɪʟᴇs ᴀɴᴅ ɴᴇᴄᴇssᴀʀʏ sᴛᴜғғ ᴛʜʀᴏᴜɢʜ sᴘᴇᴄɪᴀʟ ʟɪɴᴋ ғᴏʀ sᴘᴇᴄɪғɪᴄ ᴄʜᴀɴɴᴇʟs."
    )
    
    buttons = [
        [InlineKeyboardButton("📚 Help", callback_data="help"), InlineKeyboardButton("ℹ️ About", callback_data="about")]
    ]
    if config.UPDATES_CHANNEL:
        buttons.append([InlineKeyboardButton("📢 Updates Channel", url=f"https://t.me/{config.UPDATES_CHANNEL.replace('@', '')}")])
    if config.SUPPORT_CHAT:
        buttons.append([InlineKeyboardButton("💬 Support Chat", url=f"https://t.me/{config.SUPPORT_CHAT.replace('@', '')}")])
    if config.CUSTOM_BUTTONS:
        buttons.extend(parse_custom_buttons(config.CUSTOM_BUTTONS))
    buttons.append([InlineKeyboardButton("🔐 Close", callback_data="close")])
    
    reply_markup = InlineKeyboardMarkup(buttons)
    
    # Try to send with Pic if available
    if config.BOT_PICS:
        try:
            await message.reply_photo(
                photo=random.choice(config.BOT_PICS),
                caption=welcome_text,
                reply_markup=reply_markup,
                quote=True
            )
            return
        except: pass
    
    await message.reply_text(text=welcome_text, reply_markup=reply_markup, quote=True)

async def handle_file_request(client: Client, message: Message, file_param: str):
    import config
    user_id = message.from_user.id
    
    # Force Subscribe Check
    if config.FORCE_SUB_CHANNELS:
        if not await is_subscribed(client, user_id, config.FORCE_SUB_CHANNELS):
            buttons = []
            for channel_id in config.FORCE_SUB_CHANNELS:
                if channel_id == 0: continue
                try:
                    chat = await client.get_chat(channel_id)
                    if config.REQUEST_FSUB:
                        invite = await client.create_chat_invite_link(channel_id, creates_join_request=True)
                        buttons.append([InlineKeyboardButton(f"📢 Request Join {chat.title}", url=invite.invite_link)])
                    else:
                        url = f"https://t.me/{chat.username}" if chat.username else (await client.create_chat_invite_link(channel_id)).invite_link
                        buttons.append([InlineKeyboardButton(f"📢 Join {chat.title}", url=url)])
                except: pass
            
            buttons.append([InlineKeyboardButton("🔄 Try Again", url=f"https://t.me/{client.username}?start={file_param}")])
            await message.reply_text(
                config.FORCE_SUB_TEXT.format(mention=message.from_user.mention, first=message.from_user.first_name, last=message.from_user.last_name or "", username=message.from_user.username or "", id=message.from_user.id),
                reply_markup=InlineKeyboardMarkup(buttons),
                quote=True
            )
            return

    # Handle Link Types
    try:
        decoded = await decode(file_param)
        if decoded.startswith("get-"):
            await send_single_file(client, message, decoded)
        elif decoded.startswith("custombatch-"):
            await send_custom_batch(client, message, decoded)
        else:
            await handle_special_link(client, message, file_param)
    except:
        await message.reply_text("❌ <b>Invalid Link!</b>", quote=True)

async def send_single_file(client, message, decoded):
    import config
    try:
        file_id = int(decoded.split("-")[1])
        channel_id = abs(client.db_channel.id)
        msg_id = file_id // channel_id
        file_msg = await client.get_messages(client.db_channel.id, msg_id)
        
        if not file_msg:
            return await message.reply_text("❌ File not found.")

        caption = "" if config.HIDE_CAPTION else (file_msg.caption or "")
        if config.CUSTOM_CAPTION and not config.HIDE_CAPTION:
            media = file_msg.document or file_msg.video or file_msg.audio
            f_name = getattr(media, 'file_name', 'File')
            f_size = f"{getattr(media, 'file_size', 0) / (1024*1024):.2f} MB"
            caption = config.CUSTOM_CAPTION.format(filename=f_name, filesize=f_size, previouscaption=file_msg.caption or "")

        reply_markup = InlineKeyboardMarkup(parse_custom_buttons(config.CUSTOM_BUTTONS)) if (config.CHANNEL_BUTTON and config.CUSTOM_BUTTONS) else None
        
        sent_msg = await file_msg.copy(
            chat_id=message.chat.id,
            caption=caption,
            reply_markup=reply_markup,
            protect_content=config.PROTECT_CONTENT
        )
        
        if config.AUTO_DELETE_TIME > 0:
            link = f"https://t.me/{client.username}?start={await encode(decoded)}"
            notif = await message.reply_text(f"⏱️ <b>Auto-Delete in {config.AUTO_DELETE_TIME//60}m</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Get Again", url=link)]]))
            asyncio.create_task(delete_files([sent_msg], client, notif, link))
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

async def send_custom_batch(client, message, decoded):
    import config
    try:
        parts = decoded.split("-")[1:]
        channel_id = abs(client.db_channel.id)
        msg_ids = [int(p) // channel_id for p in parts]
        sent_msgs = []
        for m_id in msg_ids:
            try:
                m = await client.get_messages(client.db_channel.id, m_id)
                s = await m.copy(chat_id=message.chat.id, protect_content=config.PROTECT_CONTENT)
                sent_msgs.append(s)
            except: pass
        
        if config.AUTO_DELETE_TIME > 0 and sent_msgs:
            link = f"https://t.me/{client.username}?start={await encode(decoded)}"
            notif = await message.reply_text("⏱️ <b>Batch Auto-Delete Active</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Get Again", url=link)]]))
            asyncio.create_task(delete_files(sent_msgs, client, notif, link))
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

# ============================================================================
# SPECIAL LINK, SHORTENER & SETTINGS HANDLERS
# ============================================================================

async def handle_special_link(client, message, file_param):
    if hasattr(client, "db") and client.db:
        special_data = await client.db.settings.find_one({"_id": f"special_{file_param}"})
        if special_data and 'message' in special_data:
            await message.reply_text(special_data['message'], quote=True)

@Client.on_message(filters.private & filters.user(os.environ.get("ADMINS", "").split()) & filters.command("special_link"))
async def special_link_command(client: Client, message: Message):
    if not hasattr(client, "db_channel"): return await message.reply_text("❌ DB Channel not set.")
    await message.reply_text("🌟 <b>Forward messages from DB Channel and send /done</b>")
    ids = []
    while True:
        try:
            msg = await client.listen(message.chat.id, timeout=300)
            if msg.text == '/done': break
            if msg.forward_from_chat and msg.forward_from_chat.id == client.db_channel.id:
                ids.append(msg.forward_from_message_id)
                await msg.reply_text(f"✅ Added! Total: {len(ids)}")
        except: return
    
    if not ids: return
    await message.reply_text("🌟 <b>Send Custom Message for this link:</b>")
    try:
        custom = await client.listen(message.chat.id)
        txt = custom.text or "Files:"
        cid = abs(client.db_channel.id)
        l_str = f"get-{ids[0]*cid}" if len(ids)==1 else f"custombatch-{'-'.join([str(i*cid) for i in ids])}"
        enc = await encode(l_str)
        await client.db.settings.update_one({"_id": f"special_{enc}"}, {"$set": {"message": txt}}, upsert=True)
        await message.reply_text(f"✅ <b>Link:</b> <code>https://t.me/{client.username}?start={enc}</code>")
    except: pass

@Client.on_message(filters.private & filters.command("shortener"))
async def shortener_command(client, message):
    if len(message.command) < 2: return await message.reply_text("Usage: /shortener [URL]")
    url = message.command[1]
    async with aiohttp.ClientSession() as s:
        async with s.get(f"https://ulvis.net/api.php?url={url}") as r:
            if r.status == 200:
                short = await r.text()
                await message.reply_text(f"✅ <b>Shortened:</b> <code>{short}</code>")

# ============================================================================
# GENLINK, BATCH & ADMIN CMDS (Rest of your features)
# ============================================================================

@Client.on_message(filters.private & filters.command("genlink"))
async def genlink_command(client, message):
    if not hasattr(client, "db_channel"): return await message.reply_text("❌ Configure DB Channel first.")
    await message.reply_text("Forward message from DB Channel...")
    try:
        msg = await client.listen(message.chat.id, timeout=60, filters=filters.forwarded)
        if msg.forward_from_chat.id != client.db_channel.id: return await message.reply_text("❌ Not from DB Channel.")
        
        cid = abs(client.db_channel.id)
        enc = await encode(f"get-{msg.forward_from_message_id * cid}")
        link = f"https://t.me/{client.username}?start={enc}"
        await message.reply_text(f"✅ <b>Link:</b>\n<code>{link}</code>")
    except: await message.reply_text("Timeout.")

@Client.on_message(filters.private & filters.command("batch"))
async def batch_command(client, message):
    if not hasattr(client, "db_channel"): return await message.reply_text("❌ Configure DB Channel first.")
    await message.reply_text("Forward FIRST message from DB Channel...")
    try:
        first = await client.listen(message.chat.id, timeout=60, filters=filters.forwarded)
        await message.reply_text("Forward LAST message from DB Channel...")
        last = await client.listen(message.chat.id, timeout=60, filters=filters.forwarded)
        
        cid = abs(client.db_channel.id)
        enc = await encode(f"get-{first.forward_from_message_id * cid}-{last.forward_from_message_id * cid}")
        link = f"https://t.me/{client.username}?start={enc}"
        await message.reply_text(f"✅ <b>Batch Link:</b>\n<code>{link}</code>")
    except: await message.reply_text("Timeout or Error.")

@Client.on_message(filters.private & filters.command("settings"))
async def settings_command(client, message):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔒 Protection", callback_data="setting_protection"), InlineKeyboardButton("📁 Files", callback_data="setting_files")],
        [InlineKeyboardButton("🗑️ Auto Delete", callback_data="setting_auto_delete"), InlineKeyboardButton("📢 Force Sub", callback_data="setting_force_sub")],
        [InlineKeyboardButton("🔒 Close", callback_data="close")]
    ])
    await message.reply_text("⚙️ <b>SETTINGS PANEL</b>", reply_markup=buttons)

@Client.on_callback_query()
async def cb_handler(client, query):
    data = query.data
    if data == "close": await query.message.delete()
    elif data == "help": await query.answer("Use commands to interact!", show_alert=True)
    elif data == "about": await query.answer("Advanced Auto Filter Bot V3", show_alert=True)
    elif data.startswith("setting_"): await query.answer("Settings Menu Accessed", show_alert=False)
    # Add other callbacks from your original code here if needed

# ============================================================================
# MAIN EXECUTION (FIXED FOR RENDER)
# ============================================================================

async def main():
    import config
    
    # 1. Initialize Bot
    bot = Bot()
    
    # 2. Configure Channel (Initial check)
    if config.CHANNELS and config.CHANNELS[0] != 0:
        try:
            bot.db_channel = await bot.get_chat(config.CHANNELS[0])
            bot.db_channel_id = bot.db_channel.id
        except: pass

    # 3. Start Web Server (CRITICAL FOR RENDER)
    await start_web_server()

    # 4. Start Bot & Idle
    await bot.start()
    await idle()
    await bot.stop()

if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except KeyboardInterrupt:
        print("👋 Bye!")
