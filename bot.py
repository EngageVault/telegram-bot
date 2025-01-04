from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, CallbackContext

async def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton(
            "🌐 Ouvrir Web App", 
            url="https://VOTRE_USERNAME.github.io/VOTRE_REPO"
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Welcome to EngageVault!\n"
        "Click below to open the web application:",
        reply_markup=reply_markup
    )