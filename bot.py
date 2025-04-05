import json
import logging
import requests
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler
)

# --- Airtable Setup ---
AIRTABLE_API_KEY = "pat5rcPyQjiGtqHJF.e878d10e1f84ea5244ca73d34993b8acc2c74c2abcfa7eb4cce0113b8dd5fecc"  # Replace with your Airtable API Key
AIRTABLE_BASE_ID = "app8wCInTiHaT95Cq"  
AIRTABLE_TABLE_NAME = "Telegram Bot Users" 

BOT_TOKEN = "7813479172:AAEVo-u3o9C7z7ZzEHu--kRu-GmhtEVej_k"  
ADMIN_ID = 500062278
# --- Conversation States ---
ASK_NAME, ASK_PHONE = range(2)

# --- In-Memory User Storage ---
users = {}

# --- Airtable Save Function ---
def save_to_airtable(name, phone, user_id, chat_id):
    print(f"Saving to Airtable: Name: {name}, Phone: {phone}, User ID: {user_id}, Chat ID: {chat_id}")
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

# --- Start Command ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome! What's your name?")
    return ASK_NAME

# --- Save Name ---
async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    button = KeyboardButton("📱 Share phone", request_contact=True)
    markup = ReplyKeyboardMarkup([[button]], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Great! Now please share your phone number:", reply_markup=markup)
    return ASK_PHONE

# --- Save Phone & Send Welcome Video ---
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

# --- List Users (Admin Only) ---
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
        chat_id = str(fields.get("Chat ID", "N/A"))  # Use Chat ID from Airtable record
        reply += f"👤 {name}\n📱 {phone}\n💬 Chat ID: `{chat_id}`\n\n"

    await update.message.reply_text(reply, parse_mode="Markdown")

# --- Admin Send Video ---
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

# --- Main ---
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler, filters

def main():
    # Set logging level to WARNING to suppress INFO logs
    logging.basicConfig(level=logging.WARNING)  # This will suppress logs below WARNING level
    logging.getLogger("httpx").setLevel(logging.WARNING)  # Specifically suppress INFO logs from httpx

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
            ASK_PHONE: [MessageHandler(filters.CONTACT, save_user)],
        },
        fallbacks=[]
    )

    app.add_handler(conv)
    app.add_handler(CommandHandler("sendvideo", send_video_command))
    app.add_handler(CommandHandler("users", list_users))
    app.run_polling()

if __name__ == "__main__":
    main()

