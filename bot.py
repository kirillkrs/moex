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


# Кнопки бота
@bot.message_handler(commands=['start'])
def buttons(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    start_button = types.KeyboardButton('Старт')
    tick_button = types.KeyboardButton('Акции')

    markup.add(start_button, tick_button)

    bot.send_message(message.chat.id,
                     text='Привет, {0.first_name}'.format(message.from_user),
                     reply_markup=markup)


# Обработка нажатий кнопок
@bot.message_handler(content_types=['text'])
def buttons_messages(message):
    logging.info(f'Команда: {message.text} от пользователя {message.chat.id}')

    if message.text == 'Старт':
        bot.send_message(message.chat.id,
                         text='Я могу предоставить данные с московской биржи')
    elif message.text == 'Акции':
        bot.send_message(message.chat.id,
                         text='Какая акция интересует?\n' +
                              'Пример команды:\n' +
                              'MOEX 4 недели\n' +
                              '\n' +
                              'Все значения через пробелы')


# Обработчик команды /ticket
@bot.message_handler(commands=['ticket'])
def ticket_handler(message):
    logging.info(f'Обработка {message.text} с московской биржи от пользователя {message.chat.id}')

    try:
        _, tick, interval, interval_name = message.text.split()
        tick = tick.upper()
        interval = int(interval)
        interval_name = interval_name.lower()

        if interval_name not in ['недели', 'дни', 'неделя', 'день']:
            raise ValueError(f'Некорректный запрос {interval_name} от пользователя {message.chat.id}')

        img = get_tick(tick=tick, interval_name=interval_name, interval=interval)
        img.seek(0)

        bot.send_photo(message.chat.id, img)

        logging.info(f'Отправлен график для тикера {tick} пользователю {message.chat.id}')

    except (ValueError, IndexError) as ve:
        logging.error(f'Некорректный ввод {ve}')
        bot.reply_to(message,
                     text=f'Некорректные данные {ve}')

    except Exception as e:
        logging.error(f'Ошибка обработки /ticket {e}')
        bot.reply_to(message,
                     text=f'Прозошла ошибка {e}')


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id

    logging.info(f'Обработчик получает сообщение {message.text} от пользователя {chat_id}')

    if chat_id in states:
        if states[chat_id] == 'start':
            if message.text == 'Акции':
                bot.send_message(chat_id,
                                 text='Введите название акции, интервал (дни/недели) и количество дней/недель')
                states[chat_id] = 'Ожидайте'

        elif states[chat_id] == 'Ожидайте':
            try:
                stock_info = message.text.split()
                tick, interval, interval_name = stock_info[0].upper(), stock_info[1].lower(), int(stock_info[2])

                get_tick(tick=tick, interval_name=interval_name, interval=interval)
                img = BytesIO()
                plt.savefig(img, format='png')
                img.seek(0)

                bot.send_photo(chat_id, img)
                # Возвращение в начало
                states[chat_id] = 'start'

            except Exception as e:
                bot.send_message(chat_id,
                                 text=f'Произошла ошибка {e}')
                # Возвращаем в начало если ошибка
                states[chat_id] = 'start'

    else:
        bot.send_message(chat_id,
                         text=f'Для начала работы введите /start')

    logging.info(f'Конец текущего запроса от пользователя {chat_id}: {states.get(chat_id)}')


bot.polling(none_stop=True, interval=0)
