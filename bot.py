import os
import re
import telebot
import threading
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# अपना टोकन और User ID यहाँ रखें
BOT_TOKEN = "8530224634:AAEWpdn6AD3jrksLjx2DZJWwAGabyF3Gozs"
YOUR_USER_ID = 8010857405
bot = telebot.TeleBot(BOT_TOKEN)

def parse_mcq_robust(text):
    # यह पैटर्न सवाल, 4 विकल्प और आंसर को किसी भी फॉर्मेट में पकड़ेगा
    # यह (1), 1), 1. या (A), A), A. को सपोर्ट करता है
    pattern = r"(?s)(.*?)\n\s*\(?[1A-D][\.\)]\s*(.*?)\n\s*\(?[2B][\.\)]\s*(.*?)\n\s*\(?[3C][\.\)]\s*(.*?)\n\s*\(?[4D][\.\)]\s*(.*?)\n\s*(?:Answer|Ans)\s*[:\s]*\(?([1-4A-D])\)"
    match = re.search(pattern, text, re.IGNORECASE)
    
    if match:
        question = match.group(1).strip()
        options = [match.group(2).strip(), match.group(3).strip(), match.group(4).strip(), match.group(5).strip()]
        ans_raw = match.group(6).upper()
        
        # इंडेक्स निकालें (A=0, 1=0, B=1, 2=1 etc)
        correct_idx = (int(ans_raw) - 1) if ans_raw.isdigit() else (ord(ans_raw) - 65)
        return question, options, correct_idx
    return None

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    if message.from_user.id != YOUR_USER_ID: return
    
    result = parse_mcq_robust(message.text)
    if result:
        question, options, correct_idx = result
        response = f"✅ {question}\n\n"
        for i, opt in enumerate(options):
            marker = "🔹" if i == correct_idx else "⚪"
            response += f"{marker} {opt}\n"
        bot.reply_to(message, response)
    else:
        bot.reply_to(message, "❌ इस फॉर्मेट को नहीं पहचान पाया। कृपया वैसा ही फॉर्मेट भेजें जैसा स्क्रीनशॉट में है।")

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.infinity_polling()
