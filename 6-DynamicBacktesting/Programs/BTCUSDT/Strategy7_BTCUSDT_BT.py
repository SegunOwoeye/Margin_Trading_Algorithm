from requests import get
import pandas as pd
import datetime
import numpy as np
from sys import path
from os.path import exists
import time
from os import system as terminal_sys

# Statistical Imports
from statsmodels.tsa.stattools import coint
from statsmodels.tsa.vector_ar.vecm import coint_johansen
import vectorbt as vbt

#from vectorbt import Portfolio
from tqdm import tqdm
import matplotlib.pyplot as plt


""" [1] Importing Custom Library """
path.append("MM-Math_Operations/Programs")
from Time_Series_Analyzer import Time_Series_Analysis

#Used to gather price data
def price_data(trading_pair, chart_interval, name="close"):
    file_name = f"6-DynamicBacktesting/data_gathered/{trading_pair}/raw_output{chart_interval}.csv"
    price_data = pd.read_csv(file_name)[["open_time", name]]
    price_data = price_data.set_index("open_time")[name]
    price_data = pd.to_numeric(price_data, errors='coerce')

    return price_data

# BT
def num_intervals(chart_interval, bt_days, limit):
    #Turns value into a integer in minutes
    str_interval = chart_interval.lower()
    if "m" in str_interval: int_interval = int(str_interval.replace("m", ""))         
    elif "h" in str_interval: int_interval = int(str_interval.replace("h", "")) * 60        
    elif "d" in str_interval: int_interval = int(str_interval.replace("d", "")) *60*24       
    else: pass


    #Calculates the number of intervals
    num_intervals = (bt_days * 24 * 60) / int_interval
    
    #Calculates the number of iterations that need to occur to gather the required data
    iterations = -(-(num_intervals / limit) // 1)

    return num_intervals, int_interval
# BT
def date_gathering(chart_interval, bt_days, limit):
    data = num_intervals(chart_interval, bt_days, limit)
    num_interval, interval = data

    # Get the current date and time
    now = datetime.datetime.now()
    # Subtract x days from the current date and time
    bt_date = now - datetime.timedelta(days=bt_days)

    #Gets list of all timestamps
    timestamps = []
    for i in range(int(num_interval) + 1):
        delta_time = datetime.timedelta(minutes=i * interval)
        ts = bt_date + delta_time
        timestamps.append(int(ts.timestamp()))
    
    start_time = []
    end_time = []
    for i in range(int(num_interval) + 1):
        if i == 0:#Captures first iteration
            start_time.append(timestamps[i])
            end_time.append(timestamps[limit])

        elif i % limit == 0 and num_interval - i > limit: #Caputures inbetween iterations
            start_time.append(timestamps[i])
            end_time.append(timestamps[i+limit])
    
        elif num_interval - i < limit and timestamps[i] == end_time[-1] and num_interval != i:
            start_time.append(timestamps[i])
            end_time.append(timestamps[int(num_interval)])

        else:
            pass

    return (start_time, end_time)
# BT    
def data_gathering(trading_pair, chart_interval, bt_days, limit):
    start_time, end_time = date_gathering(chart_interval, bt_days, limit)
    #Checks to see if the file already exists
    file_name = f"6-DynamicBacktesting/data_gathered/{trading_pair}/raw_output{chart_interval}.csv"
    
    #Pulls the data the first time
    for i in range(1):
        url = "https://api.binance.com/api/v3/klines"
        startTime = start_time[i] * 1000
        endTime = end_time[i] * 1000

        # Make the API request
        response = get(url, params={
            'symbol': trading_pair,
            'interval': chart_interval,
            'startTime': startTime,
            'endTime': endTime,
            'limit': limit
        })

        # Parse the response as JSON
        data = response.json()

        # Convert the data to a Pandas DataFrame
        df = pd.DataFrame(data, columns=[
            'open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time',
            'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume',
            'taker_buy_quote_asset_volume', 'ignore'
        ])

        # Convert the open_time and close_time columns to datetime
        df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
        df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')

        # Set the index to the open_time column
        df.set_index('open_time', inplace=True)

        # Print the DataFrame
        #print(df)

        df.to_csv(file_name, mode='a', header=['open', 'high', 'low', 'close', 'volume', 'close_time',
                                               'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume',
                                                'taker_buy_quote_asset_volume', "ignore"], index=True)

    # Pulls the data everytime after to avoid headers reappearing
    for i in range(1,len(start_time)):
        url = "https://api.binance.com/api/v3/klines"
        startTime = start_time[i] * 1000
        endTime = end_time[i] * 1000

        # Make the API request
        response = get(url, params={
            'symbol': trading_pair,
            'interval': chart_interval,
            'startTime': startTime,
            'endTime': endTime,
            'limit': limit
        })

        # Parse the response as JSON
        data = response.json()

        # Convert the data to a Pandas DataFrame
        df = pd.DataFrame(data, columns=[
            'open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time',
            'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume',
            'taker_buy_quote_asset_volume', 'ignore'
        ])

        # Convert the open_time and close_time columns to datetime
        df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
        df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')

        # Set the index to the open_time column
        df.set_index('open_time', inplace=True)
        

        # Print the DataFrame
        #print(df)

        df.to_csv(file_name, mode='a', header=False ,index=True)



    

""" [3] Checking Signals"""
def get_signals(trading_pair, chart_interval, std_threshold=2):
    # 3.1 Stationarity
    is_stationary = []
    """TSA = Time_Series_Analysis(trading_pair=trading_pair[0], chart_interval=chart_interval)
    result = TSA.stationarity_Check()
    print(result)"""
    for i in range(len(trading_pair)):
        TSA = Time_Series_Analysis(trading_pair=trading_pair[i], chart_interval=chart_interval)
        result = TSA.stationarity_Check()
        #print(result)
        is_stationary.append({"trading_pair": trading_pair[i],
                              "chart_interval": chart_interval,
                              "Stationary": result[0],
                              "Time_Series": result[1]})
    
    # [3.2] Returns Result of the Stationarity
    stat_return = len(is_stationary)
    for p in range(len(is_stationary)):
        if is_stationary[p]["Stationary"] == True:
            stat_return -= 1
    
    # [3.3] Checking to see if the two Pairs can be cointegrated
    if stat_return == 0: 
        can_cointegrate = True
    else:
        can_cointegrate = False
    
    # [3.4] Executing trade if Cointegrated
    if can_cointegrate == True:
        returns1 = is_stationary[0]["Time_Series"] # BTC
        returns2 = is_stationary[1]["Time_Series"] # ETH

        # [3.4.1] Ensure DataFrames have the same shape
        if returns1.shape != returns2.shape:
            raise ValueError("DataFrames must have the same shape")
        
        # [3.4.2] Calculating cointegrating_vector
        merged_results = pd.concat([returns1, returns2], axis=1)
        c = coint_johansen(merged_results, det_order=0, k_ar_diff=1) 
        cointegrating_vector = c.evec[:, 0]
        #print(cointegrating_vector)
        
        # [3.4.3] Calculating Hedging Ratio
        # Normalize the vector (make the first element 1)
        hedge_ratio = round(-cointegrating_vector[1] / cointegrating_vector[0],3)

        # [3.4.4] Calculating Spread
        spread_df = returns1 - returns2 * hedge_ratio

        # [3.4.5] Determining Entry Points Based on z Score
        zscore_df = (spread_df - spread_df.mean())/spread_df.std()
        for i in range(len(zscore_df)):
            if abs(zscore_df[i]) >= 2:
                pass
                #print(zscore_df[i])
    

        signal = np.where(zscore_df >= std_threshold, 1, 0) # 1 Is a Bullish sign -> Long ETH, Short BTC
        signal = np.where(zscore_df <= -std_threshold, -1, signal) # -1 Is a Bearish sign -> Short ETH, Long BTC 
        signal = np.insert(signal, 0, 0)
        
        # [3.4.6] Determining the Exit Points
        possible_exits =  np.where(abs(round(returns1-returns2,1)) == 0, 1, 0)
        possible_exits = np.insert(possible_exits, 0, 0)

        return signal, possible_exits #Added zero to beginning since dealing with returns


        plt.plot(spread_df, label="Spread")
        plt.plot(returns1, label="BTC")
        plt.plot(returns2, label="ETH")
        plt.legend()
        plt.show()


""" [4] Backtesting Strategy 7"""
def bt_strategy7(trading_pair, chart_interval, flag= "optimise: TP/SL"):
    # [4.1] Load Data
    data = get_signals(trading_pair=trading_pair, chart_interval=chart_interval)
    signals = data[0]
    all_exit_signals = data[1]
    
    # [4.1.1] Entry Data
    # Long Entries
    long_entries = signals  == 1
    # Short Entries
    short_entries = signals == -1
    
    # [4.1.2] Exit Data
    exit_signals = all_exit_signals == 1

    # [4.1.3] Secondary Chart Data (ETH)
    #Getting the close price data
    ETH_close_price = price_data(trading_pair[1], chart_interval, name="close")
    ETH_open_price = price_data(trading_pair[1], chart_interval, name="open")
    ETH_high_price = price_data(trading_pair[1], chart_interval, name="high")
    ETH_low_price = price_data(trading_pair[1], chart_interval, name="low")
    flag=None
    # [4.2] Conducting trade analysis
    # [4.2.1] Optimising TP and SL points
    if flag == "optimise: TP/SL": 

        tp_stop =  np.linspace(2,0,21)
        sl_stop =  np.linspace(2,0,21)

        # SHORT
        short_profit_return = []
        counter = len(tp_stop) * len(sl_stop)

        short_benchmark = 0
        for i in tqdm(range(len(tp_stop))): # TP
            for n in range(len(sl_stop)): # SL
                if tp_stop[i] == 0 or sl_stop[n] == 0: # excluding 0 from list
                    counter = counter - 1
                    pass
                else:
                    # Declaring variables
                    tp = round(tp_stop[i],2)
                    sl = round(sl_stop[n],2)
        
                
                    #Short -> TP=-% | SL=+%
                    portfolio_short = vbt.Portfolio.from_signals(ETH_close_price, tp_stop=tp/100, open=ETH_open_price, #0.4
                                                        high=ETH_high_price, low=ETH_low_price, short_entries=short_entries,
                                                        sl_stop=sl/100)#, freq="5T")#, 0.8 fees=0.075/100)
                    #terminal_sys("cls")
                    

                    pfs_stats = portfolio_short.stats()
                    #print(pfs_stats)

                    total_returns = pfs_stats['Total Return [%]']
                    win_rate = pfs_stats['Win Rate [%]']
                    total_trades = pfs_stats['Total Closed Trades']

                    # Adding to List
                    short_profit_return.append({"TP": tp, "SL": sl, "Returns": total_returns, "win rate": win_rate, "total trades": total_trades})
                    #print({"TP": tp, "SL": sl, "Returns": total_returns, "win rate": win_rate, "total trades": total_trades})
                    
                    short_benchmark = pfs_stats['Benchmark Return [%]']
                    
                    #print(f'Number of iterations left: {counter}')
                    #terminal_sys("cls")
        
        
        # Nicley formatted printed list
        short_return_values = [row['Returns'] for row in short_profit_return if row['Returns'] > 0]
        average_short_returns = sum(short_return_values)/len(short_return_values)
        #terminal_sys("cls")
        print(f"Optimisation results for TP/SL: SHORT")
        for item in short_profit_return:
            if item['Returns'] < 0: #item['Returns'] < average_short_returns or (item["win rate"] <= 30): # or item['TP']< item['SL']:# or (item['Returns'] < short_benchmark):
                pass
            else:

                print(item)
        

        # Long
        long_profit_return = []
        long_benchmark = 0
        counter = len(tp_stop) * len(sl_stop)
        for i in tqdm(range(len(tp_stop))): # TP
            for n in range(len(sl_stop)): # SL
                if tp_stop[i] == 0 or sl_stop[n] == 0: # excluding 0 from list
                    counter = counter - 1
                    pass
                else:
                    # Declaring variables
                    tp = round(tp_stop[i],2)
                    sl = round(sl_stop[n],2)
        
                
                    #Short -> TP=-% | SL=+%
                    portfolio_long = vbt.Portfolio.from_signals(ETH_close_price, entries=long_entries, tp_stop=tp/100, open=ETH_open_price, #0.4
                                                        high=ETH_high_price, low=ETH_low_price,
                                                        sl_stop=sl/100)#, freq="5T")#, 0.8 fees=0.075/100)
                    #terminal_sys("cls")
                    

                    pfs_stats = portfolio_long.stats()
                    #print(pfs_stats)

                    total_returns = pfs_stats['Total Return [%]']
                    win_rate = pfs_stats['Win Rate [%]']
                    total_trades = pfs_stats['Total Closed Trades']

                    # Adding to List
                    long_profit_return.append({"TP": tp, "SL": sl, "Returns": total_returns, "win rate": win_rate, "total trades": total_trades})
                    #print({"TP": tp, "SL": sl, "Returns": total_returns, "win rate": win_rate, "total trades": total_trades})

                    counter = counter - 1
                    long_benchmark = pfs_stats['Benchmark Return [%]']
                    #print(f'Number of iterations left: {counter}')
                    #terminal_sys("cls")

        
        # Nicley formatted printed list
        #terminal_sys("cls")
        long_return_values = [row['Returns'] for row in long_profit_return if row['Returns'] > 0]
        average_long_returns = sum(long_return_values)/len(long_return_values)
        print(f"Optimisation results for TP/SL: LONG")
        for item in long_profit_return:
            if item['Returns'] < 0: #(item['Returns'] < average_long_returns) or (item["win rate"] <= 30): #or (item['TP']< item['SL']):# or (item['Returns'] < long_benchmark):
                pass
            else:

                print(item)
        
        


    # [4.2.2] Visual Inspection of Trades
    elif flag == None:
        # Short
        Short_tp = 0.90 #%
        Short_sl = 1.40 # 2 %

        # Long 
        Long_tp = 0.8
        Long_sl = 1.6 
        # customs
        trade_type = "Long"
        custom_exit = False
        
        #SHORT
        if trade_type == "Short":
            if custom_exit == False:
                portfolio_short = vbt.Portfolio.from_signals(ETH_close_price, tp_stop=Short_tp/100, open=ETH_open_price, #0.4
                                                high=ETH_high_price, low=ETH_low_price, short_entries=short_entries,
                                                sl_stop=Short_sl/100)#, 0.8 fees=0.075/100)
            else:
                portfolio_short = vbt.Portfolio.from_signals(ETH_close_price, short_exits=exit_signals, open=ETH_open_price, #0.4
                                                high=ETH_high_price, low=ETH_low_price, short_entries=short_entries,
                                                sl_stop=Short_sl/100)#, 0.8 fees=0.075/100)

        #LONG
        elif trade_type == "Long":
            if custom_exit == False:
                portfolio_short = vbt.Portfolio.from_signals(ETH_close_price, tp_stop=Long_tp/100, open=ETH_open_price, #0.4
                                                high=ETH_high_price, low=ETH_low_price, entries=long_entries,
                                                sl_stop=Long_sl/100)#, 0.8 fees=0.075/100)
            else:
                portfolio_short = vbt.Portfolio.from_signals(ETH_close_price, exits=exit_signals, open=ETH_open_price, #0.4
                                                high=ETH_high_price, low=ETH_low_price, entries=long_entries,
                                                sl_stop=Long_sl/100)#, 0.8 fees=0.075/100)
                
 

        pfs_stats = portfolio_short.stats()
        print(pfs_stats)

        total_returns = pfs_stats['Total Return [%]']
        win_rate = pfs_stats['Win Rate [%]']
        total_trades = pfs_stats['Total Closed Trades']

        print(total_returns, win_rate, total_trades)
        portfolio_short.plot().show()







"""PARAMETERS"""
#STANDARD PARAMS
trading_pair = ["BTCUSDT", "SOLUSDT"]#"ETHUSDT"]
chart_interval = "5m"


def run(trading_pair, chart_interval):
    # [0.1] Checks to see if all data files exist
    for i in range(len(trading_pair)):
        file_name = f"6-DynamicBacktesting/data_gathered/{trading_pair[i]}/raw_output{chart_interval}.csv"
        if exists(file_name): # If the file Exists | Do Nothing
            pass
        else: # If the file does NOT exist | Create the file
            #data_gathering(trading_pair[i], chart_interval, 30, 100) # -> 1h+
            data_gathering(trading_pair[i], chart_interval, 30, 1000) # -> 1m+


    # [0.2] Runs the analysis
    for i in range(len(trading_pair)):
        file_name = f"6-DynamicBacktesting/data_gathered/{trading_pair[i]}/raw_output{chart_interval}.csv"
        while True:
            bt_strategy7(trading_pair=trading_pair, chart_interval=chart_interval)
            break
        break 
            
                
            


# START PROGRAM
run(trading_pair, chart_interval)


#rand("BTCUSDT", "5m", 7, 10, "max_drawdown")


