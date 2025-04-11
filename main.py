import asyncio
import os

import aiosqlite
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from dotenv import load_dotenv

from modules import registration, solver

load_dotenv()

dp = Dispatcher()


async def check_dotenv():
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write('TOKEN=\n')
        print('Создайте файл .env и вставьте туда токен бота')
        exit()


async def start_bot():
    await check_dotenv()

    async with aiosqlite.connect("data.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                email TEXT,
                password TEXT,
                token TEXT
            )
        """)
        await db.commit()
    
    properties = DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    bot = Bot(token=os.getenv('TOKEN'), default=properties) 
    dp.include_routers(registration.dp, solver.dp)

    print('включен')
    await dp.start_polling(bot)


@dp.message(CommandStart())
async def start_command(message: types.Message):
    keyboard = ReplyKeyboardBuilder()
    async with aiosqlite.connect("data.db") as db:
        cursor = await db.execute("SELECT 1 FROM users WHERE id = ? LIMIT 1", (message.from_user.id,))
        if await cursor.fetchone():
            keyboard.button(text='Выбрать задания')
        else:
            keyboard.button(text='Регистрация')

    await message.answer('Привет', reply_markup=keyboard.as_markup(resize_keyboard=True))


if __name__ == '__main__':
    asyncio.run(start_bot())