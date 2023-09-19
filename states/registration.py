from aiogram.dispatcher.filters.state import StatesGroup, State


class Registration(StatesGroup):
    email = State()
    password = State()
    number_machines = State()
    name_machines = State()
    time_update = State()
    report_time = State()
    other_users = State()


class Accept(StatesGroup):
    user_id = State()
