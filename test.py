from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = "7813479172:AAEVo-u3o9C7z7ZzEHu--kRu-GmhtEVej_k"

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    print(f"Your Telegram ID is: {user.id}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("id", get_id))
    print("Send /id to your bot to get your Telegram ID")
    app.run_polling()

if __name__ == "__main__":
    main()
