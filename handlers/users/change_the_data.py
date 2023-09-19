""" изменение данных автомата """
from aiogram.dispatcher import FSMContext
from filters import IsPrivate, HasMachines
from aiogram.dispatcher.filters import Command
from aiogram import types

from keyboards.default import kb_data, cancel_change, kb_run_stop, kb_restart
from loader import dp
from states import ChangeData
from utils.db_api.quick_commands import get_user_number_machines, change_user_number_machines, \
    change_user_name_machines
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


@dp.message_handler(text='Отменить', state=[ChangeData.number_machines, ChangeData.choice, ChangeData.new_value])
async def cancel_changes(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('Отменено')


@dp.message_handler(HasMachines(), IsPrivate(), Command('change_data'))
async def change_data(message: types.Message):
    number_machines = await get_user_number_machines(message.from_user.id)

    # Разделение строки на отдельные номера автоматов
    machines_list = number_machines.split(',')

    # Генерация кнопок клавиатуры на основе списка автоматов
    keyboard_buttons = [KeyboardButton(text=machine.strip()) for machine in machines_list]
    keyboard_buttons.append(KeyboardButton(text='Отменить'))  # Добавление кнопки "Отменить"

    # Создание ReplyKeyboardMarkup с кнопками автоматов
    kb_machines = ReplyKeyboardMarkup(
        keyboard=[keyboard_buttons],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await message.answer('Выберете автомат, данные которого хотите изменить:', reply_markup=kb_machines)
    await ChangeData.number_machines.set()


@dp.message_handler(IsPrivate(), state=ChangeData.number_machines)
async def select_data(message: types.Message, state: FSMContext):
    await state.update_data(number_machines=message.text)

    await message.answer('Выберете параметры для изменения', reply_markup=kb_data)
    await ChangeData.choice.set()


# Функция изменения значения в зависимости от выбранной кнопки
async def change_data_option(user_id: int, selected_option: str, number_machine: str, new_value: str):
    if selected_option == "номер автомата":
        await change_user_number_machines(user_id, number_machine, new_value)
    elif selected_option == "название (локация автомата)":
        await change_user_name_machines(user_id, number_machine, new_value)


@dp.message_handler(IsPrivate(), state=ChangeData.choice)
async def handle_selected_data(message: types.Message, state: FSMContext):
    selected_option = message.text

    # Сохранение выбранной опции в состоянии
    await state.update_data(selected_option=selected_option)

    if selected_option not in ["номер автомата", "название (локация автомата)"]:
        await cancel_changes(message, state)  # Вызов функции "Отменить"
        return

    await message.answer(f'Выбрана опция: {selected_option}. Введите новое значение для изменения.',
                         reply_markup=cancel_change)
    await ChangeData.next()


@dp.message_handler(IsPrivate(), state=ChangeData.new_value)
async def handle_new_value(message: types.Message, state: FSMContext):
    new_value = message.text
    user_data = await state.get_data()
    async with state.proxy() as data:
        selected_option = data.get("selected_option")

        user_id = message.from_user.id

        if selected_option == "номер автомата" or selected_option == "название (локация автомата)":
            await change_data_option(user_id, selected_option, user_data['number_machines'], new_value)

    await message.answer(f'Значение успешно изменено. Опция: {selected_option}, Новое значение: {new_value}\n'
                         f'Чтобы изменения вступили в силу, выполните restart',
                         reply_markup=kb_restart)
    await state.finish()
