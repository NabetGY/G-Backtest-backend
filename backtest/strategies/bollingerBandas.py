import numpy as np

def signalD(x):
    closeList =  x['close'].tolist()
    maList = list( x['MA'] )
    signalInList = list( x['signalIn'] )
    signalList = []

    length = len( closeList )

    signalList.append(0)

    for i in range (1, length ):
      if ((signalInList[i] == 1 ) or ((signalList[i-1] ==1) and (closeList[i] > maList[i]))):
        signalList.append(1)
      else:
        signalList.append(0)
    return signalList

def get_BollingerBands( dataframe, dataList ):
    dataframe['TP'] = (dataframe['high'] + dataframe['low'] + dataframe['close'])/3
    dataframe['STDEV'] = dataframe['TP'].rolling(20).std()
    dataframe['MA'] = dataframe['TP'].rolling(20).mean()
    dataframe['BOLU'] = dataframe['MA'] + (2*dataframe['STDEV'])
    dataframe['BOLD'] = dataframe['MA'] - (2*dataframe['STDEV'])
    dataframe['signalIn'] = np.where( dataframe['close'] >= dataframe['BOLU'], 1, 0 )
    dataframe['signal'] = signalD(dataframe)

    # dataframe['position'] = dataframe['signal'].diff()
    # dataframe.at[0, 'position'] = 0
    # dataframe['buy']=np.where( dataframe['position'] == 1, dataframe['close'], np.NAN)
    # dataframe['sell']=np.where( dataframe['position'] == -1, dataframe['close'], np.NAN)

    return dataframe['signal']