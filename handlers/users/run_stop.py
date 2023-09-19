from filters import HasMachines
from loader import dp
from loguru import logger
from aiogram import types
import asyncio

from parser.formation import creation
from utils.db_api.quick_commands import db_run_stop, sufficient_balance, user_balance, get_number_machines, is_running


# пользователь нажал run
@dp.message_handler(HasMachines(), text="run")
async def run(message: types.Message):
    try:
        user = message.from_user.id
        # запускаем парсинг
        if not await is_running(user):
            if await sufficient_balance(user):
                await db_run_stop(user, True)
                await message.answer('работаю...')
                await creation(user)
            else:
                mashines = await get_number_machines(user)
                count = len(mashines.split(','))
                await message.answer(f"У вас недостаточно средств на счету\n"
                                     f"<i>Ваш баланс: {await user_balance(user)} ₽</i>\n"
                                     f"<b>для работы {count} автомата(ов), Ваш баланс должен составлять не менее "
                                     f"{count*5} ₽</b>")
        else:
            await message.answer(f"Бот уже запущен!")

    except Exception as e:
        logger.exception(f'Ошибка при обработке нажатия на кнопку "run": {e}')


# пользователь нажал stop
@dp.message_handler(HasMachines(), text="stop")
async def stop(message: types.Message):
    try:
        user = message.from_user.id
        if not await is_running(user):
            await message.answer('Бот остановлен')
        else:
            # останавливаем парсинг
            await db_run_stop(user, False)
            await message.answer('минуточку...')
    except Exception as e:
        logger.exception(f'Ошибка при обработке нажатия на кнопку "stop": {e}')


# пользователь нажал restart
@dp.message_handler(HasMachines(), text="restart")
async def restart(message: types.Message):
    try:
        user = message.from_user.id

        # останавливаем парсинг
        await db_run_stop(user, False)
        await message.answer('Ожидайте ответа: <b>"Бот успешно перезагружен"</b>, это займет менее 1 минуты...')
        await asyncio.sleep(60)

        # запускаем парсинг
        if await sufficient_balance(user):
            await db_run_stop(user, True)
            await message.answer('<b>Бот успешно перезагружен</b>')
            await creation(user)
        else:
            mashines = await get_number_machines(user)
            count = len(mashines.split(','))
            await message.answer(f"У вас недостаточно средств на счету\n"
                                 f"<i>Ваш баланс: {await user_balance(user)} ₽</i>\n"
                                 f"<b>для работы {count} автомата(ов), Ваш баланс должен составлять не менее "
                                 f"{count * 5} ₽</b>")
    except Exception as e:
        logger.exception(f'Ошибка при обработке нажатия на кнопку "restart": {e}')