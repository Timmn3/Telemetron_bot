from aiogram import types
from loader import dp

@dp.message_handler(text="Привет") # создаем хэндлер, который ловит сообщение Привет
async def command_hello(message: types.Message): # создаем асинхронную функцию
    await message.answer(f'Привет {message.from_user.full_name}! \n') # отправляем сообщение пользователю
