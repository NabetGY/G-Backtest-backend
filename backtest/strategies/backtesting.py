import numpy as np
import pandas as pd
from decimal import Decimal
from backtest.models import Backtest
from users.models import User

from backtest.strategies.MACD import get_MACross
from backtest.strategies.DonchianChannels import get_DonchianChannels
from backtest.strategies.bollingerBandas import get_BollingerBands
from backtest.strategies.ichimokuClouds import get_IchimokuClouds



from ticker.models import Ticker, TimeSeries

def get_time_series(symbol, intervalData, start_date, end_date):
    interval=None
    for item in TimeSeries.INTERVALS:
            if item[1] == intervalData:
                interval = item[0]
    ticker = Ticker.objects.filter(symbol=symbol).first()
    dateRange = TimeSeries.objects.filter(ticker=ticker,interval=interval ,time__range=(start_date, end_date)).order_by('time')
    return dateRange


def get_resumen( dataframe, capital, finalCapital):

    #print(dataframe["stop"].to_string())


    resumen = {}

    resumen["capital"] = capital

    resumen["capitalFinal"] = finalCapital

    resumen["operations"] = dataframe["profit_loss"].notna().sum()

    if (resumen["operations"]==0 ):
        return resumen

    resumen["winrate"] = ( np.sum(dataframe["profit_loss"] > 0 ) / resumen['operations'] ) * 100

    resumen["Total_P_L"] = dataframe["profit_loss"].sum()

    resumen["P_L_porcent"] = (resumen["Total_P_L"]/capital) * 100


    resumen["max_profit"] = dataframe["profit_loss"].max()
    
    resumen["max_loss"] = dataframe["profit_loss"].min() if dataframe["profit_loss"].min() < 0 else 0

    return resumen




def get_report( dataframe, capital, margenStr ):

    
    sizePosition = capital*0.1
    lossMax = capital*0.01
    stopLoss = lossMax/sizePosition
    target= 2*stopLoss

    dataframeReport = dataframe.loc[ dataframe['position'] != 0.0, ['position', 'time', 'buy', 'sell']]

    dataframeReport.columns = ["In_Out", "time", "price_in",  "price_out"]

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



def getMargen(margenStr):
    
    if(margenStr=='1:1'):
        return ( 1, Decimal( 0.01 ) )
    if(margenStr=='2:1'):
        return ( 2, Decimal( 0.01 ) )
    if(margenStr=='3:1'):
        return ( 3, Decimal( 0.01 ) )
    if(margenStr=='4:1'):
        return ( 4, Decimal( 0.01 ) )
    if(margenStr=='5:1'):
        return ( 5, Decimal( 0.01 ) )


def process_backtest( dataframe, capital2, margenStr ):

    margen = getMargen( margenStr )

    capital = Decimal(capital2)
    sizePosition = capital*Decimal(0.1)
    lossMax = capital*margen[1]
    stopLoss = lossMax/sizePosition
    target= margen[0]*stopLoss

    dataframe['price_in'] = np.NAN
    dataframe['price_out'] = np.NAN
    dataframe['stop'] = np.NAN
    dataframe['target'] = np.NAN
    dataframe['positions'] = np.NAN
    dataframe['profit_loss'] = np.NAN
    dataframe['in_out'] = 0

    for item in range(0, len(dataframe)):
        if( item==0 ):
            dataframe.loc[item, 'price_in'] = dataframe.loc[item, 'buy']

        elif ( (pd.notna(dataframe.loc[item-1, 'price_in']) and (dataframe.loc[item-1, 'in_out']>=0 )) and ((dataframe.loc[item, 'close'] < dataframe.loc[item-1, 'stop']) or ( dataframe.loc[item, 'close'] > dataframe.loc[item-1, 'target'] ))):
            dataframe.loc[item, 'in_out'] = -1
            dataframe.loc[item, 'price_in'] = dataframe.loc[item-1, 'price_in']
            dataframe.loc[item, 'price_out'] = dataframe.loc[item, 'close']
            dataframe.loc[item, 'stop'] = dataframe.loc[item-1, 'stop']
            dataframe.loc[item, 'target'] = dataframe.loc[item-1, 'target']
            dataframe.loc[item, 'positions'] = dataframe.loc[item-1, 'positions']
            dataframe.loc[item, 'profit_loss'] = (dataframe.loc[item, 'price_out'] - dataframe.loc[item, 'price_in'] ) * dataframe.loc[item, 'positions']
            capital = capital + (dataframe.loc[item, 'price_out'] * dataframe.loc[item, 'positions'] )


        elif ( (pd.notna(dataframe.loc[item-1, 'price_in']) and (dataframe.loc[item-1, 'in_out']>=0 ) ) and (dataframe.loc[item, 'close'] > dataframe.loc[item-1, 'stop']) and ( dataframe.loc[item, 'close'] < dataframe.loc[item-1, 'target'] ) ):
            dataframe.loc[item, 'price_in'] = dataframe.loc[item-1, 'price_in']
            dataframe.loc[item, 'stop'] = dataframe.loc[item-1, 'stop']
            dataframe.loc[item, 'target'] = dataframe.loc[item-1, 'target']
            dataframe.loc[item, 'positions'] = dataframe.loc[item-1, 'positions']
        

        elif ( pd.notna(dataframe.loc[item, 'buy']) and pd.isna(dataframe.loc[item-1, 'price_in'])):
            dataframe.loc[item, 'in_out'] = 1
            dataframe.loc[item, 'price_in'] = dataframe.loc[item, 'buy']
            sizePosition = capital*Decimal(0.1)
            lossMax = capital*margen[1]
            stopLoss = lossMax/sizePosition
            target= margen[0]*stopLoss
            dataframe.loc[item, 'stop' ] = dataframe.loc[item, 'price_in'] - (dataframe.loc[item, 'price_in'] * stopLoss)
            dataframe.loc[item, 'positions' ] =  Decimal(np.floor(sizePosition/dataframe.loc[item, 'price_in']))
            capital = capital - (dataframe.loc[item, 'positions' ] * dataframe.loc[item, 'price_in' ])
            dataframe.loc[item, 'target' ] = dataframe.loc[item, 'price_in'] + ( dataframe.loc[item, 'price_in'] * target)

    dataframe["stp%"] = margen[1]*100
    dataframe["positions%"] = margen[0]

    return dataframe, capital
 












