from aiogram import types
from aiogram.dispatcher.filters import CommandStart

from filters import IsPrivate
from keyboards.default import kb_register_machine
from loader import dp
from utils.db_api import quick_commands as commands
from utils.misc import rate_limit


@rate_limit(limit=3)
@dp.message_handler(IsPrivate(), CommandStart())  # создаем message, который ловит команду /start
async def command_start(message: types.Message):  # создаем асинхронную функцию
    try:
        user = await commands.select_user(message.from_user.id)
        if user.status == 'active':
            await message.answer(f'Привет {user.tg_first_name}\n'
                                 f'Ты уже зарегистрирован(а)!\n'
                                 # f'<b>Ты уже зарегистрирован(а)!</b>\n'  # жирный текст
                                 # f'<s>Ты уже зарегистрирован(а)</s>!\n'  # зачеркнутый
                                 # f'<i>Ты уже зарегистрирован(а)!</i>\n'  # курсивом
                                 # f'<code>Ты уже зарегистрирован(а)!</code>\n'  # текст "моно" (копируется)
                                 # f'<u>Ты уже зарегистрирован(а)!</u>\n'  # подчеркнутый текст
                                 , reply_markup=kb_register_machine)
    except Exception:
        await commands.add_user(user_id=message.from_user.id,
                                tg_first_name=message.from_user.first_name,
                                tg_last_name=message.from_user.last_name,
                                name=message.from_user.username,
                                email='',
                                password='',
                                number_machines='',
                                name_machines='',
                                sales='',
                                time_update=30,
                                report_time='',
                                other_users='',
                                status='active',
                                is_run=False,
                                balance=15,
                                bill_id='')

        await message.answer(f'Добро пожаловать, {message.from_user.first_name}!\n', reply_markup=kb_register_machine)


@rate_limit(limit=3)
@dp.message_handler(IsPrivate(), text="/my_id")  # создаем message, который ловит команду /id
async def get_unban(message: types.Message):  # создаем асинхронную функцию
    user = await commands.select_user(message.from_user.id)
    await message.answer(f'Ваш id - {user.user_id}')
