from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler, MessageHandler, CommandHandler, filters, ContextTypes
import requests
import os

ASK_NAME, ASK_PHONE = range(2)

AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY", "pat5rcPyQjiGtqHJF.e878d10e1f84ea5244ca73d34993b8acc2c74c2abcfa7eb4cce0113b8dd5fecc")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID", "app8wCInTiHaT95Cq")
AIRTABLE_TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME", "Telegram Bot Users")
VIDEO_LINK = "https://youtu.be/ESuE9Svil-Y?si=nDj0HalBBDwXu8MU"

def user_exists(user_id):
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
    headers = {
        "Authorization": f"Bearer {AIRTABLE_API_KEY}"
    }
    params = {
        "filterByFormula": f"{{User ID}} = '{user_id}'"
    }
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    return len(data.get("records", [])) > 0

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
    requests.post(url, json=data, headers=headers)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Please enter your full name:")
    return ASK_NAME

async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    contact_button = KeyboardButton("Send Phone Number", request_contact=True)
    reply_markup = ReplyKeyboardMarkup([[contact_button]], one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Now share your phone number:", reply_markup=reply_markup)
    return ASK_PHONE

async def save_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = context.user_data["name"]
    phone = update.message.contact.phone_number
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id

    username = update.message.from_user.first_name or "there"
    welcome_msg = f"Welcome {username}! This is the video for you: {VIDEO_LINK}"

    if user_exists(user_id):
        await update.message.reply_text("👋 You’re already registered!")
        await update.message.reply_text(welcome_msg)
    else:
        save_to_airtable(name, phone, user_id, chat_id)
        await update.message.reply_text("✅ Registration complete!")
        await update.message.reply_text(welcome_msg)

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Registration canceled.")
    return ConversationHandler.END

user_handlers = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
        ASK_PHONE: [MessageHandler(filters.CONTACT, save_user)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
