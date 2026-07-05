import os
import re
import threading
from flask import Flask
import telebot

# ---------------- CONFIG ----------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

bot = telebot.TeleBot(BOT_TOKEN)

# ---------------- FLASK ----------------
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# ---------------- START ----------------
@bot.message_handler(commands=["start"])
def start(message):
    if message.from_user.id != OWNER_ID:
        return

    bot.reply_to(
        message,
        "✅ DocTalk Quiz Bot is Online!\n\nSend your MCQ."
    )

# ---------------- MCQ PARSER ----------------
def parse_mcq(text):

    pattern = re.compile(
        r"(.*?)"
        r"\(1\)\s*(.*?)"
        r"\(2\)\s*(.*?)"
        r"\(3\)\s*(.*?)"
        r"\(4\)\s*(.*?)"
        r"(?:Answer|Ans)\s*:\s*\(?([1-4])\)?",
        re.S | re.I
    )

    m = pattern.search(text)

    if not m:
        return None

    question = m.group(1).strip()

    options = [
        m.group(2).strip(),
        m.group(3).strip(),
        m.group(4).strip(),
        m.group(5).strip(),
    ]

    answer = int(m.group(6)) - 1

    return question, options, answer

# ---------------- HANDLE ----------------
@bot.message_handler(func=lambda m: True)
def all_messages(message):

    if message.from_user.id != OWNER_ID:
        return

    data = parse_mcq(message.text)

    if not data:
        bot.reply_to(message, "❌ MCQ format not recognised.")
        return

    question, options, answer = data

    bot.send_poll(
        chat_id=message.chat.id,
        question=question,
        options=options,
        type="quiz",
        correct_option_id=answer,
        is_anonymous=True
    )

# ---------------- MAIN ----------------
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    print("Bot Started...")
    bot.infinity_polling(skip_pending=True)
