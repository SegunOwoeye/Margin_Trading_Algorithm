import vectorbt as vbt
import pandas as pd
import numpy as np
import datetime


def data(trading_pair, chart_interval):
    file_name = f"6-DynamicBacktesting/data_gathered/{trading_pair}/raw_output{chart_interval}.csv"
    close_price = pd.read_csv(file_name)[["open_time", "close"]]
    close_price = close_price.set_index("open_time")["close"]
    close_price = pd.to_numeric(close_price, errors='coerce')

    return close_price


close_price = data("BTCUSDT", "5m")


"""[1] Define the indicator, (like what is does)"""
def custom_indicator(data, rsi_window = 14, ma_window = 50):
    rsi = vbt.RSI.run(data, window=rsi_window).rsi.to_numpy()
    ma = vbt.MA.run(data, window=ma_window).ma.to_numpy()

    trend = np.where(rsi>70,-1,0)
    trend = np.where((rsi<30) & (data < ma),1,trend)

    #print(ma)


    return trend


"""[2] Build the indicator function for vectorbt"""
ind = vbt.IndicatorFactory(
    class_name = "Combination",
    short_name = "Comb",
    input_names= ["close"],
    param_names=["rsi_window", "ma_window"],
    output_names= ["value"]
).from_apply_func(
    custom_indicator, #python function
    rsi_window = 14,
    ma_window = 50
)

"""[3] Run function"""
res = ind.run(close_price, rsi_window=21, ma_window=50)

#print(res.value.to_string())
print(res.value)

"""entries = res.value == 1.0
exits = res.value == -1.0

pf = vbt.Portfolio.from_signals(close_price, entries, exits)

print(pf.stats())"""