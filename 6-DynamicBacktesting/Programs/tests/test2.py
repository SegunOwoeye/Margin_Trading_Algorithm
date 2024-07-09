import yfinance as yf
import vectorbt as vbt
import pandas as pd


# Load the stock data
import numpy as np

def williams_fractals(trading_pair, chart_interval, window=3):
        file_name = f"6-DynamicBacktesting/data_gathered/{trading_pair}/raw_output{chart_interval}.csv"
        price_data = pd.read_csv(file_name)[["open_time", "high", "low"]]
        copy_price_data = price_data
        price_data = price_data.set_index("open_time").loc[:, ["high", "low"]]
                
        # Convert the data type of the 'high' and 'low' columns to float
        price_data['high'] = pd.to_numeric(price_data['high'], errors='coerce')
        price_data['low'] = pd.to_numeric(price_data['low'], errors='coerce')

        # convert to a list of lists
        list_of_lists = price_data.values.tolist()
        high_list = []
        low_list = []
        
        for i in range(len(list_of_lists)):
                high_list.append(list_of_lists[i][0])
                low_list.append(list_of_lists[i][1])

        
        date = copy_price_data.loc[:, ["open_time"]].values.tolist()
        
        
        fractal_data = []
        for i in range(len(list_of_lists)):
                if i < window or i > len(list_of_lists) - window:
                        fractal_data.append(0)
                else:
                        #Bearish fractal - 1
                        
                        if all(high_list[i] > high_list[i+j] for j in range(-window, window+1) if j != 0):
                                fractal_data.append(-1)
                        
                        #Bullish fractal 1
                        elif all(low_list[i] < low_list[i+j] for j in range(-window, window+1) if j != 0):
                                fractal_data.append(1)

                        else:
                                fractal_data.append(0)
                                
        fractal_dictionary = {"time": date, "fractal": fractal_data}
        fractal_df = pd.DataFrame(fractal_dictionary)




        # Convert the DataFrame to a string
        df_str = fractal_df.to_string()
        # Print the DataFrame line by line
        for line in df_str.split('\n'):
                print(line)
        


    

# Example usage






fractals = williams_fractals("BTCUSDT", "5m")
print(fractals)