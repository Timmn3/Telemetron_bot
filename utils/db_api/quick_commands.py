from asyncpg import UniqueViolationError
from loguru import logger

from utils.db_api.db_gino import db
from utils.db_api.shemas.user_data import User_data


async def add_user(user_id: int, tg_first_name: str, tg_last_name: str, name: str, email: str, password: str,
                   number_machines: str, name_machines: str, sales: str, time_update: int, report_time: str,
                   other_users: str,
                   status: str, is_run: bool, balance: float, bill_id: str):
    try:
        user = User_data(user_id=user_id, tg_first_name=tg_first_name, tg_last_name=tg_last_name, name=name,
                         email=email, password=password, number_machines=number_machines, name_machines=name_machines,
                         sales=sales, time_update=time_update, report_time=report_time, other_users=other_users,
                         status=status, is_run=is_run, balance=balance, bill_id=bill_id)
        await user.create()
    except UniqueViolationError:
        logger.exception('Ошибка при добавлении пользователя')


async def count_users():
    try:
        count = await db.func.count(User_data.user_id).gino.scalar()
        return count
    except Exception as e:
        logger.exception(f'Ошибка при подсчете количества пользователей: {e}')


async def get_tg_first_name(user_id):
    try:
        user = await select_user(user_id)
        if user:
            return user.tg_first_name
        else:
            return None
    except Exception as e:
        logger.exception('Ошибка при получении tg_first_name пользователя')


async def select_users_with_nonempty_machines():
    users_with_nonempty_machines = []
    users = await User_data.query.gino.all()
    for user in users:
        if user.number_machines and user.balance > len(user.number_machines.split(',')) * 5:
            users_with_nonempty_machines.append(user.user_id)
    return users_with_nonempty_machines


async def get_users_with_sales():
    users_with_sales = []
    users = await User_data.query.gino.all()
    for user in users:
        sales = await get_sales(user.user_id)
        if sales:
            users_with_sales.append(user.user_id)
    return users_with_sales


async def find_machine_with_sales(user_id):
    machines_with_sales = []
    names_machines = await get_names_machines(user_id)
    if names_machines:
        machine_names = names_machines.split(', ')
        for machine_name in machine_names:
            sales = await get_sales(user_id)
            if sales and machine_name in sales:
                machines_with_sales.append(machine_name)
    return machines_with_sales


async def delete_all_sales():
    try:
        users = await User_data.query.gino.all()
        for user in users:
            await user.update(sales='').apply()
        return True
    except Exception as e:
        logger.exception('Ошибка при удалении данных по продажам')
        return False


async def select_user(user_id):
    try:
        user = await User_data.query.where(User_data.user_id == user_id).gino.first()
        return user
    except Exception as e:
        logger.exception('Ошибка при выборе пользователя')


async def get_sales(user_id):
    try:
        user = await select_user(user_id)
        if user:
            return user.sales
        else:
            return None
    except Exception as e:
        logger.exception('Ошибка при получении данных по продажам')


async def add_sales_to_database(user_id: int, new_string: str):
    """ функция добавления в БД продаж"""
    try:
        user = await select_user(user_id)
        sales = user.sales

        if sales:
            if new_string not in sales:
                sales += '\n' + new_string
                await user.update(sales=sales).apply()
                return True
            else:
                return False
        else:
            sales = new_string
            await user.update(sales=sales).apply()
            return True
    except Exception as e:
        logger.exception('Ошибка при добавлении продажи')


async def db_change_sales(user_id: int, new_data: dict):
    """Функция замены данных о продажах в БД"""
    try:
        user = await select_user(user_id)
        await user.update(sales=new_data).apply()
    except Exception as e:
        logger.exception('Ошибка при изменении данных о продажах')


async def db_get_sales(user_id: int):
    """ функция получения значения продаж из БД """
    try:
        user = await select_user(user_id)
        sales = user.sales
        return sales
    except Exception as e:
        logger.exception('Ошибка при изменении количества продаж')


async def db_clear_sales(user_id: int):
    """ функция очистки продаж в БД"""
    try:
        user = await select_user(user_id)
        await user.update(sales='').apply()
    except Exception as e:
        logger.exception('Ошибка при очистке количества продаж')


async def db_run_stop(user_id: int, value: bool):
    """ функция внесения в БД состояния работы парсинга"""
    try:
        user = await select_user(user_id)
        await user.update(is_run=value).apply()
    except Exception as e:
        logger.exception('Ошибка при изменении is_run пользователя')


async def reset_all_users_is_run():
    """ Устанавливаем всем пользователям False"""
    try:
        await User_data.update.values(is_run=False).gino.status()
    except Exception as e:
        logger.exception('Ошибка при сбросе поля is_run для всех пользователей')


