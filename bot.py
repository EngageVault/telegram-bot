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
            text="🚀 Welcome to EngageVault!\n\n"
                "⭐ Congratulations Early Adopter! ⭐\n\n"
                "You've just discovered the next big thing in social media growth - and you're among the first to join! 🎯\n\n"
                "💎 Being an early member means:\n"
                "• EXCLUSIVE ACCESS to premium features\n"
                "• PRIORITY STATUS for upcoming features\n"
                "• FREE GIFTS for early supporters\n\n"
                "📝 How you'll benefit:\n"
                "• Boost your social media presence\n"
                "• Earn real rewards while growing\n"
                "• Connect with power users\n"
                "• Get ahead of the competition\n\n"
                "⚡ Don't miss out on these early-bird benefits!\n"
                "Join now before regular rates apply! 🎁\n\n"
                "Ready to multiply your social growth? Tap below! 👇",
            reply_markup=reply_markup
        )
        logger.info("Message sent with buttons")
    except Exception as e:
        logger.error(f"Error: {e}")
        update.message.reply_text("An error occurred")

def main() -> None:
    """Start the bot."""
    try:
        # Create the Updater
        updater = Updater(TOKEN)

        # Get the dispatcher to register handlers
        dispatcher = updater.dispatcher

        # Register command handlers
        dispatcher.add_handler(CommandHandler("start", start))

        # Start the Bot
        print("Bot is starting...")
        updater.start_polling()
        
        # Run the bot until you press Ctrl-C
        updater.idle()
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")

if __name__ == '__main__':
    main()