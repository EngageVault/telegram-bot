from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext
import os
import json
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN", "7929001260:AAG_EZTbt3C11GCZauaLqkuP99YKkxB1NJg")
ADMIN_ID = 7686799533

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

# Structure pour sauvegarder les données
DATA = {
    "start_count": 0,
    "unique_users": set(),
    "user_stats": {}
}

# Charger les données au démarrage
def load_data():
    try:
        with open('bot_data.json', 'r') as f:
            data = json.load(f)
            DATA["start_count"] = data["start_count"]
            DATA["unique_users"] = set(data["unique_users"])
            DATA["user_stats"] = data["user_stats"]
    except:
        logger.info("Aucune donnée précédente trouvée")

# Sauvegarder les données
def save_data():
    try:
        data = {
            "start_count": DATA["start_count"],
            "unique_users": list(DATA["unique_users"]),
            "user_stats": DATA["user_stats"]
        }
        with open('bot_data.json', 'w') as f:
            json.dump(data, f)
    except Exception as e:
        logger.error(f"Erreur sauvegarde: {str(e)}")

def start(update: Update, context: CallbackContext):
    try:
        user = update.effective_user
        user_id = str(user.id)  # Convertir en string pour JSON
        username = user.username or "Anonymous"
        
        DATA["start_count"] += 1
        DATA["unique_users"].add(user_id)
        
        if user_id not in DATA["user_stats"]:
            DATA["user_stats"][user_id] = {"username": username, "commands": 0}
        DATA["user_stats"][user_id]["commands"] += 1
        
        save_data()  # Sauvegarder après chaque modification
        
        keyboard = [
            [InlineKeyboardButton("⭐ Join our Community", url="https://t.me/engagevaultcommunity")],
            [InlineKeyboardButton("🚀 Launch App", url="https://google.com")]
        ]
        
        update.message.reply_text(WELCOME_MESSAGE, reply_markup=InlineKeyboardMarkup(keyboard))
        logger.info("Message envoyé")
    except Exception as e:
        logger.error(f"Erreur: {str(e)}")

def get_stats(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("⛔ You don't have permission to use this command.")
        return

    try:
        # Trier les utilisateurs par nombre de commandes
        sorted_users = sorted(
            DATA["user_stats"].items(),
            key=lambda x: x[1]["commands"],
            reverse=True
        )[:5]
        
        stats_message = f"""📊 Bot Statistics:

Total /start commands: {DATA["start_count"]}
Unique users: {len(DATA["unique_users"])}

Most active users:"""

        for _, stats in sorted_users:
            username = stats["username"]
            commands = stats["commands"]
            stats_message += f"\n@{username}: {commands} commands"

        update.message.reply_text(stats_message)
    except Exception as e:
        logger.error(f"Erreur stats: {str(e)}")

if __name__ == '__main__':
    logger.info("Démarrage du bot...")
    load_data()  # Charger les données au démarrage
    try:
        updater = Updater(TOKEN)
        updater.dispatcher.add_handler(CommandHandler("start", start))
        updater.dispatcher.add_handler(CommandHandler("stats", get_stats))
        logger.info("Bot prêt à démarrer")
        updater.start_polling()
        updater.idle()
    except Exception as e:
        logger.error(f"Erreur critique au démarrage: {str(e)}")