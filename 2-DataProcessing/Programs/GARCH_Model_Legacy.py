#importing packages
import numpy as np
import pandas as pd
#from scipy.stats import shapiro


from arch import arch_model
from datetime import datetime
import sqlite3
from time import sleep
from os.path import exists
from sys import path

#Give a 10 second lead time to allow Chart history time to load

#CREATES A DATABASE FILE - WORKING
def creating_db_file(exchange_pair, exchange_names, chart_interval):
    trading_pair = exchange_pair
    
    date_and_time = (datetime.now())
    date = date_and_time.strftime("%b%d%y%H")
    ###BELOW NEEDS TO BE EDITED
    file_name = f"2-DataProcessing/data_gathered/{trading_pair}_data/" + str(date) + exchange_names + exchange_pair + "interval=" + str(chart_interval) + "GARCH_data.db"
    f = open(file_name, "x")
    
    #Defining Connection and cursor
    connection = sqlite3.connect(file_name)
    cursor = connection.cursor()

    #Creating Current exchange_tag price table]

    command1 = """CREATE TABLE IF NOT EXISTS
    processed_data(time TEXT, Volatility_n1 FLOAT, Volatility_n0 FLOAT, State TEXT)"""
    
    #IF TRADE STATUS IS OPEN, THE PURCHASE HASN'T GONE THROUGH
    #IF TRADE STATUS IS CLOSED, THE PURCHASE HAS GONE THROUGH

    cursor.execute(command1)
    connection.commit()

    #Closing the database
    connection.close()

#GATHERS THE HISTORICAL DATA OF A CERTAIN NUMBER OF KLINES - WORKING
def get_historical_data(trading_pair, exchange_name, chart_interval, indicator_interval):
    date_and_time = (datetime.now())
    date = date_and_time.strftime("%b%d%y")
    file_name = f"1-DataGathering/data_gathered/{trading_pair}_data/Historical_Klines/" + str(date) + exchange_name + trading_pair + "interval=" + str(chart_interval) + "kline_data.db"
    #print(file_name)
    if exists(file_name) == True:
        connection = sqlite3.connect(file_name)
        cursor = connection.cursor()

        cursor.execute("Select * FROM pair_price")
        
        list_check = cursor.fetchall()
        
        #COMES OUT as a LIST
        recent_log = list_check[(-indicator_interval):] #Most Recent data gathered from file
    
        connection.commit()
        #Closing the database
        connection.close()

        return recent_log
    
    else: # If the file doesn't exist, will wait 5 seconds before checking again to see if the file exists
        print("%s file does not exist" % file_name)
        sleep(5)
        get_historical_data(trading_pair, exchange_name, chart_interval, indicator_interval)

    
#GATHERS THE CURRENT DATA OF A CERTAIN NUMBER OF KLINES - WORKING
def get_current_data(trading_pair, exchange_name, chart_interval):
    date_and_time = (datetime.now())
    date = date_and_time.strftime("%b%d%y%H")
    file_name = f"1-DataGathering/data_gathered/{trading_pair}_data/Live_Data/" + str(date) + exchange_name + trading_pair + "interval=" + str(chart_interval) + "kline_data.db"
    #print(file_name)

    # Checks to see if the database exists
    if exists(file_name) == True:

        connection = sqlite3.connect(file_name)
        cursor = connection.cursor()

        cursor.execute("Select * FROM pair_price")
        
        list_check = cursor.fetchall()
        
        #COMES OUT as a LIST
        recent_log = list_check[-1] #Most Recent data gathered from file
    
        connection.commit()
        #Closing the database
        connection.close()

        return [recent_log]
    
    else: # If the file doesn't exist, will wait 5 seconds before checking again to see if the file exists
        print("%s file does not exist" % file_name)
        sleep(5)
        get_current_data(trading_pair, exchange_name, chart_interval)


def list_to_PD(trading_pair, exchange_name, chart_interval, indicator_interval):
    historical_data = get_historical_data(trading_pair, exchange_name, chart_interval, indicator_interval)
    current_data = get_current_data(trading_pair, exchange_name, chart_interval)
    data_list = historical_data + current_data # [1] Timestamp, [2] Open, [3] High, [4] Low, [5] Close, [6] Volume
    
    comp_time = []
    close_data = []
    for i in range(len(data_list)):
        data = data_list[i]
        comp_time.append(data[0])
        close_data.append(data[4])


    # dictionary of lists 
    dict = {'Timestamp': comp_time, 'Close': close_data} 
        
    df = pd.DataFrame(dict)

    return df
    

"""
USE GARCH MODEL AS A VOLATILITY FILTER FOR TRADING STRATEGIES 
- IT WILL BE USED TO ESTIMATE THE EXPECTED VOLATILITY OF AN ASSET FOR A CHOSEN TIMEFRAME
- TRADE WHEN GARCH MODEL PREDICTS VOLATILITY ABOVE THRESHOLD (FOCUSES ON TRENDING MARKETS)
"""


