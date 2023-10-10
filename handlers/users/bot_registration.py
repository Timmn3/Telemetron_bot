""" регистрация нового автомата """

import datetime
import re

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from data.config import admins
from filters import IsPrivate
from keyboards.default import cancel_registration, kb_run_stop, kb_restart
from loader import dp
from message.send_mess import send_mess
from parser.verification import main_authorize
from states import Registration
from utils.db_api.quick_commands import update_user, update_machines, get_user_email, get_tg_first_name, users_count


@dp.message_handler(text='Отменить регистрацию', state=[Registration.email, Registration.password,
                                                        Registration.number_machines, Registration.name_machines,
                                                        Registration.time_update, Registration.report_time])
async def cast(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('Регистрация отменена')


@dp.message_handler(IsPrivate(), Command('register'))
async def register(message: types.Message):
    email = await get_user_email(message.from_user.id)
    if email:
        await message.answer('Введите номер автомата (пример: 40953):', reply_markup=cancel_registration)
        await Registration.number_machines.set()
    else:
        await message.answer('Введите данные для доступа к сайту https://my.telemetron.net/\n'
                             'email:', reply_markup=cancel_registration)
        await Registration.email.set()


@dp.message_handler(text='Регистрация нового автомата')
async def register(message: types.Message):
    email = await get_user_email(message.from_user.id)
    if email:
        await message.answer('Введите номер автомата (пример: 40953):', reply_markup=cancel_registration)
        await Registration.number_machines.set()
    else:
        await message.answer('Введите данные для доступа к сайту https://my.telemetron.net/\n')
        await message.answer('email:', reply_markup=cancel_registration)
        await Registration.email.set()


@dp.message_handler(IsPrivate(), state=Registration.email)
async def get_email(message: types.Message, state: FSMContext):
    email = message.text
    if validate_email(email):  # Проверяем введенный email
        await state.update_data(email=email)

        await message.answer('пароль:', reply_markup=cancel_registration)
        await Registration.password.set()
    else:
        await message.answer('Некорректный email. Пожалуйста, повторите ввод email:',
                             reply_markup=cancel_registration)


def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None


@dp.message_handler(IsPrivate(), state=Registration.password)
async def get_password(message: types.Message, state: FSMContext):
    # Сохранение пароля в состояние
    await state.update_data(password=message.text)

    # Проверка пароля
    data = await state.get_data()
    email = data.get('email')
    password = data.get('password')

    if await main_authorize(email, password):
        await message.answer('Введите номер автомата (пример: 40953):',
                             reply_markup=cancel_registration)
        await Registration.number_machines.set()

    else:
        await message.answer('Неверный пароль. Пожалуйста, повторите ввод пароля:',
                             reply_markup=cancel_registration)


@dp.message_handler(IsPrivate(), state=Registration.number_machines)
async def get_number_machine(message: types.Message, state: FSMContext):
    number_machine = message.text
    if number_machine.isdigit():  # Проверяем, содержит ли номер автомата только цифры
        await state.update_data(number_machine=number_machine)

        await message.answer('Введите название автомата (или локацию) для уведомлений в telegram:',
                             reply_markup=cancel_registration)
        await Registration.name_machines.set()
    else:
        await message.answer('Некорректный номер автомата. Пожалуйста, введите только цифры:',
                             reply_markup=cancel_registration)


@dp.message_handler(IsPrivate(), state=Registration.name_machines)
async def get_time_update(message: types.Message, state: FSMContext):
    name_machine = message.text
    if not name_machine.strip():  # Проверяем, является ли название автомата пустым или состоящим только из пробелов
        await message.answer('Название автомата не может быть пустым. Пожалуйста, введите название автомата:',
                             reply_markup=cancel_registration)
        return

    # Сохранение времени обновления в состояние
    await state.update_data(name_machine=name_machine)

    email = await get_user_email(message.from_user.id)
    if email:
        # Получение всех данных из состояния
        user_data = await state.get_data()

        # Сохранение данных в базу данных
        await update_machines(
            user_id=message.from_user.id,
            number_machines=user_data['number_machine'],
            name_machines=user_data['name_machine']
        )

        # Сброс состояния
        await state.finish()

        await message.answer('Регистрация нового автомата успешно завершена!\n'
                             'Чтобы изменения вступили в силу, выполните restart',
                             reply_markup=kb_restart)
    else:
        await message.answer('Введите время отчета, (пример 22:00)',
                             reply_markup=cancel_registration)
        await Registration.report_time.set()


@dp.message_handler(IsPrivate(), state=Registration.report_time)
async def get_report_time(message: types.Message, state: FSMContext):
    report_time = message.text
    try:
        datetime.datetime.strptime(report_time, '%H:%M')  # Проверяем, соответствует ли время формату HH:MM
        await state.update_data(report_time=report_time)

        # Получение всех данных из состояния
        user_data = await state.get_data()

        # Сохранение данных в базу данных
        await update_user(
            user_id=message.from_user.id,
            email=user_data['email'],
            password=user_data['password'],
            number_machines=user_data['number_machine'],
            name_machines=user_data['name_machine'],
            report_time=user_data['report_time']
        )

        # Сброс состояния
        await state.finish()

        await message.answer('Регистрация успешно завершена! \n'
                             '<b>Для запуска бота, нажмите кнопку RUN</b>',
                             reply_markup=kb_run_stop)

        name = await get_tg_first_name(message.from_user.id)

        await send_mess(f'<b>Зарегистрирован новый пользователь: {name}\n'
                        f'Всего пользователей: {await users_count()}</b>', admins)

    except ValueError:
        await message.answer('Некорректный формат времени. Пожалуйста, введите время в формате HH:MM:',
                             reply_markup=cancel_registration)
