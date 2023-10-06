import os

from dotenv import load_dotenv

# запускаем функцию, которая загружает переменное окружение из файла .env
load_dotenv()

# Токен бота
BOT_TOKEN = str(os.getenv('BOT_TOKEN'))

# список администраторов бота
admins = [os.getenv('ADMINS')]

ip = os.getenv('IP')
PGUSER = str(os.getenv('PGUSER'))
PGPASSWORD = str(os.getenv('PGPASSWORD'))
DATABASE = str(os.getenv('DATABASE'))

POSTGRES_URI = f'postgresql://{PGUSER}:{PGPASSWORD}@{ip}/{DATABASE}'

QIWI_TOKEN = os.getenv('QIWI')
WALLET_QIWI = os.getenv('WALLET')
QIWI_PUB_KEY = os.getenv('QIWI_PUB_KEY')
QIWI_PRIV_KEY = os.getenv('QIWI_PRIV_KEY')
