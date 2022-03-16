import csv, sys
import pandas as pd
from ticker.models import Ticker, TimeSeries
""" df = pd.read_csv("AAPL.csv", encoding="latin9", sep=",")
for _, row in df.iterrows():

    print(row) """
nombre_archivo = "/home/nabet/backtesting/backend/backtest/strategies/AAPL.csv"
ticker = Ticker.objects.filter(symbol="AAPL").first()

interval = '30min'
with open(nombre_archivo, "r") as archivo:
    # Omitir el encabezado
    next(archivo, None)
    for linea in archivo:
        linea2 = linea.split(",")
        timeSerie = TimeSeries( ticker=ticker, interval=1, date=linea2[0], open=linea2[1], high=linea2[2], low=linea2[3], close=linea2[4], volume=linea2[5].split('\n')[0])
        timeSerie.save()
    ticker.save()
    print('Se recopilo con exito el ticket =', ticker.symbol)