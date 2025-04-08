import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
import logging

from admin import admin_handlers
from user import user_handlers

# Load tokens and secrets
BOT_TOKEN = os.getenv("BOT_TOKEN", "7813479172:AAEVo-u3o9C7z7ZzEHu--kRu-GmhtEVej_k")
ADMIN_ID = int(os.getenv("ADMIN_ID", "1854307576"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://your-domain.onrender.com")  # Replace with your actual URL or set in env

# Flask app for webhook
app = Flask(__name__)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Create the Application
application = Application.builder().token(BOT_TOKEN).build()

# Register handlers
application.add_handler(user_handlers)
for handler in admin_handlers:
    application.add_handler(handler)

# Webhook endpoint to receive updates
@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
async def webhook() -> str:
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), application.bot)
        await application.process_update(update)
        return "ok", 200

# Manual webhook setup route
@app.route("/setwebhook", methods=["GET"])
def setup_webhook():
    bot = Bot(token=BOT_TOKEN)
    full_url = f"{WEBHOOK_URL}/webhook/{BOT_TOKEN}"
    bot.set_webhook(full_url)
    return f"✅ Webhook set to {full_url}"

# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
