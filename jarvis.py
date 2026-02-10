import json
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

def load_token():
    token = os.getenv("8399881718:AAF7wvRp-QyBVk9vTJN6nKYWxbpd-uf2zJA")
    if token:
        print("Token loaded from environment")
        return token.strip()

    if os.path.exists("token.txt"):
        with open("token.txt") as f:
            token = f.read().strip()
            if token:
                print("Token loaded from token.txt")
                return token

    raise Exception("BOT_TOKEN not found")

BOT_TOKEN = load_token()

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if not text.startswith("jarvis"):
        return

    await update.message.reply_text("Jarvis online and working.")

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT, reply))

print("Jarvis Cloud started")
app.run_polling()
