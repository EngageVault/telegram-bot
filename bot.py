from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext
import os
import logging

# Configuration du logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN", "7929001260:AAG_EZTbt3C11GCZauaLqkuP99YKkxB1NJg")

WELCOME_MESSAGE = """🚀 Welcome to EngageVault!

⭐ Congratulations Early Adopter! ⭐

You've just discovered the next big thing in social media growth - and you're among the first to join! 🎯

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

def start(update: Update, context: CallbackContext):
    try:
        logger.info("Commande start reçue")
        keyboard = [
            [InlineKeyboardButton("⭐ Join our Community", url="https://t.me/engagevaultcommunity")],
            [InlineKeyboardButton("🚀 Launch App", url="https://google.com")]
        ]
        update.message.reply_text(WELCOME_MESSAGE, reply_markup=InlineKeyboardMarkup(keyboard))
        logger.info("Message envoyé avec succès")
    except Exception as e:
        logger.error(f"Erreur dans start: {str(e)}")

if __name__ == '__main__':
    try:
        logger.info("Démarrage du bot...")
        updater = Updater(TOKEN)
        updater.dispatcher.add_handler(CommandHandler("start", start))
        logger.info("Bot prêt à démarrer")
        updater.start_polling()
        logger.info("Bot démarré et en attente de commandes")
        updater.idle()
    except Exception as e:
        logger.error(f"Erreur au démarrage: {str(e)}")