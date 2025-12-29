[ACTIONS_SETUP.md](https://github.com/user-attachments/files/24366684/ACTIONS_SETUP.md)
# GitHub Actions Setup Guide

## 📋 Workflows Included

### 1. **deploy.yml** - Auto Deploy
- ✅ Tests code on push
- ✅ Auto-deploys to Heroku
- ✅ Auto-deploys to Render
- ✅ Sends Telegram notification

### 2. **quality.yml** - Code Quality
- ✅ Checks code formatting
- ✅ Runs linters
- ✅ Security checks

### 3. **update-deps.yml** - Dependency Updates
- ✅ Weekly automatic updates
- ✅ Creates PR with updates

---

## ⚙️ Setup Secrets

### Go to: GitHub Repo → Settings → Secrets → Actions

### Add these secrets:

#### For Heroku Deployment:
```
HEROKU_API_KEY = your_heroku_api_key
HEROKU_APP_NAME = beatanimebot
HEROKU_EMAIL = your_email@example.com
```

**Get Heroku API Key:**
```bash
heroku login
heroku auth:token
```

#### For Render Deployment:
```
RENDER_DEPLOY_HOOK = https://api.render.com/deploy/srv-xxxxx
```

**Get Render Deploy Hook:**
1. Go to Render dashboard
2. Your service → Settings
3. Deploy Hook → Copy URL

#### For Telegram Notifications (Optional):
```
TELEGRAM_BOT_TOKEN = 123456:ABC-DEF
TELEGRAM_CHAT_ID = your_chat_id
```

Use your bot token or create new one with @BotFather

---

## 🚀 How It Works

### Auto-Deploy Flow:
```
1. You push code to main branch
2. GitHub Actions runs tests
3. If tests pass, deploys to Heroku/Render
4. Sends notification to Telegram
```

### What Triggers Deploy:
- Push to `main` or `master` branch
- Manual trigger via GitHub Actions tab

---

## 🔧 Customize Workflows

### Change Deploy Branch:
Edit `.github/workflows/deploy.yml`:
```yaml
on:
  push:
    branches: [ main, dev ]  # Add your branches
```

### Disable Heroku/Render:
Remove the respective job from `deploy.yml`

### Change Update Schedule:
Edit `.github/workflows/update-deps.yml`:
```yaml
schedule:
  - cron: '0 0 * * 1'  # Weekly on Monday
  # Change to: '0 0 1 * *' for monthly
```

---

## 💡 Usage Examples

### Manual Deploy:
```
1. Go to: Actions tab
2. Select "Deploy Beat Anime Bot"
3. Click "Run workflow"
4. Choose branch
5. Run!
```

### Check Deployment Status:
```
Actions tab → Latest workflow run
```

### View Logs:
```
Click on workflow run → Click on job → View logs
```

---

## 🎯 Benefits

✅ **Auto-deploy** - Push code, auto-deploys
✅ **No manual work** - Everything automated
✅ **Quality checks** - Catches errors before deploy
✅ **Notifications** - Know when deployed
✅ **Easy rollback** - Redeploy previous commit

---

## 🆘 Troubleshooting

### Deploy Failed?
- Check secrets are set correctly
- View logs in Actions tab
- Verify Heroku/Render credentials

### Notifications Not Working?
- Verify TELEGRAM_BOT_TOKEN
- Check TELEGRAM_CHAT_ID is correct
- Bot must be started by you

### Quality Checks Failing?
- These are warnings, not errors
- They don't stop deployment
- Fix issues for better code quality

---

## 🎉 You're Set!

Every push to main branch = Auto-deployment! 🚀

Just add secrets and push code!