def Volatility_modeling(trading_pair, exchange_name, chart_interval, indicator_interval):
    #sleep(10)
    data = list_to_PD(trading_pair, exchange_name, chart_interval, indicator_interval)
    market = data["Close"]

    #print(data)
    #Setting up times
    start_time = data["Timestamp"].iloc[0]
    end_time = data["Timestamp"].iloc[-1]


    #data = arch.data.sp500.load()
    #market = data["Close"]

    if chart_interval == "4h" or "8h" or "1d":
        scale_factor = 1

    else:
        scale_factor = 10
    returns = (100 * scale_factor) * market.pct_change().dropna()

    
    #Getting Historical Volatility
    benchmark_historical_volatility_list = returns.values.tolist()
    historical_volatility_list = []
    for i in range(len(benchmark_historical_volatility_list)):
        historical_vol = benchmark_historical_volatility_list[i]
        historical_volatility_list.append(historical_vol)

    historical_volatility = np.var(historical_volatility_list) #Gets the mean historical volatility
    
    #GARCH Model Analysis
    am = arch_model(returns, vol = "GARCH", p=1, o=1, q=1, dist="studentst")
    res = am.fit(update_freq=5)
    forecasts = res.forecast(horizon = 5, start = 0, method='simulation')

    volatility_db = forecasts.variance
    benchmark_future_volatility_list = volatility_db.values.tolist()
    #print(res.summary())
    #print(volatility_db)

    #Putting all the results from the first forecast into a list
    future_volatility_list = []
    for i in range(len(benchmark_future_volatility_list)):
        future_vol = benchmark_future_volatility_list[i]
        future_volatility_list.append(future_vol[0])
    

    future_volatility_std = np.std(future_volatility_list)

    #check to see if most recent period is volatile based on x std
    std_count = 2
    #Checks to see that volatility is chart was predicted to be volatile for the two most recent series
    if round(abs(future_volatility_list[-1]),4) > round(abs(historical_volatility + std_count* future_volatility_std),4): #For a volatile period
        if round(abs(future_volatility_list[-2]),4) > round(abs(historical_volatility + std_count* future_volatility_std),4):
            volatility_check = "True"
        else:
            volatility_check = "False"

    else: #Period isn't volatile
        volatility_check = "False"
    
    
    """
    DEPENDING ON HOW TESTING GOES, MIGHT NEED TO CHANGE GARCH MODEL TO ONLY LOOK AT THE SECOND MOST RECENT VOLATILITY READING
    TO JUDGE WHETHER THE MARKET IS VOLATILE OR NOT AND USE THE MOST RECENT FOR MONITORING
    - Based on theory that period of volatility cluster together
    """

    #Returns recent, second recent, state
    return round(abs(future_volatility_list[-1]),4), round(abs(future_volatility_list[-2]),4),  volatility_check 


#PRINT Volatility DATA TO DATABASE - WORKING
def printTodatabase(exchange_pair, exchange_names, chart_interval, indicator_interval):
    volatility_results = Volatility_modeling(exchange_pair, exchange_names, chart_interval, indicator_interval)
    date_and_time = (datetime.now())
    date = date_and_time.strftime("%b%d%y%H")
    ###BELOW NEEDS TO BE EDITED
    file_name = f"2-DataProcessing/data_gathered/{exchange_pair}_data/" + str(date) + exchange_names + exchange_pair + "interval=" + str(chart_interval) + "GARCH_data.db"
    try:
        #Checks to see if there's an existing db file inside the data gathering dircetory
        if exists(file_name) == True:
            #Checks to see if program returns anything
            connection = sqlite3.connect(file_name)
            cursor = connection.cursor()
            current_time = (datetime.now())
            formatted_time = str(current_time.strftime('"%H:%M:%S"'))

            if volatility_results[2] == "False": 
                cursor.execute(f"""INSERT INTO processed_data (time, Volatility_n1, Volatility_n0, State) VALUES ({formatted_time}, 
                            {volatility_results[0]}, {volatility_results[1]}, "False")""")
                
            else:
                cursor.execute(f"""INSERT INTO processed_data (time, Volatility_n1, Volatility_n0, State) VALUES ({formatted_time}, 
                            {volatility_results[0]}, {volatility_results[1]}, "True")""")


            connection.commit()
            connection.close() #Closing the database
        
        else: #Creates new db file
            creating_db_file(exchange_pair, exchange_names, chart_interval) #Creates new file

    except Exception as e: #Message email that an error on... has occured
        print(f"2-DataProcessing/Programs/{exchange_pair}/GARCH_data_{exchange_pair}interval={chart_interval}.py has error: " + str(e))


#Run Programs
def run(trading_pair, exchange_name, chart_interval, indicator_interval):
    while 1:
        try: 
            # Checks to see if program should be suspended before running due to overlap error
            path.append("ZZ-General_Functions/Programs")
            from Suspend_programs import Suspend_programs
            Suspend_programs(interval=chart_interval)
            
            """ CHECKS TO SEE IF THE REQUIRED FILES ARE PRESENT, IF NOT IT WAITS"""
            # [1] Gets required filenames
            date_and_time = (datetime.now())
            live_date = date_and_time.strftime("%b%d%y%H")
            historical_date = date_and_time.strftime("%b%d%y")
            live_data_file = f"1-DataGathering/data_gathered/{trading_pair}_data/Live_Data/" + str(live_date) + exchange_name + trading_pair + "interval=" + str(chart_interval) + "kline_data.db"
            historical_data_file = f"1-DataGathering/data_gathered/{trading_pair}_data/Historical_Klines/" + str(historical_date) + exchange_name + trading_pair + "interval=" + str(chart_interval) + "kline_data.db"
            
            
            # [2] Checks to see if required files exists
            if exists(live_data_file) == True and exists(historical_data_file) == True:
                printTodatabase(trading_pair, exchange_name, chart_interval, indicator_interval)
                sleep(1)

            # [3] Waits 1 seconds if the required filenames don't exist
            else:
                sleep(1)
                #print("No Files yet")

        
        except Exception as e:
            print(f"2-DataProcessing/Programs/{trading_pair}/GARCH_data_{trading_pair}interval={chart_interval}.py has error: " + str(e))
            path.append("ZZ-General_Functions/Programs")
            from Error_handling import Handling_Error
            Handling_Error(e).No_Data_Table_Error()

#(run("BTCUSDT", "Binance", "4h", 1000))







