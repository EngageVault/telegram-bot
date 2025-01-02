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

# Messages et URLs
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
    """Gestionnaire de la commande /start"""
    # Création des boutons
    buttons = [[
        InlineKeyboardButton(
            text="⭐ Join our Community",
            url="https://t.me/engagevaultcommunity"
        )
    ], [
        InlineKeyboardButton(
            text="🚀 Launch App",
            url="https://engagevault.com"
        )
    ]]
    
    # Création du markup
    keyboard = InlineKeyboardMarkup(buttons)
    
    try:
        # Envoi du message avec les boutons
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=WELCOME_MESSAGE,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    except Exception as e:
        print(f"Error: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Une erreur s'est produite."
        )

def main():
    """Fonction principale"""
    # Créer l'application
    app = Application.builder().token(TOKEN).build()

    # Ajouter le gestionnaire de commande
    app.add_handler(CommandHandler("start", start))

    # Démarrer le bot
    print("Le bot démarre...")
    app.run_polling()
    print("Bot arrêté")

if __name__ == "__main__":
    main()