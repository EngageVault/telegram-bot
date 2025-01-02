from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext
import os
from datetime import datetime

TOKEN = os.getenv("TELEGRAM_TOKEN", "7929001260:AAG_EZTbt3C11GCZauaLqkuP99YKkxB1NJg")

# Dictionnaires pour stocker les statistiques
users = {}
stats = {
    'total_starts': 0,
    'unique_users': 0
}

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
    # Récupérer l'ID de l'utilisateur
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    # Mettre à jour les statistiques
    stats['total_starts'] += 1
    if user_id not in users:
        users[user_id] = {
            'username': username,
            'first_seen': datetime.now(),
            'commands_used': 0
        }
        stats['unique_users'] += 1
    
    users[user_id]['commands_used'] += 1

    # Message normal
    keyboard = [
        [InlineKeyboardButton("⭐ Join our Community", url="https://t.me/engagevaultcommunity")],
        [InlineKeyboardButton("🚀 Launch App", url="https://google.com")]
    ]
    update.message.reply_text(WELCOME_MESSAGE, reply_markup=InlineKeyboardMarkup(keyboard))

def get_stats(update: Update, context: CallbackContext):
    # Commande pour voir les statistiques
    stats_message = f"""📊 Bot Statistics:

Total /start commands: {stats['total_starts']}
Unique users: {stats['unique_users']}
Most active users:"""

    # Trouver les utilisateurs les plus actifs
    sorted_users = sorted(users.items(), key=lambda x: x[1]['commands_used'], reverse=True)[:5]
    
    for user_id, user_data in sorted_users:
        stats_message += f"\n@{user_data['username']}: {user_data['commands_used']} commands"

    update.message.reply_text(stats_message)

if __name__ == '__main__':
    updater = Updater(TOKEN)
    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CommandHandler("stats", get_stats))
    updater.start_polling()
    updater.idle()