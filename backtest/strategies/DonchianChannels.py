import numpy as np

def get_DonchianChannels( dataframe, dataList ):
    period = dataList[0].get('period')
    dataframe['UC'] = dataframe['high'].rolling(period).max()
    dataframe['LC'] = dataframe['low'].rolling(period).min()
    dataframe['middleChannel'] = (dataframe['UC'] + dataframe['LC'])/2
    dataframe['signal'] = np.where(dataframe['UC'] >= dataframe['UC'].shift(), 1, 0)

    # dataframe['position'] = dataframe['signal'].diff()
    # dataframe.at[0, 'position'] = 0
    # dataframe['buy']=np.where( dataframe['position'] == 1, dataframe['close'], np.NAN)
    # dataframe['sell']=np.where( dataframe['position'] == -1, dataframe['close'], np.NAN)

    return dataframe['signal']