# Module Includes Basic Time Series Manipulation Tools that Would need to be used throughout the progran

#Data processing imports
#import numpy as np
import pandas as pd
#import statsmodels
#import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller #coint, adfuller
#import matplotlib.pyplot as plt

class Time_Series_Analysis:
    def __init__(self, trading_pair, chart_interval, price_data=None, trading_pair2=""):
        self.trading_pair = trading_pair
        self.chart_interval = chart_interval
        self.trading_pair2 = trading_pair2
        
        # Setting Price Data
        if price_data is None: # For Testing
            file_name = f"6-DynamicBacktesting/data_gathered/{self.trading_pair}/raw_output{self.chart_interval}.csv"
            self.price_data = pd.read_csv(file_name)[["open_time", "close", "high", "low", "volume", "open"]]
            self.price_data = self.price_data.set_index("open_time")
        else: # user Inputted
            self.price_data = price_data


    # [2] Checking for Stationarity in the time series
    def stationarity_Check(self, data_type="close", cutoff = 0.05):
        """ If the time Series is stationary it will return a True, if not it will return a False
                -> Data type variable comes from the list of OHLCV data types where stationarity might need to be tested
        """
        
        # [2.1] Getting data array
        data = self.price_data[data_type]
        # Forcing column to be numerical
        data = pd.to_numeric(data, errors="coerce")
        returns = (data.pct_change().dropna() * 100)
        #print(returns)
        
        pvalue = adfuller(returns, autolag='AIC', regression='nc')[1]
        if pvalue < cutoff: # The series is likley stationary
            return True, returns
        else: # The series is likley non-stationary (trending)
            return False, returns

    # [3] Checking for Cointegration in the time series


    # [3] Garch

    # [4] ARIMA
"""

# Variables
trading_pair = "BTCUSDT"
trading_pair2 = "ETHUSDT"
chart_interval = "5m"


# Functions [RUN]
main = Time_Series_Analysis(trading_pair=trading_pair, chart_interval=chart_interval,
                            trading_pair2=trading_pair2)

print(main.stationarity_Check()[0])"""