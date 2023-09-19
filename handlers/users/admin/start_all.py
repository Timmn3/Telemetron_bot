# Если команда /request
from filters.admins import Admins_message
from aiogram.dispatcher.filters import Command
from aiogram import types
from loader import dp
from parser.start_users import start_all_users
from data.config import admins

@dp.message_handler(text='/run', chat_id=admins)
async def run(message: types.Message):
    # запустить процесс для всех пользователей
    await start_all_users()

# @dp.message_handler(IsPrivate(), text='/mailing', chat_id=admins)
# async def start_mailing(message: types.Message):
#     await message.answer(f'Введите текст рассылки:')
#     await bot_mailing.text.set()