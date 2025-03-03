# Minecraft Online Bot

A Telegram bot that helps users track the online status of players on a Minecraft server. Users can check who is currently online, subscribe for notifications about player connections or disconnections, and stay updated on the server's status.

## 🚀 Features

- 🌐 See the list of players currently online on the Minecraft server.
- 📲 Subscribe to get notifications when players connect or disconnect.
- 🔄 Real-time updates sent to subscribed users whenever a player joins or leaves the server.
- 📝 Logs errors and subscription activity for easy debugging.

## 🛠 Technologies Used

- **Python**: The main programming language.
- **Telegram Bot API**: For interacting with users via Telegram.
- **requests**: To make HTTP requests to the Minecraft server API and fetch player data.
- **python-telegram-bot**: Telegram bot framework to simplify development.
- **logging**: Handles error tracking and debugging.
- **dotenv**: Loads environment variables such as the bot token and API endpoint from a `.env` file.

## 📜 Usage

1. Start the bot with `/start`.
2. Use the `/help` command to learn how to interact with the bot.
3. Click the 'Online' button to see the current players online on the server.
4. Click the 'Subscription' button to subscribe/unsubscribe from notifications about player activity.

## How to Run the Bot Locally

1. Clone this repository to your local machine.
2. Create a `.env` file in the root directory and add your bot token and server API URL:

---

Made with ❤️ by Danylo Samedov
