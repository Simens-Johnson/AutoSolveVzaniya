import httpx
import aiosqlite
from aiogram import types, Router, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from vznaniya.account import Account
from vznaniya.solver import LessonSolver

dp = Router()

@dp.message(F.text == 'Выбрать задания')
async def solveTasks(message: types.Message):
    msg = await message.answer('Проверяю сессию')

    async with aiosqlite.connect("data.db") as db:
        cur = await db.execute("SELECT token FROM users WHERE id = ?", (message.from_user.id,))
        token = await cur.fetchone()
        if not token:
            await msg.edit_text('Ваша сессия истекла, пропишите /start для повторной регистрации')
            await db.execute("DELETE FROM users WHERE id = ?", (message.from_user.id,))
            await db.commit()
            return

        token = token[0]
        async with httpx.AsyncClient() as client:
            response = await client.get(
                'https://vznaniya.ru/api/v2/student-info',
                headers={'Authorization': f'Bearer {token}'}
            )
            if response.status_code != 200:
                await msg.edit_text('Ваша сессия истекла, пропишите /start для повторной регистрации')
                await db.execute("DELETE FROM users WHERE id = ?", (message.from_user.id,))
                await db.commit()
                return

    account = Account(token)
    lessons = await account.get_lessons()
    buttons = InlineKeyboardBuilder().row(
        *[types.InlineKeyboardButton(text=f'{lesson.name} | {lesson.expires.split()[0]}', callback_data=f'L{lesson.id}_{lesson.group_id}_{lesson.name}') for lesson in lessons],
        width=1
    )

    await msg.edit_text(
        '*Выберите задание для решения*\n'
        '`Формат: название | когда истекает`\n'
        '*Рекомендуется решать задания раз в 10-20 минут, чтобы у учителя не было подозрений.*',
        reply_markup=buttons.as_markup()
    )

@dp.callback_query(F.data.startswith('L'))
async def solver_callback(callback_query: types.CallbackQuery):
    await callback_query.answer('Начинаю решение задания...')
    lesson_id, lesson_group_id, lesson_name = callback_query.data[1:].split('_')
    async with aiosqlite.connect("data.db") as db:
        cur = await db.execute("SELECT token FROM users WHERE id = ?", (callback_query.from_user.id,))
        token = (await cur.fetchone())[0]
    solver = LessonSolver(lesson_id, lesson_group_id, token)
    await solver.solve_tasks()
    await solver.solve_test()

    message = callback_query.message
    keyboard = message.reply_markup.inline_keyboard
    keyboard = [
        [button for button in row if button.callback_data != callback_query.data]
        for row in keyboard
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=keyboard)
    await message.edit_reply_markup(reply_markup=keyboard)

    await callback_query.message.answer(f'Решено задание: {lesson_name}')