from aiogram import types
from filters import IsPrivate, HasMachines
from loader import dp
from message.send_report_to_user import send_report_to_user, send_small_report_to_user


@dp.message_handler(HasMachines(), IsPrivate(), text="/report")
async def command_data(message: types.Message):  # создаем асинхронную функцию
    await send_report_to_user(message.from_user.id)


@dp.message_handler(HasMachines(), IsPrivate(), text="/small_report")
async def command_data(message: types.Message):  # создаем асинхронную функцию
    await send_small_report_to_user(message.from_user.id)


