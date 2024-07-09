import vectorbt as vbt
import pandas as pd
import numpy as np



#Just used to gather data, can be deleted later
def price_data(trading_pair, chart_interval, name="close"):
    file_name = f"6-DynamicBacktesting/data_gathered/{trading_pair}/raw_output{chart_interval}.csv"
    price_data = pd.read_csv(file_name)[["open_time", name]]
    price_data = price_data.set_index("open_time")[name]
    price_data = pd.to_numeric(price_data, errors='coerce')

    return price_data


"""[1] Define the indicator, EMA Crossover function"""
def rsi_movement(close_data, rsi_window=6):

    #Getting EMAs from three different windows
    rsi = vbt.RSI.run(close_data, window=rsi_window).rsi.to_numpy()

    result = np.where(rsi > np.roll(rsi, 1), 1, 0) # 1 Is a bullish sign
    result = np.where(rsi < np.roll(rsi, 1), -1, result) # -1 Is a bearish sign
    
    
    return result



"""[2] Defining the function for vectorbt"""

rsi_direction = vbt.IndicatorFactory(
    class_name = "RSI Direction",
    short_name = "RSI Dir",
    input_names = ["close"],
    param_names = ['rsi_window'],
    output_names = ["value"]
).from_apply_func(
    rsi_movement, #python function
    rsi_window = 6,
)

"""
#FOR USE WHEN TESTING

close_data = price_data("BTCUSDT", "5m", "close")


res = rsi_direction.run(close_data, rsi_window=6)
print(res.value)
"""