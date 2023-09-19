""" удаление автомата """
from aiogram.dispatcher import FSMContext
from filters import IsPrivate, HasMachines
from aiogram.dispatcher.filters import Command
from aiogram import types

from keyboards.default import kb_restart
from loader import dp
from states import Delete
from utils.db_api.quick_commands import get_user_number_machines, delete_machine
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


@dp.message_handler(text='Отменить', state=Delete.number_machines)
async def cancel_delete(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('Удаление автомата отменено.')


@dp.message_handler(HasMachines(), IsPrivate(), Command('delete_machine'))
async def delete_machine_menu(message: types.Message):
    number_machines = await get_user_number_machines(message.from_user.id)

    # Разделение строки на отдельные номера автоматов
    machines_list = number_machines.split(', ')

    # Генерация кнопок клавиатуры на основе списка автоматов
    keyboard_buttons = [KeyboardButton(text=machine) for machine in machines_list]
    keyboard_buttons.append(KeyboardButton(text='Отменить'))  # Добавление кнопки "Отменить"

    # Создание ReplyKeyboardMarkup с кнопками автоматов
    kb_machines = ReplyKeyboardMarkup(
        keyboard=[keyboard_buttons],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await message.answer('Выберите автомат, который хотите удалить:', reply_markup=kb_machines)
    await Delete.number_machines.set()


@dp.message_handler(IsPrivate(), state=Delete.number_machines)
async def confirm_delete_machine(message: types.Message, state: FSMContext):
    machine = message.text.strip()

    if machine == 'Отменить':
        await cancel_delete(message, state)
        return

    number_machines = await get_user_number_machines(message.from_user.id)
    machines_list = number_machines.split(', ')

    if machine not in machines_list:
        await message.answer('Неверно введено значение. Пожалуйста, выберите автомат для '
                             'удаления из предоставленных кнопок.')
        return

    await delete_machine(message.from_user.id, machine)

    await state.finish()
    await message.answer(f'Автомат "{machine}" успешно удален.\n'
                         f'Чтобы изменения вступили в силу, выполните restart',
                         reply_markup=kb_restart)
