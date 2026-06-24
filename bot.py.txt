import os
import re
import telebot

YOUR_USER_ID = 8010857405
BOT_TOKEN = "8530224634:AAEWpdn6AD3jrksLjx2DZJWwAGabyF3Gozs"

bot = telebot.TeleBot(BOT_TOKEN)

# 1. Number Format Check (1, 2, 3, 4) - Super Strong Regex
def parse_mcq(text):
    import re
    pattern_1234 = r"(?s)(?:\s*|\\\s*)\(1\)(.*?)\(2\)(.*?)\(3\)(.*?)\(4\)(?:\s*|\\\s*)(?:Answer|Ans)\s*:\s*([1-4])"
    match_1234 = re.search(pattern_1234, text, re.IGNORECASE)

    if match_1234:
        question = match_1234.group(1).strip()
        question = re.sub(r"^(?:Question:[Q:]\s*)", "", question, flags=re.IGNORECASE).strip()

        options = [
            match_1234.group(2).strip(),
            match_1234.group(3).strip(),
            match_1234.group(4).strip(),
            match_1234.group(5).strip(),
        ]
        correct_idx = int(match_1234.group(6).strip()) - 1
        return question, options, correct_idx

    # 2. Alphabet Format Check (A, B, C, D) - Super Strong Regex
    pattern_abcd = r"(?s)(?:\s*|\\\s*)\(A\)(.*?)\(B\)(.*?)\(C\)(.*?)\(D\)(?:\s*|\\\s*)(?:Answer|Ans)\s*:\s*([A-D])"
    match_abcd = re.search(pattern_abcd, text, re.IGNORECASE)

    if match_abcd:
        question = match_abcd.group(1).strip()
        question = re.sub(r"^(?:Question:[Q:]\s*)", "", question, flags=re.IGNORECASE).strip()

        options = [
            match_abcd.group(2).strip(),
            match_abcd.group(3).strip(),
            match_abcd.group(4).strip(),
            match_abcd.group(5).strip(),
        ]
        correct_idx = ord(match_abcd.group(6).upper()) - 65
        return question, options, correct_idx

    return None

@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    bot.reply_to(
        message,
        "Hello! Mujhe direct text format mein MCQ bhejiye, main use Quiz Poll mein badal dunga.\n\n"
        "Format:\nQuestion: Aapka sawaal?\n(1) Option 1\n(2) Option 2\n(3) Option 3\n(4) Option 4\nAnswer: 1",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    if message.from_user.id != YOUR_USER_ID:
        bot.reply_to(message, "Access Denied. यह बॉट प्राइवेट है।")
        return

    if message.text.startswith('/start'):
        return

    blocks = message.text.split('---')
    success_count = 0

    for block in blocks:
        block = block.strip()
        if not block:
            continue
        parsed = parse_mcq(block)

        if parsed:
            question, options, correct_idx = parsed
            is_long = any(len(opt) > 100 for opt in options) or len(question) > 300

            try:
                if is_long:
                    full_text = f"{question}\n(1) {options[0]}\n(2) {options[1]}\n(3) {options[2]}\n(4) {options[3]}"
                    bot.send_message(message.chat.id, full_text)
                    bot.send_poll(
                        chat_id=message.chat.id,
                        question="Upar diye gaye saaval ka sahi javaab chunein:",
                        options=["Option 1", "Option 2", "Option 3", "Option 4"],
                        type="quiz",
                        correct_option_id=correct_idx,
                        is_anonymous=True
                    )
                else:
                    bot.send_poll(
                        chat_id=message.chat.id,
                        question=question,
                        options=options,
                        type="quiz",
                        correct_option_id=correct_idx,
                        is_anonymous=True
                    )
                success_count += 1
            except Exception as e:
                bot.send_message(message.chat.id, f"Error poll banane mein: {e}")
        else:
            bot.send_message(message.chat.id, f"Yeh format samajh nahi aaya:\n\n{block[:50]}...")

    if success_count > 0:
        bot.send_message(message.chat.id, f"Badhai ho! {success_count} Quiz Polls successfully ban gaye.")

bot.infinity_polling()
