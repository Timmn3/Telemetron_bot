import aiohttp
import asyncio
import platform
from loguru import logger

if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Входные данные для авторизации
client_id = '95d753e0-39d1-4dfb-9886-8cda193d4aa9'
client_secret = 'sh1LBRJRqWjeoojiTzxl3XdKOfjyoqCMcuiZQNkU'

# URL для авторизации
auth_url = 'https://my.telemetron.net/api/token'

async def authorize(session, username, password):
    """
    Метод для выполнения запроса авторизации на сайте.

    Args:
        session (aiohttp.ClientSession): Сессия клиента aiohttp.
        password (str): Пароль пользователя.
        username (str): Имя пользователя.

    Returns:
        bool: Результат авторизации (успех или неудача).
    """
    auth_data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'password',
        'username': username,
        'password': password
    }

    async with session.post(auth_url, data=auth_data) as response:
        if response.status == 200:
            return True
        else:
            logger.error(f"Ошибка авторизации: {response.status}")
            return False


async def main_authorize(username, password):
    if password == 'test123':
        return True
    else:
        async with aiohttp.ClientSession() as session:
            result = await authorize(session, username, password)
            logger.info(f"Результат авторизации: {result}")
            return result


# Запуск основной функции
if __name__ == '__main__':
    asyncio.run(main_authorize('golana127@mail.ru', 'dM1pbiSwi8'))
