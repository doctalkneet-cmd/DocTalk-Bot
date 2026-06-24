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
# ध्यान दें: अपना ओरिजिनल टोकन यहाँ ज़रूर रखें
BOT_TOKEN = "8530224634:AAEWpdn6AD3jrksLjx2DZJWwAGabyF3Gozs"
bot = telebot.TeleBot(BOT_TOKEN)

# --- MCQ Parsing Function ---
def parse_mcq(text):
    # 1. Number Format (1, 2, 3, 4)
    pattern_1234 = r"(?s)Question:(.*?)\(1\)(.*?)\(2\)(.*?)\(3\)(.*?)\(4\)(.*?)(?:Answer|Ans)\s*:\s*([1-4])"
    match_1234 = re.search(pattern_1234, text, re.IGNORECASE)
    if match_1234:
        question = match_1234.group(1).strip()
        options = [match_1234.group(2).strip(), match_1234.group(3).strip(), match_1234.group(4).strip(), match_1234.group(5).strip()]
        correct_idx = int(match_1234.group(6).strip()) - 1
        return question, options, correct_idx

    # 2. Alphabet Format (A, B, C, D)
    pattern_abcd = r"(?s)Question:(.*?)\(A\)(.*?)\(B\)(.*?)\(C\)(.*?)\(D\)(.*?)(?:Answer|Ans)\s*:\s*([A-D])"
    match_abcd = re.search(pattern_abcd, text, re.IGNORECASE)
    if match_abcd:
        question = match_abcd.group(1).strip()
        options = [match_abcd.group(2).strip(), match_abcd.group(3).strip(), match_abcd.group(4).strip(), match_abcd.group(5).strip()]
        # A=0, B=1, C=2, D=3
        correct_idx = ord(match_abcd.group(6).upper()) - 65
        return question, options, correct_idx
    
    return None

# --- Message Handler ---
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
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
    # Flask को अलग थ्रेड में शुरू करें
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    
    # फिर बॉट शुरू करें
    print("Bot is starting...")
    bot.infinity_polling()
