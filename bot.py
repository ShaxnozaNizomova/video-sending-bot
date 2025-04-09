import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, ContextTypes
from user import user_handlers
from admin import admin_handlers

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
ADMIN_ID = int(os.getenv("ADMIN_ID", "1854307576"))

# Flask app
app = Flask(__name__)

# Telegram bot app
application: Application = Application.builder().token(BOT_TOKEN).build()

# Register all handlers
application.add_handler(user_handlers)
for handler in admin_handlers:
    application.add_handler(handler)

# Lock and flag to ensure application is initialized only once
initialized = False
init_lock = asyncio.Lock()

# Webhook endpoint
@app.post(f"/webhook/{BOT_TOKEN}")
async def webhook():
    global initialized
    async with init_lock:
        if not initialized:
            await application.initialize()
            initialized = True

    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "ok"

# Set webhook when bot starts
async def set_webhook():
    await application.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook/{BOT_TOKEN}")

# Start the bot and Flask app
if __name__ == "__main__":
    asyncio.run(set_webhook())
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
