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
    print('00 /start commmand func')
    start_button = types.KeyboardButton('Старт')
    tick_button = types.KeyboardButton('Акции')
    markup.add(start_button, tick_button)

    bot.send_message(message.chat.id,
                     text='Привет, {0.first_name}'.format(message.from_user),
                     reply_markup=markup)
    print('00 end of /start command func' + '\n' + '=' * 5 + '\n')


# Обработка нажатий кнопок
@bot.message_handler(content_types=['text'])
def buttons_messages(message):
    logging.info(f'Команда: {message.text} от пользователя {message.chat.id}')
    if message.text == 'Старт' or message.text == 'Акции':

        print('01 Start buttons func')

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

        print('01 End buttons func')
        print('=' * 5 + '\n')


# Обработчик команды /ticket
@bot.message_handler(commands=['ticket'])
def ticket_handler(message):
    logging.info(f'Обработка {message.text} с московской биржи от пользователя {message.chat.id}')
    print('02 Start /ticket func')

    try:
        print('02 Getting values from message')
        _, tick, interval, interval_name = message.text.split()
        tick = tick.upper()
        interval = int(interval)
        interval_name = interval_name.lower()

        print('02 check correct interval_name')
        if interval_name not in ['недели', 'дни', 'неделя', 'день']:
            raise ValueError(f'Некорректный запрос {interval_name} от пользователя {message.chat.id}')

        print('02 save img to variable from get_tick func')
        img = get_tick(tick=tick, interval_name=interval_name, interval=interval)
        img.seek(0)

        print('02 send plot')
        bot.send_photo(message.chat.id, img)

        logging.info(f'Отправлен график для тикера {tick} пользователю {message.chat.id}')

    except (ValueError, IndexError) as ve:
        print(f'02 {ve}')
        logging.error(f'Некорректный ввод {ve}')
        bot.reply_to(message,
                     text=f'Некорректные данные {ve}')

    except Exception as e:
        print(f'02 {e}')
        logging.error(f'Ошибка обработки /ticket {e}')
        bot.reply_to(message,
                     text=f'Прозошла ошибка {e}')

    print('=' * 5 + '\n')


# Обработчик текстовых запросов без /ticket
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        chat_id = message.chat.id

        logging.info(f'Обработчик получает сообщение {message.text} от пользователя {chat_id}')
        print('03 start handler to get values from message')

        if chat_id in states:
            print('03 check tick in dict')
            if states[chat_id] == 'start':
                print('03 second if')
                if message.text == 'Акции':
                    bot.send_message(chat_id,
                                     text='Введите название акции, интервал (дни/недели) и количество дней/недель')
                    states[chat_id] = 'Ожидайте'

                    print('03 third if')
                    print('=' * 5 + '\n')

            elif states[chat_id] == 'Ожидайте':
                try:
                    print('03 get values from message and launch plotting func')
                    stock_info = message.text.split()
                    tick, interval, interval_name = stock_info[0].upper(), int(stock_info[1]), stock_info[2].lower()
                    print(f'03 getteble {tick}, {interval}, {interval_name}')

                    print('03 launch get_tick func')
                    get_tick(tick=tick, interval_name=interval_name, interval=interval)
                    img = BytesIO()
                    print('03 saving img')
                    # plt.savefig(img, format='png')
                    img.seek(0)

                    print('03 sending img')
                    bot.send_photo(chat_id, img)
                    # Возвращение в начало
                    states[chat_id] = 'start'

                    print('End of handler func')
                    print('=' * 5 + '\n')

                except Exception as e:
                    print(f'03 error hadler message {e}')
                    bot.send_message(chat_id,
                                     text=f'Произошла ошибка {e}')
                    # Возвращаем в начало если ошибка
                    states[chat_id] = 'start'

        else:
            print(f'04 tick in states')
            bot.send_message(chat_id,
                             text=f'Для начала работы введите /start')

        logging.info(f'Конец текущего запроса от пользователя {chat_id}: {states.get(chat_id)}')

    except Exception as e:
        print(f'Unhandled exception: {e}')




bot.polling(none_stop=True, interval=0)
