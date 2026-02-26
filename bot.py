import os
import requests
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# ========= ENV =========
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ========= FLASK (Sleep Fix) =========
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

threading.Thread(target=run_flask).start()

# ========= AI FUNCTION =========
def ask_ai(text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "You are a helpful multilingual AI assistant."},
            {"role": "user", "content": text}
        ]
    }
    r = requests.post(url, headers=headers, json=data, timeout=30)
    return r.json()["choices"][0]["message"]["content"]

# ========= TELEGRAM HANDLER =========
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await update.message.chat.send_action("typing")
    ai_text = ask_ai(user_text)
    await update.message.reply_text(ai_text)

# ========= BOT START =========
app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))
app_bot.run_polling()
