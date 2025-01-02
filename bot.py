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
        logger.info("Tentative d'initialisation de la base de données...")
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Création de la table stats
        cur.execute('''
            CREATE TABLE IF NOT EXISTS stats (
                total_starts INTEGER DEFAULT 0
            )
        ''')
        
        # Vérifier si la table est vide et l'initialiser si nécessaire
        cur.execute('SELECT COUNT(*) FROM stats')
        if cur.fetchone()[0] == 0:
            cur.execute('INSERT INTO stats (total_starts) VALUES (0)')
        
        conn.commit()
        cur.close()
        conn.close()
        logger.info("Base de données initialisée avec succès")
        return True
    except Exception as e:
        logger.error(f"Erreur d'initialisation BD: {str(e)}")
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
    logger.info("Commande /start reçue")
    try:
        keyboard = [
            [InlineKeyboardButton("⭐ Join our Community", url="https://t.me/engagevaultcommunity")],
            [InlineKeyboardButton("🚀 Launch App", url="https://google.com")]
        ]
        update.message.reply_text(WELCOME_MESSAGE, reply_markup=InlineKeyboardMarkup(keyboard))
        logger.info("Message de bienvenue envoyé")
        
        # Essayer d'enregistrer dans la BD seulement après avoir envoyé le message
        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            cur.execute('UPDATE stats SET total_starts = total_starts + 1')
            conn.commit()
            cur.close()
            conn.close()
            logger.info("Statistiques mises à jour")
        except Exception as db_error:
            logger.error(f"Erreur BD dans start: {str(db_error)}")
            
    except Exception as e:
        logger.error(f"Erreur générale dans start: {str(e)}")

def get_stats(update: Update, context: CallbackContext):
    logger.info(f"Commande /stats reçue de l'utilisateur {update.effective_user.id}")
    
    if update.effective_user.id != ADMIN_ID:
        logger.warning("Tentative d'accès non autorisée aux stats")
        update.message.reply_text("⛔ You don't have permission to use this command.")
        return
        
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute('SELECT total_starts FROM stats')
        total = cur.fetchone()[0]
        cur.close()
        conn.close()
        logger.info(f"Stats récupérées: {total} starts")
        
        update.message.reply_text(f"📊 Total /start commands: {total}")
    except Exception as e:
        logger.error(f"Erreur dans get_stats: {str(e)}")
        update.message.reply_text("❌ Error getting statistics")

if __name__ == '__main__':
    logger.info("Démarrage du bot...")
    if init_db():  # Initialiser la BD au démarrage
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
    else:
        logger.error("Échec de l'initialisation de la base de données")