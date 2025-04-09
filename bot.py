import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Get secrets from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "1854307576"))  # Replace with real fallback
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Should be like https://your-bot.onrender.com

if not BOT_TOKEN or not WEBHOOK_URL:
    raise Exception("BOT_TOKEN and WEBHOOK_URL must be set in environment variables.")

# Telegram app
application = Application.builder().token(BOT_TOKEN).build()

# Flask app
app = Flask(__name__)

# Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Bot is running via webhook on Render!")

application.add_handler(CommandHandler("start", start))

# Webhook endpoint
@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok", 200

# Set webhook once before first request
@app.before_first_request
def init_webhook():
    print("Setting webhook...")
    application.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook/{BOT_TOKEN}")

# Run Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
