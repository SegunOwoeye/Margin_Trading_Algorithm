#STRATEGY 1: MEAN REVERSION

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
    file_name = f"4-Strategies/data_gathered/{trading_pair}_data/" + str(date) + exchange_names + exchange_pair + "interval=" + str(chart_interval) + "MR_data.db"
    f = open(file_name, "x")
    
    #Defining Connection and cursor
    connection = sqlite3.connect(file_name)
    cursor = connection.cursor()

    #Creating Current exchange_tag price table]

    command1 = """CREATE TABLE IF NOT EXISTS
    processed_data(time TEXT, Type TEXT, Quantity FLOAT, Price FLOAT, Status TEXT)"""
    
    #IF TRADE STATUS IS OPEN, THE PURCHASE HASN'T GONE THROUGH
    #IF TRADE STATUS IS CLOSED, THE PURCHASE HAS GONE THROUGH

    cursor.execute(command1)
    connection.commit()

    #Closing the database
    connection.close()

# GATHERS MEAN REVERSION DATA
def get_mr_data(trading_pair, exchange_name, chart_interval):
    date_and_time = (datetime.now())
    date = date_and_time.strftime("%b%d%y%H")
    file_name = f"2-DataProcessing/data_gathered/{trading_pair}_data/" + str(date) + exchange_name + trading_pair + "interval=" + str(chart_interval) + "MR_data.db"
    #print(file_name)
    if exists(file_name) == True:
        connection = sqlite3.connect(file_name)
        cursor = connection.cursor()

        cursor.execute("Select * FROM processed_data")
        
        list_check = cursor.fetchall()
        
        #COMES OUT as a LIST
        recent_log = list_check[(-1):] #Most Recent data gathered from file
    
        connection.commit()
        #Closing the database
        connection.close()

        return recent_log
    
    else: # If the file doesn't exist, will wait 5 seconds before checking again to see if the file exists
        print("%s file does not exist" % file_name)
        sleep(5)
        get_mr_data(trading_pair, exchange_name, chart_interval)


def decision_making(trading_pair, exchange_name, chart_interval, threshold = 2):
    data = get_mr_data(trading_pair, exchange_name, chart_interval)[0]
    time = data[0]
    stationarity = data[1]
    recent_return = data[2]
    std = data[3]
    mean = data[4]

    #Checks to see if data series is stationary or not
    if stationarity == "True": # Continues to process data
        z_score = (recent_return - mean)/std # Gets the amount of standard deviations the observed value is away from the mean
        if z_score >= threshold: # Means data is in the 5% of data that doesn't fit the time series
            pass
        else:
            pass
        print(z_score)

    else: #Does nothing
        pass




trading_pair = "BTCUSDT"
exchange_name = "Binance"
chart_interval = "4h"

(decision_making(trading_pair, exchange_name, chart_interval))