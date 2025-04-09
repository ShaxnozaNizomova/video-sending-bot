import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application
from user import user_handlers
from admin import admin_handlers

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
ADMIN_ID = int(os.getenv("ADMIN_ID", "1854307576"))

# Create Flask app
app = Flask(__name__)

# Create Telegram bot application
application = Application.builder().token(BOT_TOKEN).build()

# Add handlers
application.add_handler(user_handlers)
for handler in admin_handlers:
    application.add_handler(handler)

# Webhook route
@app.post(f"/webhook/{BOT_TOKEN}")
async def webhook():
    if not application.initialized:
        await application.initialize()

    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "ok"

# Async wrapper for starting webhook then Flask
async def start():
    await application.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook/{BOT_TOKEN}")
    print("✅ Webhook set")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

# Entrypoint
if __name__ == "__main__":
    asyncio.run(start())
