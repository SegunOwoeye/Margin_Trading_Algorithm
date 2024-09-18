from gather_data import gather_data
import pandas as pd
from sys import path
import matplotlib.pyplot as plt



#main = gather_data(trading_pair=trading_pair, chart_interval=chart_interval, bt_days=bt_days, limit=limit)
#main.data_gathering()


class BT_Strategy2:
    def __init__(self, trading_pair: str, chart_interval: str, short_rsi_window: int, long_rsi_window: int, 
                 short_e1_window: int, short_e2_window: int, short_e3_window: int, 
                 long_e1_window: int, long_e2_window: int, long_e3_window: int, data: dict = None):
        self.data = data
        self.trading_pair = trading_pair
        self.chart_interval = chart_interval
        self.short_rsi_window = short_rsi_window
        self.long_rsi_window = long_rsi_window
        self.short_e1_window = short_e1_window
        self.short_e2_window = short_e2_window
        self.short_e3_window = short_e3_window
        self.long_e1_window = long_e1_window
        self.long_e2_window = long_e2_window
        self.long_e3_window = long_e3_window

    
    def read_data(self):
        file_name = f"6-DynamicBacktesting/data_gathered/{self.trading_pair}/raw_output{self.chart_interval}.csv"
        price_data = pd.read_csv(file_name)[["open_time", "close", "high", "low", "open", "volume"]]
        price_data = price_data.set_index("open_time")
        return price_data


    def format_data_vbt(self):
        # [1] Importing data, Either from a file or user inputted 
        # [1.1] Gathering data Either from a file or user inputted 
        if self.data == None:
            self.data = self.read_data()
        else:
            pass 
        
        pairs_data = self.data

        # [2] Sectioning OHLCV columns into appropriate variables

        # [2.1] Converting database columns to floats variables
        pairs_data['close'] = pd.to_numeric(pairs_data['close'], errors="coerce")
        pairs_data['high'] = pd.to_numeric(pairs_data['high'], errors="coerce")
        pairs_data['low'] = pd.to_numeric(pairs_data['low'], errors="coerce")
        pairs_data['open'] = pd.to_numeric(pairs_data['open'], errors="coerce")
        pairs_data['volume'] = pd.to_numeric(pairs_data['volume'], errors="coerce")
        
        return pairs_data

        #print(price_data.dtypes)

    
    def strategy(self, wf_window = 3):
        # [1] Importing 
        # [1.1] Importing Custom Libaries -> CUSTOM
        path.append("6-DynamicBacktesting/Programs/custom_bt")
        from william_fractal_bt import william_fractal #Need to import the indicator name
        from ema_crossover_bt import ema_crossover
        from rsi_direction_bt import rsi_direction
        from wf_cap_confirmation_bt import wf_confirmation

        # [1.2] Importing Data
        pairs_data = self.format_data_vbt()
        
        # [1.3] Seperating dataframe into columns
        close_price = pairs_data['close']
        high_price = pairs_data['high']
        low_price = pairs_data['low']
        open_price = pairs_data['open']
        asset_volume = pairs_data['volume']

        
        # [2] Getting Indicator values
        # [2.1] Short Signals
        short_wf = william_fractal.run(high_price, low_price, window=wf_window).value
        short_ema_cross = ema_crossover.run(close_price, EMA1_window=self.short_e1_window,
                                   EMA2_window=self.short_e2_window, EMA3_window=self.short_e3_window).value
        short_rsi_dir = rsi_direction.run(close_price, rsi_window=self.short_rsi_window).value
        short_wf_cap = wf_confirmation.run(high_price, low_price, close_price, window=self.short_e3_window).value
        # Taking the sum of the signals, should be -4 to Short
        short_signal_sum = short_wf + short_ema_cross + short_rsi_dir + short_wf_cap

        #[2.2] Long Signals
        long_wf = william_fractal.run(high_price, low_price, window=wf_window).value
        long_ema_cross = ema_crossover.run(close_price, EMA1_window=self.long_e1_window,
                                   EMA2_window=self.long_e2_window, EMA3_window=self.long_e3_window).value
        long_rsi_dir = rsi_direction.run(close_price, rsi_window=self.long_rsi_window).value
        long_wf_cap = wf_confirmation.run(high_price, low_price, close_price, window=self.long_e3_window).value
        # Taking the sum of the signals, should be 4 to LONG
        long_signal_sum = long_wf + long_ema_cross + long_rsi_dir + long_wf_cap

        # [2.3] Getting a Boolean List of Long/Short Entry Confirmations
        long_entries = long_signal_sum == 4.0
        short_entries = short_signal_sum == -4.0

        # [3] Portfolio

        # [3.1] Extract keys and values

        dates = []
        prices = []
        for key, value in close_price.items():
            dates.append(key)
            prices.append(value)

        print(prices)

        


         



""" TESTING """

# [1] Declaring variables
trading_pair = "BTCUSDT"
chart_interval = "5m"
bt_days = 30
limit=1000

""" [2] PARAMETERS"""
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







main = BT_Strategy2(trading_pair=trading_pair, chart_interval=chart_interval, short_rsi_window=short_rsi_window, long_rsi_window=long_rsi_window,
                    short_e1_window=short_e1_window, short_e2_window=short_e2_window, short_e3_window=short_e3_window,
                    long_e1_window=long_e1_window,long_e2_window=long_e2_window,long_e3_window=long_e3_window)
main.strategy()

