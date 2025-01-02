from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext
import os
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN", "7929001260:AAG_EZTbt3C11GCZauaLqkuP99YKkxB1NJg")
ADMIN_ID = 7686799533

# Compteurs en mémoire
start_count = 0
unique_users = set()
user_stats = {}

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
        global start_count
        user = update.effective_user
        user_id = user.id
        username = user.username or "Anonymous"
        
        # Mise à jour des stats
        start_count += 1
        unique_users.add(user_id)
        
        if user_id not in user_stats:
            user_stats[user_id] = {"username": username, "commands": 0}
        user_stats[user_id]["commands"] += 1

        keyboard = [
            [InlineKeyboardButton("⭐ Join our Community", url="https://t.me/engagevaultcommunity")],
            [InlineKeyboardButton("🚀 Launch App", url="https://google.com")]
        ]
        update.message.reply_text(WELCOME_MESSAGE, reply_markup=InlineKeyboardMarkup(keyboard))
        logger.info(f"Start command from {username}")
        
    except Exception as e:
        logger.error(f"Erreur start: {str(e)}")

def get_stats(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("⛔ You don't have permission to use this command.")
        return

    try:
        # Trier les utilisateurs par nombre de commandes
        sorted_users = sorted(
            user_stats.items(),
            key=lambda x: x[1]["commands"],
            reverse=True
        )[:5]
        
        stats_message = f"""📊 Bot Statistics:

Total /start commands: {start_count}
Unique users: {len(unique_users)}

Most active users:"""

        for user_id, stats in sorted_users:
            username = stats["username"]
            commands = stats["commands"]
            stats_message += f"\n@{username}: {commands} commands"
        
        update.message.reply_text(stats_message)
        logger.info("Stats envoyées")
        
    except Exception as e:
        logger.error(f"Erreur stats: {str(e)}")

if __name__ == '__main__':
    logger.info("Démarrage du bot...")
    try:
        updater = Updater(TOKEN)
        updater.dispatcher.add_handler(CommandHandler("start", start))
        updater.dispatcher.add_handler(CommandHandler("stats", get_stats))
        logger.info("Bot prêt à démarrer")
        updater.start_polling()
        updater.idle()
    except Exception as e:
        logger.error(f"Erreur critique au démarrage: {str(e)}")