""" Стартует всех пользователей """

from message.send_mess import send_mess
from parser.formation import creation
from parser.parser import run_main_parser
from utils.db_api.quick_commands import select_users_with_nonempty_machines, db_run_stop, get_user_data_for_pars
from loguru import logger


async def start_all_users():
    # получаем пользователей у которых есть автоматы и положительный баланс
    users = await select_users_with_nonempty_machines()
    users_data = []

    for user in users:
        try:
            users_data.append(await get_user_data_for_pars(user))
            await db_run_stop(user, True)
            await send_mess('автостарт', user)

        except Exception as e:
            logger.exception(f'Ошибка при автостарте: {e}')

    await run_main_parser(users_data)
