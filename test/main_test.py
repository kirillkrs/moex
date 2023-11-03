from typing import Optional
import logging
from io import BytesIO

import pandas as pd
import requests
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates


def get_tick(
        tick: str,
        interval_name: str = 'недели',
        interval: int = 4,
        time_interval: int = 24,
):
    try:

        """
        :param tick: Наименование акций
        :param interval_name: Желаемый интервал (Дни / недели)
        :param interval: Количество дней / недель
        :param time_interval: временной интервал внутри сессии (60 минут / 24 часа)
        :param colors: Цета отображения графиков скользящего среднего
        :return: Возвращает графики
        """

        if interval_name == 'недели' or interval_name == 'неделя':
            date_start = timedelta(weeks=interval)  # From what
        elif interval_name == 'дни' or interval_name == 'дней':
            date_start = timedelta(days=interval)

        date_end = datetime.now()  # Date now
        date_start_frame = date_end - date_start  # Starting interval data
        date_end = date_end.strftime('%Y-%m-%d')  # Data format
        date_start_frame = date_start_frame.strftime('%Y-%m-%d')
        date_format = mdates.DateFormatter('%d.%m.%Y')

        j = requests.get(
            f'http://iss.moex.com/iss/engines/stock/markets/shares/securities/{tick.upper()}/candles.json?from={date_start_frame}&till={date_end}&interval={time_interval}')
        j_dict = j.json()

        # if 'candles' in j_dict and 'columns' in j_dict['candles']:
        #     data = pd.DataFrame(
        #         [{k: r[i] for i, k in enumerate(j_dict['candles']['columns'])} for r in j_dict['candles']['data']])
        # else:
        #     error_message = f"Неожиданный API запрос для {tick.upper()}"
        #
        #     raise ValueError(error_message)

        data = pd.DataFrame(
            [{k: r[i] for i, k in enumerate(j_dict['candles']['columns'])} for r in j_dict['candles']['data']])

        data['begin'] = pd.to_datetime(data['begin'])  # Convert 'begin' column to datetime format
        data['mean_cost'] = data[['high', 'low']].mean(axis=1)
        data['sd_cost'] = data[['high', 'low']].std(axis=1)

        plt.figure(figsize=(15, 5))

        ax = sns.lineplot(data=data, x='begin', y='mean_cost', color='#0066FF', alpha=0.7, lw=2.5, label='Mean')
        ax.fill_between(data['begin'], data['mean_cost'] - data['sd_cost'], data['mean_cost'] + data['sd_cost'],
                        color='#99CCFF', alpha=0.5, label='Mean ± SD')
        sns.scatterplot(data=data, x='begin', y='close', s=45, color='#6699FF', alpha=0.7, label='Close')

        ax.xaxis.set_major_formatter(date_format)
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        plt.xticks(rotation=45, fontsize=12, fontweight='bold')

        plt.xlabel(xlabel='', fontweight='bold')
        plt.ylabel(ylabel='', fontweight='bold')
        plt.yticks(fontsize=12, fontweight='bold')

        plt.text(x=data['begin'][0], y=max(data['mean_cost']), s=f'{tick}', color='#333333', fontsize=15,
                 fontstyle='oblique', fontvariant='small-caps')
        plt.legend(loc='lower left', ncols=2)

        img = BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight')
        # plt.close()
        img.seek(0)

        return img

    # Обработка ошибки запроса и возврат ошибки
    except requests.exceptions.RequestException as e:
        error_message = f"Ошибка обработки запроса для тикера {tick.upper()}, наименованию интервала {interval_name} и интервала {interval}: {e}"
        return None, f"Error: {error_message}"
