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

# --- Configuration ---
YOUR_USER_ID = 8010857405
BOT_TOKEN = "8530224634:AAEAggfYdL1vekDXH3pkPu9xe2C1HZYncc0"
bot = telebot.TeleBot(BOT_TOKEN)

# --- MCQ Logic (ब्रैकेट सुधार के साथ) ---
def parse_mcq(text):
    # Number Format Check - अब \(? और \)? जोड़ दिया है ताकि (1) और 1 दोनों काम करें
    pattern_1234 = r"(?s)(?:\s*|\\\s*)\(1\)(.*?)\(2\)(.*?)\(3\)(.*?)\(4\)(?:\s*|\\\s*)(?:Answer|Ans)\s*:\s*\(?([1-4])\)?"
    match_1234 = re.search(pattern_1234, text, re.IGNORECASE)
    
    if match_1234:
        question = match_1234.group(1).strip()
        question = re.sub(r"^(?:Question:[Q:]\s*)", "", question, flags=re.IGNORECASE).strip()
        options = [match_1234.group(2).strip(), match_1234.group(3).strip(), match_1234.group(4).strip(), match_1234.group(5).strip()]
        correct_idx = int(match_1234.group(4).strip()) - 1
        return question, options, correct_idx

    # Alphabet Format Check - इसमें भी ब्रैकेट का सुधार किया है
    pattern_abcd = r"(?s)(?:\s*|\\\s*)\(A\)(.*?)\(B\)(.*?)\(C\)(.*?)\(D\)(?:\s*|\\\s*)(?:Answer|Ans)\s*:\s*\(?([A-D])\)?"
    match_abcd = re.search(pattern_abcd, text, re.IGNORECASE)
    
    if match_abcd:
        question = match_abcd.group(1).strip()
        question = re.sub(r"^(?:Question:[Q:]\s*)", "", question, flags=re.IGNORECASE).strip()
        options = [match_abcd.group(2).strip(), match_abcd.group(3).strip(), match_abcd.group(4).strip(), match_abcd.group(5).strip()]
        correct_idx = ord(match_abcd.group(4).upper()) - 65
        return question, options, correct_idx
    return None

# --- Handler (Privacy के साथ) ---
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    if message.from_user.id != YOUR_USER_ID:
        return

    if message.text.startswith('/start'):
        return

    blocks = message.text.split('---')
    for block in blocks:
        block = block.strip()
        if not block: continue
        parsed = parse_mcq(block)
        if parsed:
            question, options, correct_idx = parsed
            try:
                bot.send_poll(chat_id=message.chat.id, question=question, options=options, type="quiz", correct_option_id=correct_idx, is_anonymous=True)
            except Exception as e:
                bot.reply_to(message, f"Error: {e}")
        else:
            bot.reply_to(message, "यह फॉर्मेट समझ नहीं आया।")

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.infinity_polling()
