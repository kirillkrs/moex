import logging

import telebot
from telebot import types

from __init__ import secrets
from main import get_tick

token = secrets.get('BOT_API_TOKEN')
bot = telebot.TeleBot(token)

logging.basicConfig(level=logging.INFO)  # Настройка уровня логирования

while True:

    # Функция для отправки сообщения с клавиатуры
    def send_keyboard(message, text, keyboard):
        logging.info(f'Отправка сообщения: {text}')
        bot.send_message(message.chat.id, text, reply_markup=keyboard)


    # Функция для обработки команды /start
    @bot.message_handler(commands=['start'])
    def start_message(message):
        logging.info('Начало работы, активация команды /start')
        keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        button_info = types.KeyboardButton('Инфо')
        button_actions = types.KeyboardButton('Акции')
        # button_help = types.KeyboardButton('Помощь')
        # button_currency = types.KeyboardButton('Валюта')
        keyboard.add(button_info, button_actions)
        send_keyboard(message, f'Привет, {message.from_user.first_name}', keyboard)
        logging.info('Завершение обработки команды /start')


    # Функция для обработки кнопки 'ИНФО'
    @bot.message_handler(func=lambda message: message.text == 'Инфо')
    def handle_info(message):
        logging.info('Обработка кнопки Инфо')
        send_keyboard(message,
                      'Я помогу тебе получить данные по стоимости акций с московской биржи и отобразить изменение стоимости во времени',
                      None)
        logging.info('Завершение обработки кнопки Инфо')


    # Функция для обработки кнопки 'Акции'
    @bot.message_handler(func=lambda message: message.text == 'Акции')
    def handle_actions(message):
        logging.info('Handling Акции button')
        send_keyboard(message, 'Какая акция интересует?\nПример команды:\nMOEX 4 недели\n\nВсе значения через пробелы',
                      None)
        logging.info('Завершение обработки кнопки Акции')


    # # Функция для обработки кнопки 'Помощь'
    # @bot.message_handler(func=lambda message: message.text == 'Помощь')
    # def handle_actions(message):
    #     logging.info('Handling Помощь button')
    #     send_keyboard(message, 'Парам-па-рам',
    #                   None)
    #     logging.info('Завершение обработки кнопки Акции')


    # # Функция для обработки кнопки 'Акции'
    # @bot.message_handler(func=lambda message: message.text == 'Валюта')
    # def handle_actions(message):
    #     logging.info('Handling Валюта button')
    #     send_keyboard(message, 'Какая валюта интересует?\nПример команды:\n*** * *\n\nВсе значения через пробелы',
    #                   None)
    #     logging.info('Завершение обработки кнопки Валюта')


    # Функция для обработки текста от пользователя
    @bot.message_handler(func=lambda message: True)
    def handle_get_tick(message):
        logging.info('Инициализация обработки текстового сообщения')
        try:
            logging.info('Обработка сообщения пользователя')
            chat_id = message.chat.id
            text_info = message.text.split()

            if len(text_info) > 1:
                tick, interval, interval_name = str(text_info[0]).upper(), int(text_info[1]), str(text_info[2]).lower()

                logging.info(f'Запрос пользователя: тикер={tick}, интервал={interval}, дни/недели={interval_name}')
                img = get_tick(tick=tick, interval_name=interval_name, interval=interval)

                logging.info('Отправка сообщения пользователю')
                img.seek(0)
                bot.send_photo(chat_id, img)
                img.close()

            elif len(text_info) == 1:
                tick = text_info[0].upper()

                logging.info(f'Запрос пользователя: тикер={tick}, интервал и дни/недели по-умолчанию')
                img = get_tick(tick=tick)

                logging.info('Отправка сообщения пользователю')
                img.seek(0)
                bot.send_photo(chat_id, img)
                img.close()

            else:
                bot.send_message(chat_id, text='Неверный формат ввода. Убедитесь, что нет ошибки.')

            logging.info(f'Завершение запроса пользователя: тикер={tick}, интервал={interval}, дни/недели={interval_name}')
            logging.info('Запрос успешно обработан')
        except Exception as e:
            logging.error(f'Ошибка обработки запроса: {e}')


    if __name__ == "__main__":
        bot.polling(none_stop=True)
