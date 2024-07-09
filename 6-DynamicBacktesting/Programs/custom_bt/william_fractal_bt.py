import vectorbt as vbt
import pandas as pd

"""
NOTES:

- When it comes to this indicator, the user needs to keep in mind that the signal being given to buy or sell is
x window intervals behind.
    
    -For Example/
    If the user sets the window to 3, the signal will be given 3 intervals after the williams fractal appeard


"""



#Just used to gather data, can be deleted later
def price_data(trading_pair, chart_interval, name="close"):
    file_name = f"6-DynamicBacktesting/data_gathered/{trading_pair}/raw_output{chart_interval}.csv"
    price_data = pd.read_csv(file_name)[["open_time", name]]
    price_data = price_data.set_index("open_time")[name]
    price_data = pd.to_numeric(price_data, errors='coerce')

    return price_data


"""[1] Define the indicator, WF function"""
def WF(high_data, low_data, window=3):

    #Puts high and low price data into lists
    high_list = []
    low_list = []
    #date_list = []
    for i in range(len(high_data)):
        #date_list.append(high_data[i][0])
        high_list.append(high_data[i][0])
        low_list.append(low_data[i][0])
    
    #print(high_list)

    #date_list = copy_price_data.loc[:, ["open_time"]].values.tolist()
    fractal_data = []
    for i in range(len(high_data)):
        if i < window or i > len(high_data) - window:
            fractal_data.append(0)

        else:
            #Bearish fractal = 1
            if all(high_list[i] > high_list[i+j] for j in range(-window, window) if j != 0):
                fractal_data.append(-1)
            
            #Bullish fractal = 1
            elif all(low_list[i] < low_list[i+j] for j in range(-window, window) if j != 0):
                fractal_data.append(1)

            else: #No fractal = 0
                fractal_data.append(0)

    #fractal_dictionary = {"time": date_list, "fractal": fractal_data}
    fractal_data = [0] * window + fractal_data[:-window]
    fractal_dictionary = {"fractal": fractal_data}
    fractal_df = pd.DataFrame(fractal_dictionary)
    #print(fractal_df)
    #fractal_df = fractal_df.set_index("time")['fractal', "space1"]

    return fractal_df

"""[2] Defining the function for vectorbt"""

william_fractal = vbt.IndicatorFactory(
    class_name = "Williams Fractal",
    short_name = "WF",
    input_names = ["high", "low"],
    param_names = ['window'],
    output_names = ["value"]
).from_apply_func(
    WF, #python function
    window = 3
)


"""
high_data = price_data("BTCUSDT", "5m", "high")
low_data = price_data("BTCUSDT", "5m", "low")
close_data = price_data("BTCUSDT", "5m", "close")


res = william_fractal.run(high_data, low_data, window=3)
#print(res.value)



entries = res.value == 1.0
exits = res.value == -1.0


pf = vbt.Portfolio.from_signals(close_data, entries, exits,  init_cash=40000)


print(pf.stats())
pf.plot().show()

"""