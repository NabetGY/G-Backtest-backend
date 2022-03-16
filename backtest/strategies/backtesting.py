import numpy as np
import pandas as pd
from backtest.models import Backtest
from users.models import User

from backtest.strategies.MACD import get_MACross
from backtest.strategies.DonchianChannels import get_DonchianChannels
from backtest.strategies.bollingerBandas import get_BollingerBands
from backtest.strategies.ichimokuClouds import get_IchimokuClouds



from ticker.models import Ticker, TimeSeries

def get_time_series(symbol, start_date, end_date):

    ticker = Ticker.objects.filter(symbol=symbol).first()
    dateRange = TimeSeries.objects.filter(ticker=ticker,time__range=(start_date, end_date)).order_by('time')
    return dateRange, ticker


def get_resumen( dateframe ):

    print (dateframe[['date_time','price_in', 'price_out', 'positions', 'profit_loss' ]])

    resumen = {}

    resumen["operations"] = dateframe["profit_loss"].notna().sum()

    resumen["winrate"] = ( np.sum(dateframe["profit_loss"] > 0 ) / resumen['operations'] ) * 100

    resumen["Total_P_L"] = dateframe["profit_loss"].sum()

    resumen["max_profit"] = dateframe["profit_loss"].max()
    
    resumen["max_loss"] = dateframe["profit_loss"].min() if dateframe["profit_loss"].min() < 0 else 0

    return resumen


def get_report( dataframe, capital ):
    
    sizePosition = capital*0.1
    lossMax = capital*0.01
    stopLoss = lossMax/sizePosition
    target= 2*stopLoss

    dataframeReport = dataframe.loc[ dataframe['position'] != 0.0, ['position', 'time', 'buy', 'sell']]

    dataframeReport.columns = ["In_Out", "date_time", "price_in",  "price_out"]

    price_out = pd.to_numeric(dataframeReport["price_out"])
    price_in = pd.to_numeric(dataframeReport["price_in"])

    dataframeReport["stp"] = np.where( price_in.notna() , price_in-(price_in*stopLoss), price_in-(price_in*stopLoss) )

    dataframeReport["stp%"] = np.where( price_in.notna() , stopLoss*100, stopLoss*100)

    dataframeReport["positions"] = np.where( price_in.notna() , np.floor( sizePosition/price_in), np.floor( sizePosition/price_out) )

    dataframeReport["positions%"] = np.where( price_in.notna() , target*100, target*100)

    dataframeReport["tgt"] = np.where( price_in.notna() , price_in+(price_in*target), price_in+(price_in*target) )

    dataframeReport["profit_loss"] = np.where( price_out.notna() , ((price_out-price_in.shift())*dataframeReport["positions"]), np.NaN)
    
    return dataframeReport



def indicatorFilter( df, data ):

    for item in data:

        if item.get('indicatorName') == 'MACD':
            df['signal_macd'] = get_MACross( df.copy(), item.get('config') )
        
        if item.get('indicatorName') == 'DonchianChannels':
            df['signal_donchianChannels'] = get_DonchianChannels( df.copy(), item.get('config') )

        if item.get('indicatorName') == 'BollingerBands':
            df['signal_bollingerBands'] = get_BollingerBands( df.copy(), item.get('config') )

        if item.get('indicatorName') == 'ichimokuClouds':
            df['signal_ichimokuClouds'] = get_IchimokuClouds( df.copy(), item.get('config') )


    return df


def get_positions(dataframe):

    dataframe['signal']= dataframe.iloc[:,9:].prod(axis=1)
    dataframe['position'] = dataframe['signal'].diff()
    dataframe.at[0, 'position'] = 0
    dataframe['buy']=np.where( dataframe['position'] == 1, dataframe['close'], np.NAN)
    dataframe['sell']=np.where( dataframe['position'] == -1, dataframe['close'], np.NAN)

    return dataframe


def backtest(symbol, capital, start_date, end_date, indicatorData, email):

    data, ticker = get_time_series(symbol, start_date, end_date)
    
    df =  pd.DataFrame(data.values())

    df = indicatorFilter( df, indicatorData )

    df = get_positions( df )

    df2 = get_report( df, capital )

    resumen = get_resumen(df2)

    df2 = df2.fillna('')

    user = User.objects.filter(email=email).first()

    print(user, ticker)

    backtest = Backtest(ticker=ticker,capital=capital, date_start =start_date, date_end=end_date, interval='30min',indicators_data=indicatorData ,user= user)

    backtest.save()

    return resumen, df2.to_dict('tight'), data