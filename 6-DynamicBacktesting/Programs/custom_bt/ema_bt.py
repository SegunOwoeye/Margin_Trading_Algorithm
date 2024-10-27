import vectorbt as vbt
import pandas as pd

#Just used to gather data, can be deleted later
def price_data(trading_pair, chart_interval, name="close"):
    file_name = f"6-DynamicBacktesting/data_gathered/{trading_pair}/raw_output{chart_interval}.csv"
    price_data = pd.read_csv(file_name)[["open_time", name]]
    price_data = price_data.set_index("open_time")[name]
    price_data = pd.to_numeric(price_data, errors='coerce')

    return price_data


"""[1] Define the indicator, EMA function"""
def ema(close_data, window=20):

    # Puts Close Data into a list
    close_list = []
    #date_list = []
    for i in range(len(close_data)):
        #date_list.append(high_data[i][0])
        close_list.append(close_data[i][0])

    #Calculating simple moving average
    spare_close_data = list(close_list)
    limit = len(close_list)

    asset_price_sum = 0
    loop_range = limit-window #This is the amount of times the loop will be executed
    sma_list = []

    for p in range(loop_range):
        for i in range(window):
            asset_price_sum += spare_close_data[i]

        simple_moving_average = asset_price_sum/window
        asset_price_sum = 0 #Reset value
        sma_list.append(simple_moving_average)
        spare_close_data.pop(0)
    
    #Calculating EMA
    K = 2/(window+1) #WEIGHTED MULTIPLIER FOR EMA
    first_EMA = close_list[window+1]*K + sma_list[0]*(1-K) 
    
    ema_list = [first_EMA]
    
    #print(close_list[window+2+978])

    loop_range2 = limit-window-1 #This is the amount of times the loop will be executed
    for p in range(loop_range2):
        #EMA = Closing price x multiplier + EMA (previous day) x (1-multiplier)
        ema_calc = close_list[window+1+p]*K + ema_list[-1] * (1-K)
        #print(p, ema_calc, close_list[window+2+p]*K, ema_list[-1] * (1-K))
        ema_list.append(ema_calc)
        
    # this is one time interval behind
    # to fill up the list of data coming in, the first n intervals from the window will use the closing price as the EMA, 
    # same will happen for the last price
    
    ema_list = close_list[:window] + ema_list
    
    ema_dictionary = {"fractal": ema_list}
    ema_df = pd.DataFrame(ema_dictionary)
    #print(fractal_df)
    #fractal_df = fractal_df.set_index("time")['fractal', "space1"]

    return ema_df



"""[2] Defining the function for vectorbt"""
exponential_MA = vbt.IndicatorFactory(
    class_name = "Exponential Moving Average",
    short_name = "EMA",
    input_names = ["close"],
    param_names = ['window'],
    output_names = ["value"]
).from_apply_func(
    ema, #python function
    window = 20
)


"""
#FOR USE WHEN TESTING

close_data = price_data("BTCUSDT", "5m", "close")


res = exponential_MA.run(close_data, window=20)
print(res.value)

"""

