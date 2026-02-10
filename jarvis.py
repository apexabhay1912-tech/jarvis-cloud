import os
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# Load BOT TOKEN
BOT_TOKEN = os.getenv("8399881718:AAF7wvRp-QyBVk9vTJN6nKYWxbpd-uf2zJA")

if not BOT_TOKEN:
    try:
        with open("token.txt") as f:
            BOT_TOKEN = f.read().strip()
            print("Token loaded from token.txt")
    except:
        raise Exception("BOT_TOKEN not found")

print("Jarvis Cloud started")

# Load files
def load_json(file):
    if not os.path.exists(file):
        return []
    with open(file, "r") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

# Handler
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    # Wake word check
    if not text.startswith("jarvis"):
        return

    command = text.replace("jarvis", "").strip()

    # DEADLINES
    if command.startswith("add deadline"):
        deadlines = load_json("deadlines.json")
        deadlines.append(command.replace("add deadline", "").strip())
        save_json("deadlines.json", deadlines)
        await update.message.reply_text("Deadline saved.")
        return

    if command == "deadlines":
        deadlines = load_json("deadlines.json")
        if deadlines:
            await update.message.reply_text("\n".join(deadlines))
        else:
            await update.message.reply_text("No deadlines saved.")
        return

    # TASKS
    if command.startswith("add task"):
        tasks = load_json("tasks.json")
        tasks.append(command.replace("add task", "").strip())
        save_json("tasks.json", tasks)
        await update.message.reply_text("Task saved.")
        return

    if command == "tasks":
        tasks = load_json("tasks.json")
        if tasks:
            await update.message.reply_text("\n".join(tasks))
        else:
            await update.message.reply_text("No tasks saved.")
        return

    # PLAN DAY
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

    # DEFAULT RESPONSE
    await update.message.reply_text("Jarvis heard you. More intelligence coming soon.")

# App
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

print("Jarvis is online and working...")
app.run_polling()
