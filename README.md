# 📁 Telegram File Storage Bot

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Telegram](https://img.shields.io/badge/Telegram-Bot_API-green.svg)](https://core.telegram.org/bots/api)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A secure file storage Telegram bot that generates shareable download links with tracking capabilities.

**Repository:** [rocketdotpy/telegram-file-bot](https://github.com/rocketdotpy/telegram-file-bot)

## 🌟 Features
- 🔒 Secure file storage with UUID protection
- 📤 Supports documents, photos, videos, audio
- 🔗 Generates unique download links
- 📊 Download statistics tracking
- 👨‍💻 Admin dashboard with `/stats` and `/cleanup`
- 📝 File caption support
- ⚡ Fast file delivery system

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Telegram Bot Token from [@BotFather](https://t.me/BotFather)

### Installation
```bash
git clone https://github.com/rocketdotpy/telegram-file-bot.git
cd telegram-file-bot
pip install -r requirements.txt
```

### Configuration
1. Rename `config_sample.py` to `config.py`
2. Add your bot token and admin username:
```python
BOT_TOKEN = 'your_bot_token_here'
ADMIN_ID = 'rocket_0_07'  # Your Telegram username
```

### Running the Bot
```bash
python mm.py
```

## 📚 Command Reference
| Command | Description | Access |
|---------|-------------|--------|
| `/start` | Welcome message | Public |
| `/help` | Usage instructions | Public |
| `/stats` | Storage statistics | Admin |
| `/cleanup` | Delete all files | Admin |

## 🛠️ Project Structure
```
telegram-file-bot/
├── main.py               # main
├── requirements.txt    # Dependencies
├── file_storage/       # Uploaded files directory
└── README.md           # This file
```

## 🤝 Contributing
Contributions are welcome! Please fork the repository and create a pull request.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📜 License
Distributed under the MIT License. See `LICENSE` for more information.

## 📬 Contact
Rocket - [@rocket_0_07](https://t.me/rocket_0_07)

Project Link: [https://github.com/rocketdotpy/telegram-file-bot](https://github.com/rocketdotpy/telegram-file-bot)
```
