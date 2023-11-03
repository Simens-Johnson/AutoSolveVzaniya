import httpx, aiosqlite
from aiogram import types, Router
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from vznaniya.account import Account

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
        token = await Account().getToken(email, password)
        if token:
            async with aiosqlite.connect("data.db") as db:
                await db.execute("INSERT INTO users (id, email, password, token) VALUES (?, ?, ?, ?)", (message.from_user.id, email, password, token))
                await db.commit()
                
            keyboard = ReplyKeyboardBuilder()
            keyboard.button(text='Выбрать задания')
            await message.answer('*Успешно зарегал*', reply_markup=keyboard.as_markup())
        else:
            await message.answer('*Неверный логин или пароль*')
        await state.clear()

    except:
        await message.answer('*Похоже вы неправильно ввели форму*')
        await state.clear()
