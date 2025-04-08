import os
import logging
import requests
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler,
    ContextTypes, filters
)
from aiohttp import web

# --- ENV Variables ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
AIRTABLE_TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME")
ADMIN_ID = 1854307576

# --- Conversation states ---
ASK_NAME, ASK_PHONE = range(2)

# --- In-memory user storage ---
users = {}

# --- Logging ---
logging.basicConfig(level=logging.INFO)

# --- Save to Airtable ---
def save_to_airtable(name, phone, user_id, chat_id):
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "fields": {
            "Name": name,
            "Phone": phone,
            "User ID": str(user_id),
            "Chat ID": str(chat_id)
        }
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        logging.error(f"Airtable error: {response.text}")

# --- Bot Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome! What's your name?")
    return ASK_NAME

async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    button = KeyboardButton("📱 Share phone", request_contact=True)
    markup = ReplyKeyboardMarkup([[button]], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Great! Now please share your phone number:", reply_markup=markup)
    return ASK_PHONE

async def save_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    name = context.user_data['name']
    chat_id = update.effective_chat.id
    user_id = contact.user_id
    phone = contact.phone_number

    users[str(user_id)] = {
        "name": name,
        "phone": phone,
        "chat_id": chat_id
    }

    save_to_airtable(name, phone, user_id, chat_id)

    await update.message.reply_text(f"🎉 Thanks {name}, you're registered!")
    await update.message.reply_text("🎬 Here's a welcome video:\nhttps://youtu.be/ESuE9Svil-Y?si=hIqYTOLjDCwxbDfy")
    return ConversationHandler.END

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("⛔ Unauthorized!")

    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return await update.message.reply_text("⚠️ Failed to fetch users.")

    records = response.json().get("records", [])
    total_users = len(records)

    if not records:
        return await update.message.reply_text("📭 No users found.")

    reply = f"📋 *User List* ({total_users} total):\n\n"
    for rec in records:
        fields = rec["fields"]
        name = fields.get("Name", "N/A")
        phone = fields.get("Phone", "N/A")
        chat_id = str(fields.get("Chat ID", "N/A"))
        reply += f"👤 {name}\n📱 {phone}\n💬 Chat ID: `{chat_id}`\n\n"

    await update.message.reply_text(reply, parse_mode="Markdown")

async def send_video_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text("⛔ Unauthorized!")

    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /sendvideo <YouTube link>")

    video_url = context.args[0]
    for user in users.values():
        try:
            await context.bot.send_message(chat_id=user["chat_id"], text=f"Hi {user['name']}! 🎥 New video for you!\n{video_url}")
        except Exception as e:
            logging.error(f"Failed to send video to {user['chat_id']}: {e}")

    await update.message.reply_text("✅ Video sent to all users.")

# --- Webhook route ---
async def webhook_handler(request):
    data = await request.json()
    await application.update_queue.put(Update.de_json(data, application.bot))
    return web.Response()

# --- Main ---
async def main():
    global application
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
            ASK_PHONE: [MessageHandler(filters.CONTACT, save_user)],
        },
        fallbacks=[]
    )

    application.add_handler(conv)
    application.add_handler(CommandHandler("sendvideo", send_video_command))
    application.add_handler(CommandHandler("users", list_users))

    # Set webhook
    domain = os.getenv("RAILWAY_STATIC_URL")  # You’ll set this later
    if not domain:
        raise Exception("RAILWAY_STATIC_URL not set")

    await application.bot.set_webhook(f"{domain}/webhook")

    # Start web server
    app = web.Application()
    app.router.add_post("/webhook", webhook_handler)
    port = int(os.environ.get("PORT", 8000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    logging.info("Bot started with webhook.")
    await application.initialize()
    await application.start()
    await application.updater.start_polling()  # Optional fallback if needed

    await application.updater.idle()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
