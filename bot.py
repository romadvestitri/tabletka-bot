import telebot
import time as t
from datetime import datetime, date, time
from apscheduler.schedulers.asyncio import AsyncIOScheduler

bot = telebot.TeleBot("5567018975:AAGv9lvTo8gnnv_Qsp86SfwCtZIzel4XbD8")


def check_schedule(
    schedule_list,
):  # Функция для проверки корректности введеного расписания
    # Принимает массив строк, созданный из сообщения пользователя
    # Возвращает True или False

    if not schedule_list[0].isdigit():
        return False
    try:
        for i in range(int(schedule_list[0])):
            if len(schedule_list[i + 4]) != 5:
                return False
            elif schedule_list[i + 4][2] != ":":
                return False
            elif schedule_list[i + 4][2] == ":":
                hours_min = schedule_list[i + 4].split(":")
                if not hours_min[0].isdigit():
                    return False
                elif not hours_min[1].isdigit():
                    return False
    except:
        return False
    return True


def get_time(schedule_list):  # Функция для получения времени для уведомлений
    # Принимает массив строк, созданный из сообщения пользователя
    # Возвращает массив строк со временем

    time_list = []
    for i in range(int(schedule_list[0])):
        time_list.append(schedule_list[i + 4])
    return time_list


@bot.message_handler(content_types=["text"])
def get_text_messages(message):  # Функция-обработчик входящих от пользователя сообщений
    # Принимает сообщение
    global file

    # Если сообщение - включить уведомления, то включаем уведомления и отправляем пользователю информацию о уведомлениях
    # О ошибках также сообщаем пользователю
    if message.text == "/notification":
        path = str(message.from_user.id) + ".txt"
        try:
            file = open(path, "r")
        except FileNotFoundError:
            bot.send_message(
                message.from_user.id,
                "Для начала необходимо зарегистрироваться. Напиши /reg",
            )
            return False

        i = 1
        timetable = {}
        for line in file:
            if i % 2 != 0:
                name = line
                timetable[line] = None
            else:
                timetable[name] = get_time(line.split())
            i += 1
        file.close()

        time_message = ""
        for item_key, item_value in timetable.items():
            for elem in item_value:
                time_message += elem + " "
            bot.send_message(
                message.from_user.id,
                f"Уведомления о {item_key} придут в {time_message}",
            )
            time_message = ""
        # Бесконечный цикл, в котором сравнивается текущее время и время, в которое нужно отправить уведомление
        # При совпадении - отправляем пользователю сообщение
        while True:
            now = datetime.now()
            current_time = now.strftime("%H:%M")
            for item_key, item_value in timetable.items():
                for elem in item_value:
                    if current_time == elem:
                        bot.send_message(
                            message.from_user.id, f"Пора выпить лекарство: {item_key}"
                        )
                        t.sleep(60)
    # Если сообщение - регистрация пользователя, то регистрируем пользователя: создается соответствующий файл,
    # перенаправляем пользователя на дальнейшую регистрацию
    # О ошибках также сообщаем пользователю
    if message.text == "/reg":

        path = str(message.from_user.id) + ".txt"
        try:
            file = open(path, "r")
            bot.send_message(message.from_user.id, "Ты уже зарегистрован")
        except FileNotFoundError:
            file = open(path, "w")
            bot.send_message(message.from_user.id, "Какое лекарство ты принимаешь?")
            bot.register_next_step_handler(message, tablets)

    if message.text == "/start":
        bot.send_message(message.from_user.id, "Для регистрации напиши /reg \n")
    # Если сообщение - добавить расписание , то открываем файл пользователя,
    # перенаправляем пользователя на дальнейшие шаги
    # О ошибках также сообщаем пользователю
    if message.text == "/add":
        path = str(message.from_user.id) + ".txt"
        try:
            file = open(path, "r")
            file.close()
            file = open(path, "a")
            bot.send_message(message.from_user.id, "Какое лекарство ты принимаешь?")
            bot.register_next_step_handler(message, tablets)
        except FileNotFoundError:
            bot.send_message(
                message.from_user.id,
                "Для начала необходимо зарегистрироваться. Напиши /reg",
            )

    # Если сообщение - вывести расписание , то открываем файл пользователя,
    # выводим всю информацию о расписании пользователя
    # О ошибках также сообщаем пользователю
    if message.text == "/schedule":
        path = str(message.from_user.id) + ".txt"
        try:
            file = open(path, "r")
            text_message = ""
            for line in file:
                text_message += line + "\n"
            bot.send_message(message.from_user.id, text_message)
        except FileNotFoundError:

            bot.send_message(message.from_user.id, "Какое лекарство ты принимаешь?")
            bot.register_next_step_handler(message, tablets)


def tablets(message):  # Функция дальнейшей регистрации/добавления расписания
    # Принимает сообщение от пользователя
    # Перенаправляет на следующий шаг

    global tablet
    tablet = message.text
    bot.send_message(
        message.from_user.id,
        f"Напиши как часто ты употребляешь {tablet}. Например 3 раза в день 15:00 16:00 17:00",
    )
    bot.register_next_step_handler(message, how_often_take)


def how_often_take(message):  # Функция дальнейшей регистрации/добавления расписания
    # Принимает сообщение от пользователя
    # Записывает данные в файл
    # О ошибках сообщаем пользователю

    global file
    timetable = message.text
    schedule_list = timetable.split()
    if check_schedule(schedule_list):
        bot.send_message(message.from_user.id, "Расписание успешно сохранено")
        file.write(tablet + "\n")
        file.write(timetable + "\n")
        file.close()
    else:
        bot.send_message(
            message.from_user.id,
            "Ошибка в расписании. Напиши какое лекарство ты принимаешь?",
        )
        bot.register_next_step_handler(message, tablets)


bot.polling(none_stop=True, interval=0)
