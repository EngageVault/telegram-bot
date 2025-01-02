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

def start(update: Update, context: CallbackContext):
    logger.info("Commande /start reçue")
    try:
        update.message.reply_text("👋 Hello! Bot is working!")
        logger.info("Message envoyé avec succès")
    except Exception as e:
        logger.error(f"Erreur dans start: {str(e)}")

def get_stats(update: Update, context: CallbackContext):
    logger.info("Commande /stats reçue")
    try:
        update.message.reply_text("📊 Stats command received!")
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