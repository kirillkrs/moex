import telebot
from telebot import types
import logging

from __init__ import secrets  # Токен
from main import get_tick

import matplotlib.pyplot as plt
from io import BytesIO

logging.basicConfig(filename='logs/bot_handler.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

token = secrets.get('BOT_API_TOKEN')
bot = telebot.TeleBot(token)

states = {}


# кнопки бота, приветствие
@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    start_button = types.KeyboardButton("Старт")
    # help_button = types.KeyboardButton('Помощь')
    ticks_button = types.KeyboardButton("Акции")
    # valute_button = types.KeyboardButton("Валюта")

    markup.add(start_button, ticks_button)

    # приветсвие для команды /start
    bot.send_message(message.chat.id, text="Привет, {0.first_name}".format(message.from_user),
                     reply_markup=markup)


# хендлер для обработки нажатий кнопок
@bot.message_handler(content_types=['text'])
def buttons(message):
    logging.info(f"Received text message: '{message.text}' from user {message.chat.id}")

    if message.text == "Старт":
        bot.send_message(message.chat.id, text="Я могу предоставлять данные с мосбиржи по акциям")
    elif message.text == "Акции":
        bot.send_message(message.chat.id, text="Какая акция интересует?\n" +
                                               'Введи команду' +
                                               '\n' +
                                               'Пример:' +
                                               '/ticket MOEX 4 недели\n' +
                                               '\n' +
                                               'Все значения через пробел!!!!')
    # elif message.text == "Валюта":
    #     bot.send_message(message.chat.id, text="Какая валюта интересует?")


# Обработчик для команды /ticket
@bot.message_handler(commands=['ticket'])
def ticket_handler(message):
    logging.info(f"Received '/get_chart' command from user {message.chat.id}")

    try:
        _, tick, interval, interval_name = message.text.split()
        interval = int(interval)

        # Проверка корректности интервала
        if interval_name not in ['недели', 'дни'] or not 1 <= interval <= 6:
            raise ValueError("Некорректный интервал или количество интервалов")

       # Вызываем функцию get_tick для получения графика
        img = get_tick(tick=tick, interval_name=interval_name, interval=interval)
        img.seek(0)

        # Отправляем график пользователю
        bot.send_photo(message.chat.id, img)

        logging.info(f"Sent chart for '{tick}' to user {message.chat.id}")

    except (ValueError, IndexError) as ve:
        logging.error(f"Invalid input: {ve}")
        bot.reply_to(message, f"Некорректные данные: {ve}")
    except Exception as e:
        logging.error(f"Error processing '/ticket' command: {e}")
        bot.reply_to(message, f"Произошла ошибка: {e}")


# Обработчик для всех текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    chat_id = message.chat.id

    logging.info(f"Handler start received message: {message.text} from user {chat_id}")

    # Обработка состояний
    if chat_id in states:
        if states[chat_id] == "start":
            if message.text == "Акции":
                bot.send_message(chat_id,
                                 text="Введите название акции, интервал (дни/недели), и количество интервалов:")
                states[chat_id] = "Ожидайте"

        elif states[chat_id] == "Ожидайте":
            try:
                stock_info = message.text.split()
                tick, interval_name, interval = stock_info[0], stock_info[1], int(stock_info[2])

                get_tick(tick, interval_name, interval)
                img = BytesIO()
                plt.savefig(img, format='png')
                img.seek(0)
                
                bot.send_photo(chat_id, img)
                states[chat_id] = "start"  # Возвращаем пользователя в начальное состояние
            except Exception as e:
                bot.send_message(chat_id, f"Произошла ошибка: {e}")
                states[chat_id] = "start"  # Возвращаем пользователя в начальное состояние
    else:
        bot.send_message(chat_id, text="Для начала работы введите /start.")

    logging.info(f"End current state for user {chat_id}: {states.get(chat_id)}")


# бесконечное выполнение кода
bot.polling(none_stop=True, interval=0)
