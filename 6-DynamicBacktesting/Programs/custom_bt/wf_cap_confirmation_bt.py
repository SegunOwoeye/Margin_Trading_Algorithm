import vectorbt as vbt
import pandas as pd

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


"""[1] Define the indicator, WFc function"""
def WFc(high_data, low_data, close_data, window=100):
    #Getting EMA Data
    ema1 = exponential_MA.run(close_data, window=window).value.to_numpy()
    #Puts high and low price data into lists
    high_list = []
    low_list = []
    #date_list = []
    for i in range(len(high_data)):
        #date_list.append(high_data[i][0])
        high_list.append(high_data[i][0])
        low_list.append(low_data[i][0])
    

    signal_list = []
    for i in range(1,len(high_data)):
        if low_list[i-1] > ema1[i]: #long confirmation
            signal_list.append(1)
        elif high_list[i-1] < ema1[1]: #short confirmation
            signal_list.append(-1)
        else: #no confirmation
            signal_list.append(0)
    
    
    signal_data = [0] + signal_list
    signal_dictionary = {"Signal": signal_data}
    signal_df = pd.DataFrame(signal_dictionary)

    return signal_df

"""[2] Defining the function for vectorbt"""

wf_confirmation = vbt.IndicatorFactory(
    class_name = "William Fractal Limit Confirmation",
    short_name = "WF Cap Confirmation",
    input_names = ["high", "low", "close"],
    param_names = ['window'],
    output_names = ["value"]
).from_apply_func(
    WFc, #python function
    window = 100
)


"""
high_data = price_data("BTCUSDT", "5m", "high")
low_data = price_data("BTCUSDT", "5m", "low")
close_data = price_data("BTCUSDT", "5m", "close")


res = wf_confirmation.run(high_data, low_data, close_data, window=100)
print(res.value)
"""

"""
entries = res.value == 1.0
exits = res.value == -1.0


pf = vbt.Portfolio.from_signals(close_data, entries, exits,  init_cash=40000)


print(pf.stats())
pf.plot().show()

"""