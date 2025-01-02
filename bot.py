from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext
import os
import psycopg2
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN", "7929001260:AAG_EZTbt3C11GCZauaLqkuP99YKkxB1NJg")
ADMIN_ID = 7686799533
DATABASE_URL = os.getenv("DATABASE_URL")

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

def init_db():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS bot_stats (
                user_id BIGINT PRIMARY KEY,
                username TEXT,
                commands INTEGER DEFAULT 1
            )
        ''')
        conn.commit()
        cur.close()
        conn.close()
        logger.info("Base de données initialisée")
        return True
    except Exception as e:
        logger.error(f"Erreur BD: {str(e)}")
        return False

def start(update: Update, context: CallbackContext):
    try:
        user = update.effective_user
        user_id = user.id
        username = user.username or "Anonymous"

        # Mise à jour des stats
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO bot_stats (user_id, username, commands)
            VALUES (%s, %s, 1)
            ON CONFLICT (user_id) DO UPDATE 
            SET commands = bot_stats.commands + 1
        ''', (user_id, username))
        conn.commit()
        cur.close()
        conn.close()

        keyboard = [
            [InlineKeyboardButton("⭐ Join our Community", url="https://t.me/engagevaultcommunity")],
            [InlineKeyboardButton("🚀 Launch App", url="https://google.com")]
        ]
        update.message.reply_text(WELCOME_MESSAGE, reply_markup=InlineKeyboardMarkup(keyboard))
        logger.info(f"Start command from {username}")
        
    except Exception as e:
        logger.error(f"Erreur start: {str(e)}")
        # Envoyer quand même le message si la BD échoue
        keyboard = [
            [InlineKeyboardButton("⭐ Join our Community", url="https://t.me/engagevaultcommunity")],
            [InlineKeyboardButton("🚀 Launch App", url="https://google.com")]
        ]
        update.message.reply_text(WELCOME_MESSAGE, reply_markup=InlineKeyboardMarkup(keyboard))

def get_stats(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("⛔ You don't have permission to use this command.")
        return

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Total des commandes
        cur.execute('SELECT SUM(commands) FROM bot_stats')
        total_commands = cur.fetchone()[0] or 0
        
        # Utilisateurs uniques
        cur.execute('SELECT COUNT(*) FROM bot_stats')
        unique_users = cur.fetchone()[0] or 0
        
        # Top 5
        cur.execute('''
            SELECT username, commands 
            FROM bot_stats 
            ORDER BY commands DESC 
            LIMIT 5
        ''')
        top_users = cur.fetchall()
        
        stats_message = f"""📊 Bot Statistics:

Total /start commands: {total_commands}
Unique users: {unique_users}

Most active users:"""

        for username, commands in top_users:
            stats_message += f"\n@{username}: {commands} commands"
        
        update.message.reply_text(stats_message)
        logger.info("Stats envoyées")
        
        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"Erreur stats: {str(e)}")
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