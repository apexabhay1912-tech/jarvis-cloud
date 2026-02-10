import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from groq import Groq

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# Environment variables
BOT_TOKEN = os.getenv("8399881718:AAGEgHsTO3ZUGuJCEZb2ERyktrPWrkj3SMo")
GROQ_API_KEY = os.getenv("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")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is missing. Set it in Railway Variables.")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing. Set it in Railway Variables.")

# Groq client
client = Groq(api_key=GROQ_API_KEY)


# Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "JARVIS online.\nSend me anything and I'll respond."
    )


# Message handler using Groq
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "You are JARVIS, a helpful assistant."},
                {"role": "user", "content": user_message},
            ],
        )

        reply = response.choices[0].message.content

    except Exception as e:
        logging.error(f"Groq Error: {e}")
        reply = "Error talking to AI. Check API key or logs."

    await update.message.reply_text(reply)


async def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Fix Telegram conflict issue
    await application.bot.delete_webhook(drop_pending_updates=True)

    # Start polling safely
    await application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
