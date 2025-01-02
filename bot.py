from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext
import os
import psycopg2
import logging

# Configuration du logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN", "7929001260:AAG_EZTbt3C11GCZauaLqkuP99YKkxB1NJg")
ADMIN_ID = 7686799533
DATABASE_URL = os.getenv("DATABASE_URL")

def init_db():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Création de la table stats
        cur.execute('''
            DROP TABLE IF EXISTS stats;
            CREATE TABLE stats (
                total_starts INTEGER DEFAULT 0
            );
            INSERT INTO stats (total_starts) VALUES (0);
        ''')
        
        conn.commit()
        cur.close()
        conn.close()
        logger.info("Base de données réinitialisée")
        return True
    except Exception as e:
        logger.error(f"Erreur d'initialisation BD: {str(e)}")
        return False

def start(update: Update, context: CallbackContext):
    try:
        # Incrémenter le compteur
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute('UPDATE stats SET total_starts = total_starts + 1')
        conn.commit()
        cur.close()
        conn.close()
        
        update.message.reply_text("👋 Hello! Bot is working!")
        logger.info("Start command processed")
    except Exception as e:
        logger.error(f"Erreur dans start: {str(e)}")
        update.message.reply_text("👋 Hello! (Stats non mises à jour)")

def get_stats(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    logger.info(f"Stats demandées par {user_id}")
    
    if user_id != ADMIN_ID:
        update.message.reply_text("⛔ You don't have permission to use this command.")
        return
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute('SELECT total_starts FROM stats')
        total = cur.fetchone()[0]
        cur.close()
        conn.close()
        
        update.message.reply_text(f"📊 Total /start commands: {total}")
    except Exception as e:
        logger.error(f"Erreur dans stats: {str(e)}")
        update.message.reply_text("❌ Database error")

if __name__ == '__main__':
    logger.info("Démarrage du bot...")
    if init_db():  # Réinitialiser la BD au démarrage
        updater = Updater(TOKEN)
        updater.dispatcher.add_handler(CommandHandler("start", start))
        updater.dispatcher.add_handler(CommandHandler("stats", get_stats))
        logger.info("Bot prêt à démarrer")
        updater.start_polling()
        updater.idle()
    else:
        logger.error("Erreur d'initialisation de la base de données")