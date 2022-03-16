import numpy as np

def get_sma(period, dataframe):
    name = 'sma_{}'.format(period)
    dataframe[name] = dataframe['close'].rolling(period).mean()
    return name

def get_ema(period, dataframe):
    name = 'ema_{}'.format(period)
    dataframe[name] = dataframe['close'].ewm(span=period, adjust=False).mean()
    return name


def get_MACross( dataframe, dataList ):

    nameList = []

    for item in dataList:
        if item.get('MA') == 'Media movil simple':
            nameList.append( get_sma( item.get('period') , dataframe ) )
        elif item.get('MA') == 'Media movil exponencial':
            nameList.append( get_ema( item.get('period') , dataframe ) )

    first = dataframe.columns.get_loc(nameList[0])
    second = first+1

    dataframe['signal'] = np.where((dataframe.iloc[:, second:].lt(dataframe.iloc[:, first], axis=0)).all(1), 1, 0)
    
    # dataframe['position'] = dataframe['signal'].diff()
    # dataframe.at[0, 'position'] = 0
    # dataframe['buy']=np.where( dataframe['position'] == 1, dataframe['close'], np.NAN)
    # dataframe['sell']=np.where( dataframe['position'] == -1, dataframe['close'], np.NAN)
    
    return dataframe['signal']














