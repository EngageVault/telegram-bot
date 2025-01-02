from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext

TOKEN = "7929001260:AAG_EZTbt3C11GCZauaLqkuP99YKkxB1NJg"

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

def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("⭐ Join our Community", url="https://t.me/engagevaultcommunity")],
        [InlineKeyboardButton("🚀 Launch App", url="https://test.com")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text=WELCOME_MESSAGE, reply_markup=reply_markup)

def main() -> None:
    updater = Updater(TOKEN)
    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()