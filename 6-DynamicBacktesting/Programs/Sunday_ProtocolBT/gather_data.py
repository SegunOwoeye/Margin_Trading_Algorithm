from requests import get
import pandas as pd
import datetime

class gather_data:
    def __init__(self, trading_pair, chart_interval, bt_days, limit):
        self.trading_pair = trading_pair
        self.chart_interval = chart_interval
        self.bt_days = bt_days
        self.limit = limit


    def num_intervals(self):
        #Turns value into a integer in minutes
        str_interval = self.chart_interval.lower()
        if "m" in str_interval: int_interval = int(str_interval.replace("m", ""))         
        elif "h" in str_interval: int_interval = int(str_interval.replace("h", "")) * 60        
        elif "d" in str_interval: int_interval = int(str_interval.replace("d", "")) *60*24       
        else: pass


        #Calculates the number of intervals
        num_intervals = (self.bt_days * 24 * 60) / int_interval
        
        #Calculates the number of iterations that need to occur to gather the required data
        iterations = -(-(num_intervals / self.limit) // 1)

        return num_intervals, int_interval

    def date_gathering(self):
        data = self.num_intervals()
        num_interval, interval = data

        # Get the current date and time
        now = datetime.datetime.now()
        # Subtract x days from the current date and time
        bt_date = now - datetime.timedelta(days=self.bt_days)

        #Gets list of all timestamps
        timestamps = []
        for i in range(int(num_interval) + 1):
            delta_time = datetime.timedelta(minutes=i * interval)
            ts = bt_date + delta_time
            timestamps.append(int(ts.timestamp()))
        
        start_time = []
        end_time = []
        for i in range(int(num_interval) + 1):
            if i == 0:#Captures first iteration
                start_time.append(timestamps[i])
                end_time.append(timestamps[self.limit])

            elif i % self.limit == 0 and num_interval - i > self.limit: #Caputures inbetween iterations
                start_time.append(timestamps[i])
                end_time.append(timestamps[i+self.limit])
        
            elif num_interval - i < self.limit and timestamps[i] == end_time[-1] and num_interval != i:
                start_time.append(timestamps[i])
                end_time.append(timestamps[int(num_interval)])

            else:
                pass

        return (start_time, end_time)
        
    def data_gathering(self):
        start_time, end_time = self.date_gathering()
        #Checks to see if the file already exists
        file_name = f"6-DynamicBacktesting/data_gathered/{self.trading_pair}/raw_output{self.chart_interval}.csv"
        
        #Pulls the data the first time
        for i in range(1):
            url = "https://api.binance.com/api/v3/klines"
            startTime = start_time[i] * 1000
            endTime = end_time[i] * 1000

            # Make the API request
            response = get(url, params={
                'symbol': self.trading_pair,
                'interval': self.chart_interval,
                'startTime': startTime,
                'endTime': endTime,
                'limit': self.limit
            })

            # Parse the response as JSON
            data = response.json()

            # Convert the data to a Pandas DataFrame
            df = pd.DataFrame(data, columns=[
                'open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume',
                'taker_buy_quote_asset_volume', 'ignore'
            ])

            # Convert the open_time and close_time columns to datetime
            df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
            df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')

            # Set the index to the open_time column
            df.set_index('open_time', inplace=True)

            # Print the DataFrame
            #print(df)

            df.to_csv(file_name, mode='a', header=['open', 'high', 'low', 'close', 'volume', 'close_time',
                                                'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume',
                                                    'taker_buy_quote_asset_volume', "ignore"], index=True)

        # Pulls the data everytime after to avoid headers reappearing
        for i in range(1,len(start_time)):
            url = "https://api.binance.com/api/v3/klines"
            startTime = start_time[i] * 1000
            endTime = end_time[i] * 1000

            # Make the API request
            response = get(url, params={
                'symbol': self.trading_pair,
                'interval': self.chart_interval,
                'startTime': startTime,
                'endTime': endTime,
                'limit': self.limit
            })

            # Parse the response as JSON
            data = response.json()

            # Convert the data to a Pandas DataFrame
            df = pd.DataFrame(data, columns=[
                'open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume',
                'taker_buy_quote_asset_volume', 'ignore'
            ])

            # Convert the open_time and close_time columns to datetime
            df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
            df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')

            # Set the index to the open_time column
            df.set_index('open_time', inplace=True)
            

            # Print the DataFrame
            #print(df)

            df.to_csv(file_name, mode='a', header=False ,index=True)



'''

""" TESTING """

# [1] Declaring variables
trading_pair = "BTCUSDT"
chart_interval = "5m"
bt_days = 30
limit=1000

# [2] Run
main = gather_data(trading_pair=trading_pair, chart_interval=chart_interval, bt_days=bt_days, limit=limit)
main.data_gathering()'''