from io import BytesIO
import requests

import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates


def get_tick(
        tick: str,
        interval_name: str = 'недели',
        interval: int = 6,
):
    """
    :param tick: Наименование акций
    :param interval_name: Желаемый интервал (Дни / недели)
    :param interval: Количество дней / недель
    :return: Возвращает графики
    """

    try:
        # Списки для проверки интревалов
        weeks_list = ['недели', 'неделя', 'недель']
        days_list = ['дни', 'дней', 'дня']

        # Проверка вхождения в списки и выбор необходимых значений интервалов
        if interval_name.lower() in weeks_list:
            date_start = timedelta(weeks=interval)  # From what
        elif interval_name.lower() in days_list:
            date_start = timedelta(days=interval)
        else:
            date_start = timedelta(weeks=6)

        # Вычисление даты заданного периода по настоящее время
        date_end = datetime.now()  # Date now
        date_start_frame = date_end - date_start  # Starting interval data
        date_end = date_end.strftime('%Y-%m-%d')  # Data format
        date_start_frame = date_start_frame.strftime('%Y-%m-%d')
        date_format = mdates.DateFormatter('%d.%m.%Y')

        if tick:
            # Осуществить запрос по API MOEX для получения данных стоимость акций
            ticket = requests.get(
                f'http://iss.moex.com/iss/engines/stock/markets/shares/securities/{tick}/candles.json?from={date_start_frame}&till={date_end}&interval=60')
            ticket_dict = ticket.json()

            # Преобразовать в df
            data = pd.DataFrame(
                [{k: r[i] for i, k in enumerate(ticket_dict['candles']['columns'])} for r in
                 ticket_dict['candles']['data']])

            # Вычисления по df. Среднее +/- SD, SMA
            data['begin'] = pd.to_datetime(data['begin'])  # Convert 'begin' column to datetime format
            data['mean_cost'] = data[['high', 'low']].mean(axis=1)
            data['sd_cost'] = data[['high', 'low']].std(axis=1)

            data['SMA7'] = data['mean_cost'].rolling(window=7).mean()
            data['SMA21'] = data['mean_cost'].rolling(window=21).mean()
            data['SMA56'] = data['mean_cost'].rolling(window=56).mean()

            # Инициализация объекта графика
            plt.figure(figsize=(15, 5))

            # Отрисовка базового графика
            ax = sns.lineplot(data=data, x='begin', y='mean_cost', color='#0066FF', alpha=0.7, lw=2.5, label='Mean')
            ax.fill_between(data['begin'], data['mean_cost'] - data['sd_cost'], data['mean_cost'] + data['sd_cost'],
                            color='#99CCFF', alpha=0.5, label='SD')
            sns.scatterplot(data=data, x='begin', y='close', s=45, color='#6699FF', alpha=0.7, label='Close')

            # Отрисовка данных SMA
            sns.lineplot(data=data, x='begin', y='SMA7', color='#FF6600', label=f'SMA 7 дней', alpha=0.65, lw=2)
            sns.lineplot(data=data, x='begin', y='SMA21', color='#CC0033', label=f'SMA 21 день', alpha=0.65, lw=2)
            sns.lineplot(data=data, x='begin', y='SMA56', color='#00CC33', label=f'SMA 56 день', alpha=0.65, lw=2)

            # ХЗ как обозвать
            ax.xaxis.set_major_formatter(date_format)
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
            plt.xticks(rotation=45, fontsize=12, fontweight='bold')

            # Добавить значения последней цены закрытия за заданный период
            plt.text(x=data['begin'].iloc[-60], y=min(data['close']) - min(data['close']) * 0.01,
                     s=f'Последняя цена закрытия:\n{tick} = {data["close"].iloc[-1]}',
                     fontstyle='italic')

            # Добавить значения начальной цены закрытия за заданный период
            plt.text(x=data['begin'].iloc[0], y=min(data['close']) - min(data['close']) * 0.01,
                     s=f'Цена на начало интервала:\n{tick} = {data["close"].iloc[0]}',
                     fontstyle='italic')

            # Вычисление разницы начальной и конечной цены интервала в %
            # Отображение изменения за период в центре графика
            # Положительное / отрицательное изменение при -0.5% < x < 0.5%
            start_end_differences = round(data['close'].iloc[-1] * 100 / data['close'].iloc[0] - 100, 2)
            # Если изменение положительное (x > 0), зеленый цвет фона заполнения
            if start_end_differences > 0.5:
                plt.text(x=data['begin'].mean(), y=min(data['close']),
                         s=f'Изменение стоимости:\n {start_end_differences}%',
                         fontstyle='italic',
                         bbox={'fill': True, 'linestyle': 'solid', 'alpha': 0.2, 'color': '#00FF66'})
            # Если изменение отрицательное (x < 0), красный цвет фона заполнения
            elif start_end_differences < 0.5:
                plt.text(x=data['begin'].mean(), y=min(data['close']),
                         s=f'Изменение стоимости:\n {start_end_differences}%',
                         fontstyle='italic',
                         bbox={'fill': True, 'linestyle': 'solid', 'alpha': 0.2, 'color': '#FF0000'})
            # В противном случае не использовать цвет заполнения
            else:
                plt.text(x=data['begin'].mean(), y=min(data['close']),
                         s=f'Изменение стоимости:\n {start_end_differences}%',
                         fontstyle='italic',
                         bbox={'fill': True, 'linestyle': 'solid', 'alpha': 0.2, 'color': '#CCCCCC'})

            plt.xlabel(xlabel='', fontweight='bold')
            plt.ylabel(ylabel='', fontweight='bold')
            plt.yticks(fontsize=12, fontweight='bold')

            # Запрос на получение наименования тикера
            name = requests.get(
                f'http://iss.moex.com/iss/engines/stock/markets/shares/securities/{tick}/SHORTNAME.json')
            name_dict = name.json()

            name_data = pd.DataFrame([{k: r[i] for i, k in enumerate(name_dict['securities']['columns'])} for r in
                                      name_dict['securities']['data']])

            tick_name = name_data[name_data['BOARDID'] == 'TQBR'].iloc[0, 2]
            plt.text(x=data['begin'].iloc[0], y=max(data['mean_cost']) + max(data['mean_cost']) * 0.001,
                     s=f'{tick}: {tick_name}', color='#333333', fontsize=15, fontstyle='oblique',
                     fontvariant='small-caps')

            plt.legend(loc='lower right', bbox_to_anchor=(1, 1), ncols=5)

            img = BytesIO()
            plt.savefig(img, format='png', bbox_inches='tight', dpi=400)
            # plt.close()
            img.seek(0)

            return img

    # Обработка ошибки запроса и возврат ошибки
    except requests.exceptions.RequestException as e:
        error_message = f"Ошибка обработки запроса для тикера {tick.upper()}, наименованию интервала {interval_name} и интервала {interval}: {e}"
        return None, f"Error: {error_message}"


# Оптимизировать использование переменных
# Создать переменные для повторяющихся объектов
# Перенести на polars?
