import asyncio
import datetime
import json
import platform

import aiohttp
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from loguru import logger

from data.config import admins
from message.send_mess import send_mess
from message.send_report_to_user import send_report_to_user
from utils.db_api.quick_commands import is_running, add_sales_to_database, sufficient_balance, db_run_stop

if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

logger.add("file.log", format="{time} {level} {message}", level="DEBUG", rotation="50 MB", compression="zip")

# Входные данные для авторизации
client_id = '95d753e0-39d1-4dfb-9886-8cda193d4aa9'
client_secret = 'sh1LBRJRqWjeoojiTzxl3XdKOfjyoqCMcuiZQNkU'

# URL для авторизации
auth_url = 'https://my.telemetron.net/api/token'


class User:
    """
    Класс, представляющий пользователя с его параметрами и методами.
    """

    def __init__(self, *args):
        """
        Инициализация пользователя.

        Args:
            *args: Переменное количество аргументов, переданных при создании экземпляра класса.

            user_id (int): ID пользователя.
            email (str): Имя пользователя.
            password (str): Пароль пользователя.
            numbers_machines (list): Список номеров машин.
            names_machines (list): Список названий машин.
            time_update (int): Интервал обновления данных в секундах.
            report_time (str): Время отправки отчета.
            send_users_id (int): Список пользователей для отправки сообщений
        """

        self.user_id, self.username, self.password, self.numbers_machines, self.names_machines, self.time_update, \
            self.report_time, self.send_users_id = args

        self.error_data = True
        self.last_data = None
        self.no_sales = False  # Флаг для отслеживания вывода информации об отсутствии продаж
        self.first_run = True  # Флаг для отслеживания первого запуска парсера
        self.machines_count = len(self.numbers_machines)  # Количество машин пользователя

    async def authorize(self, session):
        """
        Метод для выполнения запроса авторизации на сайте.

        Args:
            session (aiohttp.ClientSession): Сессия клиента aiohttp.

        Returns:
            str: Токен доступа пользователя.
        """
        auth_data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'password',
            'username': self.username,
            'password': self.password,
            'User-Agent': UserAgent().random
        }

        async with session.post(auth_url, data=auth_data) as response:
            if response.status == 200:
                data = await response.json()
                access_token = data.get('access_token')
                return access_token
            else:
                logger.error("Ошибка авторизации:", response.status)
                return None

    async def fetch_page(self, session, access_token, number_machine, name_machine):
        """
        Метод для выполнения GET-запроса на другую страницу сайта с использованием токена доступа.

        Args:
            session (aiohttp.ClientSession): Сессия клиента aiohttp.
            access_token (str): Токен доступа пользователя.
            number_machine (str): Номер машины.
            name_machine (str): Название машины.
        """

        page_url_2 = f"https://my.telemetron.net/api/vm/{number_machine}/timeline"

        headers = {
            'Authorization': f'Bearer {access_token}',
            # 'User-Agent': UserAgent().random
        }

        async with session.get(page_url_2, headers=headers) as response:
            if response.status == 200:
                page_content = await response.text()
                soup = BeautifulSoup(page_content, 'html.parser')
                await self.parse_data_string(str(soup), name_machine)

            else:
                logger.error("Ошибка при переходе на другую страницу:", response.status)
                # await send_mess(f'{name_machine}: не могу получить доступ к данным атомата, проверьте номер автомата',
                #                 self.send_users_id)
                return False

    async def parse_data_string(self, data_string, name_machine):
        """
        Метод для извлечения значений "name", "price" и "time" из строки с данными.

        Args:
            data_string (str): Строка с данными в формате JSON.
            name_machine (str): Название машины.
        """
        data = json.loads(data_string)
        result = []
        if data == {'data': []}:
            if not self.no_sales:
                await send_mess(f"#{name_machine}:Нет продаж", self.send_users_id)
                self.no_sales = True
        else:
            try:
                # self.no_sales = False  # Сбрасываем флаг
                for item in data['data']:
                    time = item['ts'].split(' ')
                    for product in item['payload']['products']:
                        name = product['name']
                        price = product['price']
                        result.append((name, price, time))

                # если первый проход парсера выгружаем за целый день
                if self.first_run:  # Добавлено условие для первого прохода парсера
                    today = datetime.date.today().strftime('%Y-%m-%d')
                    today_purchases = [item for item in result if item[2][0] == today]

                    for item in reversed(today_purchases):
                        name, price, time = item
                        result_string = f"#{name_machine}: \n<i>{time[1]}</i>  <u>{name}</u> <b>{price} ₽</b>"
                        result_bd = f"{name_machine}, {time[1]}, {name}, {price}"
                        await add_sales_to_database(self.user_id, result_bd)
                        # print(result_string)
                        await send_mess(result_string, self.send_users_id)

                    self.last_data = result[0][2][1]  # Сохраняем значение last_data
                    self.machines_count -= 1
                    if self.machines_count == 0:
                        self.first_run = False  # Устанавливаем флаг первого запуска в False

                else:
                    time = result[0][2][1]
                    date = result[0][2][0]
                    today = datetime.date.today().strftime('%Y-%m-%d')
                    # Если время соответствует сегодняшней дате
                    if date == today:
                        name = result[0][0]
                        price = result[0][1]
                        if time != self.last_data:
                            result_string = f"#{name_machine}: \n<i>{time}</i>  <u>{name}</u> " \
                                            f"<b>{price} ₽</b>"
                            result_bd = f"{name_machine}, {time}, {name}, {price}"
                            if await add_sales_to_database(self.user_id, result_bd):
                                await send_mess(result_string, self.send_users_id)
                                self.last_data = time

                # await send_mess('Тест', self.send_users_id)

            except IndexError:
                if self.error_data:
                    await send_mess(f"#{name_machine}: нет данных", self.send_users_id)
                    self.error_data = False


