import asyncio
import aiohttp
from bs4 import BeautifulSoup
import json
from bot.send import send_mess

from loguru import logger
import platform
from fake_useragent import UserAgent
import datetime

from data.config import USERNAME, PASSWORD, USERNAME_2, PASSWORD_2

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

    def __init__(self, user_id, email, password, number_machine, name_machine, time_update, report_time):
        """
        Инициализация пользователя.

        Args:
            user_id (int): ID пользователя.
            email (str): Имя пользователя.
            password (str): Пароль пользователя.
            number_machine (str): Номер машины.
            name_machine (str): Название машины.
            time_update (int): Интервал обновления данных в секундах.
        """
        self.error_data = True
        self.last_data = None
        self.user_id = user_id
        self.username = email
        self.password = password
        self.number_machine = number_machine
        self.name_machine = name_machine
        self.time_update = time_update
        self.report_time = report_time

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
            'password': self.password
        }

        async with session.post(auth_url, data=auth_data) as response:
            if response.status == 200:
                data = await response.json()
                access_token = data.get('access_token')
                return access_token
            else:
                print("Ошибка авторизации:", response.status)
                return None

    async def fetch_page(self, session, access_token):
        """
        Метод для выполнения GET-запроса на другую страницу сайта с использованием токена доступа.

        Args:
            session (aiohttp.ClientSession): Сессия клиента aiohttp.
            access_token (str): Токен доступа пользователя.
        """
        page_url_2 = f"https://my.telemetron.net/api/vm/{self.number_machine}/timeline"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'User-Agent': UserAgent().random
        }

        async with session.get(page_url_2, headers=headers) as response:
            if response.status == 200:
                page_content = await response.text()
                soup = BeautifulSoup(page_content, 'html.parser')
                self.parse_data_string(str(soup))

            else:
                logger.error("Ошибка при переходе на другую страницу:", response.status)
                send_mess(f'{self.name_machine}: не могу получить доступ к данным атомата, проверьте номер автомата',
                          self.user_id)
                return False

    def parse_data_string(self, data_string):
        """
        Метод для извлечения значений "name", "price" и "time" из строки с данными.

        Args:
            data_string (str): Строка с данными в формате JSON.
        """
        data = json.loads(data_string)
        result = []
        try:
            for item in data['data']:
                time = item['ts'].split(' ')[1]
                for product in item['payload']['products']:
                    name = product['name']
                    price = product['price']
                    result.append((name, price, time))

            last_data = result[0][2]
            if last_data != self.last_data:  # проверка
                result_string = f"#{self.name_machine}: \n{last_data}  {result[0][0]} {result[0][1]} ₽"
                print(result_string)
                send_mess(result_string, self.user_id)
                self.last_data = last_data  # Сохраняем значение last_data

        except IndexError:
            if self.error_data:
                send_mess(f"#{self.name_machine}: нет данных", self.user_id)
                self.error_data = False


def send_report_to_user(user):
    # Ваш код для отправки отчета пользователю
    send_mess('report', user.user_id)
    print(f'Report for {user.user_id}')


async def run_user(user):
    """
    Метод для выполнения пользовательского процесса.

    Args:
        user (User): Пользователь для выполнения.
    """
    async with aiohttp.ClientSession() as session:
        access_token = await user.authorize(session)
        if access_token:
            while True:
                success = await user.fetch_page(session, access_token)
                if not success:
                    access_token = await user.authorize(session)
                    if not access_token:
                        logger.error("Не удалось выполнить повторную авторизацию")
                        break
                await asyncio.sleep(user.time_update)


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
        tasks = [run_user(user) for user in self.users]
        await asyncio.gather(*tasks)

    async def send_report(self):
        """
        Метод для отправки отчета всем пользователям в заданное время.
        """
        while True:
            current_time = datetime.datetime.now().strftime('%H:%M')

            for user in self.users:
                if user.report_time == current_time:
                    # Отправка отчета пользователю
                    send_report_to_user(user)

            await asyncio.sleep(60)  # Проверяем каждую минуту


async def main_parser():
    user_manager = UserManager()

    # Создание пользователей
    user1 = User(1089138631, USERNAME, PASSWORD, '40953', "ТЦ_Светлый", 20, "21:26")
    user2 = User(1089138631, USERNAME, PASSWORD, '42391', "Дагестан", 20, "13:30")
    user3 = User(1089138631, USERNAME_2, PASSWORD_2, '37227', "Карла_Маркса", 20, "15:45")
    user4 = User(1089138631, USERNAME_2, PASSWORD_2, '39121', "Державинская", 20, "17:00")

    # Добавление пользователей в менеджер
    user_manager.add_user(user1)
    user_manager.add_user(user2)
    user_manager.add_user(user3)
    user_manager.add_user(user4)

    tasks = [
        user_manager.run(),
        user_manager.send_report()
    ]

    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main_parser())
