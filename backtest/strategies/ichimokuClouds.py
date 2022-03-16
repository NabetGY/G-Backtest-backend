import numpy as np

def get_IchimokuClouds( dataframe, dataList ):
    
    tenkan = dataList[0].get('conversion')
    kinjun = dataList[0].get('base')
    chikou = dataList[0].get('lagging')
    spanA = dataList[0].get('spanA')
    spanB = dataList[0].get('spanB')

    dataframe['tenkan'] = ( dataframe['high'].rolling(tenkan).max() +  dataframe['low'].rolling(tenkan).min() ) / 2
    dataframe['kinjun'] = ( dataframe['high'].rolling(kinjun).max() +  dataframe['low'].rolling(kinjun).min() ) / 2
    dataframe['chikou'] = dataframe['close'].shift(periods=chikou)
    dataframe['spanA'] = (( dataframe['tenkan'] +  dataframe['kinjun'] ) / 2).shift(spanA)
    dataframe['spanB'] = (( dataframe['high'].rolling(52).max() +  dataframe['low'].rolling(52).min() ) / 2).shift(spanB)

    dataframe['signal'] = np.where((dataframe['close'] > dataframe['spanA'])&(dataframe['close'] > dataframe['spanB']), 1, 0)
    # dataframe['position'] = dataframe['signal'].diff()
    # dataframe.at[0, 'position'] = 0
    # dataframe['buy']=np.where( dataframe['position'] == 1, dataframe['close'], np.NAN)
    # dataframe['sell']=np.where( dataframe['position'] == -1, dataframe['close'], np.NAN)

    return dataframe['signal']