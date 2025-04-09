import os
import asyncio
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes,
)
import logging

from admin import admin_handlers
from user import user_handlers

# --- Configuration ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "7813479172:AAEVo-u3o9C7z7ZzEHu--kRu-GmhtEVej_k")
ADMIN_ID = int(os.getenv("ADMIN_ID", "1854307576"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://video-sending-bot.onrender.com")

# --- Flask app for webhook ---
app = Flask(__name__)

# --- Logging setup ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# --- Telegram bot setup ---
application = Application.builder().token(BOT_TOKEN).build()

# Register user and admin handlers
application.add_handler(user_handlers)
for handler in admin_handlers:
    application.add_handler(handler)

# --- Webhook route ---
@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
async def webhook() -> str:
    if request.method == "POST":
        data = request.get_json(force=True)
        print("🔔 Received update:", data)  # Log update for debug
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
        return "ok", 200

# --- Set webhook manually ---
@app.route("/setwebhook", methods=["GET"])
def set_webhook():
    if WEBHOOK_URL:
        full_url = f"{WEBHOOK_URL}/webhook/{BOT_TOKEN}"
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(application.bot.set_webhook(full_url))
        return f"✅ Webhook set to {full_url}"
    return "❌ WEBHOOK_URL not set"

# --- Run app ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
