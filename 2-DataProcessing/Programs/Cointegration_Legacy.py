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

#Give a 10 second lead time to allow Chart history time to load

#CREATES A DATABASE FILE - WIP
def creating_db_file(exchange_pair, exchange_names, chart_interval):
    trading_pair = exchange_pair
    
    date_and_time = (datetime.now())
    date = date_and_time.strftime("%b%d%y%H")
    ###BELOW NEEDS TO BE EDITED
    file_name = f"2-DataProcessing/data_gathered/{trading_pair}_data/" + str(date) + exchange_names + exchange_pair + "interval=" + str(chart_interval) + "Cointegration_data.db"
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
    
# Checks to see if the data series is stationary or not
def stationarity_check(trading_pair, exchange_name, chart_interval, indicator_interval, cutoff = 0.01):
    data = list_to_PD(trading_pair, exchange_name, chart_interval, indicator_interval)
    market = data["Close"]
    returns = (market.pct_change().dropna() * 100)

    #graphical observations
    plt.plot(returns)
    plt.show()

    pvalue = adfuller(returns)[1]
    if pvalue < cutoff: # The series is likley stationary
        return True
    else: # The series is likley non-stationary (trending)
        return False

"""

"""

def cointegration(trading_pair1, trading_pair2, exchange_name, chart_interval, indicator_interval, cutoff = 0.05):
    #Returns for Asset 1
    data1 = list_to_PD(trading_pair1, exchange_name, chart_interval, indicator_interval)
    market1 = data1["Close"]
    returns1 = market1.pct_change().dropna() * 100
    
    #Returns for Asset 2
    data2 = list_to_PD(trading_pair2, exchange_name, chart_interval, indicator_interval)
    market2 = data2["Close"]
    returns2 = market2.pct_change().dropna() * 100

    plt.plot(returns1)
    plt.plot(returns2)
    plt.legend([trading_pair1, trading_pair2])
    plt.show()

    
    c = coint(returns1, returns2)
    pvalue = c[1]
    print(c)
    if pvalue < cutoff: # The series is likley cointegrated
        return True
    else: # The series is likley non-cointegrated 
        return False
    


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
            printTodatabase(trading_pair, exchange_name, chart_interval, indicator_interval)
            sleep(1)
        except Exception as e:
            print(f"2-DataProcessing/Programs/{trading_pair}/GARCH_data_{trading_pair}interval={chart_interval}.py has error: " + str(e))

#print(stationarity_check("BTCUSDT", "Binance", "4h", 100))
print(cointegration("BTCUSDT", "ETHUSDT", "Binance", "4h", 100))
#(run("BTCUSDT", "Binance", "4h", 1000))







