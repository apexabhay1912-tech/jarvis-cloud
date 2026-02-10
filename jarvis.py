import json
import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler

# -------- TOKEN LOADING --------
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

# -------- FILE HELPERS --------
def load_json(filename, default):
    try:
        if not os.path.exists(filename):
            return default
        with open(filename, "r") as f:
            return json.load(f)
    except:
        return default

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

# -------- STUDY --------
def add_study(hours, subject):
    data = load_json("study_hours.json", {"records": []})
    data["records"].append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "hours": hours,
        "subject": subject
    })
    save_json("study_hours.json", data)

def get_study_report():
    data = load_json("study_hours.json", {"records": []})
    totals = {}

    for r in data["records"]:
        totals[r["subject"]] = totals.get(r["subject"], 0) + r["hours"]

    if not totals:
        return "No study records yet."

    report = "Study Report:\n"
    for subject, hrs in totals.items():
        report += f"{subject}: {hrs} hrs\n"

    return report

# -------- DEADLINES --------
def get_deadlines():
    data = load_json("deadlines.json", {"deadlines": []})
    if not data["deadlines"]:
        return "No deadlines saved."
    return "Deadlines:\n" + "\n".join(data["deadlines"])

# -------- REMINDER --------
CHAT_ID_FILE = "chat_id.txt"

async def send_morning_reminder(app):
    if not os.path.exists(CHAT_ID_FILE):
        return

    with open(CHAT_ID_FILE) as f:
        chat_id = f.read().strip()

    message = "Good morning.\n\n"
    message += get_deadlines()
    message += "\n\nSay 'jarvis study report' to see study hours."

    await app.bot.send_message(chat_id=chat_id, text=message)

# -------- TELEGRAM HANDLERS --------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open(CHAT_ID_FILE, "w") as f:
        f.write(str(update.effective_chat.id))

    await update.message.reply_text(
        "Jarvis Cloud Online.\n\n"
        "Examples:\n"
        "jarvis studied 2 tax\n"
        "jarvis study report\n"
        "jarvis deadlines"
    )

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower().strip()

    if not text.startswith("jarvis"):
        return

    command = text.replace("jarvis", "", 1).strip()

    if command.startswith("studied"):
        try:
            parts = command.split()
            hours = float(parts[1])
            subject = " ".join(parts[2:])
            add_study(hours, subject)
            await update.message.reply_text("Study saved.")
        except:
            await update.message.reply_text("Format: jarvis studied 2 accounts")
        return

    if "study report" in command:
        await update.message.reply_text(get_study_report())
        return

    if "deadlines" in command:
        await update.message.reply_text(get_deadlines())
        return

    await update.message.reply_text("Command not recognized.")

# -------- MAIN --------
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

scheduler = BackgroundScheduler()

async def reminder_wrapper():
    await send_morning_reminder(app)

scheduler.add_job(reminder_wrapper, "cron", hour=10, minute=0)
scheduler.start()

print("Jarvis Cloud running...")
app.run_polling()
