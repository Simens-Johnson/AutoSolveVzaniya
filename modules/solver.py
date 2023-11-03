import httpx, aiosqlite
from aiogram import types, Router
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from vznaniya.account import Account
from vznaniya.solver import LessonSolver

dp = Router()


@dp.message(lambda message: message.text == 'Выбрать задания') # создаем функцию которая проверяет сообщение на команду
async def solveTasks(message: types.Message):
    msg = await message.answer('Проверяю сессию')

    async with aiosqlite.connect("data.db") as db:
        async with db.cursor() as cur:
            token = await cur.execute("SELECT token FROM users WHERE id = ?", (message.from_user.id,))
            token = await token.fetchone()

            if not token:
                await msg.edit_text('Ваша сессия истекла, пропишите /start для повторной регистрации')
                await cur.execute("DELETE FROM users WHERE id = ?", (message.from_user.id,))
                await db.commit()
                return 
            
            token = token[0]
            async with httpx.AsyncClient() as r:
                if (await r.get('https://vznaniya.ru/api/v2/student-info', headers={'Authorization': f'Bearer {token}'})).status_code != 200:
                    await msg.edit_text('Ваша сессия истекла, пропишите /start для повторной регистрации')
                    await cur.execute("DELETE FROM users WHERE id = ?", (message.from_user.id,))
                    await db.commit()
                    return 
        
                
    buttons = InlineKeyboardBuilder()
    account = Account(token)
    for lesson in await account.getLessons():
        buttons.button(text=f'{lesson.name} | {lesson.expires.split()[0]}', callback_data=f'L{lesson.id}_{lesson.group_id}')
    buttons.adjust(1)

    await msg.edit_text(f'''
*Выберите задание для решения*
`Формат: название | когда истекает`
*Рекомендуется решать задания раз в 10-20 минут, чтобы у учителя не было подозрений.*                     
''')
    await msg.edit_reply_markup(reply_markup=buttons.as_markup())


@dp.callback_query(lambda x: x.data.startswith('L'))
async def solver_callback(callback_query: types.CallbackQuery):
    lesson_id, lesson_group_id = callback_query.data.replace('L', '').split('_')

    async with aiosqlite.connect("data.db") as db:
        async with db.cursor() as cur:
            token = await cur.execute("SELECT token FROM users WHERE id = ?", (callback_query.from_user.id,))
            token = (await token.fetchone())[0]
    solver = LessonSolver(lesson_id, lesson_group_id, token)
    await solver.solveTasks()
    await solver.solveTest()

    await callback_query.message.answer(f'Решил')