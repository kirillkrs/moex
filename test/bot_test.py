import base64
from concurrent.futures import ThreadPoolExecutor

import telebot
from telebot import types
import logging

from __init__ import secrets  # Токен
from main_test import get_tick

import matplotlib.pyplot as plt
from io import BytesIO


token = secrets.get('BOT_API_TOKEN')
bot = telebot.TeleBot(token)


# Функция обработчика команды /start
# Запуск кнопок при запуске команды /start
@bot.message_handler(commands=['start'])
def start_message(message):
    # принт для отображения запуска в консоли для отладки функций
    print('00 запуск функции обработчика команды /start')

    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button_info = types.KeyboardButton('Инфо')
    button_actions = types.KeyboardButton('Акции')
    keyboard.add(button_info, button_actions)

    # Отправляем приветственное сообщение с клавиатурой пользователю
    bot.send_message(message.chat.id, 'Привет, {0.first_name}'.format(message.from_user),
                     reply_markup=keyboard)

    # принт для отображения окончания работы в консоли для отладки функций
    print('00 окночание функции обработчика команды /start' +
          '\n' +
          '=' * 5 +
          '\n')


# Обработчик кнопки 'ИНФО'
@bot.message_handler(func=lambda message: message.text == 'Инфо')
def handle_info(message):
    # принт для отображения запуска в консоли для отладки функций
    print('01 Запуск обработчика кнопки ИНФО')

    # Логика обработки нажатия кнопки 'Инфо'
    bot.send_message(message.chat.id,
                     text='Я помогу тебе получить данные по стоимости акций с московской биржи ' +
                          'и отобразить в виде графика')

    # принт для отображения окончания работы в консоли для отладки функций
    print('01 Окончание работы обработчика кнопки ИНФО' +
          '\n' +
          '=' * 5 +
          '\n')


# Обработчик кнопки 'Акции'
@bot.message_handler(func=lambda message: message.text == 'Акции')
def handle_actions(message):
    # принт для отображения запуска в консоли для отладки функций
    print('02 Запуск обработчика кнопки Акции')

    # Логика обработки нажатия кнопки 'Акции'
    bot.send_message(message.chat.id, text='Какая акция интересует?\n' +
                                           'Пример команды:\n' +
                                           'MOEX 4 недели\n' +
                                           '\n' +
                                           'Все значения через пробелы')

    # принт для отображения окончания работы в консоли для отладки функций
    print('02 Окончание работы обработчика кнопки Акции' +
          '\n' +
          '=' * 5 +
          '\n')


@bot.message_handler(func=lambda message: True)
def handle_get_tick(message):
    # принт для отображения запуска в консоли для отладки функций
    print('03 Запуск обработчика текста от пользователя')

    try:
        # принт для отображения запуска в консоли для отладки функций
        print('03_01 Запуск try внутри функции обработчика текста' +
              '\n' +
              '-' * 5 +
              '\n')

        chat_id = message.chat.id

        text_info = message.text.split()
        tick, interval, interval_name = text_info[0], text_info[1], text_info[2]
        tick = str(tick.upper())
        interval = int(interval)
        interval_name = str(interval_name.lower())

        # принт после разделения запроса пользователя
        print(
            f'03_02 Разделение запроса пользователя на тик {tick}, интервал {interval} и название интервала {interval_name}' +
            '\n' +
            '-' * 5 +
            '\n')

        # принт запуска функции построения графика
        print('03_03 Запуск функции обработки запроса пользователя и доступ к moex' +
              '\n' +
              '-' * 5 +
              '\n')

        # get_tick(tick=tick, interval_name=interval_name, interval=interval)
        img = get_tick(tick=tick, interval_name=interval_name, interval=interval)

        # принт после запуска фунции получения данных с биржи + построение графика
        print(f'03_04 Функция get_tick отработала с параметрами {tick, interval, interval_name}' +
              '\n' +
              '-' * 5 +
              '\n')

        # сохранение изображения в байтовый поток
        # img = BytesIO()
        # plt.savefig(img, format='png', bbox_inches='tight')
        img.seek(0)
        # img_png = img.getvalue()
        img.close()

        # graphic = base64.b64encode(img_png)
        # graphic = graphic.decode('utf-8')

        # отправка результата функции пользователю
        bot.send_photo(chat_id, img)
        # bot.send_photo(chat_id, graphic)

        # принт окончания выполнения обработчиика сообщения пользователя
        print(f'03 Функция get_tick завершила работу с параметрами {tick, interval, interval_name}' +
              '\n' +
              '=' * 5 +
              '\n')

    except Exception as e:
        # ошибка обработчика функции get_tick
        print(f'03 Ошибка обработчика функции get_tick {e}' +
              '\n' +
              '=' * 5 +
              '\n')


bot.polling(none_stop=True)
