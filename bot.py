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
ADMIN_ID = 7686799533

# Compteur en mémoire
start_count = 0
unique_users = set()

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
    logger.info("Commande /start reçue")
    try:
        global start_count, unique_users
        start_count += 1
        unique_users.add(update.effective_user.id)
        
        keyboard = [
            [InlineKeyboardButton("⭐ Join our Community", url="https://t.me/engagevaultcommunity")],
            [InlineKeyboardButton("🚀 Launch App", url="https://google.com")]
        ]
        
        update.message.reply_text(
            WELCOME_MESSAGE,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        logger.info("Message de bienvenue envoyé")
    except Exception as e:
        logger.error(f"Erreur dans start: {str(e)}")

def get_stats(update: Update, context: CallbackContext):
    logger.info("Commande /stats reçue")
    try:
        user_id = update.effective_user.id
        if user_id != ADMIN_ID:
            update.message.reply_text("⛔ You don't have permission to use this command.")
            return
            
        stats_message = f"""📊 Bot Statistics:

Total /start commands: {start_count}
Unique users: {len(unique_users)}"""

        update.message.reply_text(stats_message)
        logger.info("Stats envoyées")
    except Exception as e:
        logger.error(f"Erreur dans stats: {str(e)}")

if __name__ == '__main__':
    logger.info("Démarrage du bot...")
    try:
        updater = Updater(TOKEN)
        updater.dispatcher.add_handler(CommandHandler("start", start))
        updater.dispatcher.add_handler(CommandHandler("stats", get_stats))
        logger.info("Handlers ajoutés")
        
        logger.info("Démarrage du polling...")
        updater.start_polling()
        logger.info("Bot démarré avec succès")
        updater.idle()
    except Exception as e:
        logger.error(f"Erreur critique au démarrage: {str(e)}")