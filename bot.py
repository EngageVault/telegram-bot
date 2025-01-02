"""
EngageVault Telegram Bot
------------------------
A professional Telegram bot for EngageVault platform.
"""

import os
import logging
import platform
import asyncio
from typing import Final
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackContext
)

# Configuration du logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Constants
TOKEN: Final = os.getenv("TELEGRAM_TOKEN", "7929001260:AAG_EZTbt3C11GCZauaLqkuP99YKkxB1NJg")
WELCOME_MESSAGE: Final = """🚀 Welcome to EngageVault!

⭐ Congratulations Early Adopter! ⭐

You've just discovered the next big thing in social media growth, and you're among the first to join! 🎯

💎 Being an early member means:
• EXCLUSIVE ACCESS to premium features
• PRIORITY STATUS for upcoming features
• FREE GIFTS for early supporters

📝 How you'll benefit:
• Boost your social media presence
• Earn real rewards while growing
• Connect with power users
• Get ahead of the competition

⚡ Don't miss out on these early-bird benefits!
Join now before regular rates apply! 🎁

Ready to multiply your social growth? Tap below! 👇"""

async def start_command(update: Update, context: CallbackContext) -> None:
    """
    Handler for the /start command.
    Sends a welcome message to the user.
    """
    try:
        user = update.effective_user
        logger.info(f"User {user.id} started the bot")
        await update.message.reply_text(WELCOME_MESSAGE)
    except Exception as e:
        logger.error(f"Error in start command: {str(e)}")
        await update.message.reply_text("An error occurred. Please try again later.")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler for bot errors.
    Logs errors and notifies users if necessary.
    """
    logger.error(f"Update {update} caused error {context.error}")

def init_bot() -> Application:
    """
    Initializes and configures the bot application.
    Returns the configured application instance.
    """
    try:
        app = Application.builder().token(TOKEN).build()
        
        # Add command handlers
        app.add_handler(CommandHandler("start", start_command))
        
        # Add error handler
        app.add_error_handler(error_handler)
        
        return app
    except Exception as e:
        logger.critical(f"Failed to initialize bot: {str(e)}")
        raise

async def main() -> None:
    """
    Main function to run the bot.
    """
    try:
        logger.info("Starting bot...")
        app = init_bot()
        await app.initialize()
        await app.start()
        await app.run_polling()
    except Exception as e:
        logger.critical(f"Critical error: {str(e)}")
    finally:
        logger.info("Bot stopped")

if __name__ == "__main__":
    # Configure event loop policy for Windows
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # Run the bot
    asyncio.run(main())