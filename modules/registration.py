import httpx, aiosqlite
from aiogram import types, Router
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from vznaniya import signin

dp = Router()

class States(StatesGroup): 
    registration = State()


@dp.message(lambda message: message.text == 'Регистрация') # создаем функцию которая проверяет сообщение на команду
async def userRegistration(message: types.Message, state: FSMContext):
    await message.answer(
        """
*Введите данные в формате:*
    `Почта`
    `Пароль`
*ИЛИ*
    `Почта` `Пароль`
        """
    )
    await state.set_state(States.registration) 


@dp.message(States.registration)
async def getAccount(message: types.Message, state: FSMContext):

    try:
        email, password = message.text.split()
        token = signin.get_token(email, password)
        if token:
            async with aiosqlite.connect("mydatabase.db") as db:
                await db.execute("INSERT INTO users (id, email, password, token) VALUES (?, ?, ?, ?)", (message.from_user.id, email, password, token))
                await db.commit()
            await message.answer('*Успешно зарегал*')
        else:
            await message.answer('*Неверный логин или пароль*')
        await state.clear()

    except:
        await message.answer('*Похоже вы неправильно ввели форму*')
        await state.clear()
