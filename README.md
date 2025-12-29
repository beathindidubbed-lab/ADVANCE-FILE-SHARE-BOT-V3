# 🤖 Advanced Auto Filter Bot V3

**Complete file-sharing bot with beautiful interactive UI - EvaMaria Style**

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Pyrogram](https://img.shields.io/badge/Pyrogram-2.0+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ Features

### 📁 File Sharing
- ✅ Share files via unique links
- ✅ Batch link generation
- ✅ Auto-forward to database channel
- ✅ Support for all file types

### 🎨 Beautiful Interactive UI
- ✅ Button-based menus
- ✅ Settings panels with toggles
- ✅ Anime-style welcome interface
- ✅ Interactive admin panel
- ✅ Real-time status indicators

### 🔒 Protection & Privacy
- ✅ Protect content (disable forwarding)
- ✅ Hide/show captions
- ✅ Custom captions support
- ✅ Channel button control

### 📢 Force Subscribe
- ✅ Multiple force-sub channels
- ✅ Request join mode
- ✅ Auto-detect join status
- ✅ Custom force-sub message

### 🗑️ Auto Delete
- ✅ Auto-delete files after time
- ✅ Configurable timer
- ✅ User notifications
- ✅ Re-access via link

### 👥 User Management
- ✅ User database
- ✅ Ban/unban system
- ✅ Broadcast messages
- ✅ User statistics

### ⚙️ Admin Commands
- ✅ `/users` - User statistics
- ✅ `/broadcast` - Broadcast message
- ✅ `/ban` / `/unban` - User management
- ✅ `/stats` - Bot statistics
- ✅ `/settings` - Bot settings
- ✅ `/forcesub` - Force sub settings
- ✅ `/files` - File settings
- ✅ `/auto_del` - Auto-delete settings
- ✅ `/req_fsub` - Request FSub settings
- ✅ `/batch` - Batch link generator

---

## 📥 Installation

### Prerequisites
- Python 3.8 or higher
- MongoDB database
- Telegram Bot Token
- Telegram API ID and Hash

### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/AdvanceAutoFilterBot
cd AdvanceAutoFilterBot
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment
```bash
cp .env.sample .env
nano .env
```

Edit `.env` with your details:
```env
API_ID=12345678
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
DATABASE_URI=mongodb+srv://...
CHANNELS=-1003606299423
ADMINS=your_user_id
FORCE_SUB_CHANNELS=-1001234567890
```

### Step 4: Run Bot
```bash
python3 bot.py
```

---

## 🚀 Deployment

### Deploy on Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)

1. Click the button above
2. Add environment variables
3. Deploy!

### Deploy on Heroku

[![Deploy on Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

1. Click the button above
2. Fill in config vars
3. Deploy!

### Deploy on VPS

```bash
# Install dependencies
sudo apt update
sudo apt install python3 python3-pip git

# Clone and setup
git clone https://github.com/yourusername/AdvanceAutoFilterBot
cd AdvanceAutoFilterBot
pip3 install -r requirements.txt

# Configure
cp .env.sample .env
nano .env

# Run in background
nohup python3 bot.py &

# Or use screen
screen -S bot
python3 bot.py
# Press Ctrl+A then D to detach
```

---

## 📖 Commands

### User Commands
- `/start` - Start the bot
- `/help` - Get help
- `/about` - About bot

### Admin Commands
- `/users` - View user statistics
- `/broadcast` - Broadcast message to all users
- `/ban <user_id>` - Ban a user
- `/unban <user_id>` - Unban a user
- `/stats` - View bot statistics
- `/settings` - Bot settings panel
- `/batch` - Generate batch links

### Settings Commands
- `/forcesub` - Force subscribe commands
- `/files` - File protection settings
- `/auto_del` - Auto-delete settings
- `/req_fsub` - Request force-sub mode

---

## ⚙️ Configuration

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `API_ID` | Telegram API ID | `12345678` |
| `API_HASH` | Telegram API Hash | `abcdef1234567890` |
| `BOT_TOKEN` | Bot token from @BotFather | `123456:ABC-DEF` |
| `DATABASE_URI` | MongoDB connection URI | `mongodb+srv://...` |
| `CHANNELS` | File storage channel ID | `-1003606299423` |
| `ADMINS` | Admin user IDs (space-separated) | `123456 789012` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_NAME` | MongoDB database name | `AdvanceAutoFilterBot` |
| `LOG_CHANNEL` | Log channel ID | None |
| `FORCE_SUB_CHANNELS` | Force subscribe channels | None |
| `REQUEST_FSUB` | Enable request join mode | `False` |
| `PROTECT_CONTENT` | Disable forwarding | `True` |
| `HIDE_CAPTION` | Hide original captions | `False` |
| `AUTO_DELETE_TIME` | Auto-delete time (seconds) | `0` |
| `SUPPORT_CHAT` | Support chat username | None |
| `UPDATES_CHANNEL` | Updates channel username | None |

---

## 📱 Screenshots

### Start Menu
<img src="https://via.placeholder.com/800x400?text=Beautiful+Start+Menu" alt="Start Menu">

### Settings Panel
<img src="https://via.placeholder.com/800x400?text=Interactive+Settings" alt="Settings">

### Force Subscribe
<img src="https://via.placeholder.com/800x400?text=Force+Subscribe+UI" alt="Force Sub">

### Admin Panel
<img src="https://via.placeholder.com/800x400?text=Admin+Commands" alt="Admin">

---

## 🛠️ How to Use

### For Admins

#### 1. Upload Files
Forward any file (document/video/audio) to the bot in private chat.
Bot will:
- Upload to database channel
- Generate a shareable link
- Send you the link

#### 2. Create Batch Links
Use `/batch` command:
1. Forward FIRST message from channel
2. Forward LAST message from channel
3. Bot generates batch link for all files in between

#### 3. Configure Settings
Use `/settings` to access:
- File protection settings
- Force subscribe configuration
- Auto-delete settings
- Request force-sub mode

### For Users

#### 1. Access Files
Click on shared links → Bot sends files

#### 2. Join Channels (if force-sub enabled)
Join required channels → Click "Try Again"

---

## 🎨 Customization

### Change Welcome Image
```python
# In .env
BOT_PICS=https://telegra.ph/file/your-image.jpg
```

### Customize Messages
Edit messages in `.env`:
- `WELCOME_TEXT` - Start message
- `HELP_TEXT` - Help message
- `ABOUT_TEXT` - About message
- `FORCE_SUB_TEXT` - Force subscribe message

### Custom Buttons
```python
# Format: Text | URL
CUSTOM_BUTTONS=Button1 | https://link1.com : Button2 | https://link2.com
```

---

## 🔧 Troubleshooting

### Bot not starting?
- Check API_ID, API_HASH, BOT_TOKEN
- Verify MongoDB connection
- Check Python version (3.8+)

### Files not sending?
- Verify CHANNELS configuration
- Check bot is admin in database channel
- Ensure channel ID has minus sign

### Force subscribe not working?
- Bot must be admin in force-sub channel
- Verify FORCE_SUB_CHANNELS format
- Check bot can create invite links

---

## 📝 License

This project is licensed under the MIT License.

---

## 💝 Support

- **Telegram:** @YourSupport
- **Channel:** @YourChannel
- **Email:** your@email.com

---

## 🙏 Credits

- [Pyrogram](https://docs.pyrogram.org) - MTProto API Framework
- [MongoDB](https://www.mongodb.com) - Database
- Inspired by EvaMaria bots

---

## ⭐ Star this repo if you like it!

**Made with ❤️ by [Your Name]**
