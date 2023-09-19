import datetime
import re

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from filters import IsPrivate, HasMachines
from keyboards.default import kb_user_data, cancel_change, kb_run_stop, kb_restart
from loader import dp
from parser.verification import main_authorize
from states import ChangeUserData
from utils.db_api.quick_commands import change_user_email, change_user_password, \
    change_user_report_time, change_user_other_users
from utils.db_api.quick_commands import get_user_email


@dp.message_handler(text='Отменить', state=[ChangeUserData.choice, ChangeUserData.new_value, ChangeUserData.email,
                                            ChangeUserData.password])
async def cast(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('Отменено')


@dp.message_handler(HasMachines(), IsPrivate(), Command('change_user'))
async def register(message: types.Message):
    await message.answer('Выберете параметры для изменения', reply_markup=kb_user_data)
    await ChangeUserData.choice.set()


# Функция изменения значения в зависимости от выбранной кнопки
async def change_data(user_id: int, selected_option: str, new_value: str):
    if selected_option == "email":
        await change_user_email(user_id, new_value)
    elif selected_option == "пароль":
        await change_user_password(user_id, new_value)
    elif selected_option == "время отчета":
        await change_user_report_time(user_id, new_value)
    elif selected_option == "добавить пользователя":
        await change_user_other_users(user_id, new_value)


@dp.message_handler(IsPrivate(), state=ChangeUserData.choice)
async def handle_selected_data(message: types.Message, state: FSMContext):
    selected_option = message.text

    # Сохранение выбранной опции в состоянии
    await state.update_data(selected_option=selected_option)

    if selected_option not in ["email", "пароль", "время отчета", "добавить пользователя"]:
        await cast(message, state)  # Вызов функции "Отменить"
        return

    if selected_option == "добавить пользователя":
        await message.answer(f'Введите id одного или нескольких пользователей через запятую (пример: 5089138631, '
                             f'3863110891). Обращаю внимание, что введенное значение заменит предыдущее, '
                             f'если Вы хотите добавить пользователей к существующим, то объедините все id '
                             f'в одну строку через запятую как в примере', reply_markup=cancel_change)
    else:
        await message.answer(f'Выбрана опция: {selected_option}. Введите новое значение для изменения.',
                             reply_markup=cancel_change)
    await ChangeUserData.next()


async def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None


@dp.message_handler(IsPrivate(), state=ChangeUserData.new_value)
async def handle_new_value(message: types.Message, state: FSMContext):
    new_value = message.text
    async with state.proxy() as data:
        selected_option = data.get("selected_option")

        if selected_option == "email" and not await validate_email(new_value):
            await message.answer("Некорректный email. Введите заново.", reply_markup=cancel_change)
            return

        if selected_option == "пароль":
            # Получаем email пользователя
            user_email = await get_user_email(message.from_user.id)
            # Проверяем авторизацию
            if not await main_authorize(user_email, new_value):
                await message.answer("Ошибка авторизации. Пароль не может быть изменен, "
                                     "введите пароль заново или нажмите отмена.", reply_markup=cancel_change)
                return

        if selected_option == "время отчета":
            try:
                datetime.datetime.strptime(new_value, '%H:%M')  # Проверяем, соответствует ли время формату HH:MM
            except ValueError:
                await message.answer("Некорректное время отчета. Введите время в формате HH:MM.",
                                     reply_markup=cancel_change)
                return

        user_id = message.from_user.id
        await change_data(user_id, selected_option, new_value)

    await message.answer(f'Значение успешно изменено. Опция: {selected_option}, Новое значение: {new_value}\n'
                         f'Чтобы изменения вступили в силу, выполните restart',
                         reply_markup=kb_restart)
    await state.finish()
