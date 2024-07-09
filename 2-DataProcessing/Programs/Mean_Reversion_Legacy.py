#get a model that models mean reversion to have a notion of when a asset might mean revert

#Data processing imports
import numpy as np
import pandas as pd
import statsmodels
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint, adfuller
import matplotlib.pyplot as plt

#from scipy.stats import shapiro

#General Use Imports
from datetime import datetime
import sqlite3
from time import sleep
from os.path import exists

#CREATES A DATABASE FILE - DONE
def creating_db_file(exchange_pair, exchange_names, chart_interval):
    trading_pair = exchange_pair
    
    date_and_time = (datetime.now())
    date = date_and_time.strftime("%b%d%y%H")
    ###BELOW NEEDS TO BE EDITED
    file_name = f"2-DataProcessing/data_gathered/{trading_pair}_data/" + str(date) + exchange_names + exchange_pair + "interval=" + str(chart_interval) + "MR_data.db"
    f = open(file_name, "x")
    
    #Defining Connection and cursor
    connection = sqlite3.connect(file_name)
    cursor = connection.cursor()

    #Creating Current exchange_tag price table]

    command1 = """CREATE TABLE IF NOT EXISTS
    processed_data(time TEXT, Stationarity TEXT, recent_return FLOAT, std FLOAT, mean FLOAT, var FLOAT, cov FLOAT, corrcoeff FLOAT)"""
    
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
THE PROGRAM CHECKS TO SEE IF THE DATA SERIES IS STATIONARY, BECAUSE IF THE TIME SERIES IS STATIONARY
THEN IT IS IMPLIED TO BE MEAN REVERTING IN ADDITION.

IF THE TIME SERIES IS MEAN REVERTING, THAN ESSENTIAL STATISTICAL DATA ABOUT THE SERIES IS GATHERED
AND LISTED ON A DATABASE
"""
# Checks to see if the data series is stationary or not - WORKING
def stationarity_check(trading_pair, exchange_name, chart_interval, indicator_interval, cutoff = 0.01):
    data = list_to_PD(trading_pair, exchange_name, chart_interval, indicator_interval)
    market = data["Close"]
    returns = (market.pct_change().dropna() * 100)

    #graphical observations
    """plt.plot(returns)
    plt.show()"""

    pvalue = adfuller(returns)[1]
    #print(pvalue)
    if pvalue < cutoff: # The series is likley stationary
        return True, returns
    else: # The series is likley non-stationary (trending)
        return False

# CONFIRMS THE DATA SERIES IS STATIONARY, IMPLYING THE SERIES IS MEAN REVERTING - WORKING
def mean_reversion(trading_pair, exchange_name, chart_interval, indicator_interval):
    info = stationarity_check(trading_pair, exchange_name, chart_interval, indicator_interval)
    stationarity = info[0]
    returns = info[1]
    
    #Checks to see if the returns are stationary or not
    if stationarity == True: # Stationary
        returns_standard_deviation = np.std(returns)
        returns_mean = np.mean(returns)
        returns_variance = np.var(returns)
        returns_covriance = np.cov(returns) + 0.00
        returns_correlationcoefficient = np.corrcoef(returns) 
        #plt.plot(returns)
        #plt.show()
        
        recent_return = returns.iloc[-1]
        return ((stationarity), recent_return, returns_standard_deviation, returns_mean,
            returns_variance, returns_covriance, returns_correlationcoefficient
        )



    else: # Non Stationary
        return (stationarity), recent_return

#PRINT MEAN REVERSION DATA TO DATABASE - WORKING
def printTodatabase(exchange_pair, exchange_names, chart_interval, indicator_interval):
    mr_results = mean_reversion(exchange_pair, exchange_names, chart_interval, indicator_interval) #mean reversion results
    #print(mr_results[0])
    date_and_time = (datetime.now())
    date = date_and_time.strftime("%b%d%y%H")
    file_name = f"2-DataProcessing/data_gathered/{exchange_pair}_data/" + str(date) + exchange_names + exchange_pair + "interval=" + str(chart_interval) + "MR_data.db"
    try:
        #Checks to see if there's an existing db file inside the data gathering dircetory
        if exists(file_name) == True:
            #Checks to see if program returns anything
            connection = sqlite3.connect(file_name)
            cursor = connection.cursor()
            current_time = (datetime.now())
            formatted_time = str(current_time.strftime('"%H:%M:%S"'))

            if mr_results[0] == 1: # Stationary time series
                #time TEXT, Stationarity TEXT, std FLOAT, mean FLOAT, var FLOAT, cov FLOAT, corrcoeff FLOAT
                cursor.execute(f"""INSERT INTO processed_data (time, Stationarity, recent_return, std, mean, var, cov, corrcoeff) VALUES 
                               ({formatted_time}, "{mr_results[0]}", {mr_results[1]},  {mr_results[2]}, {mr_results[3]}, 
                               {mr_results[4]}, {mr_results[5]}, {mr_results[6]})""")
                
            else: # Non-Stationary time series
                cursor.execute(f"""INSERT INTO processed_data (time, Stationarity, recent_return, std, mean, var, cov, corrcoeff) VALUES 
                               ({formatted_time}, "{mr_results[0]}", {mr_results[1]}, 0, 0, 0, 0, 0)""")


            connection.commit()
            connection.close() #Closing the database
        
        else: #Creates new db file
            creating_db_file(exchange_pair, exchange_names, chart_interval) #Creates new file

    except Exception as e: #Message email that an error on... has occured
        print(f"2-DataProcessing/Programs/{exchange_pair}/Mean_Reversion_{exchange_pair}interval={chart_interval}.py has error: " + str(e))

#Run Programs
def run(trading_pair, exchange_name, chart_interval, indicator_interval):
    while 1:
        try: 
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
            print(f"2-DataProcessing/Programs/{trading_pair}/Mean_Reversion_{trading_pair}interval={chart_interval}.py has error: " + str(e))


#(run("BTCUSDT", "Binance", "5m", 100))