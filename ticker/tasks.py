import datetime

import pytz
import requests
import csv
from celery import shared_task

from ticker.models import Ticker, TimeSeries

@shared_task
def get_info_ticker():

    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=IBM&interval=5min&apikey=demo'
    try:
        r = requests.get(url)
    except requests.ConnectionError as e:
        raise Exception("Failed operation...", e)

    if r.status_code in [200, 201]:
        data = r.json()
        print(data.get("Meta Data"))


def get_tickers():
# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
    CSV_URL = 'https://www.alphavantage.co/query?function=LISTING_STATUS&apikey=ZZEAYA9XZ9SNIFGT'

    with requests.Session() as s:
        download = s.get(CSV_URL)
        decoded_content = download.content.decode('utf-8')
        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        my_list = list(cr)
        for row in my_list:
            symbol = row[0]
            name = row[1]
            print(symbol)
            Ticker.objects.create(name=name, symbol=symbol)


@shared_task
def update_time_series( intervalStr ):

    ticker = None
    url  = ''
    intervalID = None
    timeSerieString = ''
    format = ''
    

    if intervalStr == '30min':
        timeSerieString = 'Time Series (30min)'
        format = '%Y-%m-%d %H:%M:%S'
        ticker = Ticker.objects.filter(is_active=True).earliest('last_Refreshed_30m')
        intervalID = TimeSeries.INTERVAL_30

        try:
            time_serie = TimeSeries.objects.filter(ticker=ticker, interval=intervalID).latest('time')
            last_time_serie = time_serie.time.replace(tzinfo=datetime.timezone.utc)
        except TimeSeries.DoesNotExist:
            last_time_serie = None

        url = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={}&interval={}&outputsize=full&apikey=ZZEAYA9XZ9SNIFGT'.format(
        ticker.symbol, intervalStr
        )

    elif intervalStr == '60min':
        timeSerieString = 'Time Series (60min)'
        format = '%Y-%m-%d %H:%M:%S'
        ticker = Ticker.objects.filter(is_active=True).earliest('last_Refreshed_60m')
        intervalID = TimeSeries.INTERVAL_HOUR
        try:
            time_serie = TimeSeries.objects.filter(ticker=ticker, interval=intervalID).latest('time')
            last_time_serie = time_serie.time.replace(tzinfo=datetime.timezone.utc)

        except TimeSeries.DoesNotExist:
            last_time_serie = None

        url = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={}&interval={}&outputsize=full&apikey=ZZEAYA9XZ9SNIFGT'.format(
        ticker.symbol, intervalStr
        )

    if intervalStr == '1Day':
        timeSerieString = 'Time Series (Daily)'
        format = '%Y-%m-%d'
        ticker = Ticker.objects.filter(is_active=True).earliest('last_Refreshed_1D')
        intervalID = TimeSeries.INTERVAL_DAY
        try:
            time_serie = TimeSeries.objects.filter(ticker=ticker, interval=intervalID).latest('time')
            last_time_serie = time_serie.time.replace(tzinfo=datetime.timezone.utc)
        except TimeSeries.DoesNotExist:
            last_time_serie = None

        url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={}&apikey=ZZEAYA9XZ9SNIFGT'.format(
        ticker.symbol
        )

    print(url)

    try:
        r = requests.get(url)
    except requests.ConnectionError as e:
        raise Exception("Failed operation...", e)

    if r.status_code in [200, 201]:

        data = r.json()

        if 'Note' in data :
            """ Alpha Vantage standard API call frequency is 5 calls per minute and 500 calls per day. """
            print("limite excedido...")

        elif 'Error Message' in data :
            """ "Invalid API call. """
            ticker.is_active = False
            ticker.save()

        elif "Meta Data" in data :

            time_serie = data.get( timeSerieString )

            for key, value in time_serie.items():

                date_time_obj = datetime.datetime.strptime(key, format).replace(tzinfo=datetime.timezone.utc)

                if last_time_serie == None :
                    timeSerie = TimeSeries( ticker=ticker, interval=intervalID, time=date_time_obj, open=value['1. open'], high=value['2. high'], low=value['3. low'], close=value['4. close'], volume=value['5. volume'],)
                    timeSerie.save()


                elif last_time_serie < date_time_obj:

                    timeSerie = TimeSeries( ticker=ticker, interval=intervalID, time=date_time_obj, open=value['1. open'], high=value['2. high'], low=value['3. low'], close=value['4. close'], volume=value['5. volume'],)
                    timeSerie.save()
                    
                else:
                    print('No hay mas registros para agregar al actual ticker...')
                    return
                
            if intervalStr == '30min':
                ticker.last_Refreshed_30m = datetime.datetime.now()
                ticker.save()

            elif intervalStr == '60min':
                ticker.last_Refreshed_60m = datetime.datetime.now()
                ticker.save()

            elif intervalStr == '1Day':
                ticker.last_Refreshed_1D = datetime.datetime.now()
                ticker.save()

            print('Se recopilo con exito el ticket =', ticker.symbol)
        
        else:
            print("Error: ", data)
    else:
        print("Error, code: ", r.status_code)


