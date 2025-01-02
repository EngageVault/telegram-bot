import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot Token
TOKEN = "7929001260:AAG_EZTbt3C11GCZauaLqkuP99YKkxB1NJg"

def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    try:
        keyboard = [
            [InlineKeyboardButton("⭐ Join our Community", url="https://t.me/engagevaultcommunity")],
            [InlineKeyboardButton("🚀 Launch App", url="https://test.com")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text(
            text="TEST MESSAGE\n\nClick the buttons below!",
            reply_markup=reply_markup
        )
        logger.info("Test message sent with buttons")
    except Exception as e:
        logger.error(f"Error: {e}")
        update.message.reply_text("An error occurred")

def main() -> None:
    """Start the bot."""
    try:
        updater = Updater(TOKEN)
        dispatcher = updater.dispatcher
        dispatcher.add_handler(CommandHandler("start", start))
        print("Bot is starting...")
        updater.start_polling()
        updater.idle()
    except Exception as e:
        logger.error(f"Error starting bot: {e}")

if __name__ == '__main__':
    main()