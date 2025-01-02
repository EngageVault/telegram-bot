from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, ConversationHandler, MessageHandler, Filters
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

# États de la conversation
FEEDBACK = 0

def init_db():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Table existante
        cur.execute('''
            CREATE TABLE IF NOT EXISTS bot_stats (
                user_id BIGINT PRIMARY KEY,
                username TEXT,
                commands INTEGER DEFAULT 1
            )
        ''')
        
        # Nouvelle table pour les feedbacks
        cur.execute('''
            CREATE TABLE IF NOT EXISTS feedbacks (
                id SERIAL PRIMARY KEY,
                user_id BIGINT,
                username TEXT,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

def feedback_start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "📝 Thank you for contacting EngageVault support!\n\n"
        "Please send your message below.\n\n"
        "⚠️ Important Security Notice:\n"
        "• Our staff will ONLY respond through THIS bot\n"
        "• Never trust anyone claiming to be EngageVault staff in private messages\n"
        "• All official responses will come directly through this conversation\n\n"
        "You can cancel anytime by sending /cancel"
    )
    return FEEDBACK

def feedback_received(update: Update, context: CallbackContext):
    user = update.effective_user
    feedback_text = update.message.text
    
    try:
        # Sauvegarde en BD
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO feedbacks (user_id, username, message) VALUES (%s, %s, %s)',
            (user.id, user.username or "Anonymous", feedback_text)
        )
        conn.commit()
        cur.close()
        conn.close()
        
        # Notification à l'admin
        context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"""📬 Nouveau Feedback:

De: @{user.username or 'Anonymous'}
ID: {user.id}

Message:
{feedback_text}"""
        )
        
        # Message de confirmation à l'utilisateur
        update.message.reply_text(
            "✅ Your message has been received!\n\n"
            "If needed, you will receive a response directly through this bot.\n\n"
            "⚠️ Security Reminder:\n"
            "• Our team will NEVER contact you outside of this bot\n"
            "• All official responses will be sent here\n"
            "• Stay safe and ignore any direct messages claiming to be from our staff"
        )
    except Exception as e:
        logger.error(f"Erreur feedback: {str(e)}")
        update.message.reply_text(
            "❌ Sorry, there was an error processing your message.\n"
            "Please try again later."
        )
    
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text(
        "❌ Feedback cancelled.\n"
        "Feel free to send your feedback anytime using /feedback"
    )
    return ConversationHandler.END

if __name__ == '__main__':
    logger.info("Démarrage du bot...")
    if init_db():
        try:
            updater = Updater(TOKEN)
            dp = updater.dispatcher
            
            # Handlers existants
            dp.add_handler(CommandHandler("start", start))
            dp.add_handler(CommandHandler("stats", get_stats))
            
            # Nouveau handler pour feedback
            feedback_handler = ConversationHandler(
                entry_points=[CommandHandler('feedback', feedback_start)],
                states={
                    FEEDBACK: [MessageHandler(Filters.text & ~Filters.command, feedback_received)]
                },
                fallbacks=[CommandHandler('cancel', cancel)]
            )
            dp.add_handler(feedback_handler)
            
            logger.info("Bot prêt à démarrer")
            updater.start_polling()
            updater.idle()
        except Exception as e:
            logger.error(f"Erreur critique au démarrage: {str(e)}")
    else:
        logger.error("Échec de l'initialisation de la base de données")