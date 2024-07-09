"""THIS FILE IS ONLY MEANT FOR TAKING GATHERING SMA DATA TO BE USED IN CALCULATING EMA"""


"""[1] Gather an exstensive list of previous price data"""

from sys import path
path.append("1-DataGathering/Programs")
from Data_Gathering_Binance_Historical_LEGACY import get_historical_kline_data

"""#chart_interval
chart_interval = "5m"
trading_pair = "BTCUSDT"
indicator_interval = 100
exchange_name = "Binance"
limit = 1000
"""
def extensive_data_gather(trading_pair, chart_interval, limit):
#ORDER [0] Timestamp, [1] Open, [2] High, [3] Low, [4] Close, [5] Trading Volume in security
    data = get_historical_kline_data(trading_pair, chart_interval, limit)
    
    close_data = []
    #for loop to gather closing price data
    for i in range(len(data)):
        close_data.append(float(data[i][4]))

    return close_data


"""[2] CALCULATES THE SIMPLE MOVING AVERAGE"""
def backed_SMA(trading_pair, chart_interval, indicator_interval, limit):
    close_data = extensive_data_gather(trading_pair, chart_interval, limit)
    spare_close_data = list(close_data)
    
    asset_price_sum = 0
    loop_range = limit-indicator_interval #This is the amount of times the loop will be executed
    sma_list = []
    for p in range(loop_range):
        for i in range(indicator_interval):
            asset_price_sum += spare_close_data[i]

        simple_moving_average = asset_price_sum/indicator_interval
        asset_price_sum = 0 #Reset value
        sma_list.append(simple_moving_average)
        spare_close_data.pop(0)
            
    return close_data, sma_list

def backed_EMA(trading_pair, chart_interval, indicator_interval, limit):
    data = backed_SMA(trading_pair, chart_interval, indicator_interval, limit)
    close_data = data[0]
    #print(close_data)
    sma_list = data[1]
    K = 2/(indicator_interval+1) #WEIGHTED MULTIPLIER FOR EMA
    first_EMA = close_data[indicator_interval+1]*K + sma_list[0]*(1-K) 

    ema_list = [first_EMA]
    loop_range = limit-indicator_interval-3 #This is the amount of times the loop will be executed
    for p in range(loop_range):
        #EMA = Closing price x multiplier + EMA (previous day) x (1-multiplier)
        ema_calc = close_data[indicator_interval+2+p]*K + ema_list[-1] * (1-K)
        ema_list.append(ema_calc)

    return ema_list
        

    

#print(backed_EMA(trading_pair, chart_interval, indicator_interval, limit))