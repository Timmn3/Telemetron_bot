from aiogram import types

from filters import IsPrivate
from filters.has_mashine import HasMachines
from loader import dp
from utils.db_api.quick_commands import get_user_data


@dp.message_handler(HasMachines(), IsPrivate(), text="/info", )
async def command_data(message: types.Message):
    data = await get_user_data(message.from_user.id)
    for key, value in data.items():
        if key != 'время обновления':
            await message.answer(f"{key}: {value}")
