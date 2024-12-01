import asyncio, os, aiosqlite
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from importlib import import_module
from dotenv import load_dotenv

load_dotenv()

dp = Dispatcher()

async def start_bot():
    async with aiosqlite.connect("data.db") as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS users 
            (
                id INTEGER PRIMARY KEY, 
                email TEXT, 
                password TEXT,
                token TEXT
            )
            """
        )
        await db.commit()

    bot = Bot(
        token=os.getenv('TOKEN'), 
        parse_mode=ParseMode.MARKDOWN
    )
    
    for filename in os.listdir('modules'):
        if filename.endswith('.py'):
            router = import_module(f'modules.{filename[:-3]}').dp
            dp.include_router(router) 
    
    print('мя')
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

    await message.answer('Привет', reply_markup=keyboard.as_markup())

if __name__ == '__main__':
    asyncio.run(start_bot())


