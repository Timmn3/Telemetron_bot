# если первый проход парсера выгружаем за целый день
if self.first_run:  # Добавлено условие для первого прохода парсера
    today = datetime.date.today().strftime('%Y-%m-%d')
    today_purchases = [item for item in result if item[2][0] == today]

    for item in reversed(today_purchases):
        name, price, time = item
        result_string = f"#{name_machine}: \n<i>{time[1]}</i>  <u>{name}</u> <b>{price} ₽</b>"
        result_bd = f"{name_machine}, {time[1]}, {name}, {price}"
        await db_add_sales(self.user_id, result_bd)
        # print(result_string)
        await send_mess(result_string, self.send_users_id)

    self.last_data = result[0][2][1]  # Сохраняем значение last_data
    self.machines_count -= 1
    if self.machines_count == 0:
        self.first_run = False  # Устанавливаем флаг первого запуска в False