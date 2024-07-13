# FILE COMPLETE - V1.0
from datetime import datetime
from os.path import exists
from sys import path
import sqlite3
from time import sleep

"""[1] Creating Storage File"""
#CREATES A DATABASE FILE - WORKING
def creating_db_file(trading_pair, exchange_name, chart_interval, indicator_interval, db_name = "WFC"):    
    date_and_time = (datetime.now())
    date = date_and_time.strftime("%b%d%y%H")
    ###BELOW NEEDS TO BE EDITED
    file_name = f"2-DataProcessing/data_gathered/{trading_pair}_data/{str(date)}{exchange_name}{trading_pair}interval={str(chart_interval)}tick={indicator_interval}{str(db_name)}data.db"
    f = open(file_name, "x")
    
    #Defining Connection and cursor
    connection = sqlite3.connect(file_name)
    cursor = connection.cursor()

    #Creating Current exchange_tag price table]
    #Fractal type can either be Bullish or Bearish
    command1 = f"""CREATE TABLE IF NOT EXISTS
    processed_data(time TEXT, {db_name} FLOAT)"""
    
    #IF TRADE STATUS IS OPEN, THE PURCHASE HASN'T GONE THROUGH
    #IF TRADE STATUS IS CLOSED, THE PURCHASE HAS GONE THROUGH

    cursor.execute(command1)
    connection.commit()

    #Closing the database
    connection.close()

"""[2] Gathering Necessary data for evaluation"""
#GATHERS THE HISTORICAL DATA OF A CERTAIN NUMBER OF KLINES - WORKING
def get_historical_data(trading_pair, exchange_name, chart_interval, indicator_interval):
    date_and_time = (datetime.now())
    date = date_and_time.strftime("%b%d%y")
    file_name = f"1-DataGathering/data_gathered/{trading_pair}_data/Historical_Klines/" + str(date) + exchange_name + trading_pair + "interval=" + str(chart_interval) + "kline_data.db"
    #print(file_name)
    connection = sqlite3.connect(file_name)
    cursor = connection.cursor()

    cursor.execute("Select * FROM pair_price")
    
    list_check = cursor.fetchall()
    recent_log = list_check[-(indicator_interval-1):] #Most Recent data gathered from file
  
    connection.commit()
    #Closing the database
    connection.close()

    return recent_log
# GATHERS THE DATA IN THE EMA DB FILE - WORKING
def ema_read(trading_pair, exchange_name, chart_interval, indicator_interval):
    date_and_time = (datetime.now())
    date = date_and_time.strftime("%b%d%y")
    file_name = f"2-DataProcessing/data_gathered/{trading_pair}_data/{str(date)}{exchange_name}{trading_pair}interval={str(chart_interval)}tick={indicator_interval}EMAdata.db"
    connection = sqlite3.connect(file_name)
    cursor = connection.cursor()
    cursor.execute("Select * FROM processed_data")
    list_check = cursor.fetchall()
    #COMES OUT as a LIST
    recent_log = list_check[-1] #Most Recent data gathered from file
    connection.commit()
    #Closing the database
    connection.close()
    EMA_value = recent_log[1]

    return EMA_value

"""[3] Calculating WFC"""
def WFC(trading_pair, exchange_name, chart_interval, indicator_interval):
    historical_data = get_historical_data(trading_pair, exchange_name, chart_interval, indicator_interval)
    
    #EMA Data
    EMA_value = ema_read(trading_pair, exchange_name, chart_interval, indicator_interval)
    
    if historical_data[-1][3] > EMA_value: # Long confirmation
        return 1
    elif historical_data[-1][2] < EMA_value: # Short confirmation
        return -1
    else: # No confirmation
        return 0

"""[4] PRINTING THE CALCULATED DATA TO A DATABASE"""
#PRINT WFC DATA TO DATABASE - WORKING
def printTodatabase(trading_pair, exchange_name, chart_interval, indicator_interval, db_name = "WFC"):
    wfc = WFC(trading_pair, exchange_name, chart_interval, indicator_interval)
    date_and_time = (datetime.now())
    date = date_and_time.strftime("%b%d%y%H")
    ###BELOW NEEDS TO BE EDITED
    file_name = f"2-DataProcessing/data_gathered/{trading_pair}_data/{str(date)}{exchange_name}{trading_pair}interval={str(chart_interval)}tick={indicator_interval}{str(db_name)}data.db"
    try:
        #Checks to see if there's an existing db file inside the data gathering dircetory
        if exists(file_name) == True:            
            connection = sqlite3.connect(file_name)
            cursor = connection.cursor()

            current_time = (datetime.now())
            formatted_time = str(current_time.strftime('"%H:%M:%S"'))
            cursor.execute(f"""INSERT INTO processed_data (time, {db_name}) VALUES ({formatted_time}, {(wfc)})""")

            connection.commit()
            connection.close() #Closing the database
        
        else: #Creates new db file
            creating_db_file(trading_pair, exchange_name, chart_interval, indicator_interval, db_name) #Creates new file

    except Exception as e: #Message email that an error on... has occured
        print(f"2-DataProcessing/Programs/{trading_pair}/Relative_Strength_Indicator_{trading_pair}interval={str(chart_interval)}tick={indicator_interval}.py has error: " + str(e))

"""[5] RUNNING THE PROGRAM"""
def run(trading_pair, exchange_name, chart_interval, indicator_interval, db_name = "WFC"):
    while 1:
        try: 
            """ CHECKS TO SEE IF THE REQUIRED FILES ARE PRESENT, IF NOT IT WAITS"""
            # [1] Gets required filenames
            date_and_time = (datetime.now())
            ema_date = date_and_time.strftime("%b%d%y")
            historical_date = date_and_time.strftime("%b%d%y")
            ema_data_file = f"2-DataProcessing/data_gathered/{trading_pair}_data/{str(ema_date)}{exchange_name}{trading_pair}interval={str(chart_interval)}tick={indicator_interval}EMAdata.db"
            historical_data_file = f"1-DataGathering/data_gathered/{trading_pair}_data/Historical_Klines/" + str(historical_date) + exchange_name + trading_pair + "interval=" + str(chart_interval) + "kline_data.db"
            
            # [2] Checks to see if required files exists
            if exists(ema_data_file) == True and exists(historical_data_file) == True:
                # Run File
                printTodatabase(trading_pair, exchange_name, chart_interval, indicator_interval, db_name)
                sleep(1)

            # [3] Waits 1 seconds if the required filenames don't exist
            else:
                sleep(1)
                #print("No Files yet")






        except Exception as e:
            print(f"2-DataProcessing/Programs/{trading_pair}/Relative_Strength_Indicator_{trading_pair}interval={str(chart_interval)}tick={indicator_interval}.py has error: " + str(e))
            path.append("ZZ-General_Functions/Programs")
            from Error_handling import Handling_Error
            Handling_Error(e).No_Data_Table_Error()



"""TESTING"""
#run("BTCUSDT", "Binance", "5m", 100)


