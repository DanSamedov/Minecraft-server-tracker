import logging
import requests
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, filters, MessageHandler


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


reply_keyboard = [
    ["Online"],
    ["Subscription"]
]
markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)


players = []
subscribed_users = []


with open("userslist.txt", "r") as file:
    for line in file:
        words = line.split()

        for word in words:
            if word not in subscribed_users:
                subscribed_users.append(int(word))


async def api_func():
    global players
    global temporary_players

    x = requests.get("https://4c6b-91-218-194-203.ngrok-free.app/status/java/149.255.33.162:50651")
    y = x.json()

    a = y["players"]["list"]

    temporary_players = list(players)
    players = []

    for i in a:
        players.append(i["name_clean"])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! Use command /help to get help",
        reply_markup=markup,
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("To see current server online once use button 'Online'. " 
                                    "To get notification when someone connect or "
                                    "disconnect from the server, "
                                    "click on the 'Subscribe' button.")


async def active_players(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await api_func()

    players_online = ", ".join(players)
    if players_online != "":
        await update.message.reply_text(f"Players online: {players_online}\n"
                                        f"Players quantity: {len(players)}")
    else: 
        await update.message.reply_text("No one is online")


async def players_activity(context: ContextTypes.DEFAULT_TYPE) -> None:    
    await api_func()
    text = ''

    if list(set(players) - set(temporary_players)) != []:
        player_conn = list(set(players) - set(temporary_players))
        player_conn_str = ", ".join(player_conn)
        text = (f"{player_conn_str} connected")
    

    elif list(set(temporary_players) - set(players)) != []:
        player_disconn = list(set(temporary_players) - set(players))
        player_diconn_str = ", ".join(player_disconn)
        text = (f"{player_diconn_str} left")
    
    if text != '':
        for i in subscribed_users:    
            await context.bot.send_message(i, text)


async def subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_message.chat_id
    global subscribed_users

    if chat_id not in subscribed_users:
        subscribed_users.append(chat_id)
        chat_id_str = str(chat_id)
        with open("userslist.txt", "a") as file:
            file.write(' ' + chat_id_str)
        await update.message.reply_text('You are subscribed')   
    else:
        subscribed_users.remove(chat_id)
        subscribed_users_str = " "
        subscribed_users_str = subscribed_users_str.join(str(x) for x in subscribed_users)
        with open("userslist.txt", "w") as file:
            file.write(subscribed_users_str)
        await update.message.reply_text('You are unsubscribed')   


def main() -> None:
    application = Application.builder().token("6546676822:AAHhTVF6nb3mJ1nDAgDNRgTF3an_EZouc2o").build()
        
    application.job_queue.run_repeating(players_activity, 3, name='subscription')
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("online", active_players))
    application.add_handler(CommandHandler("subscription", subscription))

    application.add_handler(MessageHandler(filters.Regex("Online"), active_players))
    application.add_handler(MessageHandler(filters.Regex("Subscription"), subscription))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()