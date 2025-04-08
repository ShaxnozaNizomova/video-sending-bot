from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes
import requests
import os

ADMIN_ID = int(os.getenv("ADMIN_ID", "1854307576"))
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY", "pat5rcPyQjiGtqHJF.e878d10e1f84ea5244ca73d34993b8acc2c74c2abcfa7eb4cce0113b8dd5fecc")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID", "app8wCInTiHaT95Cq")
AIRTABLE_TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME", "Telegram Bot Users")

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
    headers = {"Authorization": f"Bearer {AIRTABLE_API_KEY}"}
    res = requests.get(url, headers=headers).json()
    text = "👥 Registered Users:\n"
    for r in res.get("records", []):
        f = r["fields"]
        text += f'- {f.get("Name", "N/A")} | {f.get("Phone", "N/A")}\n'
    await update.message.reply_text(text)

async def send_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("Please send the YouTube or Telegram video link after /sendvideo")
        return
    video_link = context.args[0]
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}"
    headers = {"Authorization": f"Bearer {AIRTABLE_API_KEY}"}
    res = requests.get(url, headers=headers).json()
    for r in res.get("records", []):
        chat_id = r["fields"].get("Chat ID")
        if chat_id:
            try:
                await context.bot.send_message(chat_id=chat_id, text=video_link)
            except Exception as e:
                print(f"Failed to send to {chat_id}: {e}")
    await update.message.reply_text("✅ Video sent to all users.")

admin_handlers = [
    CommandHandler("listusers", list_users),
    CommandHandler("sendvideo", send_video),
]
