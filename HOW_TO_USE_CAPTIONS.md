# 📝 Complete Caption Usage Guide

## 🎯 How to Add Captions to Your Files

You have **3 EASY OPTIONS** to format captions!

---

## ✅ OPTION 1: Simple Text (Auto-Converts!)

### When You Send File:
```
[Forward video to bot]

Caption you type:
This is a **great** movie! Must watch 🎬
Rating: *5/5*
```

### What User Gets:
```
[Video plays]

Caption shows:
This is a great movie! Must watch 🎬  ← Bold!
Rating: 5/5  ← Italic!
```

### 🎨 Auto-Convert Syntax:

| You Type | Converts To | Shows As |
|----------|-------------|----------|
| `**text**` | `<b>text</b>` | **text** (bold) |
| `__text__` | `<b>text</b>` | **text** (bold) |
| `*text*` | `<i>text</i>` | *text* (italic) |
| `_text_` | `<i>text</i>` | *text* (italic) |
| `~~text~~` | `<s>text</s>` | ~~text~~ (strikethrough) |
| `` `text` `` | `<code>text</code>` | `text` (code) |
| `++text++` | `<u>text</u>` | <u>text</u> (underline) |
| `||text||` | `<tg-spoiler>text</tg-spoiler>` | ||text|| (spoiler) |

### 💡 Examples:

#### Example 1: Movie
```
Caption you type:
**Movie Name:** Avengers Endgame
**Quality:** HD 1080p
**Size:** 2.5 GB

*The epic conclusion!*
```

Shows as:
```
Movie Name: Avengers Endgame  ← Bold
Quality: HD 1080p  ← Bold
Size: 2.5 GB  ← Bold

The epic conclusion!  ← Italic
```

#### Example 2: With Spoiler
```
Caption you type:
**Episode 5** is here!

||WARNING: Spoilers ahead!||

Rating: *10/10*
```

Shows as:
```
Episode 5 is here!  ← Bold

WARNING: Spoilers ahead!  ← Hidden until clicked

Rating: 10/10  ← Italic
```

#### Example 3: Mixed
```
Caption you type:
**Title:** Naruto Episode 1
*Quality:* HD
~~Old version~~
++NEW VERSION++

Join: `@YourChannel`
```

Shows as:
```
Title: Naruto Episode 1  ← Bold
Quality: HD  ← Italic
Old version  ← Strikethrough
NEW VERSION  ← Underlined

Join: @YourChannel  ← Code style
```

---

## ✅ OPTION 2: Direct HTML (Advanced)

### When You Send File:
```
[Forward video to bot]

Caption you type:
<b>Movie Name:</b> Avengers
<i>Quality:</i> HD

<tg-spoiler>Hidden text</tg-spoiler>
```

### What User Gets:
```
[Video plays]

Caption shows exactly as formatted!
Movie Name: Avengers  ← Bold
Quality: HD  ← Italic

Hidden text  ← Spoiler (click to reveal)
```

### 🎨 HTML Tags Supported:

```html
<b>bold text</b>
<strong>bold text</strong>

<i>italic text</i>
<em>italic text</em>

<u>underlined text</u>

<s>strikethrough</s>
<strike>strikethrough</strike>
<del>strikethrough</del>

<code>monospace code</code>

<pre>code block</pre>
<pre language="python">python code</pre>

<a href="https://t.me/channel">clickable link</a>

<tg-spoiler>hidden text</tg-spoiler>

<blockquote>visible quote</blockquote>
<blockquote expandable>collapsed quote (click to show)</blockquote>
```

### 💡 Examples:

#### Example 1: Full HTML
```html
<b>🎬 Movie Name:</b> Avengers Endgame

<blockquote expandable>
<b>📊 Details:</b>
• Quality: HD 1080p
• Size: 2.5 GB
• Language: English

<b>📝 Plot:</b>
The epic conclusion to the Infinity Saga!
</blockquote>

<i>Join:</i> <a href="https://t.me/yourchannel">@YourChannel</a>
```

Shows as:
```
🎬 Movie Name: Avengers Endgame

[▶ Show Details]  ← Click to expand

Join: @YourChannel  ← Clickable link
```

#### Example 2: With Code
```html
<b>Software:</b> Python Installer

<code>Version: 3.11.0</code>
<code>Size: 25 MB</code>

<pre>
Install command:
python setup.py install
</pre>

<a href="https://t.me/software">Download More</a>
```

---

## ✅ OPTION 3: Custom Template (Automatic)

### In Your .env File:
```env
CUSTOM_CAPTION=📁 <b>{filename}</b>\n\nSize: {filesize}\n\n@YourChannel
```

### When You Send File:
```
[Forward video]
Caption: Great movie!
```

### What User Gets:
```
[Video plays]

Caption shows:
📁 Avengers.mkv  ← Bold, from template

Size: 2.5 GB  ← From template

@YourChannel  ← From template

Great movie!  ← Your original caption
```

### With Original Caption in Spoiler:
```env
CUSTOM_CAPTION=📁 <b>{filename}</b>\n\nSize: {filesize}\n\n<tg-spoiler>{previouscaption}</tg-spoiler>\n\n@YourChannel
```

Shows as:
```
📁 Avengers.mkv

Size: 2.5 GB

Great movie!  ← Hidden until clicked

@YourChannel
```

---

## 🎯 Which Option Should You Use?

### For Beginners: **OPTION 1** (Auto-Convert)
```
Just type naturally:
**Bold text**
*Italic text*
||Spoiler||
```
✅ Easy
✅ No HTML knowledge needed
✅ Auto-converts

