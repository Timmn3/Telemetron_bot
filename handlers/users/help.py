from aiogram import types
from loader import dp

@dp.message_handler(text="/help")
async def command_help(message: types.Message):
    await message.answer(f'Возможно Вы найдете ответ в нашем чате: https://t.me/+oWpLo97sR-k3NTcy\n'
                         f'Или напишите мне: @Timmn3')
