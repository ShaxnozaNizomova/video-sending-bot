import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, ContextTypes
from user import user_handlers
from admin import admin_handlers

# Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
ADMIN_ID = int(os.getenv("ADMIN_ID", "1854307576"))

# Create Flask app and Telegram app
app = Flask(__name__)
application: Application = Application.builder().token(BOT_TOKEN).build()

# Register handlers
application.add_handler(user_handlers)
for handler in admin_handlers:
    application.add_handler(handler)

# Ensure init runs once
initialized = False
init_lock = asyncio.Lock()

# Webhook route
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

# Async webhook setup function
async def set_webhook():
    await application.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook/{BOT_TOKEN}")
    print("Webhook set!")

# Flask startup hook to set webhook
@app.before_first_request
def activate_webhook():
    loop = asyncio.get_event_loop()
    loop.create_task(set_webhook())

# Run the app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
