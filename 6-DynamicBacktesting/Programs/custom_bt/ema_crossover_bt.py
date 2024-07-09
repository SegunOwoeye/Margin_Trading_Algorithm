import vectorbt as vbt
import pandas as pd
import numpy as np


from sys import path

# Custom indicators
path.append("6-DynamicBacktesting/Programs/custom_bt")
from ema_bt import exponential_MA #Need to import the indicator name



#Just used to gather data, can be deleted later
def price_data(trading_pair, chart_interval, name="close"):
    file_name = f"6-DynamicBacktesting/data_gathered/{trading_pair}/raw_output{chart_interval}.csv"
    price_data = pd.read_csv(file_name)[["open_time", name]]
    price_data = price_data.set_index("open_time")[name]
    price_data = pd.to_numeric(price_data, errors='coerce')

    return price_data


"""[1] Define the indicator, EMA Crossover function"""
def ema_cross(close_data, EMA1_window=20, EMA2_window=50, EMA3_window=100):

    #Getting EMAs from three different windows
    ema1 = exponential_MA.run(close_data, window=EMA1_window).value.to_numpy()
    ema2 = exponential_MA.run(close_data, window=EMA2_window).value.to_numpy()
    ema3 = exponential_MA.run(close_data, window=EMA3_window).value.to_numpy()
    
    result = np.where((ema1 > ema2) & (ema1 > ema3), 1, 0)
    result = np.where((ema1 < ema2) & (ema1 < ema3), -1, result)
    
    return result



"""[2] Defining the function for vectorbt"""

ema_crossover = vbt.IndicatorFactory(
    class_name = "Exponential Moving Average Crossover",
    short_name = "EMA Cross",
    input_names = ["close"],
    param_names = ['EMA1_window', 'EMA2_window', "EMA3_window"],
    output_names = ["value"]
).from_apply_func(
    ema_cross, #python function
    EMA1_window = 20,
    EMA2_window = 50, 
    EMA3_window = 100
)


"""FOR USE WHEN TESTING

close_data = price_data("BTCUSDT", "5m", "close")


res = ema_crossover.run(close_data, EMA1_window=20, EMA2_window=50, EMA3_window=100)
print(res.value)
"""