async def run_user(user, user_manager):
    """
    Метод для выполнения пользовательского процесса.

    Args:
        user (User): Пользователь для выполнения.
        user_manager (UserManager): Менеджер пользователей.
    """
    try:
        await send_mess(f'Запущено для {user.user_id}', admins)
        async with aiohttp.ClientSession() as session:
            access_token = await user.authorize(session)
            if access_token:
                while await is_running(user.user_id):
                    if await sufficient_balance(user.user_id):
                        for number_machine, name_machine in zip(user.numbers_machines, user.names_machines):
                            success = await user.fetch_page(session, access_token, number_machine, name_machine)
                            if not success:
                                access_token = await user.authorize(session)
                                if not access_token:
                                    logger.error("Не удалось выполнить повторную авторизацию")
                                    break
                        await send_report(user.send_users_id, user.report_time)  # отправка отчета пользователю
                        await asyncio.sleep(user.time_update)
                    else:
                        await send_mess('У вас недостаточно средств на счету!', user.send_users_id)
                        await db_run_stop(user.user_id, False)
                else:
                    await send_mess('Остановлено!', user.send_users_id)
                    # Удаление экземпляра пользователя из списка
                    user_manager.users.remove(user)

    except aiohttp.client_exceptions.ClientConnectorError:
        # Перезапустить сессию для этого пользователя
        await run_user(user, user_manager)
        await send_mess(f'Перезапуск сессии {user.user_id}', admins)
    except Exception as e:
        # Обработка исключений, которые могут возникнуть во время запроса
        logger.error(f"Ошибка подключения: {e}")
        await send_mess(f'Ошибка подключения {user.user_id}', admins)


async def send_report(users, report_time):
    """
    Метод для отправки отчета всем пользователям в заданное время.
    """
    current_time = datetime.datetime.now().strftime('%H:%M')

    if report_time == current_time:
        for user in users:
            # Отправка отчета пользователю
            await send_report_to_user(user)


class UserManager:
    """
    Класс, управляющий выполнением пользователей и асинхронным запуском.
    """

    def __init__(self):
        """
        Инициализация менеджера пользователей.
        """
        self.users = []

    def add_user(self, user):
        """
        Метод для добавления пользователя в список.

        Args:
            user (User): Пользователь для добавления.
        """
        self.users.append(user)

    async def run(self):
        """
        Метод для запуска выполнения всех пользователей.
        """
        tasks = [run_user(user, self) for user in self.users]
        await asyncio.gather(*tasks)


async def run_main_parser(users_data_main):
    user_manager = UserManager()

    for user_data in users_data_main:
        # Создание пользователей
        user = User(*user_data)

        # Добавление пользователей в менеджер
        user_manager.add_user(user)

    tasks = [
        user_manager.run()
    ]

    await asyncio.gather(*tasks)


if __name__ == '__main__':
    users_data = [
        (1086439015, 'golana127@mail.ru', 'dM1pbiSwi8', [40953, 42391], ['Тц_Светлый', 'Дагестан'], 60, "22:00",
         [1089138631, 5669831950]),
        (1089138631, 'remli.vasily@mail.ru', 'GI74ysHBxz', ['37227', '39121'], ['Карла_Маркса', 'Державинская'], 60,
         '13:00', [1089138631, 5669831950])
    ]

    run_main_parser(users_data)
