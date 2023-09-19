from parser.parser import run_main_parser
from utils.db_api.quick_commands import get_user_data_for_pars


async def creation(user_id):
    user_id, email, password, numbers_machines, names_machines, time_update, report_time, send_users_id = \
        await get_user_data_for_pars(user_id)

    users_data = [
        (user_id, email, password, numbers_machines, names_machines, time_update, report_time, send_users_id),
    ]

    await run_main_parser(users_data)


