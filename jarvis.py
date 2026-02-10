import os
import json
import requests
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# ---------- TOKENS ----------
BOT_TOKEN = os.getenv("8399881718:AAF7wvRp-QyBVk9vTJN6nKYWxbpd-uf2zJA")
AI_API_KEY = os.getenv("708901dffb53496ea4f3830735e99419")

# fallback for local testing
if not BOT_TOKEN and os.path.exists("token.txt"):
    with open("token.txt") as f:
        BOT_TOKEN = f.read().strip()

if not BOT_TOKEN:
    raise Exception("BOT_TOKEN not found")

print("Jarvis Cloud started")

# ---------- FILE HELPERS ----------
def load_json(file):
    if not os.path.exists(file):
        return []
    with open(file, "r") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

# ---------- TELEGRAM HANDLER ----------
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower().strip()

    if not text.startswith("jarvis"):
        return

    command = text.replace("jarvis", "").strip()

    # ---------- DEADLINES ----------
    if command.startswith("add deadline"):
        deadlines = load_json("deadlines.json")
        deadlines.append(command.replace("add deadline", "").strip())
        save_json("deadlines.json", deadlines)
        await update.message.reply_text("Deadline saved.")
        return

    if command == "deadlines":
        deadlines = load_json("deadlines.json")
        await update.message.reply_text("\n".join(deadlines) if deadlines else "No deadlines saved.")
        return

    # ---------- TASKS ----------
    if command.startswith("add task"):
        tasks = load_json("tasks.json")
        tasks.append(command.replace("add task", "").strip())
        save_json("tasks.json", tasks)
        await update.message.reply_text("Task saved.")
        return

    if command == "tasks":
        tasks = load_json("tasks.json")
        await update.message.reply_text("\n".join(tasks) if tasks else "No tasks saved.")
        return

    # ---------- PLAN DAY ----------
    if command == "plan my day":
        tasks = load_json("tasks.json")
        deadlines = load_json("deadlines.json")

        message = "Today's Plan:\n\n"

        if deadlines:
            message += "Deadlines:\n" + "\n".join(deadlines) + "\n\n"

        if tasks:
            message += "Tasks:\n" + "\n".join(tasks)

        await update.message.reply_text(message)
        return

    # ---------- AI RESPONSE ----------
    if AI_API_KEY:
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {AI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": "You are Jarvis, a helpful assistant for CA Intermediate studies, office work, and planning."},
                        {"role": "user", "content": command}
                    ],
                    "max_tokens": 500
                },
                timeout=30
            )

            if response.status_code == 200:
                answer = response.json()["choices"][0]["message"]["content"]
                await update.message.reply_text(answer[:3500])
                return
            else:
                await update.message.reply_text("AI error. Please try again.")
                return

        except Exception as e:
            await update.message.reply_text("AI unreachable right now.")
            return

    # ---------- FALLBACK ----------
    await update.message.reply_text("Jarvis is running but AI not configured.")

# ---------- START BOT ----------
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

print("Jarvis is online and working...")
app.run_polling()
