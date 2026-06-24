import os
import re
import telebot
import threading
from flask import Flask

# --- Flask Server (Render के लिए) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- Bot Setup ---
YOUR_USER_ID = 8010857405
BOT_TOKEN = "8530224634:AAEAggfYdL1vekDXH3pkPu9xe2C1HZYncc0"
bot = telebot.TeleBot(BOT_TOKEN)

# --- MCQ Parsing Function ---
def parse_mcq(text):
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if len(lines) < 6:
        return None

    question_lines = []
    option_lines = []
    answer_line = None

    for line in lines:
        if re.match(r'^(?:Answer|Ans|सही उत्तर|जवाब)', line, re.IGNORECASE):
            answer_line = line
        elif re.match(r'^[a-dA-D1-4][\.\)]', line) or re.match(r'^[\(\[]?[a-dA-D1-4][\)\]]', line):
            option_lines.append(line)
        else:
            question_lines.append(line)

    if len(option_lines) != 4 or not answer_line:
        return None

    question = "\n".join(question_lines).strip()
    options = [re.sub(r'^[\(\[]?[a-dA-D1-4][\.\)\]]?\s*', '', opt).strip() for opt in option_lines]

    ans_match = re.search(r'([a-dA-D1-4])', answer_line)
    if not ans_match:
        return None
    
    answer = ans_match.group(1)
    if answer.isdigit():
        correct_idx = int(answer) - 1
    else:
        correct_idx = ord(answer.upper()) - 65

    return question, options, correct_idx

# --- Message Handler ---
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    if message.from_user.id != YOUR_USER_ID:
        bot.reply_to(message, "Access Denied. यह बोट प्राइवेट है।")
        return

    result = parse_mcq(message.text)
    if result:
        question, options, correct_idx = result
        response = f"✅ **Question Identified:**\n{question}\n\n"
        for i, opt in enumerate(options):
            marker = "🔹" if i == correct_idx else "⚪"
            response += f"{marker} {opt}\n"
        bot.reply_to(message, response)
    else:
        bot.reply_to(message, "❌ Sorry, I couldn't understand the MCQ format. Please check the text.")

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    print("Bot is starting...")
    bot.infinity_polling()
