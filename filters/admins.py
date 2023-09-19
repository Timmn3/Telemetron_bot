from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from data.config import admins


class Admins_message(BoundFilter):  # проверка подписки
    async def check(self, message: types.Message):
        # id пользователя
        user = int(message.from_user.id)
        if user in admins:
            return True
        else:
            return False