def backtest(symbol, interval, capital, start_date, end_date, indicatorData, margen):

    data = get_time_series(symbol, interval, start_date, end_date)

    if len(data) == 0:
        return 2, None, None
    
    df =  pd.DataFrame(data.values())

    df = indicatorFilter( df, indicatorData )

    df = get_positions( df )

    df2, finalCapital = process_backtest( df, capital, margen )

    resumen = get_resumen( df2, capital, finalCapital)

    if(resumen.get("operations")==0):
        return 3, None, None
    df2 = df2.fillna('')

    return 1, resumen , df2.to_dict('tight')




""" 
def process_backtest( dataframe, capital2, margenStr ):

    margen = getMargen( margenStr )

    capital = Decimal(capital2)
    sizePosition = capital*Decimal(0.1)
    lossMax = capital*margen[1]
    stopLoss = lossMax/sizePosition
    target= margen[0]*stopLoss

    for item in range(0, len(dataframe)):
        if( item==0 ):
            dataframe.loc[item, 'price_in'] = dataframe.loc[item, 'buy']

        elif ( pd.notna(dataframe.loc[item-1, 'price_in']) and ((dataframe.loc[item, 'close'] < dataframe.loc[item-1, 'stop']) or ( dataframe.loc[item, 'close'] > dataframe.loc[item-1, 'target'] ))):
            dataframe.loc[item, 'price_in'] = dataframe.loc[item-1, 'price_in']
            dataframe.loc[item, 'price_out'] = dataframe.loc[item, 'close']
            dataframe.loc[item, 'stop'] = dataframe.loc[item-1, 'stop']
            dataframe.loc[item, 'target'] = dataframe.loc[item-1, 'target']
            dataframe.loc[item, 'positions'] = dataframe.loc[item-1, 'positions']
            dataframe.loc[item, 'profit_loss'] = (dataframe.loc[item, 'price_out'] - dataframe.loc[item, 'price_in'] ) * dataframe.loc[item, 'positions']
            capital = capital + (dataframe.loc[item, 'price_out'] * dataframe.loc[item, 'positions'] )

        elif ( (pd.notna(dataframe.loc[item-1, 'price_in']) and pd.isna(dataframe.loc[item-1, 'profit/loss'])) and (dataframe.loc[item, 'close'] > dataframe.loc[item-1, 'stop']) and ( dataframe.loc[item, 'close'] < dataframe.loc[item-1, 'target'] ) ):
            dataframe.loc[item, 'price_in'] = dataframe.loc[item-1, 'price_in']
            dataframe.loc[item, 'stop'] = dataframe.loc[item-1, 'stop']
            dataframe.loc[item, 'target'] = dataframe.loc[item-1, 'target']
            dataframe.loc[item, 'positions'] = dataframe.loc[item-1, 'positions']
        

        elif ( pd.notna(dataframe.loc[item, 'buy']) and pd.isna(dataframe.loc[item-1, 'price_in'])):
            dataframe.loc[item, 'price_in'] = dataframe.loc[item, 'buy']
            sizePosition = capital*Decimal(0.1)
            lossMax = capital*margen[1]
            stopLoss = lossMax/sizePosition
            target= margen[0]*stopLoss
            dataframe.loc[item, 'stop' ] = dataframe.loc[item, 'price_in'] - dataframe.loc[item, 'price_in'] * stopLoss
            dataframe.loc[item, 'positions' ] =  np.floor(sizePosition/dataframe.loc[item, 'price_in'])
            capital = capital - (dataframe.loc[item, 'positions' ] * dataframe.loc[item, 'price_in' ])
            dataframe.loc[item, 'target' ] = dataframe.loc[item, 'price_in'] + dataframe.loc[item, 'price_in'] * target

    dataframe["stp%"] = margen[1]
    dataframe["positions%"] = margen[0]

    return dataframe
 """