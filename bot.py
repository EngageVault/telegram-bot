from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext
import os
import psycopg2
import logging
from datetime import datetime

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
        logger.info("Initialisation de la base de données...")
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Table des utilisateurs
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                username TEXT,
                first_seen TIMESTAMP,
                commands_used INTEGER DEFAULT 0
            )
        ''')
        
        # Table des statistiques globales
        cur.execute('''
            CREATE TABLE IF NOT EXISTS stats (
                id SERIAL PRIMARY KEY,
                total_starts INTEGER DEFAULT 0,
                unique_users INTEGER DEFAULT 0
            )
        ''')
        
        # Initialiser stats si vide
        cur.execute('INSERT INTO stats (total_starts, unique_users) SELECT 0, 0 WHERE NOT EXISTS (SELECT 1 FROM stats)')
        
        conn.commit()
        cur.close()
        conn.close()
        logger.info("Base de données initialisée avec succès")
        return True
    except Exception as e:
        logger.error(f"Erreur d'initialisation BD: {str(e)}")
        return False

def update_user_stats(user_id, username):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Mettre à jour ou créer l'utilisateur
        cur.execute('''
            INSERT INTO users (user_id, username, first_seen, commands_used)
            VALUES (%s, %s, %s, 1)
            ON CONFLICT (user_id) 
            DO UPDATE SET 
                username = EXCLUDED.username,
                commands_used = users.commands_used + 1
        ''', (user_id, username, datetime.now()))
        
        # Mettre à jour les stats globales
        cur.execute('''
            WITH new_user AS (
                SELECT COUNT(*) as is_new
                FROM users
                WHERE user_id = %s AND commands_used = 1
            )
            UPDATE stats SET 
                total_starts = total_starts + 1,
                unique_users = unique_users + (SELECT is_new FROM new_user)
        ''', (user_id,))
        
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Erreur mise à jour stats: {str(e)}")
        return False

def get_user_stats():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Récupérer les stats globales
        cur.execute('SELECT total_starts, unique_users FROM stats')
        total_starts, unique_users = cur.fetchone()
        
        # Récupérer le top 5 des utilisateurs
        cur.execute('''
            SELECT username, commands_used 
            FROM users 
            ORDER BY commands_used DESC 
            LIMIT 5
        ''')
        top_users = cur.fetchall()
        
        cur.close()
        conn.close()
        return total_starts, unique_users, top_users
    except Exception as e:
        logger.error(f"Erreur récupération stats: {str(e)}")
        return None

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
        user = update.effective_user
        update_user_stats(user.id, user.username or "Anonymous")
        
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
        if update.effective_user.id != ADMIN_ID:
            update.message.reply_text("⛔ You don't have permission to use this command.")
            return
        
        stats = get_user_stats()
        if stats:
            total_starts, unique_users, top_users = stats
            
            stats_message = f"""📊 Bot Statistics:

Total /start commands: {total_starts}
Unique users: {unique_users}

Most active users:"""

            for username, commands in top_users:
                stats_message += f"\n@{username}: {commands} commands"
            
            update.message.reply_text(stats_message)
        else:
            update.message.reply_text("❌ Error getting statistics")
            
    except Exception as e:
        logger.error(f"Erreur dans stats: {str(e)}")
        update.message.reply_text("❌ Error getting statistics")

if __name__ == '__main__':
    logger.info("Démarrage du bot...")
    if init_db():
        try:
            updater = Updater(TOKEN)
            updater.dispatcher.add_handler(CommandHandler("start", start))
            updater.dispatcher.add_handler(CommandHandler("stats", get_stats))
            logger.info("Bot prêt à démarrer")
            updater.start_polling()
            updater.idle()
        except Exception as e:
            logger.error(f"Erreur critique au démarrage: {str(e)}")
    else:
        logger.error("Échec de l'initialisation de la base de données")