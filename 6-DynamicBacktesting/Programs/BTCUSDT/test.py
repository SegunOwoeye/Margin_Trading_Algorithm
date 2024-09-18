from requests import get
import pandas as pd
import datetime
#import vectorbt as vbt
import numpy as np
from sys import path
from os.path import exists
import time
from os import system as terminal_sys
from vectorbt import Portfolio


# Custom indicators
path.append("6-DynamicBacktesting/Programs/custom_bt")
from william_fractal_bt import william_fractal #Need to import the indicator name
from ema_crossover_bt import ema_crossover
from rsi_direction_bt import rsi_direction
from wf_cap_confirmation_bt import wf_confirmation

#path.append("")#reset import

#Used to gather price data
def price_data(trading_pair, chart_interval, name="close"):
    file_name = f"6-DynamicBacktesting/data_gathered/{trading_pair}/raw_output{chart_interval}.csv"
    price_data = pd.read_csv(file_name)[["open_time", name]]
    price_data = price_data.set_index("open_time")[name]
    price_data = pd.to_numeric(price_data, errors='coerce')

    return price_data


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


# Custom
def get_signals(trading_pair, chart_interval, rsi_window, ema1_window, ema2_window, 
                ema3_window, hm_spaceing, metric):
    
    #long = (out_a > out_b) and (out_a > out_c) and downFractal and low[2] > out_c and rsi[2] < rsi
    #short = (out_a < out_b) and (out_a < out_c) and upFractal and high[2] < out_c and rsi[2] > rsi

    file_name = f"6-DynamicBacktesting/data_gathered/{trading_pair}/raw_output{chart_interval}.csv"
    price_data = pd.read_csv(file_name)[["open_time", "close", "high", "low"]]
    price_data = price_data.set_index("open_time")

    #Converting database columns to floats variables
    price_data['close'] = pd.to_numeric(price_data['close'], errors="coerce")
    price_data['high'] = pd.to_numeric(price_data['high'], errors="coerce")
    price_data['low'] = pd.to_numeric(price_data['low'], errors="coerce")

    close_price = price_data['close']
    high_price = price_data['high']
    low_price = price_data['low']

    #print(price_data.dtypes)

    wf = william_fractal.run(high_price, low_price, window=3)
    ema_cross = ema_crossover.run(close_price, EMA1_window=ema1_window,
                                   EMA2_window=ema2_window, EMA3_window=ema3_window)
    rsi_dir = rsi_direction.run(close_price, rsi_window=rsi_window)
    wf_cap = wf_confirmation.run(high_price, low_price, close_price, window=ema3_window)
    
    return wf.value, ema_cross.value, rsi_dir.value, wf_cap.value

#####################################################################################

def it_bt(trading_pair, chart_interval, short_rsi_window, short_ema1_window, short_ema2_window, 
                short_ema3_window, long_rsi_window, long_ema1_window, long_ema2_window, 
                long_ema3_window, hm_spaceing, metric, sl, tp):
    #Short
    short_signals = get_signals(trading_pair, chart_interval, short_rsi_window, short_ema1_window, short_ema2_window, 
                short_ema3_window, hm_spaceing, metric)
    short_wf = short_signals[0]
    short_ema_cross = short_signals[1]
    short_rsi_dir = short_signals[2]
    short_wf_cap = short_signals[3]

    # Taking the sum of the signals, should be 4 to buy or -4 to sell
    short_signal_sum = short_wf + short_ema_cross + short_rsi_dir + short_wf_cap
    
    #Long
    long_signals = get_signals(trading_pair, chart_interval, long_rsi_window, long_ema1_window, long_ema2_window, 
                long_ema3_window, hm_spaceing, metric)
    
    long_wf = long_signals[0]
    long_ema_cross = long_signals[1]
    long_rsi_dir = long_signals[2]
    long_wf_cap = long_signals[3]

    # Taking the sum of the signals, should be 4 to buy or -4 to sell
    long_signal_sum = long_wf + long_ema_cross + long_rsi_dir + long_wf_cap
    
    #long
    long_entries = long_signal_sum == 4.0

    #short
    short_entries = short_signal_sum == -4.0
    
    #Getting the close price data
    close_price = price_data(trading_pair, chart_interval, name="close")
    open_price = price_data(trading_pair, chart_interval, name="open")
    high_price = price_data(trading_pair, chart_interval, name="high")
    low_price = price_data(trading_pair, chart_interval, name="low")

    #Short
    portfolio_short = Portfolio.from_signals(close_price, tp_stop=tp, open=open_price, #0.4
                                        high=high_price, low=low_price, short_entries=short_entries,
                                        sl_stop=sl)#, 0.8 fees=0.075/100)
    #terminal_sys("cls")
    

    pfs_stats = portfolio_short.stats()
    #print(pfs_stats)

    total_returns = pfs_stats['Total Return [%]']
    win_rate = pfs_stats['Win Rate [%]']
    total_trades = pfs_stats['Total Closed Trades']

    # Adding to List
    return ({"TP": tp, "SL": sl, "Returns": total_returns, "win rate": win_rate, "total trades": total_trades})
    


def strategy(trading_pair, chart_interval, short_rsi_window, short_ema1_window, short_ema2_window, 
                short_ema3_window, long_rsi_window, long_ema1_window, long_ema2_window, 
                long_ema3_window, hm_spaceing, metric, flag ="optimise: TP/SL"):
    tp_stop =  np.linspace(0,1,11)
    sl_stop =  np.linspace(0,1,11)

    # Testing
    profit_return = []
    for i in range(len(tp_stop)): # TP
        for n in range(len(sl_stop)): # SL
            if tp_stop[i] == 0 or sl_stop[n] == 0: # excluding 0 from list
                pass
            else:
                # Declaring variables
                tp = round(tp_stop[i],2)
                sl = round(sl_stop[n],2)
                test = it_bt(trading_pair, chart_interval, short_rsi_window, short_ema1_window, short_ema2_window, 
                            short_ema3_window, long_rsi_window, long_ema1_window, long_ema2_window, 
                            long_ema3_window, hm_spaceing, metric, sl, tp)
                print(test)

"""PARAMETERS"""
#SHORT
short_rsi_window = 12 #RSI window Short 14 
short_e1_window = 15 #EMA 1 window short: 15 
short_e2_window = 45 #EMA 2 window short: 45
short_e3_window = 90 #EMA 3 window short: 90 

#LONG
long_rsi_window = 6 #RSI window Long: 6
long_e1_window = 20 #EMA 1 window Long: 20
long_e2_window = 50 #EMA 2 window Long: 50
long_e3_window = 100 #EMA 3 window Long: 100

#STANDARD PARAMS
trading_pair = "BTCUSDT"
chart_interval = "5m"


strategy(trading_pair, chart_interval, short_rsi_window, short_e1_window, short_e2_window, short_e3_window,
                        long_rsi_window, long_e1_window, long_e2_window, long_e3_window, 
                        10, "total_return")