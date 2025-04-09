import os
import asyncio
from quart import Quart, request
from telegram import Update
from telegram.ext import Application
from user import user_handlers
from admin import admin_handlers

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
ADMIN_ID = int(os.getenv("ADMIN_ID", "500062278"))

# Create Quart app
app = Quart(__name__)

# Create Telegram bot application
application = Application.builder().token(BOT_TOKEN).build()

# Add handlers
application.add_handler(user_handlers)
for handler in admin_handlers:
    application.add_handler(handler)

# Ensure bot is initialized
@app.before_serving
async def startup():
    await application.initialize()
    await application.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook/{BOT_TOKEN}")
    print("✅ Webhook set")

# Webhook route
@app.post(f"/webhook/{BOT_TOKEN}")
async def webhook():
    data = await request.get_json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return "ok"

# Only needed for local testing (not used on Render)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
