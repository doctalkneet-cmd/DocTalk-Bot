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

BOT_TOKEN = "8530224634:AAEAggfYdL1vekDXH3pkPu9xe2C1HZYncc0"
YOUR_USER_ID = 8010857405
bot = telebot.TeleBot(BOT_TOKEN)

def parse_mcq(text):
    # यह आपके स्क्रीनशॉट वाले फॉर्मेट (सवाल, 4 विकल्प, आंसर) को पहचानता है
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if len(lines) < 6: return None

    question = lines[0]
    options = [re.sub(r'^\(?[1-4A-Da-d][\.\)]?\s*', '', l).strip() for l in lines[1:5]]
    answer_line = lines[5]
    
    ans_match = re.search(r'([1-4A-Da-d])', answer_line)
    if not ans_match: return None
    
    correct_idx = (int(ans_match.group(1)) - 1) if ans_match.group(1).isdigit() else (ord(ans_match.group(1).upper()) - 65)
    return question, options, correct_idx

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    if message.from_user.id != YOUR_USER_ID: return
    
    result = parse_mcq(message.text)
    if result:
        question, options, correct_idx = result
        # यहाँ बॉट 'send_poll' का उपयोग करेगा ताकि एक असली क्विज़ बने
        bot.send_poll(
            chat_id=message.chat.id,
            question=question,
            options=options,
            type='quiz',
            correct_option_id=correct_idx,
            is_anonymous=False
        )
    else:
        bot.reply_to(message, "❌ क्विज़ नहीं बन पाई। कृपया फॉर्मेट चेक करें।")

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.infinity_polling()
