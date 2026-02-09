import json
import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest

BOT_TOKEN = os.getenv("8399881718:AAF7wvRp-QyBVk9vTJN6nKYWxbpd-uf2zJA")
CHAT_ID_FILE = "chat_id.txt"

# ---------- File Helpers ----------
def load_json(filename, default):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except:
        return default

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

# ---------- Study Tracking ----------
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

# ---------- Deadlines ----------
def get_deadlines():
    data = load_json("deadlines.json", {"deadlines": []})
    if not data["deadlines"]:
        return "No deadlines saved."
    return "Deadlines:\n" + "\n".join(data["deadlines"])

# ---------- Morning Reminder ----------
def send_morning_reminder(app):
    try:
        with open(CHAT_ID_FILE, "r") as f:
            chat_id = f.read().strip()

        msg = "Good morning.\n\n"
        msg += get_deadlines()
        msg += "\n\nSay 'jarvis study report' to see study hours."

        app.bot.send_message(chat_id=chat_id, text=msg)

    except Exception as e:
        print("Reminder error:", e)

# ---------- Telegram ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open(CHAT_ID_FILE, "w") as f:
        f.write(str(update.effective_chat.id))

    await update.message.reply_text(
        "Jarvis Cloud Online.\n"
        "Commands:\n"
        "jarvis studied 2 accounts\n"
        "jarvis study report\n"
        "jarvis deadlines"
    )

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower().strip()

    if not text.startswith("jarvis"):
        return

    command = text.replace("jarvis", "", 1).strip()

    # Study record
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

    # Study report
    if "study report" in command:
        await update.message.reply_text(get_study_report())
        return

    # Deadlines
    if "deadlines" in command:
        await update.message.reply_text(get_deadlines())
        return

    await update.message.reply_text("Command not recognized.")

# ---------- Error Handler ----------
async def error_handler(update, context):
    print("Error:", context.error)

# ---------- Start Bot ----------
request = HTTPXRequest(connect_timeout=60, read_timeout=300)

app = ApplicationBuilder().token(BOT_TOKEN).request(request).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))
app.add_error_handler(error_handler)

scheduler = BackgroundScheduler()
scheduler.add_job(lambda: send_morning_reminder(app), "cron", hour=10, minute=0)
scheduler.start()

print("Jarvis Cloud running...")
app.run_polling()
