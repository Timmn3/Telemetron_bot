from parser.restart_parser import restart_parser_for_all
from utils.db_api.quick_commands import delete_all_sales, balance_daily_write_off, reset_all_users_is_run
import aiocron


async def on_startup(dp):
    from loguru import logger
    logger.add("file.log", format="{time} {level} {message}", level="DEBUG", rotation="50 MB", compression="zip")

    import filters
    filters.setup(dp)
    import middlewares
    middlewares.setup(dp)

    from loader import db
    from utils.db_api.db_gino import on_startup
    # logger.info('Подключение к PostgreSQL')
    await on_startup(db)

    # print('Удаление базы данных')
    # await db.gino.drop_all()

    # logger.info('создание таблиц')
    await db.gino.create_all()
    # logger.info('Готово')

    # устанавливаем всем пользователям False в is_run в БД
    await reset_all_users_is_run()

    # импортирует функцию, которая отправляет сообщение о запуске бота всем администраторам
    from utils.notify_admins import on_startup_notufy
    await on_startup_notufy(dp)

    # импортирует функцию, которая устанавливает команды бота
    from utils.set_bot_commands import set_default_commands
    await set_default_commands(dp)

    # выдает в консоль бот запущен
    logger.info("Бот запущен")

    # Создаем задачу, которая будет выполняться каждый день в 00:00
    # очистка всех покупок
    aiocron.crontab('0 0 * * *', func=delete_all_sales, start=True)  # 15:43 '43 15 * * *',
    # снятие баланса
    aiocron.crontab('0 0 * * *', func=balance_daily_write_off, start=True)
    # перезапуск бота
    aiocron.crontab('1 0 * * *', func=restart_parser_for_all, start=True)  # в 00:01

if __name__ == '__main__':
    from aiogram import executor  # импортируем executor для запуска поллинга
    from handlers import dp  # из хендлеров импортируем dp

    executor.start_polling(dp, on_startup=on_startup)
