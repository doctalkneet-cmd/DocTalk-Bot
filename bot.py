import os
import re
import telebot
import threading
from flask import Flask

# Flask server setup
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

# Bot configuration
BOT_TOKEN = "8530224634:AAEAggfYdL1vekDXH3pkPu9xe2C1HZYncc0"
YOUR_USER_ID = 8010857405
bot = telebot.TeleBot(BOT_TOKEN)

# यह फंक्शन हर सवाल को अलग-अलग पहचानेगा
def parse_and_send_quiz(chat_id, text):
    # सवालों को अलग करने के लिए स्प्लिट (मानते हुए कि एक सवाल और दूसरे के बीच खाली लाइन है)
    question_blocks = [b.strip() for b in text.split('\n\n') if b.strip()]
    
    for block in question_blocks:
        lines = [l.strip() for l in block.split('\n') if l.strip()]
        if len(lines) < 6: continue
        
        question = lines[0]
        options = [re.sub(r'^\(?[1-4A-Da-d][\.\)]?\s*', '', l).strip() for l in lines[1:5]]
        answer_line = lines[5]
        
        # आंसर ढूँढना (जैसे 1, A, (1), (A))
        ans_match = re.search(r'([1-4A-Da-d])', answer_line)
        if ans_match:
            val = ans_match.group(1).upper()
            correct_idx = (int(val) - 1) if val.isdigit() else (ord(val) - 65)
            
            # पोल भेजें
            bot.send_poll(chat_id, question, options, type='quiz', correct_option_id=correct_idx, is_anonymous=False)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.from_user.id == YOUR_USER_ID:
        bot.reply_to(message, "नमस्ते! मैं तैयार हूँ। अब अपने MCQs भेजें।")

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if message.from_user.id == YOUR_USER_ID:
        parse_and_send_quiz(message.chat.id, message.text)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.infinity_polling()

