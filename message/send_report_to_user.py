from message.send_mess import send_mess
from utils.db_api.quick_commands import get_sales
import datetime
from loguru import logger


async def send_report_to_user(user):
    try:
        # код для отправки отчета пользователю
        data = await get_sales(user)
        if data is None or data == '':
            await send_mess(f'Данных для отчета нет', user)
        else:
            report = await analyze_report(data)
            current_time = datetime.datetime.now().strftime('%H:%M')
            await send_mess(f'<u>Отчет по состоянию на {current_time}</u>:', user)
            total_cups = 0
            total_sum = 0
            for location, stats in report.items():
                count = stats['count']
                total_sum += stats['sum']
                total_cups += count
                await send_mess(f"#{location}: <i>{count} чашек, на сумму </i><b>{stats['sum']} ₽</b>", user)

            await send_mess(f"<u>#Всего_чашек:</u> {total_cups}\n<u>#Общая_сумма:</u> <b>{total_sum} ₽</b>", user)
    except AttributeError:
        logger.error('Ошибка send_report_to_user')


async def send_small_report_to_user(user):
    try:
        # код для отправки отчета пользователю
        data = await get_sales(user)
        if data is None or data == '':
            await send_mess(f'Данных для отчета нет', user)
        else:
            report = await analyze_report(data)
            report_messages = []
            total_cups = 0
            total_sum = 0
            for location, stats in report.items():
                count = stats['count']
                total_sum += stats['sum']
                total_cups += count
                report_messages.append(f"#{location}: <i>{count} ч. - </i><b>{stats['sum']} ₽</b>")
            report_messages.append(f"Итого: <b>{total_sum} ₽</b>")
            report_text = "\n".join(report_messages)
            await send_mess(report_text, user)
    except AttributeError:
        logger.error('Ошибка send_report_to_user')

async def analyze_report(data):
    try:
        lines = data.strip().split('\n')
        report = {}

        for line in lines:
            parts = line.split(',')
            location = parts[0].strip()
            amount = int(parts[-1].strip())

            if location in report:
                report[location]['count'] += 1
                report[location]['sum'] += amount
            else:
                report[location] = {'count': 1, 'sum': amount}

        return report
    except ValueError:
        logger.error('Нет данных для analyze_report')

