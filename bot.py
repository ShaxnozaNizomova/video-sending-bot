import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CallbackContext
from user import user_handlers
from admin import admin_handlers

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)

# Telegram bot token and other config from environment
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Full URL including your bot token
ADMIN_ID = int(os.getenv("ADMIN_ID", "1854307576"))

# Create the bot application
application = Application.builder().token(BOT_TOKEN).build()

# Register handlers
application.add_handler(user_handlers)
for handler in admin_handlers:
    application.add_handler(handler)

@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
async def webhook():
    """Handle incoming Telegram webhook updates."""
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "OK"

@app.before_first_request
def set_webhook():
    """Set webhook when the server starts."""
    from telegram import Bot
    bot = Bot(BOT_TOKEN)
    bot.delete_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/webhook/{BOT_TOKEN}")
    logger.info("✅ Webhook set!")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
