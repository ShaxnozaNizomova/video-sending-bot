import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application
from user import user_handlers
from admin import admin_handlers

# Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
ADMIN_ID = int(os.getenv("ADMIN_ID", "1854307576"))

# Create Flask app and Telegram Application
app = Flask(__name__)
application: Application = Application.builder().token(BOT_TOKEN).build()

# Register handlers
application.add_handler(user_handlers)
for handler in admin_handlers:
    application.add_handler(handler)

# Flag for one-time initialization
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

# Webhook setup for Flask 3.x (async)
@app.before_serving
async def setup_webhook():
    await application.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook/{BOT_TOKEN}")
    print("✅ Webhook set successfully.")

# Run app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
