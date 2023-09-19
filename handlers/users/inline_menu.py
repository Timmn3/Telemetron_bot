from aiogram import types
from aiogram.types import CallbackQuery

from keyboards.inline import ikb_menu, ikb_menu2
from loader import dp

@dp.message_handler(text="Инлайн меню")
async def show_inline_menu(message: types.Message):
    await message.answer('Инлайн кнопки ниже', reply_markup=ikb_menu)

@dp.callback_query_handler(text="Сообщение")
async def send_message(call: CallbackQuery):
    await call.message.answer('Кнопки заменены', reply_markup=ikb_menu)

@dp.callback_query_handler(text="alert")
async def send_message(call: CallbackQuery):
    await call.answer('Кнопки заменены', show_alert=True)  # show_alert=True окно с кнопкой ok

@dp.callback_query_handler(text="Кнопки 2")
async def send_message(call: CallbackQuery):
    await call.message.edit_reply_markup(ikb_menu2)

