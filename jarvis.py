import os
import json
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from groq import Groq

# ---------- LOGGING ----------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ---------- LOAD TOKENS ----------
BOT_TOKEN = os.getenv("8399881718:AAGEgHsTO3ZUGuJCEZb2ERyktrPWrkj3SMo")
GROQ_API_KEY = os.getenv("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")

# fallback for local testing
if not BOT_TOKEN and os.path.exists("token.txt"):
    with open("token.txt") as f:
        BOT_TOKEN = f.read().strip()

if not BOT_TOKEN:
    raise Exception("BOT_TOKEN not found!")

print("BOT_TOKEN loaded:", bool(BOT_TOKEN))
print("GROQ_API_KEY loaded:", bool(GROQ_API_KEY))

# ---------- INIT GROQ ----------
groq_client = None
if GROQ_API_KEY:
    groq_client = Groq(api_key=GROQ_API_KEY)
    print("Groq initialized")
else:
    print("Groq not configured")

# ---------- FILE HELPERS ----------
def load_json(file):
    if not os.path.exists(file):
        return []
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return []

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

# ---------- MAIN HANDLER ----------
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message or not update.message.text:
        return

    text = update.message.text.lower().strip()

    # Wake word filter
    if not text.startswith("jarvis"):
        return

    command = text.replace("jarvis", "", 1).strip()

    if command == "":
        await update.message.reply_text("Yes? How can I help?")
        return

    # ---------- DEADLINES ----------
    if command.startswith("add deadline"):
        deadlines = load_json("deadlines.json")
        new_deadline = command.replace("add deadline", "").strip()

        if new_deadline:
            deadlines.append(new_deadline)
            save_json("deadlines.json", deadlines)
            await update.message.reply_text(f"✅ Deadline saved: {new_deadline}")
        else:
            await update.message.reply_text("Please provide deadline details.")
        return

    if command == "deadlines":
        deadlines = load_json("deadlines.json")
        if deadlines:
            msg = "📅 Deadlines:\n\n" + "\n".join(f"• {d}" for d in deadlines)
        else:
            msg = "No deadlines saved."
        await update.message.reply_text(msg)
        return

    # ---------- TASKS ----------
    if command.startswith("add task"):
        tasks = load_json("tasks.json")
        new_task = command.replace("add task", "").strip()

        if new_task:
            tasks.append(new_task)
            save_json("tasks.json", tasks)
            await update.message.reply_text(f"✅ Task saved: {new_task}")
        else:
            await update.message.reply_text("Please provide task details.")
        return

    if command == "tasks":
        tasks = load_json("tasks.json")
        if tasks:
            msg = "📝 Tasks:\n\n" + "\n".join(f"• {t}" for t in tasks)
        else:
            msg = "No tasks saved."
        await update.message.reply_text(msg)
        return

    # ---------- PLAN DAY ----------
    if command == "plan my day":
        tasks = load_json("tasks.json")
        deadlines = load_json("deadlines.json")

        msg = "☀ Today's Plan\n\n"

        if deadlines:
            msg += "Deadlines:\n" + "\n".join(f"• {d}" for d in deadlines) + "\n\n"

        if tasks:
            msg += "Tasks:\n" + "\n".join(f"• {t}" for t in tasks)

        if not tasks and not deadlines:
            msg += "Nothing scheduled yet."

        await update.message.reply_text(msg)
        return

    # ---------- AI RESPONSE ----------
    if groq_client:
        try:
            response = groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are Jarvis, a concise assistant helping with CA Intermediate studies, productivity and planning."
                    },
                    {
                        "role": "user",
                        "content": command
                    }
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                max_tokens=500
            )

            answer = response.choices[0].message.content
            await update.message.reply_text(answer)

        except Exception as e:
            logging.error(e)
            await update.message.reply_text("AI error occurred.")
    else:
        await update.message.reply_text("⚠️ AI API key missing.")

# ---------- START BOT ----------
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

    print("Jarvis cloud is running...")
    app.run_polling()
