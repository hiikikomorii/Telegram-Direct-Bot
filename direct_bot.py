import telebot
from datetime import datetime
import json

TOKEN = " "
ADMIN_ID = 1234567890
bot = telebot.TeleBot(TOKEN)
try:
    with open("banned_users.json", "r", encoding="utf-8") as f:
        banned = json.load(f)

except FileNotFoundError:
    banned = {"banned": []}


@bot.message_handler(commands=['ban'], func=lambda m: m.chat.id == ADMIN_ID)
def ban_user(message):
    try:
        user_id = int(message.text.split()[1])

        if user_id not in banned["banned"]:
            banned["banned"].append(user_id)
            with open("banned_users.json", "w") as b:
                json.dump(banned, b)
            bot.send_message(ADMIN_ID, f"{user_id} был забанен")
        else:
            bot.send_message(ADMIN_ID, f"ошибка бана {user_id}")


    except Exception:
        bot.send_message(ADMIN_ID, "/ban id")

@bot.message_handler(commands=['unban'], func=lambda m: m.chat.id == ADMIN_ID)
def unban_user(message):
    try:
        user_id = int(message.text.split()[1])
        if user_id in banned["banned"]:
            banned["banned"].remove(user_id)

            with open("banned_users.json", "w") as b:
                json.dump(banned, b)

            bot.send_message(ADMIN_ID, f"{user_id} был разбанен")
        else:
            bot.send_message(ADMIN_ID, f"{user_id} не был забанен")


    except Exception:
        bot.send_message(ADMIN_ID, "/unban id")

@bot.message_handler(commands=['start'])
def start(message):
    user = message.from_user
    bot.send_message(message.chat.id, "Привет. напиши сообщение или отправь фото, которое бы вы хотели передать.\nОсновные команды: /ping | /me", parse_mode='HTML')
    bot.send_message(ADMIN_ID, f"@{user.username} |  <code>{user.id}</code>\nзапустил бота (/start)", parse_mode='HTML')


@bot.message_handler(commands=['ping'])
def ping(message):
    user = message.from_user
    bot.send_message(message.chat.id,"True ✅")
    bot.send_message(ADMIN_ID, f"@{user.username} | <code>{user.id}</code>\nиспользовал команду /ping", parse_mode='HTML')


@bot.message_handler(commands=['me'])
def me(message):
    user = message.from_user
    bot.send_message(
        message.chat.id,
        f"Имя: {user.first_name}\n"
        f"Фамилия: {user.last_name}\n"
        f"Username: @{user.username}\n"
        f"ID: <code>{user.id}</code>\n"
        f"Язык: {user.language_code}",
        parse_mode='HTML'
    )
    bot.send_message(ADMIN_ID, f"@{user.username} | <code>{user.id}</code>\nиспользовал команду /me", parse_mode='HTML')

@bot.message_handler(func=lambda message: message.chat.id != ADMIN_ID)
def forward_to_admin(message):
    time1 = datetime.now().strftime("%H:%M:%S")
    if message.from_user.id in banned["banned"]:
        bot.reply_to(message, f"you have been blocked. write to admin for unblock")
        return
    text = (
        f"Время: {time1}\n\n"
        f"Username: @{message.from_user.username}\n\n"
        f"ID: {message.from_user.id}\n"
        f"Сообщение:\n{message.text}"
    )

    bot.send_message(ADMIN_ID, text)
    bot.send_message(message.chat.id, "Сообщение отправлено")

@bot.message_handler(func=lambda m: m.chat.id != ADMIN_ID, content_types=['photo'])
def forward_photo_to_admin(message):
    time1 = datetime.now().strftime("%H:%M:%S")
    if message.from_user.id in banned["banned"]:
        bot.reply_to(message, f"you have been blocked. write to admin for unblock")
        return
    caption = message.caption if message.caption else ""
    text = (
        f"Время: {time1}\n\n"
        f"Username: @{message.from_user.username}\n"
        f"ID: {message.from_user.id}\n"
        f"Подпись:\n{caption}"
    )
    bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=text)
    bot.send_message(message.chat.id, "Сообщение отправлено ✓")

@bot.message_handler(func=lambda m: m.chat.id == ADMIN_ID and m.reply_to_message, content_types=['text'])
def reply_to_user_text(message):
    try:
        original = message.reply_to_message.caption or message.reply_to_message.text
        user_id = int(original.split("ID: ")[1].split("\n")[0])
        bot.send_message(user_id, message.text)
    except Exception as e:
        bot.send_message(ADMIN_ID, "Не удалось отправить сообщение")
        print(e)

@bot.message_handler(func=lambda m: m.chat.id == ADMIN_ID and m.reply_to_message, content_types=['photo'])
def reply_to_user_photo(message):
    try:
        original = message.reply_to_message.caption or message.reply_to_message.text
        user_id = int(original.split("ID: ")[1].split("\n")[0])
        caption = message.caption if message.caption else ""
        bot.send_photo(user_id, message.photo[-1].file_id, caption=caption)
    except Exception as e:
        bot.send_message(ADMIN_ID, "Не удалось отправить фото")
        print(e)


bot.infinity_polling()
