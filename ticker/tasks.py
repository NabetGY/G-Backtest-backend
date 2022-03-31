import datetime
from time import sleep

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


def saveData(CSV_URL, ticker, timeSerieString, last_time_serie, intervalID, intervalStr, format, item=None):
    print(CSV_URL)

    with requests.Session() as s:
        try:
            download = s.get(CSV_URL)
            decoded_content = download.content.decode('utf-8')
            cr = csv.reader(decoded_content.splitlines(), delimiter=',')
            my_list = list(cr)
            size = len(my_list)

            if 'Note' in decoded_content :
                """ Alpha Vantage standard API call frequency is 5 calls per minute and 500 calls per day. """
                print("limite excedido...")
                return False
            
            elif 'Error Message' in decoded_content :
                """ "Invalid API call. """
                ticker.is_active = False
                ticker.save()
                return False

            elif size == 1 and item != 'year1month1':
                """ "Invalid API call. """
                ticker.is_active = False
                ticker.save()
                return False

            
            for row in my_list[1:]:
                date_time_obj = datetime.datetime.strptime(row[0], format).replace(tzinfo=datetime.timezone.utc)
                if last_time_serie == None :
                    timeSerie = TimeSeries( ticker=ticker, interval=intervalID, time=date_time_obj, open=row[1], high=row[2], low=row[3], close=row[4], volume=row[5])
                    timeSerie.save()
                elif last_time_serie < date_time_obj :
                    timeSerie = TimeSeries( ticker=ticker, interval=intervalID, time=date_time_obj, open=row[1], high=row[2], low=row[3], close=row[4], volume=row[5])
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

            return True
        except requests.ConnectionError as e:
            raise Exception("Failed operation...", e )
            return False




@shared_task
def update_time_series( intervalStr ):

    ticker = None
    url  = ''
    intervalID = None
    timeSerieString = ''
    format = ''
    

    if intervalStr == '30min':

        get_IntradayData('Time Series (30min)', 'last_Refreshed_30m', intervalStr)


    elif intervalStr == '60min':
        get_IntradayData('Time Series (60min)', 'last_Refreshed_60m', intervalStr)


    elif intervalStr == '1Day':
        get_DailyData('Time Series (Daily)', 'last_Refreshed_1D', intervalStr)


    

    
lista = [
    'year1month1', 'year1month2', 'year1month3', 'year1month4', 'year1month5', 'year1month6',
    'year1month7', 'year1month8', 'year1month9', 'year1month10','year1month11', 'year1month12', 
    'year2month1', 'year2month2', 'year2month3', 'year2month4', 'year2month5', 'year2month6',
    'year2month7', 'year2month8', 'year2month9', 'year2month10','year2month11', 'year2month12' 
    ]


def get_IntradayData(timeSerieString, last_Refresh, intervalStr):

    format = '%Y-%m-%d %H:%M:%S'
    ticker = Ticker.objects.filter(is_active=True).earliest(last_Refresh)
    intervalID = None
    
    if '30min' == intervalStr:
        intervalID = TimeSeries.INTERVAL_30
    if '60min' == intervalStr:
        intervalID = TimeSeries.INTERVAL_HOUR

    try:
        time_serie = TimeSeries.objects.filter(ticker=ticker, interval=intervalID).latest('time')
        last_time_serie = time_serie.time.replace(tzinfo=datetime.timezone.utc)

    except TimeSeries.DoesNotExist:
        last_time_serie = None

    for item in lista:
        url = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY_EXTENDED&symbol={}&interval={}&slice={}&apikey=ZZEAYA9XZ9SNIFGT'.format(
            ticker.symbol, intervalStr, item
        )

        ok = saveData(url, ticker, timeSerieString, last_time_serie, intervalID, intervalStr, format, item )
        if(not ok): return
        sleep(450)







def get_DailyData(timeSerieString,last_Refresh, intervalStr):
    format = '%Y-%m-%d'
    ticker = Ticker.objects.filter(is_active=True).earliest(last_Refresh)
    intervalID = TimeSeries.INTERVAL_DAY
    try:
        time_serie = TimeSeries.objects.filter(ticker=ticker, interval=intervalID).latest('time')
        last_time_serie = time_serie.time.replace(tzinfo=datetime.timezone.utc)
    except TimeSeries.DoesNotExist:
        last_time_serie = None

    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={}&outputsize=full&apikey=ZZEAYA9XZ9SNIFGT&datatype=csv'.format(
    ticker.symbol
    )
    saveData(url, ticker, timeSerieString, last_time_serie, intervalID, intervalStr, format )