### For Advanced Users: **OPTION 2** (Direct HTML)
```html
Full control:
<b>Bold</b>
<blockquote expandable>Collapsed text</blockquote>
<a href="url">Link</a>
```
✅ More features
✅ Blockquote support
✅ Links

### For Automation: **OPTION 3** (Template)
```env
CUSTOM_CAPTION=your template
```
✅ Consistent style
✅ Auto-adds info
✅ No manual work

---

## 💡 Mix & Match!

You can use **ALL THREE** together!

### Example Workflow:

**Step 1: Set Template** (in .env)
```env
CUSTOM_CAPTION=📁 <b>{filename}</b>\n\n<blockquote expandable>{previouscaption}</blockquote>\n\n@YourChannel
```

**Step 2: Send File with Caption**
```
[Forward video]

Caption you type:
**Movie:** Avengers
*Quality:* HD
||Spoiler warning!||
```

**Step 3: User Gets**
```
📁 Avengers.mkv  ← From template (bold)

[▶ Show Details]  ← Click to expand
Movie: Avengers  ← Your caption (bold)
Quality: HD  ← Your caption (italic)
Spoiler warning!  ← Your caption (hidden)

@YourChannel  ← From template
```

**Perfect combination!** 🎉

---

## 🔧 Configuration

### Enable Auto-Convert (Recommended)
```env
# In .env - no special setting needed!
# Auto-convert is ALWAYS enabled
```

### Use Template + Auto-Convert
```env
# Set your template
CUSTOM_CAPTION=📁 <b>{filename}</b>\n\nSize: {filesize}\n\n<blockquote expandable>{previouscaption}</blockquote>\n\n@YourChannel

# Don't hide original caption
HIDE_CAPTION=False
```

### Template Only (No Original Caption)
```env
CUSTOM_CAPTION=📁 <b>{filename}</b>\n\nSize: {filesize}\n\n@YourChannel

# Hide original caption
HIDE_CAPTION=True
```

---

## 📋 Quick Reference Card

### Simple Formatting:
```
**bold** or __bold__
*italic* or _italic_
~~strikethrough~~
`code`
++underline++
||spoiler||
```

### HTML Formatting:
```html
<b>bold</b>
<i>italic</i>
<u>underline</u>
<s>strike</s>
<code>code</code>
<a href="url">link</a>
<tg-spoiler>hidden</tg-spoiler>
<blockquote>quote</blockquote>
<blockquote expandable>collapsed</blockquote>
```

### Template Placeholders:
```
{filename} - File name
{filesize} - Size (formatted)
{mime_type} - File type
{previouscaption} - Your caption
```

---

## 🎨 Real Examples

### Example 1: Movie Caption (Simple)
```
You type:
**🎬 Movie:** Avengers Endgame
**📊 Quality:** HD 1080p
**💾 Size:** 2.5 GB

*The epic conclusion to the Infinity Saga!*

||Spoiler: Tony Stark dies||

Join: @YourMovieChannel
```

### Example 2: Anime Caption (HTML)
```html
<b>📺 Anime:</b> Naruto Shippuden
<i>Episode 500</i>

<blockquote expandable>
<b>Synopsis:</b>
The final battle begins as Naruto faces Sasuke!

<tg-spoiler>Major plot twist ahead!</tg-spoiler>
</blockquote>

<a href="https://t.me/youranimechannel">More Episodes</a>
```

### Example 3: Software Caption (Mixed)
```
**📱 App Name:** TikTok Premium
**Version:** 32.0.4

Features:
• No Ads
• HD Download
• ++Premium++ Unlocked

||Download link in group||

Join: `@YourSoftwareChannel`
```

---

## ⚙️ Settings Summary

```env
# Your custom template (optional)
CUSTOM_CAPTION=📁 <b>{filename}</b>\n\nSize: {filesize}\n\n@YourChannel

# Hide original caption? (False = show both, True = template only)
HIDE_CAPTION=False

# Protect content (disable forwarding)
PROTECT_CONTENT=True
```

---

## 🎯 Best Practices

### ✅ DO:
- Use simple formatting for quick posts
- Use HTML for complex layouts
- Use templates for consistency
- Test your captions before deploying
- Keep captions readable

### ❌ DON'T:
- Mix markdown and HTML (choose one)
- Use too many emojis
- Make captions too long
- Forget line breaks (`\n`)
- Use broken HTML tags

---

## 🆘 Troubleshooting

### Caption Not Formatted?
**Check:**
- Using correct syntax: `**text**` not `*text*` for bold
- HTML tags closed: `<b>text</b>` not `<b>text`
- No typos in tags

### Template Not Working?
**Check:**
- `.env` file has `CUSTOM_CAPTION=...`
- Restarted bot after changes
- `HIDE_CAPTION=False` to see both

### Blockquote Not Collapsing?
**Check:**
- Using `<blockquote expandable>` not just `<blockquote>`
- Telegram app is updated
- Some old Telegram versions don't support expandable

---

## 🎉 Summary

### Three Easy Ways:

1. **Auto-Convert** (Easiest)
   - Type: `**bold** *italic* ||spoiler||`
   - Automatic conversion!

2. **Direct HTML** (Powerful)
   - Type: `<b>bold</b> <blockquote>quote</blockquote>`
   - Full control!

3. **Template** (Consistent)
   - Set: `CUSTOM_CAPTION=...`
   - Automatic addition!

**All work together perfectly!** 🚀

---

Need more help? Check:
- `CAPTION_GUIDE.md` - Detailed guide
- `CAPTION_TEMPLATES.md` - Ready templates
- `.env.complete` - Configuration examples