async def is_running(user_id: int):
    """ Проверка состояния запущенного парсинга"""
    try:
        user = await select_user(user_id)
        if user:
            return user.is_run
        else:
            return None
    except Exception as e:
        logger.exception('Ошибка при получении состояния is_run пользователя')


async def delete_machine(user_id: int, machine_number: str):
    try:
        user = await select_user(user_id)
        number_machines = await get_number_machines(user_id)
        name_machines = await get_names_machines(user_id)

        number_machines_list = number_machines.split(', ')
        name_machines_list = name_machines.split(', ')

        if machine_number in number_machines_list:
            index = number_machines_list.index(machine_number)
            number_machines_list.pop(index)
            name_machines_list.pop(index)

            await user.update(
                number_machines=', '.join(number_machines_list),
                name_machines=', '.join(name_machines_list)
            ).apply()
    except Exception as e:
        logger.exception('Ошибка при удалении номера машины и названия машины')


async def update_machines(user_id: int, number_machines: str, name_machines: str):
    try:
        user = await select_user(user_id)
        machines = await get_number_machines(user_id)
        if machines:
            machines = machines + ', ' + number_machines
        else:
            machines = number_machines
        name = await get_names_machines(user_id)
        if name:
            name = name + ', ' + name_machines
        else:
            name = name_machines
        await user.update(
            number_machines=machines,
            name_machines=name,
        ).apply()
    except Exception as e:
        logger.exception('Ошибка при обновлении всех параметров пользователя')


async def get_user_data(user_id):
    try:
        user = await select_user(user_id)
        if user:
            return {
                'email': user.email,
                'password': user.password,
                'номера автоматов': user.number_machines,
                'названия автоматов': user.name_machines,
                'время обновления': user.time_update,
                'время отчета': user.report_time,
                'пользователи': user.other_users
            }
        else:
            return None
    except Exception as e:
        logger.exception('Ошибка при получении данных пользователя')


async def get_user_data_for_pars(user_id):
    try:
        user = await select_user(user_id)
        if user:
            number_machines = user.number_machines.split(', ')
            name_machines = user.name_machines.split(', ')
            other_users = [int(user.user_id)]
            if user.other_users:
                other_users.append(int(user.other_users))  # Добавить user.user_id в список other_users
            return (
                int(user.user_id),
                user.email,
                user.password,
                number_machines,
                name_machines,
                user.time_update,
                user.report_time,
                other_users
            )
        else:
            return None
    except Exception as e:
        logger.exception('Ошибка при получении данных пользователя')


async def get_number_machines(user_id):
    try:
        user = await select_user(user_id)
        if user:
            return user.number_machines
        else:
            return None
    except Exception as e:
        logger.exception('Ошибка при получении данных номеров автоматов')


async def get_names_machines(user_id):
    try:
        user = await select_user(user_id)
        if user:
            return user.name_machines
        else:
            return None
    except Exception as e:
        logger.exception('Ошибка при получении данных имен автоматов')


async def change_user_email(user_id: int, new_email: str):
    try:
        user = await select_user(user_id)
        await user.update(email=new_email).apply()
    except Exception as e:
        logger.exception('Ошибка при изменении email пользователя')


async def get_user_email(user_id: int):
    try:
        user = await select_user(user_id)
        if user is not None:
            return user.email
        else:
            return None
    except Exception as e:
        logger.exception('Ошибка при запросе email пользователя')


async def change_user_password(user_id: int, new_password: str):
    try:
        user = await select_user(user_id)
        await user.update(password=new_password).apply()
    except Exception as e:
        logger.exception('Ошибка при изменении пароля пользователя')


async def change_user_number_machines(user_id: int, old_machine, new_number_machines: str):
    try:
        user = await select_user(user_id)
        number_machines = await get_number_machines(user_id)
        number_machines_list = number_machines.split(', ')

        if old_machine in number_machines_list:
            index = number_machines_list.index(old_machine)
            number_machines_list[index] = new_number_machines

        new_number_machines = ', '.join(number_machines_list)
        await user.update(number_machines=new_number_machines).apply()
    except Exception as e:
        logger.exception('Ошибка при изменении номеров автоматов пользователя')


async def change_user_name_machines(user_id: int, number_machine, new_name_machines: str):
    try:
        user = await select_user(user_id)
        number_machines = await get_number_machines(user_id)
        name_machines = await get_names_machines(user_id)

        number_machines_list = number_machines.split(', ')
        name_machines_list = name_machines.split(', ')

        if number_machine in number_machines_list:
            index = number_machines_list.index(number_machine)
            name_machines_list[index] = new_name_machines

            await user.update(
                name_machines=', '.join(name_machines_list)
            ).apply()
    except Exception as e:
        logger.exception('Ошибка при изменении названий автоматов пользователя')


