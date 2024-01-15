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

        weeks_list = ['недели', 'неделя', 'недель']
        days_list = ['дни', 'дней', 'дня']

        if interval_name.lower() in weeks_list:
            date_start = timedelta(weeks=interval)  # From what
        elif interval_name.lower() in days_list:
            date_start = timedelta(days=interval)
        else:
            date_start = timedelta(weeks=6)

        date_end = datetime.now()  # Date now
        date_start_frame = date_end - date_start  # Starting interval data
        date_end = date_end.strftime('%Y-%m-%d')  # Data format
        date_start_frame = date_start_frame.strftime('%Y-%m-%d')
        date_format = mdates.DateFormatter('%d.%m.%Y')

        if tick:
            ticket = requests.get(
                f'http://iss.moex.com/iss/engines/stock/markets/shares/securities/{tick}/candles.json?from={date_start_frame}&till={date_end}&interval=60')
            ticket_dict = ticket.json()

            data = pd.DataFrame(
                [{k: r[i] for i, k in enumerate(ticket_dict['candles']['columns'])} for r in
                 ticket_dict['candles']['data']])

            data['begin'] = pd.to_datetime(data['begin'])  # Convert 'begin' column to datetime format
            data['mean_cost'] = data[['high', 'low']].mean(axis=1)
            data['sd_cost'] = data[['high', 'low']].std(axis=1)

            data['SMA7'] = data['mean_cost'].rolling(window=7).mean()
            data['SMA21'] = data['mean_cost'].rolling(window=21).mean()
            data['SMA56'] = data['mean_cost'].rolling(window=56).mean()

            plt.figure(figsize=(15, 5))

            ax = sns.lineplot(data=data, x='begin', y='mean_cost', color='#0066FF', alpha=0.7, lw=2.5, label='Mean')
            ax.fill_between(data['begin'], data['mean_cost'] - data['sd_cost'], data['mean_cost'] + data['sd_cost'],
                            color='#99CCFF', alpha=0.5, label='SD')
            sns.scatterplot(data=data, x='begin', y='close', s=45, color='#6699FF', alpha=0.7, label='Close')

            sns.lineplot(data=data, x='begin', y='SMA7', color='#FF6600', label=f'SMA 7 дней', alpha=0.65, lw=2)
            sns.lineplot(data=data, x='begin', y='SMA21', color='#CC0033', label=f'SMA 21 день', alpha=0.65, lw=2)
            sns.lineplot(data=data, x='begin', y='SMA56', color='#00CC33', label=f'SMA 56 день', alpha=0.65, lw=2)

            ax.xaxis.set_major_formatter(date_format)
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
            plt.xticks(rotation=45, fontsize=12, fontweight='bold')

            plt.xlabel(xlabel='', fontweight='bold')
            plt.ylabel(ylabel='', fontweight='bold')
            plt.yticks(fontsize=12, fontweight='bold')

            # Получить полное (ну почти) название  для тикета {tick}
            name = requests.get(
                f'http://iss.moex.com/iss/engines/stock/markets/shares/securities/{tick}/SHORTNAME.json')
            name_dict = name.json()

            name_data = pd.DataFrame([{k: r[i] for i, k in enumerate(name_dict['securities']['columns'])} for r in
                                      name_dict['securities']['data']])

            plt.text(x=data['begin'][0], y=max(data['mean_cost']) + max(data['mean_cost']) * 0.001,
                     s=f'{tick}: {name_data.iloc[0, 2]}', color='#333333', fontsize=15, fontstyle='oblique',
                     fontvariant='small-caps', backgroundcolor='#CCCCCC', bbox={'fill': True, 'linestyle': 'solid',
                                                                                'linewidth': '2'})

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
