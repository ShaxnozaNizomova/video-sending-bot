import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, ContextTypes
from user import user_handlers
from admin import admin_handlers

# Environment variables for deployment
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Full URL including your bot token
ADMIN_ID = int(os.getenv("ADMIN_ID", "1854307576")) 

# Create Flask app
app = Flask(__name__)

# Create the Telegram bot application
application = Application.builder().token(BOT_TOKEN).build()

# Add handlers
application.add_handler(user_handlers)
for handler in admin_handlers:
    application.add_handler(handler)

# Flask route for Telegram webhook
@app.post(f"/webhook/{BOT_TOKEN}")
async def webhook():
    if request.method == "POST":
        await application.initialize()  # ✅ Add this line
        update = Update.de_json(request.get_json(force=True), application.bot)
        await application.process_update(update)
    return "ok"


# Set the webhook when the bot starts
async def set_webhook():
    await application.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook/{BOT_TOKEN}")

# Start the Flask app and bot
if __name__ == "__main__":
    import asyncio
    asyncio.run(set_webhook())
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
