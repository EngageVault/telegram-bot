import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)

# Bot Token
TOKEN = "7929001260:AAG_EZTbt3C11GCZauaLqkuP99YKxB1NJg"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    try:
        buttons = [
            [InlineKeyboardButton("⭐ Join our Community", url="https://t.me/engagevaultcommunity")],
            [InlineKeyboardButton("🚀 Launch App", url="https://test.com")]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)

        await update.message.reply_text(
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
            "Ready to multiply your social growth? Tap below! 👇",
            reply_markup=reply_markup
        )
        logging.info("Message sent successfully with buttons")
    except Exception as e:
        logging.error(f"Error sending message: {e}")
        await update.message.reply_text("An error occurred. Please try again.")

def main() -> None:
    """Start the bot."""
    try:
        # Create the Application
        application = Application.builder().token(TOKEN).build()

        # Add command handler
        application.add_handler(CommandHandler("start", start))

        # Start the Bot
        print("Bot is starting...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logging.error(f"Error starting bot: {e}")

if __name__ == "__main__":
    main()