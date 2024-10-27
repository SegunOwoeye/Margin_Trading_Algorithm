import vectorbt as vbt
import pandas as pd
import numpy as np

# [0] Data for Testing
def price_data(trading_pair, chart_interval, name="close"):
    file_name = f"6-DynamicBacktesting/data_gathered/{trading_pair}/raw_output{chart_interval}.csv"
    price_data = pd.read_csv(file_name)[["open_time", name]]
    price_data = price_data.set_index("open_time")[name]
    price_data = pd.to_numeric(price_data, errors='coerce')

    return price_data



"""[1] Define the indicator, EMA function"""
def tick_returns(close_data, open_data, p_threshold=1):
    # [1.1.1] Puts Close Data into a list
    close_list = []
    for i in range(len(close_data)):
        close_list.append(close_data[i])
        
    # [1.1.2] Puts Open Data into a list
    open_list = []
    for i in range(len(open_data)):
        open_list.append(open_data[i])


    # [1.2] Calculates the Dailey Returns
    tick_returns = []
    for i in range(len(close_list)):
        tick_return = float((close_list[i] - open_list[i]) / open_list[i] * 100)
        tick_return = round(tick_return,3)
        tick_returns.append(tick_return)

    tick_p_dictionary = {"Tick_Returns": tick_returns}
    tick_df = pd.DataFrame(tick_p_dictionary)
    tick_df = tick_df.to_numpy()

    # Gathering Results
    result = np.where((tick_df>p_threshold), 1, 0) # Bullish
    result = np.where((tick_df<-p_threshold), -1, result) # Bearish

    return result


"""[2] Defining the function for vectorbt"""
tick_pReturns = vbt.IndicatorFactory(
    class_name = "Tick Percentage Returns",
    short_name = "tick_p",
    input_names = ["close", "open"],
    param_names = ['p_threshold'],
    output_names = ["value"]
).from_apply_func(
    tick_returns, #python function
    p_threshold = 1
)



"""
#FOR USE WHEN TESTING

close_data = price_data("BTCUSDT", "5m", "close")
open_data = price_data("BTCUSDT", "5m", "open")


tick_returns(close_data=close_data, open_data=open_data)

res = tick_pReturns.run(close_data, open_data, p_threshold=1)
print(res.value)"""


