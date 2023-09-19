from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand('register', 'Регистрация нового автомата'),
        types.BotCommand('info', 'Посмотреть пользовательские данные'),
        types.BotCommand('report', 'Показать отчет'),
        types.BotCommand('small_report', 'Короткий отчет'),
        types.BotCommand('show_buttons', 'Показать кнопки RUN/STOP'),
        types.BotCommand('change_data', 'Изменить данные автомата'),
        types.BotCommand('change_user', 'Изменить данные пользователя'),
        types.BotCommand('delete_machine', 'Удалить автомат'),
        types.BotCommand('balance', 'Баланс'),
        types.BotCommand('start', 'Старт'),
        types.BotCommand('help', 'Помощь'),
        types.BotCommand('my_id', 'Узнать свой ID'),
    ])
