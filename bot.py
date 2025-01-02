import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot Token
TOKEN = "7929001260:AAG_EZTbt3C11GCZauaLqkuP99YKkxB1NJg"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    try:
        # Création des boutons avec les URLs
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton(text="⭐ Join our Community", url="https://t.me/engagevaultcommunity")],
            [InlineKeyboardButton(text="🚀 Launch App", url="https://test.com")]
        ])

        # Envoi du message avec les boutons
        await update.message.reply_text(
            text=(
                "🚀 Welcome to EngageVault!\n\n"
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
                "Ready to multiply your social growth? Tap below! 👇"
            ),
            reply_markup=buttons,
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await update.message.reply_text("An error occurred. Please try again.")

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(TOKEN).build()

    # Add command handler
    application.add_handler(CommandHandler("start", start))

    # Start the Bot
    print("Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    print("Bot is stopped")

if __name__ == "__main__":
    main()