async def change_user_report_time(user_id: int, new_report_time: str):
    try:
        user = await select_user(user_id)
        await user.update(report_time=new_report_time).apply()
    except Exception as e:
        logger.exception('Ошибка при изменении времени отчета пользователя')


async def change_user_other_users(user_id: int, new_other_users: str):
    try:
        user = await select_user(user_id)
        await user.update(other_users=new_other_users).apply()
    except Exception as e:
        logger.exception('Ошибка при изменении других пользователей пользователя')


async def get_user_number_machines(user_id):
    try:
        user = await select_user(user_id)
        if user:
            return user.number_machines
        else:
            return None
    except Exception as e:
        logger.exception('Ошибка при получении number_machines пользователя')


async def update_user(user_id: int, email: str, password: str, number_machines: str, name_machines: str,
                      report_time: str):
    try:
        user = await select_user(user_id)
        await user.update(
            email=email,
            password=password,
            number_machines=number_machines,
            name_machines=name_machines,
            report_time=report_time
        ).apply()
    except Exception as e:
        logger.exception('Ошибка при обновлении всех параметров пользователя')


async def select_all_users():
    try:
        users = await User_data.query.gino.all()
        return users
    except Exception as e:
        logger.exception('Ошибка при выборе всех пользователей')


async def count_users():
    try:
        count = await db.func.count(User_data.user_id).gino.scalar()
        return count
    except Exception as e:
        logger.exception('Ошибка при подсчете количества пользователей')


async def update_status(user_id, status):
    try:
        user = await select_user(user_id)
        await user.update(status=status).apply()
    except Exception as e:
        logger.exception('Ошибка при обновлении статуса пользователя')


async def check_args(args, user_id: int):
    try:
        if args == '':
            args = '0'
            return args
        elif not args.isnumeric():
            args = '0'
            return args
        elif args.isnumeric():
            if int(args) == user_id:
                args = '0'
                return args
            elif await select_user(user_id=int(args)) is None:
                args = '0'
                return args
            else:
                args = str(args)
                return args
        else:
            args = '0'
            return args
    except Exception as e:
        logger.exception('Ошибка при проверке аргументов')


async def balance_daily_write_off():
    """ Ежедневное списание остатка """
    try:
        users = await User_data.query.gino.all()
        for user in users:
            number_machines = user.number_machines
            balance = user.balance

            if number_machines and balance >= 5:
                machines_count = len(number_machines.split(','))  # Считаем количество машин через запятую
                machines_sum = machines_count * 5

                balance -= machines_sum
                balance = max(balance, 0)
                await user.update(balance=balance).apply()

        return True

    except Exception as e:
        logger.exception('Ошибка при обновлении баланса пользователей')
        return False


async def change_balance(user_id: int, amount):
    try:
        user = await select_user(user_id)
        new_balance = float(user.balance) + float(amount)
        await user.update(balance=new_balance).apply()
    except Exception as e:
        logger.exception('Ошибка при изменении баланса пользователя')


async def check_balance(user_id: int, amount):
    try:
        user = await select_user(user_id=user_id)
        try:
            amount = float(amount)
            if user.balance + amount >= 0:
                await change_balance(user_id, amount)
                return True
            elif user.balance + amount < 0:
                return 'no maney'
        except Exception as e:
            logger.exception(e)
            return False
    except Exception as e:
        logger.exception('Ошибка при проверке баланса')


async def user_balance(user_id: int):  # какой баланс у пользователя
    user = await select_user(user_id)  # получаем юзера
    try:
        return user.balance
    except Exception as e:
        return False


async def user_bill_id(user_id: int):  # получаем идентификатор заказа
    user = await select_user(user_id)  # получаем юзера
    return user.bill_id


async def change_bill_id(user_id: int, value):  # измененяем идентификатор заказа
    user = await select_user(user_id)
    new_bill_id = value
    await user.update(bill_id=new_bill_id).apply()


async def clear_bill_id(user_id: int):  # очищаем идентификатор заказа
    user = await select_user(user_id)
    await user.update(bill_id='').apply()


# выбрать всех пользователей с необходимым балансом
async def select_all_users_big_balance():
    users = await User_data.select('user_id').where(User_data.balance > 4).gino.all()
    return users


# выбрать всех пользователей с балансом меньше 15 рублей
async def select_all_users_balance_lower():
    users = await User_data.select('user_id').where(User_data.balance < 15).gino.all()
    return users


async def sufficient_balance(user_id: int) -> bool:
    try:
        user = await select_user(user_id)
        number_machines = user.number_machines
        balance = user.balance

        if balance >= len(number_machines.split(',')) * 5:
            return True
        else:
            return False
    except Exception as e:
        logger.exception('Ошибка при проверке достаточности баланса')
        return False
