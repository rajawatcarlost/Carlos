# Carlos Promoter 🎯

**Multi-Account Telegram Message Broadcaster** - Manage multiple Telegram accounts and broadcast messages to multiple groups simultaneously!

## ✨ Features

✅ **Multi-Account Management** - Login and manage multiple Telegram accounts simultaneously  
✅ **One-Time Setup** - API ID & Hash stored permanently (never ask again)  
✅ **Session Persistence** - Accounts auto-login after app restart  
✅ **Group Management** - Load groups from each account with "Select All" option  
✅ **Bulk Broadcasting** - Send messages to multiple groups at once  
✅ **Anti-Spam Protection** - Adjustable delay between messages  
✅ **Auto-Repeat** - Messages auto-repeat at custom intervals  
✅ **Dark Theme UI** - Beautiful dark interface with red accents & smooth animations  
✅ **Broadcast History** - Track all sent messages  
✅ **Cross-Platform** - Works on Windows, Mac, and Linux  
✅ **Fast & Lightweight** - Flask localhost, zero lags  
✅ **No Dependencies** - No Telegram client installation required  
✅ **2FA Support** - Password-protected accounts fully supported  
✅ **Local Database** - SQLite (everything stays on your PC)  

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/rajawatcarlost/carlos.git
cd carlos
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
python app.py
```

4. **Open in browser**
Navigate to `http://127.0.0.1:5000` in your web browser

### First Time Setup

1. On first run, you'll be asked for **Telegram API credentials**
2. Get them from https://my.telegram.org
3. Enter **API ID** and **API Hash** - they're saved permanently!

## 📱 How to Use

### Step 1: Add Telegram Account
- Click **"Add New Account"** on dashboard
- Enter phone number (with country code)
- Verify with the code sent to your Telegram app
- If 2FA is enabled, enter your password

### Step 2: Select Groups
- Click **"Select Groups"** from dashboard
- Click **"Load Groups from Telegram"**
- Choose groups with checkboxes or **"Select All"**
- Save your selection

### Step 3: Send Messages
- Click **"Send Message"** from dashboard
- Write your message
- Set delay (2 seconds recommended to avoid Telegram spam limits)
- Enable auto-repeat if needed
- Click **"Send to All Groups"**

### Step 4: Manage Multiple Accounts
- Repeat steps 1-3 for each account
- All accounts work independently and simultaneously
- Broadcast history shows all activities

## 🔧 Configuration

### Telegram API Credentials
- Visit https://my.telegram.org
- Go to "API development tools"
- Get your **API ID** and **API Hash**
- Enter in setup page (first time only)

### Message Delays
- **Minimum 1 second**: Broadcast speed
- **Recommended 2-5 seconds**: Avoid Telegram rate limits
- **Maximum 60 seconds**: Custom delay

### Auto-Repeat Settings
- **Off**: Send once
- **On**: Repeat at custom interval (minimum 60 seconds)

## 📁 Project Structure

```
carlos/
├── app.py                    # Main Flask application
├── config.py                 # Configuration settings
├── models.py                 # Database models
├── telegram_handler.py       # Telethon integration
├── requirements.txt          # Python dependencies
├── templates/
│   ├── setup.html           # Initial setup page
│   ├── index.html           # Dashboard
│   ├── add_account.html     # Add new account
│   ├── accounts.html        # Accounts list
│   ├── groups.html          # Group selection
│   ├── broadcast.html       # Message broadcast
│   ├── history.html         # Broadcast history
│   ├── 404.html             # Error page
│   └── 500.html             # Server error page
├── static/
│   └── css/
│       └── style.css        # Dark theme styling
├── .gitignore               # Git ignore file
└── README.md                # This file
```

## 🎨 Theme

- **Dark Background**: Easy on the eyes
- **Red Accents**: Primary brand color (#e63946)
- **Smooth Animations**: Professional feel
- **Responsive Design**: Works on desktop & mobile
- **Modern UI**: Clean and intuitive interface

## 💾 Data Storage

- **Database**: SQLite (local, no server needed)
- **Sessions**: Stored locally in `telegram_sessions/` folder
- **Settings**: Auto-saved in database
- **No cloud sync**: Everything stays on your PC
- **No external dependencies**: No API calls to third parties

## ⚠️ Important Notes

1. **Telegram Rate Limits**: Don't send too many messages too fast
2. **2FA Accounts**: Password-protected accounts fully supported
3. **Group Permissions**: Ensure account has permission to send in selected groups
4. **Session Recovery**: Close app properly to save sessions
5. **Privacy**: All data stays on your computer
6. **No Logs**: No telemetry or tracking

## 🔒 Security

- API credentials stored securely in SQLite database
- Session strings stored locally (not transmitted)
- No external API calls (except to Telegram)
- No user data sent anywhere
- Open source - inspect code anytime
- Local execution only

## 📡 API Endpoints

```
GET  /                       - Dashboard
GET  /setup                  - Setup page
POST /save-setup             - Save API credentials
GET  /accounts               - Accounts list
GET  /add-account            - Add account page
POST /api/start-login        - Start login process
POST /api/verify-login-code  - Verify code
POST /api/verify-password    - Verify 2FA
GET  /api/get-groups/<id>    - Get groups for account
POST /api/save-groups        - Save selected groups
GET  /groups/<id>            - Groups page
GET  /broadcast/<id>         - Broadcast page
POST /api/send-broadcast     - Send message
DELETE /api/delete-account/<id> - Delete account
GET  /history                - Broadcast history
```

## 🐛 Troubleshooting

### "Code Request Failed"
- Check internet connection
- Ensure phone number format is correct
- Wait 30 seconds and try again

### "Account Already Added"
- That phone number is already logged in
- Delete account first if you want to re-add it

### "No Groups Found"
- Account may not be in any groups
- Ensure account has joined telegram groups
- Try loading again

### "Message Not Sent"
- Check account has permission to post in group
- Verify group membership
- Check message isn't too long

### Application Won't Start
- Ensure Python 3.7+ is installed
- Check all dependencies: `pip install -r requirements.txt`
- Try running on different port (modify app.py last line)

### Database Error
- Delete `carlos_promoter.db` and restart
- Database will be recreated automatically

## 📞 Support

For issues and feature requests, please open an issue on GitHub.

## 📄 License

This project is provided as-is for personal use.

## 🤝 Contributing

Feel free to fork and submit pull requests!

---

**Made with ❤️ for Telegram enthusiasts**

⭐ If you find this useful, please star the repository!
