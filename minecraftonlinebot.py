import logging
import requests
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, filters, MessageHandler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SERVER_API = os.getenv("SERVER_API")

# Configure logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Reply keyboard for the bot
reply_keyboard = [["Online"], ["Subscription"]]
markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)

# Using a set for fast lookup of subscribed users
subscribed_users = set()

# Load the subscribed users from file at startup
def load_subscribed_users():
    try:
        with open("userslist.txt", "r") as file:
            for line in file:
                subscribed_users.update(map(int, line.split()))
    except Exception as e:
        logger.error(f"Error loading users from file: {e}")

load_subscribed_users()

# Players and temporary players to track server state
players = []
temporary_players = []

# Function to fetch player data from the server API
async def api_func():
    global players, temporary_players
    try:
        response = requests.get(SERVER_API)
        response.raise_for_status()
        data = response.json()
        player_data = data.get("players", {}).get("list", [])
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data from the server API: {e}")
        return

    temporary_players = list(players)
    players = [player["name_clean"] for player in player_data]

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! Use command /help to get help",
        reply_markup=markup,
    )

# Help command handler
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "To see current server online once use button 'Online'. "
        "To get notification when someone connects or disconnects from the server, "
        "click on the 'Subscribe' button."
    )

# Active players handler
async def active_players(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await api_func()

    players_online = ", ".join(players)
    if players_online:
        await update.message.reply_text(f"Players online: {players_online}\nPlayers quantity: {len(players)}")
    else:
        await update.message.reply_text("No one is online")

# Periodic check for player activity (connected/disconnected players)
async def players_activity(context: ContextTypes.DEFAULT_TYPE) -> None:
    await api_func()
    text = ''

    # Players who connected
    player_conn = set(players).difference(set(temporary_players))
    if player_conn:
        text = f"{', '.join(player_conn)} connected"

    # Players who disconnected
    player_disconn = set(temporary_players).difference(set(players))
    if player_disconn:
        text = f"{', '.join(player_disconn)} left"

    if text:
        for user_id in subscribed_users:
            try:
                await context.bot.send_message(user_id, text)
            except Exception as e:
                logger.error(f"Failed to send message to {user_id}: {e}")


# Subscription handler
async def subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_message.chat_id

    if chat_id not in subscribed_users:
        subscribed_users.add(chat_id)
        logger.info(f"User {chat_id} subscribed.")
        update_user_list()
        await update.message.reply_text('You are subscribed')
    else:
        subscribed_users.remove(chat_id)
        logger.info(f"User {chat_id} unsubscribed.")
        update_user_list()
        await update.message.reply_text('You are unsubscribed')

# Helper function to update the subscription list in the file
def update_user_list():
    try:
        with open("userslist.txt", "w") as file:
            file.write(" ".join(str(x) for x in subscribed_users))
    except Exception as e:
        logger.error(f"Error writing to userslist.txt: {e}")

def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    # Run periodic job to check player activity
    application.job_queue.run_repeating(players_activity, interval=3, first=0, name='subscription')

    # Add handlers for commands and messages
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("online", active_players))
    application.add_handler(CommandHandler("subscription", subscription))

    application.add_handler(MessageHandler(filters.Regex("Online"), active_players))
    application.add_handler(MessageHandler(filters.Regex("Subscription"), subscription))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
