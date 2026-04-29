from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.keyboard import ReplyKeyboardBuilder, KeyboardButton
import asyncio
import json
import time
from datetime import datetime
user_clocks = {}

try:
    with open("banned_users.json", "r", encoding="utf-8") as f:
        banned = json.load(f)
except FileNotFoundError:
    banned = {"banned": []}

class Feedback:
    def __init__(self, admin_id: int):
        self.router = Router()
        self.admin_id = admin_id

        self.user_router = Router()
        self.user_router.message.filter(F.chat.id != self.admin_id)
        self.user_router.message.register(self.to_admin, F.text | F.photo)

        self.admin_router = Router()
        self.admin_router.message.filter(F.chat.id == self.admin_id, F.reply_to_message)
        self.admin_router.message.register(self.reply_to, F.text | F.photo)

        self.router.include_router(self.admin_router)
        self.router.include_router(self.user_router)

    async def to_admin(self, message: types.Message):
        if message.from_user.id in banned["banned"]:
            await message.reply("you have been blocked. write to admin for unblock")
            return

        time_str = datetime.now().strftime("%H:%M:%S")
        info = (
            f"Время: {time_str}\n"
            f"Username: @{message.from_user.username or 'N/A'}\n"
            f"ID: {message.from_user.id}\n"
        )

        if message.text:
            text = f"{info}message:\n{message.text}"
            await message.bot.send_message(self.admin_id, text)
        elif message.photo:
            caption = f"{info}caption:\n{message.caption or ''}"
            await message.bot.send_photo(self.admin_id, message.photo[-1].file_id, caption=caption)

        await message.answer("сообщение отправлено")

    async def reply_to(self, message: types.Message):
        try:
            original = message.reply_to_message.caption or message.reply_to_message.text
            user_id = int(original.split("ID: ")[1].split("\n")[0])

            if message.text:
                await message.bot.send_message(user_id, message.text)
            elif message.photo:
                await message.bot.send_photo(user_id, message.photo[-1].file_id, caption=message.caption or "")

            await message.bot.send_message(self.admin_id, "ответ отправлен")
        except Exception as e:
            await message.answer(e)


class AdminLogic:
    def __init__(self, admin, bot):
        self.router = Router()
        self.admin_id = admin
        self.bot = bot

        self.router.message.filter(F.from_user.id == self.admin_id)
        self.router.message.register(self.ban_command, Command("ban"))
        self.router.message.register(self.unban_command, Command("unban"))


    async def ban_command(self, message: types.Message):
        try:
            user_id = int(message.text.split()[1])

            if user_id not in banned["banned"]:
                banned["banned"].append(user_id)
                with open("banned_users.json", "w") as b:
                    json.dump(banned, b)
                await self.bot.send_message(self.admin_id, f"{user_id} был забанен")
            else:
                await self.bot.send_message(self.admin_id, f"ошибка бана {user_id}")

        except Exception:
            await self.bot.send_message(self.admin_id, "/ban id")

    async def unban_command(self, message: types.Message):
        try:
            user_id = int(message.text.split()[1])
            if user_id in banned["banned"]:
                banned["banned"].remove(user_id)

                with open("banned_users.json", "w") as b:
                    json.dump(banned, b)

                await self.bot.send_message(self.admin_id, f"{user_id} был разбанен")
            else:
                await self.bot.send_message(self.admin_id, f"{user_id} не был забанен")

        except Exception:
            await self.bot.send_message(self.admin_id, "/unban id")

class BotLogic:
    def __init__(self, admin, bot):
        self.router = Router()
        self.admin = admin
        self.bot = bot


        self.router.message.register(self.start_command, Command("start"))
        self.router.message.register(self.me_command, Command("me"))
        self.router.message.register(self.ping_command, Command("ping"))

    async def start_command(self, message: types.Message):
        global user_clocks
        current_time = time.time()
        commandn = "start"

        user_data = user_clocks.get(message.from_user.id, {})
        last_time = user_data.get(commandn, 0)

        if current_time - last_time < 5:
            return

        user_data[commandn] = current_time
        user_clocks[message.from_user.id] = user_data
        builder = ReplyKeyboardBuilder()
        builder.add(KeyboardButton(text="/ping"))
        builder.add(KeyboardButton(text="/me"))
        builder.adjust(2)
        await message.answer("Привет. напиши сообщение или отправь фото, которое бы ты хотел передать\n\nкд на каждую команду - 5 секунд", reply_markup=builder.as_markup(resize_keyboard=True))

        await self.bot.send_message(self.admin, f"@{message.from_user.username} | <code>{message.from_user.id}</code>\ncommand: /start")

    async def ping_command(self, message: types.Message):
        global user_clocks
        current_time = time.time()
        commandn = "ping"

        user_data = user_clocks.get(message.from_user.id, {})
        last_time = user_data.get(commandn, 0)

        if current_time - last_time < 5:
            return

        user_data[commandn] = current_time
        user_clocks[message.from_user.id] = user_data
        await message.answer("True ✅")
        await self.bot.send_message(self.admin, f"@{message.from_user.username} | <code>{message.from_user.id}</code>\ncommand: /ping")

    async def me_command(self, message: types.Message):
        global user_clocks
        current_time = time.time()
        commandn = "me"

        user_data = user_clocks.get(message.from_user.id, {})
        last_time = user_data.get(commandn, 0)

        if current_time - last_time < 5:
            return

        user_data[commandn] = current_time
        user_clocks[message.from_user.id] = user_data
        import html
        name = html.escape(message.from_user.first_name)
        last_name = html.escape(message.from_user.last_name or "")

        await message.answer(
f"Имя: {name}\n"
f"Фамилия: {last_name}\n"
f"Username: @{message.from_user.username}\n"
f"ID: <code>{message.from_user.id}</code>\n"
f"<a href='tg://user?id={message.from_user.id}'>link</a>\n"
f"Язык: {message.from_user.language_code}")

        await self.bot.send_message(self.admin, f"@{message.from_user.username} | <code>{message.from_user.id}</code>\ncommand: /me")

class Core:
    def __init__(self, token: str, admin_id: int):
        self.bot = Bot(token=token, default=DefaultBotProperties(parse_mode="HTML"))
        self.admin_id = admin_id
        self.dp = Dispatcher()


        self.feedback = Feedback(self.admin_id)
        self.admlogic = AdminLogic(self.admin_id, self.bot)
        self.usrlogic = BotLogic(self.admin_id, self.bot)

        self.dp.include_router(self.usrlogic.router)
        self.dp.include_router(self.admlogic.router)
        self.dp.include_router(self.feedback.router)
        


    async def run(self):
        try:
            import logging
            logging.basicConfig(level=logging.INFO)
            await self.dp.start_polling(self.bot, skip_updates=False)
        finally:
            await self.bot.session.close()

if __name__ == '__main__':
    TOKEN = " " #your token
    ADMIN_ID = 123 # your account id

    core = Core(TOKEN, ADMIN_ID)
    try:
        asyncio.run(core.run())
    except KeyboardInterrupt:
        print("FALSE")
