from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext
import os
import psycopg2
from datetime import datetime

TOKEN = os.getenv("TELEGRAM_TOKEN", "7929001260:AAG_EZTbt3C11GCZauaLqkuP99YKkxB1NJg")
ADMIN_ID = 7686799533
DATABASE_URL = os.getenv("DATABASE_URL")

def init_db():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Création de la table users si elle n'existe pas
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            first_seen TIMESTAMP,
            commands_used INTEGER DEFAULT 0
        )
    ''')
    
    # Création de la table stats si elle n'existe pas
    cur.execute('''
        CREATE TABLE IF NOT EXISTS stats (
            id SERIAL PRIMARY KEY,
            total_starts INTEGER DEFAULT 0,
            unique_users INTEGER DEFAULT 0
        )
    ''')
    
    # Initialiser stats s'il n'existe pas
    cur.execute('INSERT INTO stats (total_starts, unique_users) SELECT 0, 0 WHERE NOT EXISTS (SELECT 1 FROM stats)')
    
    conn.commit()
    cur.close()
    conn.close()

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
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Mettre à jour les stats
    cur.execute('UPDATE stats SET total_starts = total_starts + 1')
    
    # Vérifier si l'utilisateur existe
    cur.execute('SELECT 1 FROM users WHERE user_id = %s', (user_id,))
    if not cur.fetchone():
        # Nouvel utilisateur
        cur.execute(
            'INSERT INTO users (user_id, username, first_seen, commands_used) VALUES (%s, %s, %s, 1)',
            (user_id, username, datetime.now())
        )
        cur.execute('UPDATE stats SET unique_users = unique_users + 1')
    else:
        # Utilisateur existant
        cur.execute(
            'UPDATE users SET commands_used = commands_used + 1 WHERE user_id = %s',
            (user_id,)
        )
    
    conn.commit()
    cur.close()
    conn.close()

    keyboard = [
        [InlineKeyboardButton("⭐ Join our Community", url="https://t.me/engagevaultcommunity")],
        [InlineKeyboardButton("🚀 Launch App", url="https://google.com")]
    ]
    update.message.reply_text(WELCOME_MESSAGE, reply_markup=InlineKeyboardMarkup(keyboard))

def get_stats(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        update.message.reply_text("⛔ You don't have permission to use this command.")
        return

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Obtenir les stats globales
    cur.execute('SELECT total_starts, unique_users FROM stats LIMIT 1')
    total_starts, unique_users = cur.fetchone()
    
    # Obtenir les utilisateurs les plus actifs
    cur.execute('''
        SELECT username, commands_used 
        FROM users 
        ORDER BY commands_used DESC 
        LIMIT 5
    ''')
    top_users = cur.fetchall()
    
    stats_message = f"""📊 Bot Statistics:

Total /start commands: {total_starts}
Unique users: {unique_users}

Most active users:"""

    for username, commands in top_users:
        stats_message += f"\n@{username}: {commands} commands"

    cur.close()
    conn.close()
    
    update.message.reply_text(stats_message)

if __name__ == '__main__':
    init_db()  # Initialiser la base de données
    updater = Updater(TOKEN)
    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CommandHandler("stats", get_stats))
    updater.start_polling()
    updater.idle()