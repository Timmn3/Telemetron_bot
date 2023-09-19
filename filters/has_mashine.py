from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from utils.db_api.quick_commands import get_number_machines


class HasMachines(BoundFilter):
    async def check(self, message: types.Message):
        number_machines = await get_number_machines(message.from_user.id)
        if len(number_machines) > 0:
            return True
        else:
            await message.answer(f'Команда {message.text} будет доступна после регистрации автомата')
            return False