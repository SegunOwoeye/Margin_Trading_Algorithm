from datetime import datetime
from os.path import exists
import sqlite3
from time import sleep
from statistics import median

#CREATES A DATABASE FILE - WORKING
def creating_db_file(trading_pair, exchange_name, chart_interval, db_name):    
    date_and_time = (datetime.now())
    date = date_and_time.strftime("%b%d%y%H")
    ###BELOW NEEDS TO BE EDITED
    file_name = f"2-DataProcessing/data_gathered/{trading_pair}_data/" + str(date) + exchange_name + trading_pair + "interval=" + str(chart_interval) + str(db_name) + "_data.db"
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
#GATHERS THE CURRENT DATA OF A CERTAIN NUMBER OF KLINES - WORKING
def get_current_data(trading_pair, exchange_name, chart_interval):
    date_and_time = (datetime.now())
    date = date_and_time.strftime("%b%d%y%H")
    file_name = f"1-DataGathering/data_gathered/{trading_pair}_data/Live_Data/" + str(date) + exchange_name + trading_pair + "interval=" + str(chart_interval) + "kline_data.db"
    #print(file_name)
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
#CALCULATES THE Simple Moving Average  - WORKING
def SMA(trading_pair, exchange_name, chart_interval, indicator_interval, historical_data, current_data):
    #historical_data = get_historical_data(trading_pair, exchange_name, chart_interval, indicator_interval)
    #current_data = get_current_data(trading_pair, exchange_name, chart_interval)

    data_set = historical_data + current_data

    #Gathering Closing prices
    closing_prices_list = []
    for i in range(len(data_set)):
        closing_price = data_set[i][4]
        closing_prices_list.append(closing_price)
    
    #Gathering the sum of the closing prices
    asset_price_sum = 0
    for i in range(len(closing_prices_list)):
        asset_price_sum += closing_prices_list[i]
    
    simple_moving_average = asset_price_sum/indicator_interval

    return simple_moving_average




def EMA(trading_pair, exchange_name, chart_interval, indicator_interval):
    K = 2/(indicator_interval+1) #WEIGHTED MULTIPLIER FOR EMA
    
    historical_data = get_historical_data(trading_pair, exchange_name, chart_interval, indicator_interval)
    current_data = get_current_data(trading_pair, exchange_name, chart_interval)
    recent_closing_price = current_data[-1][4]

    date = date_and_time.strftime("%b%d%y%H")
    ###BELOW NEEDS TO BE EDITED
    file_name = f"2-DataProcessing/data_gathered/{trading_pair}_data/" + str(date) + exchange_name + trading_pair + "interval=" + str(chart_interval) + "EMA_data.db"
    try:
        if exists(file_name) == True: #CHECKS TO SEE IF THE DB FILE EXISTS
            #Gathering data fro database
            connection = sqlite3.connect(file_name)
            cursor = connection.cursor()
            cursor.execute("Select * FROM processed_data")
            list_check = cursor.fetchall()



            if len(list_check) == 0: #Checks t0 see if the file has any data
                #Calculate EMA from SMA
                Simple_MA = SMA(trading_pair, exchange_name, chart_interval, indicator_interval, historical_data, current_data)
                
                first_EMA = recent_closing_price*K +Simple_MA*(1-K)
                print(first_EMA)
                



            else: #MEANS THE FILE HAS DATA
                #Calculates the EMA from previous EMA
                pass

        else: #THE FILE DOESN'T EXIST
            #Creates a new file and runs the function again
            creating_db_file(trading_pair, exchange_name, chart_interval)
            EMA(trading_pair, exchange_name, chart_interval, indicator_interval)

    except:
        pass
    

print(EMA("BTCUSDT", "ByBit", 1, 14))


