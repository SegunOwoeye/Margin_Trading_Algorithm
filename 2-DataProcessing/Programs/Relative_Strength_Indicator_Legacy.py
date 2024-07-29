from datetime import datetime
from os.path import exists
from sys import path
import sqlite3
from time import sleep

#CREATES A DATABASE FILE - WORKING
def creating_db_file(trading_pair, exchange_name, chart_interval, indicator_interval, db_name = "RSI"):    
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
    recent_log = list_check[-(indicator_interval):] #Most Recent data gathered from file
  
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
#CALCULATES THE Relative Strength Indicator  - WORKING
def RSI(trading_pair, exchange_name, chart_interval, indicator_interval):
    historical_data = get_historical_data(trading_pair, exchange_name, chart_interval, indicator_interval)
    current_data = get_current_data(trading_pair, exchange_name, chart_interval)

    data_set = historical_data + current_data

    #Gathering Closing prices
    closing_prices_list = []
    for i in range(len(data_set)):
        closing_price = data_set[i][4]
        closing_prices_list.append(closing_price)
    
    # Calculating the returns 
    returns_list = []
    for i in range(len(closing_prices_list)):
        try:
            returns = (closing_prices_list[i] - closing_prices_list[i-1])
            returns_list.append(returns)
        except:
            pass
    
    returns_list.remove(returns_list[0])

    # Calculating the average gain and loss
    gains = []
    losses = []
    for i in range(len(returns_list)):
        if returns_list[i] > 0: #Gains
            gains.append(returns_list[i])
        elif returns_list[i] < 0: #Loss
            losses.append(returns_list[i])
        else:
            pass

    average_gains = sum(gains)/len(closing_prices_list)
    average_losses = sum(losses)/len(closing_prices_list)
    
    try:
        rsi = 100 - (100/(1+abs(average_gains/average_losses)))
        rsi = round(rsi,2)
    except Exception as e:
        path.append("ZZ-General_Functions/Programs")
        from Error_handling import Handling_Error
        rsi = Handling_Error(e).div_by_zero_error()




    return rsi

    


#PRINT RSI DATA TO DATABASE - WORKING
def printTodatabase(trading_pair, exchange_name, chart_interval, indicator_interval, db_name = "RSI"):
    rsi = RSI(trading_pair, exchange_name, chart_interval, indicator_interval)
    date_and_time = (datetime.now())
    date = date_and_time.strftime("%b%d%y%H")
    ###BELOW NEEDS TO BE EDITED
    file_name = f"2-DataProcessing/data_gathered/{trading_pair}_data/{str(date)}{exchange_name}{trading_pair}interval={str(chart_interval)}tick={indicator_interval}{str(db_name)}data.db"
    try:
        #Checks to see if there's an existing db file inside the data gathering dircetory
        if exists(file_name) == True:
            #Checks to see if program returns anything
            
            connection = sqlite3.connect(file_name)
            cursor = connection.cursor()

            current_time = (datetime.now())
            formatted_time = str(current_time.strftime('"%H:%M:%S"'))
            cursor.execute(f"""INSERT INTO processed_data (time, {db_name}) VALUES ({formatted_time}, {(rsi)})""")

            connection.commit()
            connection.close() #Closing the database
        
        else: #Creates new db file
            creating_db_file(trading_pair, exchange_name, chart_interval, indicator_interval, db_name) #Creates new file

    except Exception as e: #Message email that an error on... has occured
        print(f"2-DataProcessing/Programs/{trading_pair}/Relative_Strength_Indicator_{trading_pair}interval={str(chart_interval)}tick={indicator_interval}.py has error: " + str(e))


def run(trading_pair, exchange_name, chart_interval, indicator_interval, db_name = "RSI"):
    while 1:
        try: 
            # Checks to see if program should be suspended before running due to overlap error
            path.append("ZZ-General_Functions/Programs")
            from Suspend_programs import Suspend_programs
            Suspend_programs()

            
            """ CHECKS TO SEE IF THE REQUIRED FILES ARE PRESENT, IF NOT IT WAITS"""
            # [1] Gets required filenames
            date_and_time = (datetime.now())
            live_date = date_and_time.strftime("%b%d%y%H")
            historical_date = date_and_time.strftime("%b%d%y")
            live_data_file = f"1-DataGathering/data_gathered/{trading_pair}_data/Live_Data/" + str(live_date) + exchange_name + trading_pair + "interval=" + str(chart_interval) + "kline_data.db"
            historical_data_file = f"1-DataGathering/data_gathered/{trading_pair}_data/Historical_Klines/" + str(historical_date) + exchange_name + trading_pair + "interval=" + str(chart_interval) + "kline_data.db"
            
            
            # [2] Checks to see if required files exists
            if exists(live_data_file) == True and exists(historical_data_file) == True:
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
#print(RSI("BTCUSDT", "Binance", "5m", 6))
#run("BTCUSDT", "Binance", "5m", 14)
#(run("BTCUSDT", "Binance", 1, 14, "RSI"))




