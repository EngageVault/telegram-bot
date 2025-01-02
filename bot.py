"""
EngageVault Telegram Bot
"""

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# Configuration du logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Token du bot
TOKEN = "7929001260:AAG_EZTbt3C11GCZauaLqkuP99YKkxB1NJg"

# Message de bienvenue
WELCOME_MESSAGE = """🚀 Welcome to EngageVault!

⭐ Congratulations Early Adopter! ⭐

You've just discovered the next big thing in social media growth, and you're among the first to join! 🎯

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("⭐ Join our Community", url="https://t.me/engagevaultcommunity")],
        [InlineKeyboardButton("🚀 Launch App", url="https://engagevault.com")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text=WELCOME_MESSAGE, reply_markup=reply_markup)

def main():
    # Créer l'application
    app = Application.builder().token(TOKEN).build()
    
    # Ajouter la commande /start
    app.add_handler(CommandHandler("start", start))
    
    # Démarrer le bot
    print("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()