import time
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

    blocks = message.text.split("---")

    total = 0

    for block in blocks:

        block = block.strip()

        if not block:
            continue

        data = parse_mcq(block)

        if not data:
            continue

        question, options, answer = data

        # Long Question Handling
        if len(question) > 290:
            bot.send_message(message.chat.id, question)
            poll_question = "Choose the Correct Answer"
        else:
            poll_question = question

        # Long Options Handling
        options = [opt[:100] for opt in options]

        bot.send_poll(
            chat_id=message.chat.id,
            question=poll_question,
            options=options,
            type="quiz",
            correct_option_id=answer,
            is_anonymous=True
        )

        total += 1

        # Telegram Rate Limit
        time.sleep(0.5)

    if total == 0:
        bot.reply_to(message, "❌ No valid MCQs found.")
    else:
        bot.send_message(
            message.chat.id,
            f"✅ {total} Quiz Created Successfully."
        )

# ---------------- MAIN ----------------
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    print("Bot Started...")
    bot.infinity_polling(skip_pending=True)
