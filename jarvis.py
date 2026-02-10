import os
import json
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from groq import Groq  # IMPORT GROQ CLIENT

# ---------- CONFIGURATION ----------
# Set up logging to see errors in Railway logs
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = os.getenv("8399881718:AAGEgHsTO3ZUGuJCEZb2ERyktrPWrkj3SMo")
GROQ_API_KEY = os.getenv("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") # Changed from AI_API_KEY

# Fallback for local testing (optional)
if not BOT_TOKEN and os.path.exists("token.txt"):
    with open("token.txt") as f:
        BOT_TOKEN = f.read().strip()

if not BOT_TOKEN:
    raise Exception("BOT_TOKEN not found! Check your Railway variables.")

# Initialize Groq Client
groq_client = None
if GROQ_API_KEY:
    groq_client = Groq(api_key=GROQ_API_KEY)
else:
    print("Warning: GROQ_API_KEY not found. AI features will be disabled.")

print("Jarvis Cloud started")

# ---------- FILE HELPERS ----------
def load_json(file):
    if not os.path.exists(file):
        return []
    try:
        with open(file, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return [] # Return empty list if file is corrupted

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

# ---------- TELEGRAM HANDLER ----------
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Check if message has text (avoids crash on stickers/files)
    if not update.message or not update.message.text:
        return

    text = update.message.text.lower().strip()

    # Filter: Only respond if message starts with "jarvis"
    if not text.startswith("jarvis"):
        return

    # Remove "jarvis" to get the actual command
    command = text.replace("jarvis", "", 1).strip()

    # ---------- DEADLINES ----------
    if command.startswith("add deadline"):
        deadlines = load_json("deadlines.json")
        new_deadline = command.replace("add deadline", "").strip()
        if new_deadline:
            deadlines.append(new_deadline)
            save_json("deadlines.json", deadlines)
            await update.message.reply_text(f"✅ Deadline saved: {new_deadline}")
        else:
            await update.message.reply_text("Please specify the deadline details.")
        return

    if command == "deadlines":
        deadlines = load_json("deadlines.json")
        if deadlines:
            response = "📅 **Upcoming Deadlines:**\n\n" + "\n".join(f"• {d}" for d in deadlines)
            await update.message.reply_text(response, parse_mode="Markdown")
        else:
            await update.message.reply_text("No deadlines saved.")
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
            await update.message.reply_text("Please specify the task details.")
        return

    if command == "tasks":
        tasks = load_json("tasks.json")
        if tasks:
            response = "📝 **Pending Tasks:**\n\n" + "\n".join(f"• {t}" for t in tasks)
            await update.message.reply_text(response, parse_mode="Markdown")
        else:
            await update.message.reply_text("No tasks saved.")
        return

    # ---------- PLAN DAY ----------
    if command == "plan my day":
        tasks = load_json("tasks.json")
        deadlines = load_json("deadlines.json")

        message = "☀ **Today's Plan:**\n\n"
        if deadlines:
            message += "*Deadlines:*\n" + "\n".join(f"• {d}" for d in deadlines) + "\n\n"
        if tasks:
            message += "*Tasks:*\n" + "\n".join(f"• {t}" for t in tasks)
        
        if not deadlines and not tasks:
            message += "You have no tasks or deadlines recorded! Enjoy your day."

        await update.message.reply_text(message, parse_mode="Markdown")
        return

    # ---------- GROQ AI RESPONSE ----------
    if groq_client:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        try:
            chat_completion = groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are Jarvis, a helpful assistant for CA Intermediate studies, office work, and planning. Keep answers concise and professional."
                    },
                    {
                        "role": "user",
                        "content": command
                    }
                ],
                model="llama-3.3-70b-versatile", # Reliable and fast model
                max_tokens=500,
                temperature=0.7
            )

            answer = chat_completion.choices[0].message.content
            await update.message.reply_text(answer)
        
        except Exception as e:
            logging.error(f"Groq API Error: {e}")
            await update.message.reply_text("⚠️ Jarvis AI is currently unavailable.")
    else:
        await update.message.reply_text("⚠️ AI API Key is missing.")

# ---------- START BOT ----------
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))
    print("Jarvis is online and working...")
    app.run_polling()

