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
        logger.info("Connexion à la base de données...")
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Création d'une table simple pour les stats
        cur.execute('''
            CREATE TABLE IF NOT EXISTS stats (
                total_starts INTEGER DEFAULT 0
            )
        ''')
        
        # Insérer une ligne si la table est vide
        cur.execute('INSERT INTO stats SELECT 0 WHERE NOT EXISTS (SELECT 1 FROM stats)')
        
        conn.commit()
        cur.close()
        conn.close()
        logger.info("Base de données initialisée")
        return True
    except Exception as e:
        logger.error(f"Erreur base de données: {str(e)}")
        return False

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
        # Incrémenter le compteur
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute('UPDATE stats SET total_starts = total_starts + 1')
        conn.commit()
        cur.close()
        conn.close()
        
        keyboard = [
            [InlineKeyboardButton("⭐ Join our Community", url="https://t.me/engagevaultcommunity")],
            [InlineKeyboardButton("🚀 Launch App", url="https://google.com")]
        ]
        update.message.reply_text(WELCOME_MESSAGE, reply_markup=InlineKeyboardMarkup(keyboard))
        logger.info("Message envoyé avec succès")
    except Exception as e:
        logger.error(f"Erreur dans start: {str(e)}")
        # Envoyer quand même le message si la BD échoue
        keyboard = [
            [InlineKeyboardButton("⭐ Join our Community", url="https://t.me/engagevaultcommunity")],
            [InlineKeyboardButton("🚀 Launch App", url="https://google.com")]
        ]
        update.message.reply_text(WELCOME_MESSAGE, reply_markup=InlineKeyboardMarkup(keyboard))

def get_stats(update: Update, context: CallbackContext):
    logger.info("Commande stats reçue")
    user_id = update.effective_user.id
    logger.info(f"ID utilisateur: {user_id}")
    
    if user_id != ADMIN_ID:
        logger.warning(f"Accès non autorisé de l'utilisateur {user_id}")
        update.message.reply_text("⛔ You don't have permission to use this command.")
        return

    try:
        logger.info("Tentative de connexion à la base de données pour stats")
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute('SELECT total_starts FROM stats')
        total = cur.fetchone()[0]
        cur.close()
        conn.close()
        logger.info(f"Stats récupérées: {total} starts")
        
        update.message.reply_text(f"📊 Total /start commands: {total}")
    except Exception as e:
        logger.error(f"Erreur stats: {str(e)}")
        update.message.reply_text("❌ Error getting statistics")

if __name__ == '__main__':
    logger.info("Démarrage du bot...")
    if init_db():
        updater = Updater(TOKEN)
        updater.dispatcher.add_handler(CommandHandler("start", start))
        updater.dispatcher.add_handler(CommandHandler("stats", get_stats))
        logger.info("Bot prêt à démarrer")
        updater.start_polling()
        logger.info("Bot démarré")
        updater.idle()
    else:
        logger.error("Erreur d'initialisation de la base de données")