from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio
import platform

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = """🚀 Welcome to EngageVault!

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

    await update.message.reply_text(welcome_message)

def main():
    # Configuration de la politique d'événements pour Windows
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Création de l'application
    app = Application.builder().token("7929001260:AAG_EZTbt3C11GCZauaLqkuP99YKkxB1NJg").build()
    
    # Ajout du gestionnaire de commande
    app.add_handler(CommandHandler("start", start))
    
    # Lancement du bot
    print("Le bot démarre...")
    app.run_polling()
    print("Bot arrêté")

if __name__ == "__main__":
    main()